# -*- coding: utf-8 -*-
"""环境体检 —— 跑批之前先跑这个，比跑到一半才发现路径不对省事。

    python doctor.py
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C   # noqa: E402

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))


def main():
    print("=" * 62)
    print("  ai-film-skills 环境体检")
    print("=" * 62)
    rows = C.check()
    bad = 0
    for name, val, ok, hint in rows:
        mark = "OK " if ok else "!! "
        if not ok:
            bad += 1
        v = val if len(str(val)) <= 46 else "..." + str(val)[-43:]
        print("  %s %-16s %-48s" % (mark, name, v))
        if not ok:
            print("       ^ 改这里: %s" % hint)

    # ComfyUI 在不在跑
    print("-" * 62)
    try:
        with urllib.request.urlopen(C.API + "/system_stats", timeout=5) as f:
            st = json.load(f)
        dev = (st.get("devices") or [{}])[0]
        total = dev.get("vram_total", 0) / 1024 ** 3
        print("  OK  ComfyUI 在跑     %s  显存 %.1f GB" % (C.API, total))
        if total and total < 11:
            print("       ^ 显存不足 12 GB，H3 跑不动，先看 profiles/ 挑轻一点的档")
    except Exception:
        bad += 1
        print("  !!  ComfyUI 没起来   %s" % C.API)
        print("       ^ 先启动 ComfyUI，或改 AIFILM_API")

    # 模型在不在
    print("-" * 62)
    for label, sub, fn in [("LTX", "unet", C.UNET_LTX),
                           ("H3", "diffusion_models", C.UNET_H3)]:
        p1 = os.path.join(C.COMFY, "models", sub, fn)
        p2 = os.path.join(C.COMFY, "models", "diffusion_models", fn)
        ok = os.path.isfile(p1) or os.path.isfile(p2)
        print("  %s %-4s %s" % ("OK " if ok else "-- ", label, fn))
    print("=" * 62)
    if bad:
        print("  %d 项没就绪。skill 本身不受影响（它是方法论和知识），" % bad)
        print("  只有 examples/scripts/ 里的参考实现需要这些。")
    else:
        print("  全部就绪。")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
