---
name: local-ai-film
description: |
  用本地或云端模型生产 AI 短片（氛围片/情绪片/预告片/vlog/带对白的剧情片）。导演总控入口：管开片决策、反同质化、踩坑规避、执行流程、后期总装。
  触发场景：「做一部短片」「生成一个 XX 风格的视频」「跑一批氛围视频」「用 LTX/Wan/H3/可灵 出片」「AI 短片」「AI 剧情片」。
  风格、时长、结构每次由需求决定，不预设。模型参数由 profile 决定，不写死。
  不适用于：单张配图、已有实拍素材的剪辑。
  Produce AI short films with local or cloud models. Directing hub: shot decisions, anti-homogenization, pitfall avoidance, execution, post.
  Trigger: "make a short film" / "generate an atmospheric video" / "batch-run some AI films" / "AI trailer".
---

# 本地 AI 短片生产线

**本文档只管装配。** 内容在五个目录里：

| 目录 | 管什么 |
|---|---|
| `profiles/` | 模型能力参数。**所有秒数、尺寸、重启策略都从这里取，正文不写常数** |
| `directing/` | 反同质化：变量表、指纹库、骨架库 |
| `knowledge/` | 踩坑经验：工程坑、提示词、分镜表、链式一致性、后期、声音 |
| `examples/prompts/` | 实测过的提示词范例 |
| `examples/scripts/` | 参考实现（**我这台机器的配置，你必须改**） |

---

## 先分路：你的模型是哪一族

一切都从这里分叉。判据是 profile 的 `family`：

| | **short-shot** | **long-shot** |
|---|---|---|
| 代表 | LTX 2.3、Wan 2.1/2.2 | MiniMax H3 |
| 单次产出 | **一个连续镜头**（2–5 秒） | **一个可含 1–3 个镜头的段落**（5–15 秒） |
| 段内硬切 | 不存在 | ✅ 写 `SHOT 1 / HARD CUT / SHOT 2` |
| 节奏靠什么 | 剪辑层排每镜秒数 | 提示词层定每段塞几镜 + 剪辑层再调 |
| 原生音频 | 无 | 可能有（H3 有） |
| 写分镜读哪份 | `knowledge/prompt-craft.md` | `knowledge/shot-list-prompt.md` |
| 20 秒片 | 11–14 镜 / 11–14 次生成 | 4 段 / 8–12 镜 / 4 次生成 |

⚠️ **两族的知识互相矛盾，读知识库前先确认自己在哪一族：**

| 知识点 | short-shot | long-shot |
|---|---|---|
| 动作弧线 | ✗ 会执行过头，只能写凝住的瞬间 | ✅ 三拍动作完整执行 |
| 文字载体 | ✗ 必出乱码，只能换主体 | ✅ 可正面拍招牌菜单 |
| 关系性动作 | 不适用（单镜太短） | ✗ 抽象关系失败，**要写距离 + 朝向镜头的物理动作** |
| 段内切镜 | 不存在 | ✅ 有效 |
| 提示词文字渗漏 | 低 | **高 —— 台词、年龄、动作描述都可能被画成字幕** |

**Wan 归 short-shot**，与 LTX 同族，直接复用 LTX 那套。
但 `motion_style` / `neg_path` / `text_sensitivity` **必须亲自量**，
这三项在同族模型之间也会翻转。

---

## 再分模式：一次性 还是 链式

正交于上面的分族。**决定要不要读 `knowledge/chain-consistency.md`。**

| | **一次性** | **链式** |
|---|---|---|
| 用在哪 | 氛围片、预告片、20–60 秒 | 剧情片、3 分钟以上、同一角色贯穿 |
| 段间关系 | 各段独立，靠剪辑拼 | **尾帧接首帧**，像素级连续 |
| 主要风险 | 同质化 | **角色漂移** |
| 额外必读 | — | `knowledge/chain-consistency.md` |

链式在 short-shot 和 long-shot 上都能做，前提是 profile 的 `first_last_frame` 为真。

---

## 开片流程

**第 1–3 步是闸门，没走完不准进第 6 步。** 这不是流程洁癖 ——
旧版本因为没有闸门，四部预告片长成了同一部（详见 `directing/fingerprint.md`）。

```
1.  选 profile        → profiles/            没有匹配的？先跑 calibration.md
2.  掷变量表          → directing/variables.md
3.  查指纹            → directing/fingerprint.md   ← 撞维即重来
4.  选/写骨架         → directing/structures/      优先 use_count 小的
5.  算镜头数 / 段数    → 按 family 分两路
6.  写分镜            → prompt-craft.md 或 shot-list-prompt.md
7.  出探针            → 第一段/第一镜先看，别直接跑全片
8.  跑批              → examples/scripts/          链式的另读 chain-consistency.md
9.  后期总装          → knowledge/post-production.md
10. 验收              → knowledge/pitfalls.md 坑 ⑩ 逐条查
11. 写回指纹          → directing/films.jsonl      ← 闭环，漏了下次就失效
```

### 第 1 步：选 profile

| profile | `family` | `kind` | 单镜/单段时长 | `verified` |
|---|---|---|---|---|
| `ltx-2.3-q4-12g` | short-shot | local | 2.04 s 固定 | **本机实测** |
| `wan-2.1-i2v-14b-local` | short-shot | local | ⬜ 待标定 | 🔴 未自测 |
| `minimax-h3-local` | long-shot | local | 5.17–15.08 s（`17k+5` 网格） | 部分实测（见文件内逐项标注） |
| `minimax-h3-cloud` | long-shot | cloud | 4–15 s 整秒 | 🔴 转述，未自测 |
| `_TEMPLATE` | — | — | — | 空白 |

⚠️ **同一条经验在不同 profile 上可能结论相反。** 已知的一组：

| | `ltx-2.3-q4-12g` | `minimax-h3-local` |
|---|---|---|
| `text_sensitivity` | `high` —— 主体不能带文字载体 | `low` —— **可以正面拍招牌菜单** |
| `text_bleed` | 低 | **`any` —— 提示词里任何标签化短语都可能被画成字幕** |
| `motion_style` | `frozen` —— 只能写「凝住的瞬间」 | **`arc`** —— 完整动作弧线可执行 |
| `neg_path` | `zeroed` —— I2V 时负向词根本没接上 | 待补测 |
| 音频 | 无，需另配 BGM | **原生 32 kHz，含中文对白 + 口型同步 + 音色迁移** |

`knowledge/prompt-craft.md` 第二节（文字载体清单）**只对 `text_sensitivity: high` 的档成立**。

没有匹配的档，先走 `profiles/calibration.md`（本地五步约 40 分钟；云端跳过标定 3，改测排队与成本）。

**不做标定就开跑，所有秒数和镜头数都是错的。**

⚠️ 换 profile 不是只换几个数：
- `max_shot_sec` 差一个量级会**让现有骨架全部失效**（20 秒片在 2.04 s 档是 14 镜，在 15 s 档是 2 镜）
- 云端档要重算**重抽判停规则** —— 本地按时间成本定的「≤3–5 次」，在 $0.13/秒的模型上是几十美元
- 云端档解锁本地做不到的变量表取值，见 `directing/variables.md`

### 第 2 步：掷变量表

`directing/variables.md` 五维必填：时间结构 / 视点 / 节奏型 / 声音 / 结尾。

注意取值的状态标记 —— `⬜ 未自测` 的选项没跑过，选了要留返工预算；
`⚠️` 的有前置条件，要对照 profile 核实。

### 第 3 步：查指纹

`directing/fingerprint.md` 两层判定：

| 层 | 规则 | 范围 | 动作 |
|---|---|---|---|
| `vars` | 撞 ≥3 维 | 最近 3 部 | 重选，硬拦 |
| `structure` | 相同 | 最近 3 部 | 须给显式理由 |
| `signature` | 撞 ≥2 项 | **全部历史** | 重设计 |

当前历史里三处已知重复，新片主动避开：`ending_size: 大远景`（7/8 部）、
`shot_count: 17`（4/4 氛围片）、`structure: trailer-8seg`（4/4 预告片）。

### 第 5 步：算镜头数 / 段数

**short-shot**：

```
镜头数   = round((目标秒数 - 转场秒数) / (max_shot_sec - 转场秒数))
切换密度 = (镜头数 - 1) / 时长 × 60
```

**切换密度要提前报给用户**。`ltx-2.3-q4-12g` 下 30 秒 = 17 镜 = 32 次/分，
比常见氛围片（15 次/分）快一倍，可能被判「碎」。

**long-shot**：

```
段数 = ceil(目标秒数 / max_shot_sec)     # H3 还要吸附到 17k+5 帧网格
每段镜数 → 由片型定，见 knowledge/shot-list-prompt.md「按片型调节奏」
```

⚠️ long-shot **不报切换密度**，报「镜数曲线」，如 `1-3-3-1`（慢→密→密→慢）。

### 第 6 步：写分镜

先定题材，再写镜头。题材层的判据只有一条：

> **这个世界里的东西，模型见过真的吗？**

山海经异兽没有真实照片作底 → 30 镜砸 6 镜。
SCP 的收容间、防化服、混凝土、监控画质全是模型强项 → 几乎不砸。
**戏剧强度越高越假，普通瞬间才真。**

**两族共同的纪律**（`knowledge/prompt-craft.md` 第一、三节）：

1. 不堆「电影感/史诗/masterpiece」，换成具体摄影参数
2. 人物镜脱离通用 LOOK，换纪录片语言
3. 同一角色每段原样带同一段角色描述，**一字不改**（剪影镜也要带）
4. **配角和主角一样要有完整定妆描述，尤其是发色**（见 `chain-consistency.md` ④）
5. **描述里不写数字**（年龄、身高）—— 会被画成字幕（坑 ⑫）

**short-shot 额外**：主体里不能出现文字载体（`text_sensitivity: high` 时）；
运动提示词只能写「凝住的瞬间 + 微呼吸」。

**long-shot** 改读 `knowledge/shot-list-prompt.md`：
写时间码控切点、关系感写成「距离 + 朝向镜头的物理动作」、【导演备注】写硬规则。
现成范例在 `examples/prompts/`。

⚠️ **要后期配音的片子，台词不要写进提示词。**
只有需要口型时才写，而且音轨仍然后期重配（见 `post-production.md` 第 0 节）。

### 第 8 步：跑批

**必须「独立进程 + Monitor」两件套**（坑 ⑦）。
普通后台任务实测 8 分钟就被会话回收，Monitor 的过滤必须覆盖失败路径。

**长跑脚本必须加 mkdir 互斥锁**（坑 ⑭）——
没有锁的话，一次失败的「杀掉重启」就会变成两条流水线抢同一个 GPU 端口。

配置写法见 `examples/scripts/_example_films.py`。**完全可断点续跑** —— 已存在的产物一律跳过。

链式跑批另读 `knowledge/chain-consistency.md`，那里有锚定密度、空镜清单、尾帧抽法。

### 第 9 步：后期总装

`knowledge/post-production.md`，顺序不能颠倒：

```
剥掉模型音频 → 掐头去尾修接缝 → 变节奏剪辑 → 按段分治超分 → 统一调色 → 旁白 → BGM → 字幕 → 总装
```

三条最容易漏的：

- **concat 前必须 `setpts=N/FPS/TB`**，否则静默丢帧、音画累积漂移（坑 ⑪）
- **超分要按段分治**，人脸 < 110px 的段走原生放大，否则脸会被拧变形（坑 ⑮）
- **时间轴按磁盘实测**，不能用计划值推算

### 第 11 步：写回指纹

追加一行到 `directing/films.jsonl`。**漏了整套反同质化机制静默失效。**

---

## 什么时候调卫星 skill

| 卡在哪 | 调谁 |
|---|---|
| 只说得出「氛围感/电影感」，写不出提示词 | `emotion-to-camera-language` |
| 角色基准形象跑不稳、换机位就变脸 | `lock-character-reference` |
| 批量出图后不知道怎么筛、该不该重抽 | `shot-breakdown` |
| 镜间秒数怎么排、疏密怎么对比 | `rhythm-density` |
| 想要的镜头做不出来，手上没对应素材 | `material-driven-storyboard` |

卫星也可被单独触发，不必经过中枢。但**反同质化闸门只在中枢**。

⚠️ **五个卫星都是为 short-shot 蒸馏的**，在 long-shot 上部分失效：

| 卫星 | long-shot 上 |
|---|---|
| `rhythm-density` | 🟡 疏密比例仍成立，但秒数按 `max_shot_sec` 重算；节奏改由「每段镜数」控制 |
| `lock-character-reference` | 🟡 一次性片用角色前缀就够；**链式片反而更需要它** —— 见 `chain-consistency.md` |
| `shot-breakdown` | 🟡 一次生成 5 秒素材，判停规则要按段而非按镜重算 |
| `emotion-to-camera-language` | ✅ 四件套仍适用，是分镜表里「画面」那行的写法 |
| `material-driven-storyboard` | ✅ 「凑不出来就改故事」与路线无关 |

---

## 可选：一致性自动校验

**默认不开。** 用户明确提出「人物要一致」「环境要连得上」时才配。

```python
"consistency": {
    "s02": ["face"],                 # 必须是同一个人
    "s06": ["env"],                  # 同一个世界/季节/时段
    "s07": ["scene"],                # 同一个具体地点（比 env 严）
},
"anchor": r"...\kf_xxx_s01.png",     # 可选，显式指定人物锚点
```

生成即验，不合格自动换种子重抽（上限 4 次）。不声明的镜头**零开销**。

阈值必须本机标定，**别抄真人照片的 0.5+** —— AI 生成的同一角色相似度天然偏低（坑 ⑥）。

链式长片不要依赖这套 —— 漂移是渐进的，逐段阈值判定抓不住。用定期重锚定。

---

## 可选：镜头标注 / 字幕

**氛围片默认不加字。** 之前加字幕被判「不高级」。

**剧情片要加**，但用 ASS + libass，不要用 `drawtext`（本机会段错误，坑 ⑯）。
写法见 `post-production.md` 第 6 节 —— 注意 `Format` 行必须写完整 10 个字段，
少写会让每行字幕前面凭空多一个逗号。

---

## 产出位置

```
<输出根>/
├── 成品/        所有成片，编号即时间顺序
└── <片名>/      broll/（逐镜后期素材）+ out/（该片成片）
```

输出根在 `examples/scripts/run_films.py` 的 `ROOT` 里，**改成你自己的**。

废弃产物统一移到一个回收目录，不要散建 —— 中间产物（裁剪版/超分版/剪辑版）
在定稿前不要删，删了要从头重跑生成。
