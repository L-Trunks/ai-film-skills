# -*- coding: utf-8 -*-
"""统一把成品的 BGM 提到目标 RMS。只重编码音轨，视频流直接 copy —— 几秒一部。

⚠ 目标值分两套：
  有旁白的科普片  RMS 0.05-0.06（BGM 要压在人声下面）
  无对白氛围片    RMS 0.075     （BGM 是唯一音轨，可以更饱满）
之前把前者的标准套到后者上，导致整批偏轻。

削波保护：先用 volumedetect 量 max_volume，增益上限 = -max_volume - 0.5dB。
"""
import os, re, subprocess, math, sys, glob

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C   # 机器相关的路径全在 config.py，见同目录 README

G = os.path.join(C.ROOT, "成品")
TARGET = 0.075


def rms(p):
    import librosa, numpy as np
    y, _ = librosa.load(p, sr=22050)
    return float((y ** 2).mean() ** 0.5)


def max_vol(p):
    # ⚠ 不能用 text=True：ffmpeg 在中文 Windows 上的 stderr 会让 GBK 解码炸掉，
    # 结果 max_volume 取不到默认值 -1.0，增益被误卡在 +0.5dB（踩过）。
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True)
    err = (r.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"max_volume:\s*(-?[\d.]+) dB", err)
    return float(m.group(1)) if m else 0.0


def main():
    files = sorted(glob.glob(os.path.join(G, "*.mp4")))
    for p in files:
        cur = rms(p)
        if cur <= 0:
            print("  %-30s 无音轨，跳过" % os.path.basename(p)[:28]); continue
        want = 20 * math.log10(TARGET / cur)
        head = -max_vol(p) - 0.5           # 削波余量
        gain = min(want, head)
        if gain <= 0.3:
            print("  %-30s RMS %.4f 已够，跳过" % (os.path.basename(p)[:28], cur)); continue
        tmp = p + ".tmp.mp4"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p,
                            "-af", "volume=%.2fdB" % gain,
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", tmp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("  %-30s 失败 %s" % (os.path.basename(p)[:28], (r.stderr or "")[-200:]))
            if os.path.exists(tmp):
                os.remove(tmp)
            continue
        os.replace(tmp, p)
        new = rms(p)
        cap = "（受削波限制）" if gain < want - 0.05 else ""
        print("  %-30s %.4f -> %.4f  +%.1fdB%s" % (os.path.basename(p)[:28], cur, new, gain, cap))


if __name__ == "__main__":
    main()
