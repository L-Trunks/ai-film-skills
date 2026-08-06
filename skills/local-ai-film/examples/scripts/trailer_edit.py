# -*- coding: utf-8 -*-
"""预告片剪辑器 —— 通用拼接做不了这个，必须单独一套。

和氛围片拼接的四处根本不同：
  1. 逐镜变长（0.35–2.6s），不是统一 2.04s
  2. 硬切，不是 xfade —— ⚠ xfade duration=0 是退化参数，产出 2 秒的垃圾（踩过）
  3. 逐镜运镜（zoompan 推轨），快切段急推
  4. 音效层驱动：braam / riser / impact / whoosh / 急停静音

用法: python trailer_edit.py <films模块> <片键>
"""
import os, sys, math, subprocess, shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MOD = sys.argv[1] if len(sys.argv) > 1 else "films8"
KEY = sys.argv[2] if len(sys.argv) > 2 else "shanhai"
import importlib

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C   # 机器相关的路径全在 config.py，见同目录 README
F = importlib.import_module(MOD)
CFG = F.FILMS[KEY]

ROOT = C.ROOT
BASE = os.path.join(ROOT, CFG["dir"])
BR, CUT, OUT = os.path.join(BASE, "broll"), os.path.join(BASE, "cut"), os.path.join(BASE, "out")
FPS = 24
OW, OH = 1920, 804          # 2.39 内容
FW, FH = 1920, 1080         # 成片画幅（上下黑边）
SR = 48000


def run(cmd, quiet=False):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 and not quiet:
        print("  ffmpeg 失败:", (r.stderr or b"").decode("utf-8", "replace")[-500:])
    return r.returncode == 0


# ───────────────── 运镜 ─────────────────
def zoom_expr(kind, n):
    """返回 (z, x, y) 表达式。n = 输出帧数。
    smoothstep 缓动，避免线性推轨的机械感。"""
    p = "min(on/%d,1)" % max(1, n - 1)
    s = "(pow(%s,2)*(3-2*%s))" % (p, p)
    C = {"in": (1.00, 1.06), "IN": (1.00, 1.20), "out": (1.06, 1.00),
         "OUT": (1.20, 1.00), "up": (1.08, 1.08), "side": (1.08, 1.08),
         "shake": (1.10, 1.10), "still": (1.0, 1.0)}
    a, b = C.get(kind, (1.0, 1.0))
    z = "%.4f" % a if a == b else "(%.4f+(%.4f)*%s)" % (a, b - a, s)
    if kind == "up":            # 上摇：画面从下往上
        return z, "iw/2-(iw/zoom/2)", "ih-(ih/zoom)-(ih-(ih/zoom))*%s" % s
    if kind == "side":          # 侧移
        return z, "(iw-(iw/zoom))*%s" % s, "ih/2-(ih/zoom/2)"
    if kind == "shake":         # 手持：小幅随机抖
        return (z, "iw/2-(iw/zoom/2)+sin(on*1.7)*9", "ih/2-(ih/zoom/2)+cos(on*2.3)*7")
    return z, "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"


def cut_shot(sid, dur, trim, cam):
    src, dst = os.path.join(BR, sid + ".mp4"), os.path.join(CUT, sid + ".mp4")
    if not os.path.exists(src):
        print("  %s 源缺失" % sid); return None
    n = max(1, int(round(dur * FPS)))
    avail = (F.FRAMES - trim) / float(FPS)
    slow = dur / avail if dur > avail else 1.0
    z, x, y = zoom_expr(cam, n)
    parts = ["trim=start_frame=%d" % trim, "setpts=PTS-STARTPTS"]
    if slow > 1.001:
        # 长镜靠慢放补足；插值防顿挫
        parts = ["trim=start_frame=%d" % trim, "setpts=PTS-STARTPTS",
                 "minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:vsbmc=1" % int(FPS * slow + 2),
                 "setpts=%.5f*PTS" % slow, "fps=%d" % FPS]
    parts += ["scale=%d:%d:flags=lanczos" % (int(OW * 1.25), int(OH * 1.25)),
              "zoompan=z='%s':x='%s':y='%s':d=1:s=%dx%d:fps=%d" % (z, x, y, OW, OH, FPS),
              CFG["grade"],
              # curves 从配置读。v1 写死 '0.25/0.16' 叠上 eq 的高对比+减亮度，
              # 整片黑到看不清内容 —— 压黑要保留暗部细节，过犹不及。
              "curves=all='%s'" % CFG.get("curves", "0/0 0.25/0.22 0.75/0.84 1/1"),
              "trim=end_frame=%d" % n, "setpts=PTS-STARTPTS", "format=yuv420p"]
    ok = run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an",
              "-vf", ",".join(parts), "-c:v", "libx264", "-crf", "16",
              "-preset", "medium", "-r", str(FPS), dst])
    return dst if ok else None


def make_title(text, dur):
    dst = os.path.join(CUT, "_title.mp4")
    font = os.path.join(HERE, "kai.ttf")
    if not os.path.exists(font):
        shutil.copyfile(C.FONT, font)
    n = int(dur * FPS)
    a = "if(lt(t,0.5),t/0.5,if(lt(t,%.2f),1,max(0,(%.2f-t)/0.6)))" % (dur - 0.6, dur)
    z = "(1.00+0.05*(pow(min(on/%d,1),2)*(3-2*min(on/%d,1))))" % (n - 1, n - 1)
    vf = ("color=c=black:s=%dx%d:d=%.2f:r=%d,"
          "drawtext=fontfile=kai.ttf:text='%s':x=(w-tw)/2:y=(h-th)/2:"
          "fontsize=132:fontcolor=0xE8D9A8:alpha='%s',"
          "zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d,"
          "format=yuv420p" % (OW, OH, dur, FPS, text, a, z, OW, OH, FPS))
    os.chdir(HERE)
    return dst if run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                       "color=c=black:s=%dx%d:d=%.2f:r=%d" % (OW, OH, dur, FPS),
                       "-vf", vf.split(",", 1)[1], "-c:v", "libx264", "-crf", "16",
                       "-preset", "medium", dst]) else None


# ───────────────── 音效合成 ─────────────────
def _env(n, a=0.01, d=0.3):
    t = np.arange(n) / SR
    e = np.ones(n)
    na, nd = int(a * SR), int(d * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nd: e[-nd:] = np.linspace(1, 0, nd)
    return e


def braam(dur=2.5, f=45):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 2, 3, 4))
    x += np.random.randn(n) * 0.04
    return x * _env(n, 0.05, dur * 0.5) * 0.9


def riser(dur=4.0, f0=110, f1=1400):
    n = int(dur * SR); t = np.arange(n) / SR
    p = (t / dur) ** 1.7
    ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * p) / SR
    x = np.sin(ph) * 0.5 + np.random.randn(n) * 0.10 * p
    return x * (p ** 0.8) * _env(n, 0.2, 0.05)


def impact(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    lo = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 5)
    hi = np.random.randn(n) * np.exp(-t * 28)
    return (lo * 1.0 + hi * 0.5) * 0.95


def whoosh(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.random.randn(n)
    w = np.sin(np.pi * t / dur) ** 2
    return x * w * 0.35


def subdrop(dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 70 * np.exp(-t * 1.1) + 22
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return x * np.exp(-t * 0.7) * 1.0


def build_sfx(marks, total):
    """marks: [(时间秒, 类型, 音量)]"""
    buf = np.zeros(int((total + 3) * SR))
    G = {"braam": braam, "riser": riser, "impact": impact,
         "whoosh": whoosh, "subdrop": subdrop}
    for at, kind, vol in marks:
        s = G[kind]()
        i = int(at * SR)
        j = min(len(buf), i + len(s))
        buf[i:j] += s[:j - i] * vol
    m = np.abs(buf).max()
    if m > 0:
        buf = buf / m * 0.85
    out = os.path.join(CUT, "_sfx.wav")
    import wave
    with wave.open(out, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())
    return out


# ───────────────── 主流程 ─────────────────
def main():
    os.makedirs(CUT, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    E, order, title = CFG["edit"], CFG["order"], CFG.get("title")
    seq, marks, t = [], [], 0.0

    for sid in order:
        dur, trim, cam = E[sid]
        p = cut_shot(sid, dur, trim, cam)
        if not p:
            continue
        seq.append(p)
        # 音效编排：快切段每镜一记 whoosh，爆发段每镜一记 impact
        if dur <= 0.45:
            marks.append((t, "impact", 0.55))
        elif dur <= 0.75:
            marks.append((max(0, t - 0.06), "whoosh", 0.5))
        t += dur
        if title and sid == title["after"]:
            tp = make_title(title["text"], title["dur"])
            if tp:
                seq.append(tp)
                marks.append((t - 0.15, "subdrop", 1.0))
                t += title["dur"]

    total = t
    # 段落级音效
    marks.append((1.0, "braam", 0.5))                 # 冷开场后第一记
    marks.append((9.0, "braam", 0.6))                 # 第一幕收口
    marks.append((16.0, "riser", 0.55))               # 第二幕开始爬升
    marks.append((total * 0.62, "impact", 0.8))       # 急停前一击
    print("  %d 段 + 标题卡，总长 %.2f 秒" % (len(seq), total))

    lst = os.path.join(CUT, "_concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in seq:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    raw = os.path.join(OUT, "_raw.mp4")
    if not run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                "-i", lst, "-c", "copy", raw]):
        return

    sfx = build_sfx(marks, total)
    final = os.path.join(OUT, "成片_%s.mp4" % CFG["name"])
    bgm, vol = CFG["bgm"], CFG.get("bgm_vol", 0.20)
    af = ("[1:a]volume=%.2f,afade=t=in:st=0:d=1.5,afade=t=out:st=%.2f:d=2[b];"
          "[2:a]volume=1.0[s];[b][s]amix=inputs=2:duration=first:normalize=0[a]"
          % (vol, max(0, total - 2)))
    ok = run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-stream_loop", "-1", "-i", bgm,
              "-i", sfx, "-filter_complex",
              "[0:v]pad=%d:%d:0:(oh-ih)/2:color=black[v];%s" % (FW, FH, af),
              "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
              "-preset", "medium", "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-b:a", "192k", "-shortest", final])
    if ok:
        d = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
        print("  成片 -> %s  %.2fs" % (final, float(d)))


if __name__ == "__main__":
    main()
