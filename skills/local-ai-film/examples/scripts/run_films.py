# -*- coding: utf-8 -*-
"""通宵跑三部片：关键帧 → LTX（每镜重启 ComfyUI）→ 后期 → 拼片。
完全可断点续跑：已存在的产物一律跳过，中途挂了重新执行本脚本即可接上。"""
import json, os, sys, time, ctypes, shutil, subprocess, urllib.request

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib
F = importlib.import_module(os.environ.get('FILMS_MODULE','films'))

API = "http://127.0.0.1:8188"
PY_COMFY = r"D:\Software\conda\envs\comfyui_env\python.exe"
CO = r"D:\ComfyUI\output"
CI = r"D:\ComfyUI\input"
ROOT = r"E:\Projects\AI\popsci-studio\_短片"   # 所有短片统一收在这里
WF = os.path.join(HERE, "ltx_gguf_api.json")
UNET = "LTX-2.3-22B-distilled-1.1-Q4_K_M.gguf"
LOG = os.path.join(HERE, "films_comfy.log")


class M(ctypes.Structure):
    _fields_ = [('l', ctypes.c_ulong), ('mem', ctypes.c_ulong), ('tp', ctypes.c_ulonglong),
                ('ap', ctypes.c_ulonglong), ('tpg', ctypes.c_ulonglong), ('apg', ctypes.c_ulonglong),
                ('tv', ctypes.c_ulonglong), ('av', ctypes.c_ulonglong), ('ae', ctypes.c_ulonglong)]


def ram():
    m = M(); m.l = ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ap / 2 ** 30


def log(s):
    print(s, flush=True)


def kill_comfy():
    # ⚠ 必须排除自身 PID：本脚本可能也跑在 comfyui_env 下
    # （一致性模块依赖 insightface/open_clip，只装在那个环境），
    # 不排除的话每次重启 ComfyUI 会把自己一起杀掉 —— 静默退出、无 traceback（踩过）。
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process python -ErrorAction SilentlyContinue | "
                    "Where-Object {$_.Path -like '*comfyui_env*' -and $_.Id -ne %d} | "
                    "Stop-Process -Force" % os.getpid()],
                   capture_output=True)
    time.sleep(6)


def alive():
    try:
        urllib.request.urlopen(API + "/system_stats", timeout=15).read()
        return True
    except Exception:
        return False


def start_comfy():
    if alive():
        return True
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1",
               PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
    f = open(LOG, "ab")
    subprocess.Popen([PY_COMFY, "-s", r"D:\ComfyUI\main.py", "--listen", "127.0.0.1",
                      "--port", "8188", "--cache-none"],
                     cwd=r"D:\ComfyUI", env=env, stdout=f, stderr=f,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(70):
        time.sleep(5)
        if alive():
            return True
    return False


def post(url, payload, timeout=120):
    req = urllib.request.Request(API + url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def wait_job(pid, timeout=2400):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(6)
        if not alive():
            return None, "ComfyUI 挂了"
        try:
            h = json.load(urllib.request.urlopen(API + "/history/" + pid, timeout=30))
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    for m in st.get("messages", []):
                        if "error" in m[0]:
                            return None, json.dumps(m[1], ensure_ascii=False)[:300]
                    return None, "错误"
                fl = [i.get("filename") for o in h[pid].get("outputs", {}).values()
                      for i in (o.get("images", []) or [])]
                return (fl[0] if fl else None), "%.0fs" % (time.time() - t0)
        except Exception:
            pass
    return None, "超时"


# ---------- 1. 关键帧 ----------
MAX_RETRY = 4      # 同镜重抽上限，与 skill 的判停规则一致

def gen_keyframes(key, cfg):
    # cfg["consistency"] = {镜号: ["face"] / ["env","scene"] / ...}
    # 不声明的镜头零开销，完全不加载模型
    CONS = cfg.get("consistency", {})
    ATTRS = cfg.get("attrs", {})
    REFS = {}
    if CONS:
        try:
            import consistency as CN
        except Exception as e:
            log("[%s] 一致性模块加载失败，降级为不检查: %s" % (key, str(e)[:100]))
            CONS = {}
    if CONS:
        anchor = cfg.get("anchor")     # 可选：显式指定人物锚点图
        if anchor and os.path.exists(anchor):
            REFS.update(CN.build_refs(anchor, ["face"])); REFS["_anchor"] = anchor
            log("[%s] 人物锚点(显式) %s" % (key, os.path.basename(anchor)))
    todo = [(sid, p) for sid, p in cfg["shots"]
            if not os.path.exists(os.path.join(CI, "kf_%s_%s.png" % (key, sid)))]
    if not todo:
        log("[%s] 关键帧齐全，跳过" % key); return
    zwf = r"E:\Projects\AI\popsci-studio\z-image.json"
    # z-image 泄漏比 LTX 慢，但 70 张连跑同样能把 ComfyUI 撑到 17GB 常驻，
    # 把后续 LTX 的 offload 逼进页面文件 → 采样从 12s/it 掉到 120s/it（踩过）。
    # 所以每 KF_BATCH 张重启一次。
    KF_BATCH = 15
    for i, (sid, pos) in enumerate(todo):
        if i % KF_BATCH == 0:
            kill_comfy()
            if not start_comfy():
                log("[%s] ComfyUI 起不来" % key); return
            log("[%s] 关键帧批次重启  内存 %.1fGB" % (key, ram()))
        wf = json.load(open(zwf, encoding="utf-8"))
        wf["67"]["inputs"]["text"] = pos
        wf["71"]["inputs"]["text"] = cfg["neg"]
        wf["68"]["inputs"].update(width=F.W, height=F.H, batch_size=1)
        wf["70"]["inputs"]["seed"] = cfg["seed"] + int(sid[1:])
        wf["9"]["inputs"]["filename_prefix"] = "kf_%s_%s" % (key, sid)
        need = CONS.get(sid, [])
        tries = MAX_RETRY if need else 1
        okimg = None
        for attempt in range(tries):
            wf["70"]["inputs"]["seed"] = cfg["seed"] + int(sid[1:]) + attempt * 7919
            try:
                pid = post("/prompt", {"prompt": wf})["prompt_id"]
            except Exception as e:
                log("[%s] %s 提交失败 %s" % (key, sid, e)); break
            fn, info = wait_job(pid, 600)
            if not fn:
                log("[%s] 关键帧 %s 失败 %s" % (key, sid, info)); break
            cand = os.path.join(CO, fn)
            if not need:
                okimg = cand
                log("[%s] 关键帧 %s %s" % (key, sid, info)); break
            passed, sc, why = CN.check(cand, REFS, need, attrs=ATTRS.get(sid))
            tag = CN.fmt(sc)
            if passed:
                okimg = cand
                log("[%s] 关键帧 %s %s 一致性OK %s" % (key, sid, info, tag)); break
            log("[%s] 关键帧 %s 第%d次不合格(%s) → 换种子重抽" % (key, sid, attempt + 1, why))
            okimg = cand      # 全部失败时留最后一张，不阻断流程
        if okimg:
            dst = os.path.join(CI, "kf_%s_%s.png" % (key, sid))
            shutil.copyfile(okimg, dst)
            # 首张带 face 的图当锚点；声明 env/scene 的用上一镜当参考
            if need and REFS.get("_anchor") is None and "face" in need:
                REFS.update(CN.build_refs(dst, ["face"])); REFS["_anchor"] = dst
                log("[%s] 人物锚点已锁定 -> %s" % (key, sid))
            if "outfit" in need and REFS.get("outfit") is None:
                v = CN.outfit_embedding(dst)
                if v is not None:
                    REFS["outfit"] = v
                    log("[%s] 服装锚点已锁定 -> %s" % (key, sid))
            if "env" in need or "scene" in need:
                r2 = CN.build_refs(dst, [k for k in ("env", "scene") if k in need])
                REFS.update(r2)


# ---------- 2. LTX ----------
def build_ltx(key, cfg, sid):
    wf = json.load(open(WF, encoding="utf-8"))
    for v in wf.values():
        if v["class_type"] == "UnetLoaderGGUF":
            v["inputs"]["unet_name"] = UNET
        if v["class_type"] == "SaveVideo":
            v["inputs"]["filename_prefix"] = "video/%s_%s" % (key.upper(), sid)
        if v["class_type"] == "RandomNoise":
            v["inputs"]["noise_seed"] = cfg["seed"] + 500 + int(sid[1:])
    d = [v for v in wf.values() if v["class_type"] == "LTXDirector"][0]
    td = json.loads(d["inputs"]["timeline_data"])
    mv = cfg["move"][sid]
    td["global_prompt"] = mv
    td["normalDurationFrames"] = F.FRAMES
    td["segments"] = [{"type": "image", "imageFile": "kf_%s_%s.png" % (key, sid),
                       "start": 0, "length": 1, "prompt": ""}]
    d["inputs"]["timeline_data"] = json.dumps(td, ensure_ascii=False)
    d["inputs"]["global_prompt"] = mv
    d["inputs"].update(start_frame=0, end_frame=F.FRAMES, duration_frames=F.FRAMES,
                       start_second=0.0, end_second=round(F.FRAMES / 24.0, 2),
                       duration_seconds=round(F.FRAMES / 24.0, 2))
    return wf


def ltx_done(key, sid):
    vd = os.path.join(CO, "video")
    if not os.path.isdir(vd):
        return False
    return any(f.startswith("%s_%s_" % (key.upper(), sid)) and f.endswith(".mp4")
               for f in os.listdir(vd))


def gen_ltx(key, cfg):
    for sid in cfg["order"]:
        if sid not in cfg["move"]:
            continue                       # 沿用的老素材（heal 的 t01-t12）
        if ltx_done(key, sid):
            log("[%s] %s 已存在" % (key, sid)); continue
        kill_comfy()
        if not start_comfy():
            log("[%s] %s ComfyUI 起不来，中止本片" % (key, sid)); return
        try:
            pid = post("/prompt", {"prompt": build_ltx(key, cfg, sid)})["prompt_id"]
        except Exception as e:
            log("[%s] %s 提交失败 %s" % (key, sid, str(e)[:200])); continue
        fn, info = wait_job(pid)
        log("[%s] %s %s %s  内存 %.1fGB" % (key, sid, "OK" if fn else "失败", info, ram()))


# ---------- 3. 后期 + 拼片 ----------
def post_and_assemble(key, cfg):
    base = os.path.join(ROOT, cfg["dir"])
    br, out = os.path.join(base, "broll"), os.path.join(base, "out")
    os.makedirs(br, exist_ok=True); os.makedirs(out, exist_ok=True)
    vd = os.path.join(CO, "video")

    # 柔焦链必须在 RGB(gbrp) 空间：blend=screen 逐平面运算，
    # 在 YUV 下会把 U/V 也 screen，整片泛品红（踩过两次）。
    # 画幅按 cfg["canvas"] 走，默认横版 (1920,1080)；竖版填 (1080,1920)。
    # crop 用 min() 同时覆盖两种情况：
    #   横版源 1280x704(1.818) → 目标 1.778，裁宽
    #   竖版源 768x1344(0.571) → 目标 0.5625，也裁宽
    OW, OH = cfg.get("canvas", (1920, 1080))
    _r = OW / float(OH)
    vf = ("[0:v]crop=floor(min(iw\\,ih*{r})/2)*2:floor(min(ih\\,iw/{r})/2)*2,"
          "scale={ow}:{oh}:flags=lanczos,"
          "format=gbrp,split[a][b];"
          "[b]lutrgb=r='if(gt(val,170),val,0)':g='if(gt(val,170),val,0)':b='if(gt(val,170),val,0)',"
          "gblur=sigma=24[glow];"
          "[a][glow]blend=all_mode=screen:all_opacity={g:.2f},{gr},format=yuv420p[v]"
          ).format(r="%.6f" % _r, ow=OW, oh=OH, g=cfg["glow"], gr=cfg["grade"])

    ok = []
    for sid in cfg["order"]:
        dst = os.path.join(br, sid + ".mp4")
        if os.path.exists(dst):
            ok.append(sid); continue
        if sid in cfg["move"]:
            cand = [f for f in os.listdir(vd) if f.startswith("%s_%s_" % (key.upper(), sid))]
            src = os.path.join(vd, cand[0]) if cand else None
        else:                                   # heal 沿用 v2 的老素材
            cand = [f for f in os.listdir(vd) if f.startswith("V2_%s_" % sid)]
            src = os.path.join(vd, cand[0]) if cand else None
        if not src or not os.path.exists(src):
            log("[%s] %s 源缺失，跳过" % (key, sid)); continue
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an",
                            "-filter_complex", vf, "-map", "[v]", "-c:v", "libx264",
                            "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", dst],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok.append(sid)
        else:
            log("[%s] %s 后期失败 %s" % (key, sid, (r.stderr or "")[-300:]))

    if len(ok) < 2:
        log("[%s] 可用镜头不足，未拼片" % key); return
    D, T = F.FRAMES / 24.0, F.TRANS
    ins = []
    for s in ok:
        ins += ["-i", os.path.join(br, s + ".mp4")]
    parts, cur, off = [], "[0:v]", D - T
    for i in range(1, len(ok)):
        lbl = "[x%d]" % i
        parts.append("%s[%d:v]xfade=transition=dissolve:duration=%.2f:offset=%.2f%s"
                     % (cur, i, T, off, lbl))
        cur = lbl; off += D - T
    total = D * len(ok) - T * (len(ok) - 1)
    raw = os.path.join(out, "_raw.mp4")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins +
                       ["-filter_complex", ";".join(parts), "-map", cur,
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-r", "24", raw], capture_output=True, text=True)
    if r.returncode != 0:
        log("[%s] 拼接失败 %s" % (key, (r.stderr or "")[-400:])); return

    final = os.path.join(out, "成片_%s.mp4" % cfg["name"])
    af = ("[1:a]volume=%.2f,afade=t=in:st=0:d=2,afade=t=out:st=%.1f:d=2.5[a]"
          % (cfg["bgm_vol"], total - 2.5))
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-stream_loop", "-1",
                        "-i", cfg["bgm"], "-filter_complex", af, "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("[%s] 混音失败 %s" % (key, (r.stderr or "")[-400:])); return
    log("[%s] ★ 成片 %d 镜 / %.1fs -> %s" % (key, len(ok), total, final))


if __name__ == "__main__":
    keys = sys.argv[1].split(",") if len(sys.argv) > 1 else ["heal", "epic", "tomb"]
    t0 = time.time()
    for k in keys:
        cfg = F.FILMS[k]
        log("\n===== %s（%s） 开始  内存 %.1fGB =====" % (k, cfg["name"], ram()))
        try:
            gen_keyframes(k, cfg)
            gen_ltx(k, cfg)
            kill_comfy()
            post_and_assemble(k, cfg)
        except Exception as e:
            log("[%s] 异常中断: %r" % (k, e))
    kill_comfy()
    log("\n全部结束，总耗时 %.0f 分钟" % ((time.time() - t0) / 60))
