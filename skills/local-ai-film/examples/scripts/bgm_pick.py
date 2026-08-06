# -*- coding: utf-8 -*-
"""BGM 频谱体检与选曲 —— 把「选 BGM 不能只看节奏强度」这条变成可执行的判据。

零新依赖：ffmpeg 解码 + numpy FFT，不装 librosa
（不要往跑模型的环境里塞 librosa，numba/numpy 版本冲突会毁掉 ComfyUI）。

量三项（见 knowledge/bgm-spectral.md）：
  质心 centroid  亮度
  滚降 rolloff85 高频空气感 —— 「深邃」和「发闷」的分界就在这
  低频占比        <250Hz 能量占比
另加调性判定（大调/小调）与 RMS。

⚠ 这三项量的是【音色】，量不到【有没有明确节拍】——
  一段 140BPM 的 hip-hop loop 可以和氛围 pad 有完全相同的三项指标。
  试过用谱通量自相关做节拍显著度，全频段和低频段两版都无法区分
  （纯 drone 的 Ambiment 反而高于 hip-hop loop），已放弃。
  流派筛选交给 bgm_fetch.py 的曲名排除表 + 人工试听。

用法：
  python bgm_pick.py <目录或文件> [目标档]
  目标档: fresh 清新通透 / deep 深邃有质感 / dark 压抑惊悚
"""
import os, sys, subprocess, math
import numpy as np

SR = 22050
TARGETS = {
    # 名称: (质心Hz, 滚降Hz, 低频占比, 期望调性)
    "fresh": (2000, 4200, 0.15, "major"),
    "deep":  (1400, 2960, 0.33, "minor"),
    # dark 原定 (550,440,0.61) —— 取自 Ambiment 那首「被判诡异」的曲子，
    # 是极端样本不是档位中心，实测 36 个候选全部够不着（距离 7~10）。
    # 放宽到「暗调氛围」而非「低频嗡鸣」。
    "dark":  (800,  1200, 0.55, "minor"),
}
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def decode(path, sr=SR, max_sec=180):
    """ffmpeg → 单声道 f32 PCM。stderr 不能用 text=True 读（中文 Windows 会 GBK 解码炸）。"""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-t", str(max_sec),
           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        err = (r.stderr or b"").decode("utf-8", "replace")[-200:]
        raise RuntimeError("解码失败 %s: %s" % (os.path.basename(path), err))
    return np.frombuffer(r.stdout, dtype=np.float32)


def spectrum(y, sr=SR, n_fft=2048, hop=512):
    if len(y) < n_fft:
        raise RuntimeError("音频太短")
    win = np.hanning(n_fft).astype(np.float32)
    n = 1 + (len(y) - n_fft) // hop
    n = min(n, 4000)                                  # 够统计就行，别全跑
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n)[:, None]
    frames = y[idx] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    return mag, freqs


def analyze(path):
    y = decode(path)
    rms = float(np.sqrt(np.mean(y ** 2)))
    mag, freqs = spectrum(y)
    e = mag.sum(axis=1) + 1e-9

    centroid = float(np.mean((mag * freqs).sum(axis=1) / e))

    cum = np.cumsum(mag, axis=1)
    thr = 0.85 * cum[:, -1:]
    rolloff = float(np.mean(freqs[np.argmax(cum >= thr, axis=1)]))

    low = float(np.mean(mag[:, freqs < 250].sum(axis=1) / e))

    # 调性：把能量折叠到 12 半音，比大三和弦 vs 小三和弦
    chroma = np.zeros(12)
    valid = (freqs > 55) & (freqs < 4000)
    pitch = np.zeros_like(freqs)
    pitch[valid] = 69 + 12 * np.log2(freqs[valid] / 440.0)
    pc = np.mod(np.round(pitch).astype(int), 12)
    m = mag.mean(axis=0)
    for i in range(12):
        chroma[i] = m[valid & (pc == i)].sum()
    chroma = chroma / (chroma.sum() + 1e-9)
    root = int(np.argmax([chroma[r] + chroma[(r + 4) % 12] + chroma[(r + 7) % 12] +
                          chroma[r] + chroma[(r + 3) % 12] + chroma[(r + 7) % 12]
                          for r in range(12)]))
    maj = chroma[root] + chroma[(root + 4) % 12] + chroma[(root + 7) % 12]
    mino = chroma[root] + chroma[(root + 3) % 12] + chroma[(root + 7) % 12]
    key = "%s %s" % (NOTES[root], "major" if maj >= mino else "minor")
    return dict(centroid=centroid, rolloff=rolloff, low=low, rms=rms,
                key=key, mode=("major" if maj >= mino else "minor"),
                dur=len(y) / float(SR))


def score(a, target):
    """与目标档的距离，越小越贴。三项各自归一化后加权。"""
    tc, tr, tl, tm = TARGETS[target]
    d = (abs(a["centroid"] - tc) / tc * 1.0 +
         abs(a["rolloff"] - tr) / tr * 1.4 +          # 滚降权重最高：深邃 vs 发闷的分界
         abs(a["low"] - tl) / max(tl, .05) * 0.8)
    if tm and a["mode"] != tm:
        d += 0.5
    return d


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "."
    target = sys.argv[2] if len(sys.argv) > 2 else None
    files = ([src] if os.path.isfile(src) else
             [os.path.join(src, f) for f in sorted(os.listdir(src))
              if f.lower().endswith((".mp3", ".wav", ".flac", ".m4a", ".ogg"))])
    if not files:
        print("没有音频文件"); return

    print("%-26s %8s %8s %7s %8s %-9s %s"
          % ("文件", "质心Hz", "滚降Hz", "低频", "RMS", "调性", "评价"))
    print("-" * 92)
    rows = []
    for f in files:
        try:
            a = analyze(f)
        except Exception as e:
            print("%-26s %s" % (os.path.basename(f)[:26], e)); continue
        # 自动归档
        best = min(TARGETS, key=lambda t: score(a, t))
        note = {"fresh": "清新通透", "deep": "深邃有质感", "dark": "压抑惊悚"}[best]
        if a["rolloff"] < 800:
            note += " [!!低频嗡鸣]"                  # 滚降掉到 800 以下会被判「诡异」
        rows.append((f, a, best))
        print("%-26s %8.0f %8.0f %6.0f%% %8.4f %-9s %s"
              % (os.path.basename(f)[:26], a["centroid"], a["rolloff"],
                 a["low"] * 100, a["rms"], a["key"], note))

    if target:
        tc, tr, tl, tm = TARGETS[target]
        print("\n目标档 %s：质心~%d 滚降~%d 低频~%.0f%% %s"
              % (target, tc, tr, tl * 100, tm or "调性不限"))
        print("按贴合度排序：")
        for f, a, _ in sorted(rows, key=lambda x: score(x[1], target)):
            print("   %.3f  %s" % (score(a, target), os.path.basename(f)))


if __name__ == "__main__":
    main()
