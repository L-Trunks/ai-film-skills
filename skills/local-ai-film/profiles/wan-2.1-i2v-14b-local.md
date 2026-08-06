# profile: wan-2.1-i2v-14b-local

> **🔴 本档尚未标定。** 权重在本机（`Wan14Bi2vFusioniX.safetensors` 等），
> 但没有按 `calibration.md` 跑过一轮，所有数值都是**待填**。
> 直接拿来跑 = 所有秒数和镜头数都是错的。
>
> 建档的目的是说明 **Wan 系应当归入哪条路线**，以及标定时该重点量什么。

```yaml
kind: local
family: short-shot          # 与 LTX 同族，不是 H3 那种长单镜
verified: 未自测
```

---

## 为什么归入短单镜路线

Wan 2.1 / 2.2 的 I2V 与 LTX 的形态一致：

- 单次生成产出**一个连续镜头**，不支持段内硬切
- 时长以秒计（通常 5 秒档，81 帧 @16fps），远低于 H3 的 15 秒上限
- **无原生音频**，必须另配 BGM 与旁白
- 靠首帧（可选尾帧）控画面，靠剪辑排节奏

因此 Wan 直接复用短单镜路线的全部知识：
`prompt-craft.md`（关键帧 + 运动分写）、`rhythm-density`、`lock-character-reference`。

**不要读 `shot-list-prompt.md`** —— 那是长单镜路线的格式，
在不支持段内切镜的模型上写 `SHOT 1 / HARD CUT / SHOT 2` 只会得到一个混乱的镜头。

---

## 待标定字段

| 字段 | 怎么量 | 值 |
|---|---|---|
| `max_shot_sec` | 跑满帧数上限，看末段有没有崩 | ⬜ |
| `frame_grid` | Wan 常见约束是 `4k+1` 帧，需实测确认 | ⬜ |
| `native_fps` | 2.1 多为 16fps，2.2 有 24fps 变体 | ⬜ |
| `resolution` | 12 GB 显存下的稳定档 | ⬜ |
| `sec_per_run` | 单段墙钟时间，决定重抽预算 | ⬜ |
| `vram_peak` | 是否需要每镜重启（坑 ①） | ⬜ |
| `text_sensitivity` | 拍招牌/菜单会不会出乱码 | ⬜ |
| `motion_style` | `frozen` 还是 `arc` —— 决定运动提示词怎么写 | ⬜ |
| `neg_path` | I2V 时负向提示词是否真的接进采样器（坑 ⑧） | ⬜ |

`motion_style` 和 `neg_path` 这两项**必须亲自量**，
它们在 LTX 和 H3 上结论相反，不能靠"同族"推断。

---

## 本机现有权重

```
diffusion_models/
  Wan14Bi2vFusioniX.safetensors              I2V 14B，FusionX 融合版
  Wan2_1-T2V-14B_fp8_e4m3fn.safetensors      T2V 14B fp8
  Wan2_1-T2V-1_3B_bf16.safetensors           T2V 1.3B，显存友好
  WanVideo/Wan2_1_VACE_1_3B_preview_bf16.safetensors
unet/
  Wan2.2-Animate-14B-Q4_K_S.gguf             动作驱动
  Wan2.2-S2V-14B-Q3_K_M.gguf                 声音驱动
loras/
  Wan2.1_T2V_14B_FusionX_LoRA.safetensors
```

节点：`ComfyUI-WanVideoWrapper`、`ComfyUI-WanStartEndFramesNative`。
后者提供首尾帧控制 —— **链式长片需要的就是它**，见 `knowledge/chain-consistency.md`。

---

## 标定完之后要回填的地方

1. 本文件的 `⬜` 字段
2. `SKILL.md` 第 1 步的 profile 表
3. 如果 `text_sensitivity` / `motion_style` 与 LTX 不同，
   补进 `SKILL.md` 的「同一条经验在不同 profile 上结论相反」那张表
