---
id: ltx-2.3-q4-12g
verified: 本机实测
verified_date: 2026-07
---

# ltx-2.3-q4-12g

我这台机器的实测档。**这是本仓库唯一有真实数据的 profile。** 你的机器不同，照 `calibration.md` 测你自己的。

## 组合

| | |
|---|---|
| T2I | z-image（ComfyUI 工作流） |
| I2V | LTX-2.3-22B-distilled-1.1-Q4_K_M.gguf |
| 硬件 | RTX 4070Ti 12 GB / 32 GB RAM / Windows 11 |
| 依赖 | ComfyUI + ComfyUI-GGUF + WhatDreamsCost-ComfyUI（LTX Director） |

## 参数

```yaml
# ── 时长与尺寸 ──
max_shot_sec: 2.04          # 标定 1
frame_count: 49
fps: 24
align_to: 32                # 标定 2 —— 宽高须被 32 整除（VAE 空间压缩率）
resolutions:
  - [1280, 704]             # 16:9 横版
  - [768, 1344]             # 9:16 竖版
  - [1376, 576]             # 2.39:1 宽银幕

# ── 性能 ──
sec_per_shot: 150           # 单镜生成耗时
vram_peak_gb: 12.3
restart_each_shot: true     # 标定 3 —— 进程不释放 offload 内存
kf_batch_restart: 15        # 出图每 N 张重启

# ── 模型行为 ──
text_sensitivity: high      # 标定 4 —— 主体含文字载体必出乱码
motion_style: frozen        # 标定 5 —— 只能写「凝住的瞬间+微呼吸」
concept_blindspots:
  - 洞螈                     # 三次全出成墨西哥钝口螈
  - 山海经异兽               # 无真实照片作训练底，30镜砸6镜
  - 缺席表达                 # 「某物不在场但留下痕迹」必被补出本体
```

## `max_shot_sec: 2.04` 的由来

主体在 3.4 秒转出画面，4 秒完全漂走。取「肉眼开始察觉」的前一档 = 49 帧 / 24fps = 2.04 秒。

**这个数治不了，以下全试过无效**：

- 提示词写「不要转头」—— 只能改善
- `image_attention_strength` —— 上限就是 1.0 且默认已是 1.0，没有调高空间
- 截前 30 帧再慢放 —— 漂移是全程持续的，不是尾段突然坏
- 正放 + 倒放回旋 —— 能补时长且画面必回起点，但**摆荡感肉眼可见**，被直接指出来

**要更长只能加镜头数。**

## 派生公式

```
镜头数   = round((目标秒数 - 转场秒数) / (2.04 - 转场秒数))
切换密度 = (镜头数 - 1) / 时长 × 60
可用秒数 = (49 - trim) / 24        # 快切段取前段时用
```

转场 0.3 秒时：20 秒 ≈ 11 镜，30 秒 ≈ 17 镜，45 秒 ≈ 26 镜，60 秒 ≈ 35 镜。

## 这个 profile 排除的变量表取值

| 取值 | 为什么不行 |
|---|---|
| `tempo: 全片凝滞` | 2.04 秒上限意味着最慢也是 30 次/分，达不到凝滞观感。需 `max_shot_sec ≥ 5` |

## 一致性校验阈值

标定值见 `../knowledge/pitfalls.md` 坑 ⑥。摘要：

| 项 | 判据 | 阈值 |
|---|---|---|
| `face` | InsightFace 人脸嵌入余弦 | **0.28** |
| `env` | CLIP ViT-B-32 图像嵌入 | 0.55 |
| `scene` | 同上 | 0.65 |

依赖 `insightface` / `open_clip`，只装在 `comfyui_env` —— 跑批脚本必须用那个环境的 python，否则校验静默降级成「不检查」。

## 模型文件

`D:\ComfyUI\models\` 下：

- `LTX-2.3-22B-distilled-1.1-Q4_K_M.gguf`
- `gemma-3-12b-it-Q3_K_M.gguf`（文本编码器，**不是** text_projection）
- `LTX23_video_vae_bf16`、`LTX23_audio_vae_bf16`
- `taeltx2_3`、`ltx-2.3-spatial-upscaler-x2-1.1`

z-image 工作流：`E:\Projects\AI\popsci-studio\z-image.json`
