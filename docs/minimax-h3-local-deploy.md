# MiniMax H3 本地部署实录（12 GB 卡）

> 独立文档。不依赖本仓库其余部分，可单独阅读、单独搬运。
>
> 环境：RTX 4070 Ti 12 GB / 32 GB RAM / Windows 11 / ComfyUI + conda
> 时间：2026-08-05，H3 开源第 3 天

---

## 0. 一句话结论

**12 GB 跑得动 33B 的 H3，但 DiT 必须用官方权重，只有文本编码器能换 GGUF。**

社区给的门槛是 16 GB 用 Q4_0，12 GB 低于这条线。能过是因为权重可 offload 到系统内存 ——
代价是单镜 443 秒、内存峰值 31.7 / 31.8 GB（**余量 0.1 GB**）、分辨率降到 0.4 MP。

三条实测结论，每条都和「照着文档装」的直觉相反：

1. **DiT 不能用社区 GGUF** —— 纯 T2V 正常，但 I2V 从第 1 帧起崩坏（第 2 节）
2. **默认时长是 5.17 秒不是 5 秒**，且时长是量化网格不是自由区间（第 4 节）
3. **文字可以正面拍** —— H3 的 `text_sensitivity` 是 `low`，与 LTX 的必出乱码相反（第 8 节）

---

## 1. 前置：ComfyUI 必须 ≥ 0.30.0

H3 节点是 2026-08-03 随 ComfyUI 0.30.0 进的主线。

```bash
cd ComfyUI
git rev-parse HEAD > rollback.txt      # 先存回滚点
git fetch origin --tags
git checkout v0.30.2
```

⚠️ **`git checkout` 只更新代码，不更新 pip 依赖。**

少了这步的后果比看起来严重：`comfy_kitchen` 版本对不上时，启动日志只会说一句
「fp8 and fp4 support will not be available」，**但实际影响是官方 `int8_convrot` /
`fp8_scaled` 权重整个加载不了** —— 而报错信息完全没提这一点。

```bash
pip install "comfyui-frontend-package==1.47.12" \
            "comfyui-workflow-templates==0.11.31" \
            "comfy-kitchen==0.2.26" \
            "comfy-angle"
```

版本号以你那个 tag 的 `requirements.txt` 为准，别照抄本文。装完自检：

```python
from comfy_kitchen.tensor import TensorCoreConvRotW4A4Layout, TensorCoreFP8Layout
# 两个都能导入才说明官方 int8_convrot / fp8_scaled 权重可用
```

升级前后对比（本机）：

| | `comfy_kitchen` | 可用算子 |
|---|---|---|
| 升级前 | 0.2.10 | 无（`Failed to import comfy_kitchen`） |
| 升级后 | 0.2.26 | `TensorCoreConvRotW4A4Layout` / `TensorCoreFP8Layout` / `TensorCoreMXFP8Layout` |

### 升级会打断什么

本机 49 个自定义节点，升级后 4 个 IMPORT FAILED：

| 节点 | 原因 |
|---|---|
| ComfyUI-TeaCache | `precompute_freqs_cis` 从 `comfy.ldm.lightricks.model` 移走了 |
| ComfyUI_Yvann-Nodes | torchaudio API 变更 |
| comfyui_nyjy | 缺 gradio_client |
| nodes_glsl | 缺 comfy-angle（上面装了就好） |

`lightricks` 就是 LTX —— **升级动了 LTX 的内部模块**。所幸 `UnetLoaderGGUF / LTXDirector /
LTXVConditioning` 等 10 个节点全部健在，LTX 工作流实测未受影响。

**升级前务必存回滚点，升级后立刻查 `/object_info` 确认你依赖的节点还在。**

---

## 2. 选型：GGUF 省内存，但 DiT 不能用 GGUF

### 官方变体全表（先看清楚再选）

**DiT（`fl2va` 系列，`ref2va` 同尺寸）**

| 文件 | 体积 | 说明 |
|---|---|---|
| `bf16` | 61.73 GB | 超出 43.8 GB 总容量，装不下 |
| `pruned_bf16` | **37.46 GB** | 全精度，**仅两段式下可行** |
| `int8_convrot` | 31.70 GB | 与 pruned_int8 权重相同，**纯浪费 12 GB** |
| `pruned_int8_convrot` | **19.53 GB** | 本文采用 |
| `pruned_fp8_scaled` | **19.52 GB** | 同体积，Ada 卡原生 fp8，值得对照 |

**文本编码器**

| 文件 | 体积 |
|---|---|
| `bf16` | 47.97 GB |
| `int8_convrot` | 25.28 GB |
| **`nvfp4_awq`** | **14.61 GB** ← 官方推荐 |
| GGUF `Q4_K_M`（社区） | 13.58 GB |

### 「pruned」不是阉割

`61.73 → 37.46` 是 −39%，`31.70 → 19.53` 也是 −39%。两个精度档同一比例 ——
印证了官方说法：pruned 靠**预计算 adaLN 曲线表**瘦身。

**它省的是存储，不是能力。** 所以从 `pruned_int8` 换成 `int8_convrot` 画质零收益，
白占 12 GB。**选权重时先分清「量化档」和「打包方式」这两个正交维度。**

### 内存账

| 路线 | DiT | 编码器 | 合计 | 32 GB 内存 |
|---|---|---|---|---|
| 全 GGUF Q4_0 | 17.36 | 13.58 | 30.94 | ✓ 但 **I2V 是坏的** |
| **官方 DiT + GGUF 编码器** | **19.53** | **13.58** | **33.11** | 本文采用 |
| 官方 DiT + 官方编码器 | 19.53 | 14.61 | 34.14 | 仅大 1 GB |
| `pruned_bf16` + 官方编码器 | 37.46 | 14.61 | 52.07 | ✗ 单段式；两段式取 max=37.46 ✓ |

⚠️ 官方 `nvfp4_awq` 只有 **14.61 GB**，比社区 GGUF 编码器仅大 1 GB。
本文最初选 GGUF 编码器的理由（「官方那个 25 GB 太大」）**是记错了数** ——
25.28 GB 的是 `int8_convrot`，不是 `nvfp4_awq`。
**若重新来过，编码器应直接用官方 `nvfp4_awq`**：多 1 GB，换 AWQ 校准 + 官方支持。

### ⚠️ 实测：社区 GGUF 的 DiT 跑不了 I2V

同一套 DiT + 文本编码器 + VAE + 采样器：

| 路径 | 结果 |
|---|---|
| 纯 T2V | ✅ 完全正常，提示词逐条落实 |
| 加首帧 I2V | ❌ **第 0 帧正常，之后全是碎片** |

第 0 帧正常不能说明任何问题 —— 源码注释写明关键帧是
`re-injected every step (never denoised)`，它根本不是模型生成的。
**模型实际产出的每一帧都是废的。**

推断：坏在**关键帧注入**这一段。而它恰好是官方权重做了特殊处理的地方 ——
官方 `pruned_int8` 靠**预计算 adaLN 曲线表**比标准 int8 小 40%，属于非常规结构，
社区 GGUF 转换很可能没能正确处理。

官方立场也支持这个判断：**MiniMax 与 Comfy-Org 从未发布 H3 的 GGUF**，
社区转换是第三方实验路径，兼容性未经验证。

### 结论：DiT 必须官方，编码器随意

| 组件 | 建议 | 理由 |
|---|---|---|
| **DiT** | 官方 `pruned_int8_convrot`（19.53 GB）或 `pruned_fp8_scaled`（19.52 GB） | GGUF 版 I2V 是坏的，**没得选** |
| **文本编码器** | 官方 `nvfp4_awq`（14.61 GB） | 比社区 GGUF 只大 1 GB，AWQ 校准且官方支持 |
| VAE | 官方两个 | 无替代 |

> 本文实测走的是「官方 DiT + 社区 GGUF 编码器」，因为编码器先下好了、且 T2V 已验证可用。
> **新装机建议编码器直接用官方 `nvfp4_awq`**，省一次踩坑。

💡 **`pruned_fp8_scaled` 值得试**：与 int8 版体积完全相同（19.52 vs 19.53 GB），
而 RTX 40 系（Ada）**原生支持 fp8 张量核**。同样的内存占用下可能更快。
注意这条依赖 `comfy_kitchen` ≥ 0.2.26 —— 旧版本 fp8/fp4 支持是坏的。

⚠️ 官方 DiT 是 `int8_convrot` 格式，**依赖 `comfy_kitchen` 提供 int8/fp4 算子**。
版本对不上会直接加载失败 —— 见第 1 节，必须把 pip 依赖一起升上去。

### 下载清单

DiT 与 VAE 来自官方 [`Comfy-Org/MiniMax-H3`](https://huggingface.co/Comfy-Org/MiniMax-H3)，
文本编码器来自 [`Abiray/MiniMax-H3-GGUF`](https://huggingface.co/Abiray/MiniMax-H3-GGUF)：

| 文件 | 体积 | 放哪 |
|---|---|---|
| `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 19.5 GB | `models/diffusion_models/` |
| `text_encoders/qwen3vl_32b_minimax_h3-Q4_K_M.gguf` | 13.58 GB | `models/text_encoders/` |
| `vae/minimax_h3_video_vae_fp16.safetensors` | 4.85 GB | `models/vae/` |
| `vae/minimax_h3_audio_vae_fp32.safetensors` | 0.56 GB | `models/vae/` |

合计 38.5 GB。

`FL2VA` = first/last-frame to video+audio（收首帧和尾帧）；
`Ref2VA` = reference to video+audio（参考驱动，最多 9 图 / 3 视频 / 3 音频），按需另下。

### 省钱的诊断法：T2V / I2V 二分

怀疑某个组件坏了时，**先跑一条纯 T2V**：

- T2V 也崩 → 文本编码器或 DiT 的通用路径有问题
- T2V 正常、I2V 崩 → 关键帧注入路径的问题，**别动文本编码器**

这一条实验（7 分钟）把嫌疑从「GGUF 缺视觉塔」「Q4_0 量化太狠」两个猜测上同时洗清，
省掉了 13.58 GB 的无谓重下。**别凭猜测换权重。**

---

## 3. 三个静默失败陷阱

### ① `CLIPLoaderGGUF` 的 type 填错不报错

ComfyUI-GGUF 的实现：

```python
clip_type = getattr(comfy.sd.CLIPType, type.upper(), comfy.sd.CLIPType.STABLE_DIFFUSION)
```

**填错会静默退回 SD 类型**，不抛异常，只是出一堆垃圾。H3 必须填 `minimax`。

验证 `CLIPType.MINIMAX` 存在：

```python
import comfy.sd as S; print('MINIMAX' in [e.name for e in S.CLIPType])
```

### ② `MiniMaxH3ImageToVideo` 的 vae 收的是 video VAE

不是 audio VAE。audio VAE 只接在 `VAEDecodeAudio` 上。

### ③ 视频和音频从同一个 latent 解码

`SamplerCustomAdvanced` 输出的是 NestedTensor，同时装着视频和音频两路。
`VAEDecode` 和 `VAEDecodeAudio` **接同一个输出**，不要以为要跑两次采样。

---

## 4. 时长：不是区间，是量化网格

这是 H3 与多数模型最不一样的地方。ComfyUI 源码 `comfy_extras/nodes_minimax_h3.py`：

```python
def align_frame_count(n):
    while n % 17 != 5:
        n += 1            # 向上吸附
FPS = 24
length: default=124, min=5, max=3600, step=17
```

官方模板里秒 → 帧的换算：

```
frames = max(5, round(sec*24)) + (5 - (max(5, round(sec*24)) % 17)) % 17
```

| k | 帧 | 秒 | |
|---|---|---|---|
| 7 | 124 | **5.17** | 默认值，也是训练下限 |
| 10 | 175 | 7.29 | |
| 14 | 243 | 10.13 | |
| 21 | 362 | 15.08 | 训练上限 |

**源码 tooltip 明写「trained range is ~124-362」** —— `min=5` 只是不报错，
低于 124 帧没训练过，出什么都不奇怪。**所以 H3 的实际下限是 5.17 秒，不是 API 宣称的 4 秒。**

---

## 5. 分辨率：按百万像素选，别照抄 1344×768

官方 i2v 模板默认 **0.4 MP = 864×480**，不是原生的 1344×768。

| MP | 16:9（32 对齐） |
|---|---|
| 0.2 | 608 × 352 |
| **0.4** | **864 × 480** ← 官方默认 |
| 0.98 | 1344 × 768 |
| 2.0 | 1920 × 1088 |

**显存随分辨率是平方级、随帧数是线性。12 GB 上先降分辨率再降帧数。**

---

## 6. 工作流

管线拓扑（从官方 subgraph 的真实连接关系转出，非手搓）：

```
UnetLoaderGGUF ─┬─→ BasicScheduler(simple, 20步) ──────→ sigmas ─┐
                └─→ BasicGuider ←── conditioning ──┐             │
CLIPLoaderGGUF(type=minimax) ─→ MiniMaxH3ImageToVideo ────────────┤
VAELoader(video) ──────────────┘         └────────→ latent ───────┤
                                                                   ↓
KSamplerSelect(res_multistep) ──→ SamplerCustomAdvanced ──→ latent
                                         ├─→ VAEDecode(video vae) ─→ images
                                         └─→ VAEDecodeAudio(audio vae) ─→ audio
                                                     └→ CreateVideo(24fps) → SaveVideo
```

采样：`res_multistep` + `simple` + 20 步，`BasicGuider` **无 CFG**（蒸馏模型）。

API 格式工作流：[`minimax_h3_gguf_api.json`](../skills/local-ai-film/examples/scripts/minimax_h3_gguf_api.json)

⚠️ 无 CFG 意味着**没有负向通路** —— 与 LTX 同病，想压住什么只能写进正向提示词。
详见 [`pitfalls.md` 坑 ⑧](../skills/local-ai-film/knowledge/pitfalls.md)。

---

## 7. 内存：先把账算清楚再选方案

### 浪费在哪

| | |
|---|---|
| 文本编码器 | 13.58 GB，**只在开头编码提示词时用一次** |
| DiT | 19.5 GB，编码完成后才开始采样 |
| 两者**串行执行**，从不同时计算 | |
| **理论内存下限** | `max(19.5, 13.58)` = **19.5 GB** |
| **实际占用** | **33.08 GB** |

多出来的 13.58 GB 是纯浪费 —— 编码器用完不释放。实测佐证：全 GGUF 组合权重合计
30.94 GB，内存峰值 31.7 GB，**两个模型全程同驻**。

**19.5 GB 对 32 GB 内存是宽裕的。** 问题不在「模型太大」，在「用完不放」。

### 三个方案的取舍

| 方案 | 峰值内存 | 代价 |
|---|---|---|
| **两段式跑批** | **19.5 GB** | 要写编码缓存 + 分阶段调度，跨进程传 conditioning |
| DisTorch 钉显存 | ~29.6 GB | 改动小，但余量只剩 2 GB，且挤占激活值空间 |
| 降分辨率 / 降帧数 | 不变 | 治标不治本，且直接损失画质 |

### ⚠️ 关于「动态卸载节点能不能解决」

社区确实有这类节点（`ComfyUI-MultiGPU` 的 DisTorch2 最成熟），但要注意**方向**：

它平常的用途是**把模型层从显存挪到内存以腾出显存**。而 12 GB 卡跑 H3 时卡住的
恰恰是**内存**（31.7 / 31.8）而不是显存（11.7 / 12）—— 所以要倒过来用，
拿 `bytes` 专家模式把权重钉进显存：

```
cuda:0,3.5gb;cpu,*      # 3.5GB 权重常驻显存，其余进内存
```

但显存还得养激活值（0.4 MP × 124 帧实测约 8 GB），最多只能钉 3.5 GB 左右。

**它治标不治本** —— 真正的浪费是编码器不释放，而 DisTorch 只重新分配、不释放。
ComfyUI 0.30 新增的 `dynamic vram`（默认开）同理，管的是显存侧动态加载。

### 两段式怎么做

```
① 只加载文本编码器，把全部分镜的 conditioning 一次编码完、落盘缓存
② 杀进程（唯一可靠的释放手段，见 pitfalls 坑 ①：POST /free 返回 200 但内存纹丝不动）
③ 只加载 DiT，逐镜采样，每镜之间照样重启
```

与 LTX 流程的 `gen_keyframes` / `gen_ltx` 两段同构，重启纪律可直接复用。

⚠️ **官方 safetensors 走 mmap，页面可被系统换出；GGUF 是整块常驻。**
所以换官方 DiT 后实际驻留可能低于名义值 —— **先跑一条实测，别按名义值提前上两段式。**

---

## 8. 实测数据

标定脚本：`h3_probe.py`（三个探针对应 `calibration.md` 的标定 3c / 4 / 5）

| 项 | 值 | 备注 |
|---|---|---|
| `sec_per_shot` | **T2V 403 s / I2V 443 s** | 124 帧 @ 0.4 MP |
| `vram_peak_gb` | **11.7** | 12 GB 卡，余量 0.3 GB |
| `ram_peak_gb` | **31.7** | 31.8 GB 内存，**余量 0.1 GB** |
| `text_sensitivity` | **low** | 见下 |
| `motion_style` | 待测 | |

### `text_sensitivity: low` —— 与 LTX 完全相反

探针 C 要一块「小面馆的木质菜单板」，H3 出的是**清晰、正确的汉字招牌**，不是乱码。

| | LTX-2.3 | H3 |
|---|---|---|
| 主体能否是文字载体 | ✗ 必出乱码，只能换主体 | ✅ 可以正面拍 |

这条直接推翻了本地 AI 视频里流传最广的一条经验（「画面里别放招牌菜单，一定是乱码」）——
**它只对特定模型成立。** 换 H3 之后，招牌、菜单、标签、书封都变成可用主体。

### 与 LTX-2.3 的性能对照

| | LTX-2.3 Q4_K_M | H3 |
|---|---|---|
| 单镜耗时 | 150 s | 443 s |
| 单镜时长 | 2.04 s | 5.17 s |
| **每秒成片的生成耗时** | 73.5 s | **85.7 s** |
| 显存峰值 | 12.3 GB | 11.7 GB |
| 内存峰值 | ~31 GB | 31.7 GB |
| 音频 | 无 | 原生 32 kHz 立体声 |
| 文字 | 必乱码 | 可用 |

**按「每秒成片」折算两者成本接近**（73.5 vs 85.7 s/秒）。H3 多花的 17% 时间，
换到的是更长的单镜、原生音频、可用的文字 —— 以及镜数塌缩一个量级带来的
剪辑工作量下降。

---

## 9. 与 LTX-2.3 的取舍

| | LTX-2.3 Q4 | H3 Q4_0 |
|---|---|---|
| 权重总量 | 17 GB | 36 GB |
| 单镜时长 | 2.04 s 固定 | 5.17–15.08 s 网格 |
| 20 秒片镜数 | 11–14 | **2–3** |
| 音频 | 无 | **原生联合生成** |
| 首尾帧 | 只有首帧 | 首尾都收 |
| 单镜耗时 | 150 s | 待测 |

**镜数塌缩一个量级，意味着换的是一门语言而不是一个参数。**
14 镜的片子靠剪辑排节奏，2 镜的片子靠镜头内部调度 —— 现有剪辑骨架全部失效，
换 H3 要连骨架一起重写。
