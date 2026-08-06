# -*- coding: utf-8 -*-
"""MiniMax H3 (Hailuo 03) 适配层 —— 云端 I2V/T2V。

⚠ 未跑通验证。规格来自公开文档，端点/字段名可能与实际不符，第一次调用后按真实响应改。

存在的意义不只是「能调 API」，而是把 run_films.py 里焊死在 LTX 上的两个假设显式化：
  ① 单镜时长由 frame_count 决定    → 云端由 duration 秒数决定，且有下限
  ② 生成完要 kill 进程还内存        → 云端无进程，改成轮询任务状态

API Key 从环境变量读，不写进配置文件（明文 key 进仓库是事故）:
    setx MINIMAX_API_KEY "..."
"""
import json, os, time, urllib.request, urllib.error

API_BASE = os.environ.get("MINIMAX_API_BASE", "https://api.minimax.io")
KEY = os.environ.get("MINIMAX_API_KEY")

T2V = "minimax-h3-text-to-video"
I2V = "minimax-h3-image-to-video"
REF = "minimax-h3-reference-to-video"

# 见 profiles/minimax-h3-cloud.md —— 全部为文档值，未自测
MIN_SEC, MAX_SEC = 4, 15
PROMPT_LIMIT = 7000
ASPECTS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")


class H3Error(RuntimeError):
    pass


def _req(method, path, payload=None):
    if not KEY:
        raise H3Error("MINIMAX_API_KEY 未设置 —— 不要把 key 写进配置文件")
    url = API_BASE.rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + KEY,
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(r, timeout=120) as f:
            return json.load(f)
    except urllib.error.HTTPError as e:
        raise H3Error("%s %s -> %s %s" % (method, path, e.code,
                                          e.read()[:400].decode("utf-8", "replace")))


def submit(prompt, seconds, aspect="16:9", image_url=None,
           last_frame_url=None, model=None):
    """提交一个生成任务，返回 task_id。"""
    if not (MIN_SEC <= seconds <= MAX_SEC):
        raise H3Error("duration 必须在 %d–%d 秒之间，收到 %s" % (MIN_SEC, MAX_SEC, seconds))
    if seconds != int(seconds):
        raise H3Error("duration 只能取整秒，收到 %s" % seconds)
    if aspect not in ASPECTS:
        raise H3Error("不支持的宽高比 %s，可选 %s" % (aspect, ASPECTS))
    if len(prompt) > PROMPT_LIMIT:
        raise H3Error("提示词 %d 字，超出 %d 上限" % (len(prompt), PROMPT_LIMIT))

    body = {"model": model or (I2V if image_url else T2V),
            "prompt": prompt, "duration": int(seconds), "aspect_ratio": aspect}
    if image_url:
        body["first_frame_image"] = image_url
    if last_frame_url:                      # 首尾帧 —— 做真闭环循环片用得上
        body["last_frame_image"] = last_frame_url
    r = _req("POST", "/v1/videos/generations", body)
    tid = r.get("task_id") or r.get("id") or (r.get("data") or {}).get("task_id")
    if not tid:
        raise H3Error("响应里找不到 task_id: %s" % json.dumps(r)[:300])
    return tid


def wait(task_id, timeout=900, interval=10):
    """轮询到出结果。返回视频 URL。"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(interval)
        r = _req("GET", "/v1/tasks/%s" % task_id)
        st = (r.get("status") or (r.get("data") or {}).get("status") or "").lower()
        if st in ("success", "succeeded", "completed"):
            d = r.get("data") or r
            url = d.get("video_url") or d.get("url") or (d.get("videos") or [{}])[0].get("url")
            if not url:
                raise H3Error("任务成功但找不到视频 URL: %s" % json.dumps(r)[:300])
            return url, time.time() - t0
        if st in ("failed", "error"):
            raise H3Error("任务失败: %s" % json.dumps(r)[:300])
    raise H3Error("超时 %ds" % timeout)


def download(url, dst):
    with urllib.request.urlopen(url, timeout=300) as f, open(dst, "wb") as o:
        o.write(f.read())
    return dst


def cost_usd(seconds, n_shots=1, per_sec=0.130):
    """按文档单价估成本。云端与本地最大的差别就是这个函数在本地不存在。"""
    return round(seconds * n_shots * per_sec, 2)


if __name__ == "__main__":
    # 标定用最小样例：跑一条 4 秒（最低消费）验证端点与字段名
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else \
        "A quiet laundromat at night, fluorescent light, a steel floor drain, no people."
    print("预计成本 $%.2f" % cost_usd(4))
    tid = submit(p, 4)
    print("task", tid)
    url, el = wait(tid)
    print("完成 %.0fs -> %s" % (el, url))
