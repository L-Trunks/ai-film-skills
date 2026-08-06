---
id: minimax-h3-cloud
kind: cloud
verified: 转述（厂商与第三方文档，本仓库未自测）
verified_date: null
---

# minimax-h3-cloud

MiniMax H3 / 海螺 03（Hailuo 03）。

> 🔴 **本档所有数值来自公开文档，一次都没跑过。**
>
> 与 `ltx-2.3-q4-12g` 不同，那份是本机实测；这份是抄来的。
> **拿它开片前必须先跑 `calibration.md` 的云端分支验证**，尤其是 `motion_style` 和 `text_sensitivity`
> —— 这两项没有任何文档会写，只能自己测。

## 组合

| | |
|---|---|
| T2I | 不需要（H3 支持纯文生视频，也支持首尾帧图生视频） |
| I2V | `minimax-h3-image-to-video` |
| T2V | `minimax-h3-text-to-video` |
| 参考驱动 | `minimax-h3-reference-to-video`（最多 9 图 / 3 视频 / 3 音频） |
| 硬件 | 无（云端 API） |

## 参数

```yaml
kind: cloud

# ── 时长与尺寸 ──
max_shot_sec: 15            # 文档：4–15 秒整数
min_shot_sec: 4             # ⚠ 云端特有：有下限，本地档没有这个字段
duration_granularity: 1     # 只能取整秒
fps: 24
resolution: 2K              # 原生 1440p；文档称 768P 在入口被拒
aspect_ratios: ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
align_to: n/a               # API 收宽高比，不收像素尺寸
prompt_char_limit: 7000

# ── 成本（取代本地档的性能项）──
cost_per_output_sec_usd: 0.130
min_charge_usd: 0.52        # 4 秒起步
sec_per_shot: null          # 待测：排队 + 生成的实际墙钟时间
vram_peak_gb: n/a
restart_each_shot: n/a
kf_batch_restart: n/a

# ── 模型行为（全部待测）──
text_sensitivity: null      # 待测 —— 文档不会写
motion_style: null          # 待测 —— 15 秒时长强烈暗示 arc，但必须验
concept_blindspots: []      # 遇到一个记一个

# ── 云端特有能力 ──
native_audio: true          # 32kHz 立体声，随视频一起出
first_last_frame: true      # 首尾帧 I2V
max_ref_images: 9
max_ref_videos: 3
max_ref_audios: 3
```

## 与本地档的关键差异

### `max_shot_sec` 从 2.04 变成 15，镜头数塌缩

```
20 秒片：
  ltx-2.3-q4-12g   (20 - 0.3) / (2.04 - 0.3) ≈ 11 镜（xfade）
  minimax-h3       20 / 15 = 2 镜
```

**这不只是省事，是换了一门语言。** 14 镜的片子靠剪辑排布节奏，2 镜的片子靠镜头内部调度 —— `rhythm-density` 的疏密对比在 2 镜上无从谈起，得改用单镜内的运动设计。

⚠️ 用本档时，`directing/structures/` 里现有的三套骨架**全部不适用**：
`ambient-flat` 和 `loop-tight` 的镜数公式会算出 1–2 镜，`trailer-8seg` 的 36 镜 × 15 秒 = 9 分钟。
需要为长单镜另写骨架。

### 解锁了本地档做不到的变量表取值

| 取值 | `ltx-2.3` | `minimax-h3` |
|---|---|---|
| `tempo: 全片凝滞` | ✗ 需 `max_shot_sec ≥ 5` | ✅ 15 秒足够 |
| `time: 循环` | 勉强（靠首末镜相似） | ✅ 首尾帧 I2V 可真闭环 |
| `audio: 环境声` | ✗ 素材无声，需另配 | ✅ 原生音频直接出 |
| `audio: 声画错位` | ✗ 同上 | 🟡 有音频了，但能否错位待测 |

### 成本模型完全不同

本地：跑 35 分钟，电费忽略，**错了重跑不心疼**。
云端：20 秒片 $2.6，**重抽 5 次就是 $13**。

这直接改变 `shot-breakdown` 的判停规则 —— 本地「重抽 ≤3-5 次」是基于时间成本定的，云端要按钱重算。

## 必须自测的两项

文档永远不会写这两个，但它们决定提示词怎么写：

| 项 | 怎么测 | 为什么关键 |
|---|---|---|
| `motion_style` | `calibration.md` 标定 5 | 决定能不能写 A→B 动作弧线。15 秒模型大概率是 `arc`，但**必须验**——猜错整批提示词作废 |
| `text_sensitivity` | `calibration.md` 标定 4 | 决定主体能不能出现招牌/菜单。2K 分辨率下文字更清晰，**乱码也更明显** |

测完把 `verified` 改成 `本机实测`，并补上 `sec_per_shot`（含排队时间）。

## 来源

规格来自公开文档与第三方 API 文档聚合页，非官方一手：

- Hailuo 03 / H3 规格与限制（分辨率、时长、参考文件数、7000 字提示词上限）
- 模型 ID、端点、宽高比、计价

**这些数可能过期或不准。** 第一次调通后以实际 API 响应为准，回来改这份文件。
