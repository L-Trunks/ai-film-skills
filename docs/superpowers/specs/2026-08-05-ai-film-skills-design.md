# ai-film-skills 设计文档

日期：2026-08-05
状态：待评审

---

## 0. 起因

现有 `local-ai-film` skill 跑出了两个具体问题，本项目为解决它们而重构并开源。

### 问题一：产出同质化

SCP 三部曲与《山海》在结构上几乎完全一致，这不是主观感受，可以在代码里指到行：

- `_example_trailer_scp.py:284` 的 `_edit(p)` 是 `_example_trailer.py:152` 那份手写 EDIT dict 的函数化副本，开头同为 `(2.6,"in") (2.6,"out") (2.4,"in")`，同为 1376×576 / canvas 1920×804 / TRANS=0
- 三部 SCP 之间逐镜同构：

  | 位置 | 收容失效 | 站点档案 | 异常现场 |
  |---|---|---|---|
  | 25（急停） | 摘眼镜擦汗，近乎全黑 | 摘口罩深吸气，近乎全黑 | 摘面具喘气，近乎全黑 |
  | 26 | 汗珠滑落反红光 | 瞳孔缓缓放大 | 睁大的眼映火光 |
  | 27 | 警报灯扫过镜头 | 指示灯变红 | 探照灯扫过镜头 |
  | 36 | 大远景荒野通风口 | 大远景灰色办公楼 | 大远景公路车开走 |

**根因**：`SKILL.md:420-426` 把「冷开场3 → 建立6-7 → 推进8-9 → 加速8-9 → 急停2 → 爆发6-7 → 标题 → 收尾3-4」写进了正文。它是一次成功的创作选择，被误当成物理定律固化，于是每部片都长一个样。

**已证无效的对策**：`SKILL.md:10` 已经写了「风格和时长不预设，每次现想」。SCP 照样长成山海。**劝告词不是约束**，约束必须可执行、可判定、有拦截动作。

### 问题二：模型焊死

- `run_films.py:13-19` — conda python 路径、`D:\ComfyUI`、UNET 文件名、输出根目录全部硬编码
- `run_films.py:140-144` — 按节点号改 z-image 工作流：`wf["67"]` 正向、`wf["71"]` 负向、`wf["70"]` seed、`wf["9"]` 文件名。换工作流即全错
- `run_films.py:195-206` — 依赖 `LTXDirector` 这个 class_type 及其 `timeline_data` JSON schema
- `FRAMES=49` / 2.04 秒是 LTX-2.3 在 12G 卡上的物理限制，却渗进了配置格式、镜头数公式、剪辑表

换 Flux/SDXL 出图或换 Wan / 可灵 生视频，等于重写 `gen_keyframes` 和 `build_ltx`。

### 问题三（重构中发现）：硬约束这个概念本身是错的

`local-ai-film` 说「2.04 秒硬顶」，`rhythm-density` 说「10 秒硬顶」。两个 skill 各自把自己那台机器/那个平台的数当成普适真理，靠 `contrasts-with` 关系互相打补丁。

**两个数都不是硬约束，都是 profile 属性。**

---

## 1. 目标与非目标

### 目标

1. 让同质化在流程上被拦截，而不是靠提醒
2. 让「换模型」成为改一个 profile 文件的事，而不是改代码
3. 把六个 skill 打包成一个可开源的套件，核心资产（踩坑经验）能被别人直接用上

### 非目标

- **不做可安装的工具包。** 不抽 provider 接口、不发 pip 包、不做 CLI。别人的机器路径、模型、显存都不同，`run_films.py` clone 下来必然跑不起来；维护跨机器兼容性的成本远超收益。脚本以「参考实现」身份提供，明确标注需按自己机器改。
- **不预置未实测的模型参数。** 只有 z-image + LTX-2.3 是真跑过的。Wan / HunyuanVideo / 可灵 / 即梦 的参数不写，写了就是编的，开源后被发现参数是抄文档的反而伤信任。
- **不重写五个卫星 skill 的方法论。** 只做三处必要改动（见 §5）。

---

## 2. 架构：中枢 + 卫星（方案 A）

`local-ai-film` 升级为唯一导演入口，承担「开片仪式」；五个卫星保持独立可触发。

**为什么门放在中枢而不是别处**：

- 六个平权 + 共享 context 文件 → 用户从 `shot-breakdown` 进来，反同质化门就没走，等于把现在的失败模式固化
- 独立 preflight gate skill → 约束最硬，但多一次跳转，真实使用中活不过一周就被绕开
- 中枢 → 门放在「开片」这个天然存在的动作上，绕不过去也不烦

### 目录结构

```
ai-film-skills/
├── README.md                      # 中文（主）
├── README.en.md                   # 英文
├── LICENSE                        # CC-BY-4.0（内容为主的仓库）
├── ATTRIBUTION.md                 # 五个蒸馏 skill 的出处
│
├── skills/
│   ├── local-ai-film/             # 中枢
│   │   ├── SKILL.md               # 装配流程 + 索引，瘦身到 ~120 行
│   │   ├── knowledge/
│   │   │   ├── pitfalls.md        # 七个坑
│   │   │   ├── prompt-craft.md    # 去AI味 / 缺席表达 / 文字载体 / 运动提示词
│   │   │   └── bgm-spectral.md    # 三档频谱参数 + RMS 双标准
│   │   ├── directing/
│   │   │   ├── variables.md       # 正交变量表
│   │   │   ├── fingerprint.md     # films.jsonl 格式 + 撞维判定
│   │   │   └── structures/
│   │   │       ├── trailer-8seg.md
│   │   │       └── _TEMPLATE.md
│   │   ├── profiles/
│   │   │   ├── ltx-2.3-q4-12g.md
│   │   │   ├── _TEMPLATE.md
│   │   │   └── calibration.md
│   │   ├── test-prompts.json      # 新增，现在没有
│   │   └── examples/scripts/      # 现有 py + 「这是我的机器配置」警告
│   │
│   ├── emotion-to-camera-language/
│   ├── lock-character-reference/
│   ├── shot-breakdown/
│   ├── rhythm-density/
│   └── material-driven-storyboard/
│
└── docs/
    ├── how-skills-differ.md
    └── gallery.md
```

### 开片流程（中枢 SKILL.md 的主体）

```
1. 选 profile          → profiles/
2. 掷变量表            → directing/variables.md
3. 查指纹              → directing/fingerprint.md   ← 撞维即重来
4. 选/写骨架           → directing/structures/
5. 算镜头数            → 公式取 profile 变量，不写常数
6. 写分镜              → 调 emotion-to-camera-language
7. 出探针图            → 调 shot-breakdown
8. 跑批                → examples/scripts/
9. 验收                → knowledge/pitfalls.md 逐条查
10. 写回指纹           → films.jsonl              ← 闭环，漏了下次就查不到
```

第 1-3 步未完成时，中枢拒绝进入第 6 步。第 10 步是闭环，缺了整个机制失效。

---

## 3. 反同质化机制

### 3.1 正交变量表（`directing/variables.md`）

开片必填五维，每维给出已验证的取值：

| 维度 | 取值 |
|---|---|
| 时间结构 | 线性 / 倒叙 / 循环 / 平行切 / 单时刻切片 |
| 视点 | 全知 / 跟随单人 / 监控·仪器 / 物的视角 / 缺席 |
| 节奏型 | 匀速 / 加速爆发 / 前紧后松 / 两次呼吸 / 全片凝滞 |
| 声音 | BGM通铺 / 音效驱动 / 环境声 / 完全静音 / 声画错位 |
| 结尾 | 空景收 / 回到首镜 / 硬切黑 / 悬而未决 / 日常化 |

### 3.2 指纹（`directing/fingerprint.md`）

**关键洞察：只查变量表拦不住 SCP 那种同质化。**

SCP 三部的 `vars` 完全可以填得不同，但成片仍然逐镜同构——因为重复发生在「段落功能 → 具体镜头设计」这一层，而不是在高层选择上。所以指纹必须记两层。

`films.jsonl` 每行一部：

```json
{
  "id": "scp-breach",
  "name": "收容失效",
  "date": "2026-07-20",
  "profile": "ltx-2.3-q4-12g",
  "structure": "trailer-8seg",
  "vars": {
    "time": "线性", "pov": "跟随单人", "tempo": "加速爆发",
    "audio": "BGM通铺", "ending": "空景收"
  },
  "signature": {
    "shot_count": 36,
    "opening_size": "极特写",
    "ending_size": "大远景",
    "peak_device": "摘面具/近乎全黑",
    "climax_pattern": "6×极特写连打"
  }
}
```

判定规则，逐条拦截：

| 层 | 规则 | 比对范围 | 动作 |
|---|---|---|---|
| `vars` | 撞 ≥3 维 | 最近 3 部 | **重选**，硬拦 |
| `structure` | 完全相同 | 最近 3 部 | 警告，须给出显式理由才放行 |
| `signature` | 撞 ≥2 项 | **全部历史** | **重设计**，不论 vars 是否已不同 |

「撞」的判定，按字段类型分：

- 文本字段（`opening_size` / `ending_size` / `peak_device` / `climax_pattern`）— 语义等价即算撞。「摘眼镜擦汗」与「摘面具喘气」是同一手法的换装，算撞；由 agent 判断，判不准时按撞处理
- 数值字段（`shot_count`）— 差值在 ±10% 以内算撞

第三条是真正拦住 SCP 问题的那道门，也是唯一比对全部历史的一条。前两条只管高层选择，第三条管具体镜头设计——SCP 三部正是高层可以不同、具体设计却完全一致。

### 3.3 骨架降级

`trailer-8seg.md` 保留完整参数（现有 `SKILL.md:420-426` 的内容），但头部标注使用记录：

```yaml
used_by: [山海, SCP-收容失效, SCP-站点档案, SCP-异常现场]
use_count: 4
last_used: 2026-07-20
```

骨架从「唯一真理」降级为「候选之一，已用过 4 次」。agent 读到使用计数会自然避开，这比写「请勿重复使用」有效。

---

## 4. Profile 机制

### 4.1 格式（`profiles/ltx-2.3-q4-12g.md`）

```yaml
id: ltx-2.3-q4-12g
t2i: z-image (ComfyUI)
i2v: LTX-2.3-22B-distilled-1.1-Q4_K_M (ComfyUI + ComfyUI-GGUF)
hardware: RTX 4070Ti 12G / 32G RAM
verified: 2026-07  # 实测，非转述

# 由标定测出
max_shot_sec: 2.04          # 主体开始漂出画面的时长
frame_count: 49
fps: 24
align_to: 32                # 宽高须整除（VAE 空间压缩率）
resolutions: [[1280,704], [768,1344], [1376,576]]
sec_per_shot: 150
vram_peak_gb: 12.3
restart_each_shot: true     # 进程不释放 offload 内存
kf_batch_restart: 15

# 模型行为
text_sensitivity: high      # 主体含文字载体必出乱码
motion_style: frozen        # 只能写「凝住的瞬间+微呼吸」，不能写动作弧线
concept_blindspots: [洞螈, 山海经异兽, 缺席表达]
```

### 4.2 公式改用变量

```
镜头数 = round((目标秒数 - 转场秒数) / (max_shot_sec - 转场秒数))
切换密度 = (镜头数 - 1) / 时长 × 60
```

不再出现 `2.0417` 这个常数。

### 4.3 标定流程（`profiles/calibration.md`）

五步，每步都是我真跑过的方法：

1. **测 `max_shot_sec`** — 固定一张关键帧，跑 2s / 3.5s / 5s 三档，逐帧看主体何时转出画面或形变。取「肉眼开始察觉」的前一档。
2. **测 `align_to`** — 故意给非整除宽高看报错，或从 VAE 配置读 spatial compression rate。
3. **测 `restart_each_shot`** — 连跑两条，看第二条是否 OOM、采样速度是否掉档。记录跑前跑后可用内存差值。
4. **测 `text_sensitivity`** — 主体描述里写一个明确的文字载体（招牌/菜单），跑 3 次数乱码次数。
5. **测 `motion_style`** — 写一句明确的动作弧线（「她慢慢转头看向窗外」），看是否执行过头。过头则记 `frozen`。

`_TEMPLATE.md` 是空白 profile，字段齐全、值留空，附上标定步骤引用。

---

## 5. 卫星 skill 的改动（只做三处）

1. **五个 R 段改写** — 去掉对他人视频的逐字引用，改为自己总结的表述；`source` 字段保留原作者名与链接，出处集中到 `ATTRIBUTION.md`。保住溯源价值，去掉搬运风险。
2. **`rhythm-density` 的 10 秒硬顶外提** — 正文改为引用 profile 的 `max_shot_sec`；「10 秒」作为云端平台档的实例保留，并**标注 `verified: 转述，未自测`**，与实测值区分。
3. **frontmatter 增加 `verified` 字段** — 区分「本机实测」与「转述」。这是整个仓库的可信度基础。

方法论本身不动。

---

## 6. 两类 skill 的说明（`docs/how-skills-differ.md`）

仓库里存在两种形态，必须明说，否则读者会困惑为什么格式不一致。

| | 蒸馏型（RIA） | 实操型 |
|---|---|---|
| 代表 | 五个卫星 | local-ai-film |
| 来源 | 他人内容蒸馏 | 自己跑出来的 |
| 格式 | R / I / A1 / A2 / E / B | 装配流程 + knowledge + profiles |
| `source_book` | 有 | 无 |
| 数值可信度 | 转述，需自测 | 本机实测，标注硬件 |
| 测试 | test-prompts.json 盲测路由 | 同 |

**不把 local-ai-film 硬塞进 RIA 格式**——它是一手经验，没有「原文」可引，套模板只会造出假的 R 段。

---

## 7. README 与 gallery

- `README.md` 中文（主），`README.en.md` 英文。skill 正文全部保持中文——中文提示词的实测经验（z-image 对中文响应更好）翻成英文会失真。
- `docs/gallery.md` **不是可选项**。纯文档仓库拿不到 star，能拿 star 的路径是「先看到片子好看，再发现方法论」。

README 必须在开头讲清一件事：**这是导演经验，不是能 clone 就跑的工具。** 预期管理做在前面，避免「跑不起来」类 issue。

---

## 8. 阶段划分

| 阶段 | 内容 |
|---|---|
| P0 | 仓库骨架 + 中枢重构（拆 knowledge / directing / profiles）+ 变量表 + 指纹 + calibration |
| P1 | 五个卫星 R 段改写 + 10 秒硬顶外提 + `verified` 字段 + ATTRIBUTION.md |
| P2 | README 中英 + gallery + how-skills-differ.md |
| P3 | 给 local-ai-film 补 test-prompts.json（现在没有）+ 盲测 |

---

## 9. 风险与未决

| 风险 | 说明 | 处理 |
|---|---|---|
| **变量表选项未经验证** | 「循环」「声画错位」「全片凝滞」这些取值在 2.04 秒硬顶下做不做得出来，没试过。变量表可能给出实际做不到的组合 | P1 阶段每维至少跑一部验证；做不到的取值标注 `需 max_shot_sec ≥ N` |
| **gallery 素材本身就是同质化样本** | 现有预告片只有山海 + SCP×3，正是问题案例。拿它们当封面等于展示反面教材 | 按新流程跑一部新片当封面。这同时是对整套机制的端到端验证 |
| **指纹靠自觉写回** | 第 10 步漏了，机制静默失效 | 中枢 SKILL.md 把「写回指纹」放进验收清单，与抽帧检查同级 |
| **受众规模** | 本地 LTX + 12G 卡的交集小。profile 机制把受众扩到「所有本地 AI 视频工作流」，但仍是小众 | 接受。核心资产（七个坑）本身有独立价值，不依赖复现 |

---

## 10. LICENSE

双许可，边界按目录划：

- `examples/scripts/` 下的代码 — **MIT**
- 其余全部内容（skill 正文、knowledge、profiles、docs）— **CC-BY-4.0**

理由：这是内容为主的仓库，CC-BY 更贴合；但代码部分用 CC-BY 会给下游带来使用障碍，单独放宽。

## 11. 待办：本文档未覆盖

- `README.en.md` 尚未撰写（本轮只交付中文 README）
