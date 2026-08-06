---
id: <t2i>-<i2v>-<硬件简写>
kind: local        # local | cloud
family: short-shot # short-shot（LTX / Wan 这类，单次一个连续镜头）
                   # long-shot （H3 这类，单次一个可含多镜头的段落）
                   # 这一项决定走哪条路线，比 max_shot_sec 更直接
verified: 未自测
verified_date: null
---

# <profile 名>

> 复制本文件改名。五个标定值照 `calibration.md` 逐项测出来填，**别抄别的 profile**。
>
> `verified` 只有两个合法值：`本机实测` / `转述`。没测过的字段留 `null`，不要猜。

## 组合

| | |
|---|---|
| T2I | |
| I2V | |
| 硬件 | |
| 依赖 | |

## 参数

**不适用的字段填 `n/a`，不要填 `null`。** `null` 意思是「待测」，`n/a` 意思是「这个概念在本档不存在」——
云端档没有显存和重启策略，本地档没有单镜下限和每秒计价，混在一起会让人以为还没测。

```yaml
# ── 时长（三种形态，只填其中一种）──
# A. 固定单值   —— LTX 这类：frame_count: 49
# B. 自由区间   —— 云端 API 这类：min_shot_sec / max_shot_sec + duration_granularity
# C. 量化网格   —— MiniMax H3 这类：frames = step·k + base，且要向上吸附
frame_count: null           # 形态 A
min_shot_sec: n/a           # 形态 B
duration_granularity: n/a   # 形态 B
frame_grid: n/a             # 形态 C，如 {base: 5, step: 17}
frame_trained_range: n/a    # 形态 C：允许范围 ≠ 训练范围，超出不报错但结果不可控
max_shot_sec: null          # 标定 1（三种形态都要有）
fps: null
align_to: null              # 标定 2（云端若只收宽高比则填 n/a）
resolutions:
  - [, ]                    # 16:9
  - [, ]                    # 9:16
  - [, ]                    # 2.39:1
prompt_char_limit: n/a      # 云端常有上限

# ── 性能 / 成本（二选一填，另一组填 n/a）──
sec_per_shot: null          # 本地=生成耗时；云端=排队+生成的墙钟时间
vram_peak_gb: null          # 云端 n/a
restart_each_shot: null     # 标定 3；云端 n/a
kf_batch_restart: null      # 云端 n/a
cost_per_output_sec_usd: n/a   # 云端必填
min_charge_usd: n/a            # 云端有起步价时填

# ── 模型行为（两类档都必测，文档不会写）──
text_sensitivity: null      # 标定 4 —— high / medium / low
                            # high = 主体带文字必出乱码；low = 可以正面拍招牌
motion_style: null          # 标定 5 —— frozen / arc / static
in_shot_cut: null           # 段内能否硬切（写 SHOT 1 / HARD CUT / SHOT 2 是否生效）
                            # 这是 short-shot / long-shot 的分界
text_bleed: null            # ★ 提示词里的文字会不会被画进画面（坑 ⑫）
                            # none / quoted（只渲染引号内容）/ any（任何标签化短语）
                            # text_sensitivity 低的档往往 text_bleed 高 —— 两回事，都要测
neg_path: null              # I2V 时负向提示词是否真的接进采样器（坑 ⑧）
                            # 值：connected / zeroed / absent。zeroed 表示白写
concept_blindspots: []      # 遇到一个记一个

# ── 链式长片能力（要跑几十段接成一部片时必测）──
first_last_frame: null      # 是否支持首/尾帧控制。链式的前提
chain_drift_segs: null      # 不重锚定的话，几段之后角色开始漂（实测 H3 是 6 段以内）
                            # 决定重锚定的密度，见 knowledge/chain-consistency.md

# ── 音频（有原生音频的档才填）──
native_audio: n/a           # 采样率 / 是否含对白 / 是否口型同步
voice_clone: n/a            # 是否支持音色迁移，走哪条权重
max_ref_images: n/a
cost_per_output_sec_usd: n/a
```

## `max_shot_sec` 的由来

记下标定 1 的观察：几秒开始漂、几秒完全失控、试过哪些无效的补救。

**这一段是给三个月后的自己看的** —— 不写，下次会重新试一遍同样无效的办法。

## 派生公式

```
镜头数   = round((目标秒数 - 转场秒数) / (max_shot_sec - 转场秒数))
切换密度 = (镜头数 - 1) / 时长 × 60
可用秒数 = (frame_count - trim) / fps
```

常用时长对照（转场 0.3 秒）：

| 目标时长 | 镜头数 | 切换密度 |
|---|---|---|
| 20 s | | |
| 30 s | | |
| 60 s | | |

## 这个 profile 排除的变量表取值

对照 `../directing/variables.md` 里带 ⚠️ 的取值，逐条判断本 profile 能否满足。

| 取值 | 能否 | 为什么 |
|---|---|---|
| `tempo: 全片凝滞` | | 需 `max_shot_sec ≥ 5` |

## 一致性校验阈值

如果用嵌入相似度做自动校验，**阈值必须本机标定**，别抄真人照片的经验值（见 `../knowledge/pitfalls.md` 坑 ⑥）。

| 项 | 判据 | 同一角色实测 | 不同角色实测 | 取值 |
|---|---|---|---|---|
| `face` | | | | |
| `env` | | | | |
| `scene` | | | | |

## 模型文件

列出路径与文件名，方便复现和排查。
