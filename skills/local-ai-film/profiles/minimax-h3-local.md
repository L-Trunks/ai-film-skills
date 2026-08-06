---
id: minimax-h3-local
kind: local
verified: 本机实测
verified_date: 2026-08-05
---

# minimax-h3-local

MiniMax H3 / 海螺 03 开源权重，本地 ComfyUI 跑。2026-08-03 开源，同日 ComfyUI 原生支持。

> **已在 RTX 4070Ti 12GB / 32GB RAM 上端到端跑通**，T2V 与 I2V 均验证通过。
> 时长网格、画布、帧数范围读自 ComfyUI 源码（`comfy_extras/nodes_minimax_h3.py`），
> 性能与模型行为为本机实测。仅 `motion_style` 尚未标定。

## 组合

| | |
|---|---|
| DiT | **`minimax_h3_fl2va_pruned_int8_convrot.safetensors`（19.53 GB，官方）** |
| 文本编码器 | `qwen3vl_32b_minimax_h3-Q4_K_M.gguf`（13.58 GB） |
| Video VAE | `minimax_h3_video_vae_fp16.safetensors`（4.85 GB） |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors`（0.56 GB） |
| 硬件 | RTX 4070Ti 12 GB / 32 GB RAM |
| 依赖 | **ComfyUI ≥ 0.30.0** + ComfyUI-GGUF |

节点：`EmptyMiniMaxH3LatentAV` / `MiniMaxH3ImageToVideo` / `MiniMaxH3ReferenceToVideo` / `MiniMaxH3SigmaShift`

## 参数

```yaml
kind: local

# ── 时长：不是单值也不是区间，是量化网格 ──
fps: 24
frame_grid: {base: 5, step: 17}     # frames = 17k + 5，源码 align_frame_count 向上吸附
frame_default: 124                  # ≈ 5.17 s ← 这就是「H3 默认 5 秒」的由来
frame_trained_range: [124, 362]     # 5.17 – 15.08 s，源码 tooltip 明示
frame_hard_range: [5, 3600]         # 允许但未训练，低于 124 出什么都不奇怪
max_shot_sec: 15.08                 # 362 帧
min_shot_sec: 5.17                  # 124 帧 —— 实际下限，不是 API 宣称的 4 秒

# ── 尺寸：按百万像素选，不是按固定分辨率 ──
align_to: 32
canvas_recommended_12g: [864, 480]  # 0.4 MP —— 官方模板默认值，不是 1344×768
canvas_native: [1344, 768]          # 0.98 MP，短边 768 的原生画布
megapixels_default: 0.4

# ── 采样（官方模板值）──
sampler: res_multistep
scheduler: simple
steps: 20
cfg: n/a                            # BasicGuider 无 CFG，蒸馏模型没有负向通路

# ── 性能（124帧 @ 0.4MP 实测）──
sec_per_shot: 475                   # 官方 DiT，124帧 @ 0.4MP，I2V
vram_peak_gb: 11.5                  # 12GB 卡
ram_peak_gb: 31.2                   # 31.8GB 内存 —— 名义 33.11GB，实际更低
                                    # 因为官方 safetensors 走 mmap，页面可被换出；
                                    # 全 GGUF 组合名义 30.94GB 反而占到 31.7GB
restart_each_shot: true             # 余量仍然只有 0.6GB，每镜重启
kf_batch_restart: n/a               # H3 不需要单独出关键帧，可纯 T2V

# ── 模型行为 ──
text_sensitivity: low               # 实测：菜单板出了清晰正确的汉字，与 LTX 的必出乱码相反
motion_style: null                  # 待测（探针 B）
concept_blindspots: []

# ── 云端 API 才有的能力，本地也具备 ──
native_audio: true                  # 视频音频联合生成，32kHz
first_last_frame: true              # MiniMaxH3ImageToVideo 收 first_frame / last_frame
max_ref_images: 9
max_ref_videos: 3
max_ref_audios: 3
```

## 时长网格怎么算

源码（`comfy_extras/nodes_minimax_h3.py`）：

```python
def align_frame_count(n):
    while n % 17 != 5:
        n += 1                       # 向上吸附，要 100 帧会给你 107
FPS = 24
```

常用档位：

| k | 帧数 | 秒 | 备注 |
|---|---|---|---|
| 7 | 124 | 5.17 | **默认**，训练下限 |
| 10 | 175 | 7.29 | |
| 14 | 243 | 10.13 | |
| 21 | 362 | 15.08 | 训练上限 |

**镜数公式必须吸附到网格**，不能直接用秒数除：

```
frames  = align(round(目标秒数 × 24))     # 向上到 17k+5
实际秒数 = frames / 24
```

## 分辨率按百万像素选（官方对照表）

**别照抄 1344×768。** 官方 i2v 模板的默认是 **0.4 MP = 864×480**，12 GB 卡应该从这里起步。

| MP | 16:9 输出（32 对齐） |
|---|---|
| 0.2 | 608 × 352 |
| 0.3 | 736 × 416 |
| **0.4** | **864 × 480** ← 官方默认 |
| 0.5 | 960 × 544 |
| 0.7 | 1152 × 640 |
| 0.98 | 1344 × 768 |
| 1.0 | 1376 × 768 |
| 2.0 | 1920 × 1088 |

分辨率对显存的影响是平方级，而 `frame_count` 是线性。**12 GB 上先降分辨率再降帧数。**

## 官方管线拓扑

```
UnetLoaderGGUF ─┬─→ BasicScheduler(simple, 20) ─→ sigmas ─┐
                └─→ BasicGuider ←─ conditioning ─┐        │
CLIPLoaderGGUF(type=minimax) ─→ MiniMaxH3ImageToVideo ─────┤
VAELoader(video) ──────────────┘         └─→ latent ───────┤
                                                            ↓
KSamplerSelect(res_multistep) ─→ SamplerCustomAdvanced ─→ latent
                                        ├─→ VAEDecode(video vae) ─→ images
                                        └─→ VAEDecodeAudio(audio vae) ─→ audio
                                                    └─→ CreateVideo(24fps) ─→ SaveVideo
```

五条容易踩的：

1. **`MiniMaxH3ImageToVideo` 的 `vae` 收的是 video VAE**，不是 audio VAE
2. **视频和音频从同一个 latent 解码** —— NestedTensor 同时装两路，别以为要跑两次采样
3. **`CLIPLoaderGGUF` 的 `type` 必须填 `minimax`** —— ComfyUI-GGUF 的实现是
   `getattr(comfy.sd.CLIPType, type.upper(), CLIPType.STABLE_DIFFUSION)`，
   **填错会静默退回 SD 类型**，不报错，只是出一堆垃圾
4. ★ **首帧必须先过 `ImageScaleToTotalPixels` + `GetImageSize`**，用缩放后的实际尺寸当
   `width`/`height`，**不能手填**。省掉这两个节点的实测后果见下方「踩坑记录」
5. **`ImageScaleToTotalPixels` 的 `resolution_steps` 在 API 格式下是必填的**，
   不会用默认值，漏了直接 `HTTP 400 required_input_missing`。取 32 对齐 `align_to`

工作流见 `../examples/scripts/minimax_h3_api.json`（官方 DiT + GGUF 编码器）。

⚠️ **DiT 绝不能用社区 GGUF。** 实测 `MiniMax-H3-FL2VA-Q4_0.gguf` 的纯 T2V 完全正常，
但 I2V 从第 1 帧起崩坏 —— 关键帧注入路径被转换破坏了（官方 pruned int8 用预计算 adaLN
曲线表，属非常规结构）。官方从未发布 GGUF。文本编码器用 GGUF 没问题，实测正常。

### 踩坑记录：省掉首帧缩放 → I2V 从第 1 帧起崩坏

第一版工作流直接把 1280×704 的关键帧喂给节点、`width`/`height` 手填 864×480。结果：

| 帧 | 内容 |
|---|---|
| 0 | 正常（这是被钉住的关键帧，源码注释：`re-injected every step, never denoised`） |
| 41 / 82 / 123 | **完全不相干的场景 + 严重伪影** |

**「第 0 帧对、后面全错」是这个故障的特征signature** —— 因为第 0 帧根本不是模型生成的。

定位方法：**跑一条纯 T2V**。
- T2V 也崩 → 文本编码器或 DiT 的问题
- T2V 正常 → 首帧注入通路的问题（本例即此）

实测 T2V 完全正常（提示词逐条落实），一次就把嫌疑从「GGUF 缺视觉塔」「Q4_0 量化太狠」
这两个猜测上洗清了。**别凭猜测换权重，先做这个二分实验。**

## 12 GB 卡上的内存：不用两段式

名义算术很吓人，实测反而更宽松：

| 组合 | 名义合计 | **实测内存峰值** |
|---|---|---|
| 全 GGUF（DiT 17.36 + TE 13.58） | 30.94 GB | **31.7 GB** |
| **官方 DiT 19.53 + GGUF TE 13.58** | **33.11 GB** | **31.2 GB** ← 更低 |

**名义大 2.2 GB，实际占用反而小 0.5 GB。** 原因是官方 safetensors 走 mmap，
页面可被系统换出；GGUF 是整块常驻内存。

结论：**单段式即可，不需要两段式跑批。** 本来准备实现的编码缓存方案用不上了。

⚠️ 但余量只剩 0.6 GB，`restart_each_shot: true` 仍然必须 ——
见 `../knowledge/pitfalls.md` 坑 ①，ComfyUI 任务结束不释放 offload 内存。

⚠️ 若要上 `pruned_bf16`（37.46 GB）或更高分辨率，两段式会重新变成必需。

## 与 `ltx-2.3-q4-12g` 的差异（换档必读）

| | LTX | H3 |
|---|---|---|
| 单镜时长 | 2.04 s 固定 | 5.17–15.08 s 网格 |
| 20 秒片镜数 | 11–14 | **2–3** |
| 音频 | 无 | 原生联合生成 |
| 首尾帧 | 只有首帧 | 首尾都收 |
| 权重总量 | 17 GB | 31 GB |

**镜数塌缩一个量级，`directing/structures/` 三套骨架全部失效。**
`ambient-flat` / `loop-tight` 会算出 1–2 镜，`trailer-8seg` 的 36 镜 × 5.17 s = 3 分钟。
用本档要先写新骨架，见 `../directing/structures/_TEMPLATE.md` 的「前置要求」段。

⚠️ 反过来，H3 解锁了 LTX 做不到的：`tempo: 全片凝滞`（需 ≥5 s）、`audio: 环境声`（原生音频）、
`time: 循环`（首尾帧真闭环）。见 `../directing/variables.md`。

## `text_sensitivity: low` —— 与 LTX 相反，这条要改写作习惯

探针 C 纯 T2V 要一块「小面馆的木质菜单板」，H3 出的是**清晰、正确的汉字招牌**，不是乱码。

| | LTX-2.3 | H3 |
|---|---|---|
| `text_sensitivity` | `high` | **`low`** |
| 主体能不能是文字载体 | ✗ 必出乱码，只能换主体 | ✅ 可以直接拍 |

⚠️ **`../knowledge/prompt-craft.md` 第二节「文字载体清单 / 改法是换主体不是加负向」
在本 profile 上不适用。** 招牌、菜单、标签、书封这些在 H3 上是可用主体，
甚至是优势 —— 《自助洗衣店》为了躲文字绕开的那些镜头（控制面板、价目表），H3 上可以正面拍。

这也是 profile 机制的价值示例：同一条「知识」在不同模型上结论相反，
写死在正文里必然误导，挂在 profile 上才成立。

## 性能对照

| | LTX-2.3 Q4_K_M | **H3 官方 DiT** |
|---|---|---|
| 单镜耗时 | 150 s | **475 s** |
| 单镜时长 | 2.04 s | 5.17 s |
| **每秒成片的生成耗时** | 73.5 s | **91.9 s** |
| 显存峰值 | 12.3 GB | 11.5 GB |
| 内存峰值 | 约 31 GB | 31.2 GB |
| 音频 | 无 | 原生 32 kHz 立体声 |
| 文字 | 必乱码 | 可正面拍 |

**按「每秒成片」折算，H3 比 LTX 贵 25%**（91.9 vs 73.5 s/秒）。
换来的是更长的单镜、原生音频、可用的文字，以及镜数塌缩一个量级带来的剪辑量下降。

## 待办

- [x] ~~跑通一条 124 帧确认端到端可用~~ —— T2V 通过
- [x] ~~标定 `text_sensitivity`~~ —— `low`
- [x] ~~测 `sec_per_shot` 与 `vram_peak_gb`~~
- [x] ~~I2V 验证~~ —— 官方 DiT 通过，124 帧全程稳定
- [x] ~~两段式跑批~~ —— **不需要**，实测单段式内存 31.2/31.8 GB
- [ ] 标定 `motion_style`（探针 B）
- [ ] 试 `minimax-h3-velocity-cache-v1` 采样器与 SageAttention 的提速幅度
- [ ] 为 H3 写新骨架（现有三套的镜数公式在 5.17s 单镜下全部失效）
