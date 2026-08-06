# test-results.md — shot-breakdown

## 通过率

**6/8 = 75%（低于 80% 门槛）**

评测方式：独立 sub-agent 盲测（未看到 type/expected_behavior/notes），给定 8 个 skill 的 name+description，逐条判断该触发哪个 skill 或 none。

## 逐条结果

| id | 预期 | 盲测结果 | 判定 |
|---|---|---|---|
| should-trigger-01 | shot-breakdown | shot-breakdown | PASS |
| should-trigger-02 | shot-breakdown | lock-character-reference | **FAIL** |
| should-trigger-03 | shot-breakdown | lock-character-reference | **FAIL** |
| should-trigger-04 | shot-breakdown | shot-breakdown | PASS |
| should-not-trigger-01 | emotion-to-camera-language（诱饵） | emotion-to-camera-language | PASS |
| should-not-trigger-02 | lock-character-reference（诱饵：形象未锁定） | lock-character-reference | PASS |
| should-not-trigger-03 | editing-triad（诱饵） | editing-triad | PASS |
| edge-01 | shot-breakdown（判停阈值未到，不应过早放弃） | shot-breakdown | PASS |

## 失败分析（<80%，按方法论要求必须回炉重做阶段 2，而非小修）

### 根因：shot-breakdown 与 lock-character-reference 在"角色形象不对/跑偏"这一语言层面高度重叠，且 description 没有给出可供盲测 agent 区分的显式信号

两条失败 case 的共同点：prompt 里出现"这个角色的形象...不对/跑偏"这类措辞时，盲测 agent **一律**倒回 lock-character-reference，即使 prompt 语境明显是"已经批量抽图之后在筛选"（should-trigger-02："重抽了好几次都不对，要不要继续抽下去" / should-trigger-03："人物形象跑偏、景别机位也不对，接下来怎么处理"）。

**逐句定位**：

1. `shot-breakdown` 自身 SKILL.md 的语言信号列出了：
   > "这个角色形象一直崩，怎么办"
   这句话与 `lock-character-reference` description 里的触发词：
   > "Trigger: 角色一致 / 人物不一样 / 换个角度就变脸 / character consistency / reference image"
   几乎是同一语义（"角色形象不对/崩"）。两个 skill 的 description 都没有给出一个**能从用户这一句话里直接读出来**的区分特征——真正的区分点（"基准形象图本身是否已经锁定/稳定" vs "锁定之后批量抽出来的具体某几张图对不对"）只存在于两个 skill 的 A2"与相邻 skill 的区分"段落里的**长文字说明**，而不在 description 的**触发词/trigger 列表**里。盲测 agent 只被给了 description，没有被给 A2 全文，因此只能靠触发词表面匹配，自然会一律匹配到语言更直接的 lock-character-reference（"人物不一样"直接命中它的 trigger 列表）。

2. `shot-breakdown` description 现有的边界表述：
   > "不适用于：单镜提示词（见 emotion-to-camera-language）、时长剪辑（见 rhythm-density/editing-triad）、形象未锁定（见 lock-character-reference）"
   这句话只讲清楚了"形象**未锁定**"这一种情况要转 lock-character-reference，但没有讲清楚"形象**已锁定，但这一批具体抽出来的图里人物又跑偏了**"仍然属于 shot-breakdown 的范围——这正是 should-trigger-02/03 想测的场景，而 description 里没有一句话能让盲测 agent 排除"跑偏=形象没锁好"这个第一反应。

### 判断：修 skill，不是修测试

这两条 should_trigger 场景是真实、典型、大概率会在实际使用中出现的用户表达（"抽出来的图这个角色又不对了"是 A1 案例 2 里原文出现过的真实场景："人是不对的，但是小孩是对的"），不是为了凑数设计出的刁钻场景。是 description 本身缺少让 blind agent 能分辨的信号，必须回炉修 A2/description，而不是弱化或删除这两条测试。

### 修改建议（供主流程参考，未直接改 SKILL.md）

1. 在 `shot-breakdown` 的 description 里，把边界句从：
   > "不适用于：...形象未锁定（见 lock-character-reference）"

   扩展为同时说明"锁定之后仍然可以在这里判断"的正面信号，例如：
   > "前提是角色基准形象图已经锁定稳定（若怀疑连基准图本身都没锁定/不稳定，先见 lock-character-reference）；在此前提满足后，这一批具体抽出来的图里人物形象是否跑偏、要不要继续重抽，仍然属于本 skill 的判断范围，不要因为出现'形象跑偏/形象不对'字眼就转回 lock-character-reference。"

2. 在 `lock-character-reference` 的 description 里，反向补一句排除信号，明确它管的是"基准图"这一张图，而不是"某一批批量抽卡结果"：
   > "不适用于：角色基准形象图已经锁定稳定，只是某一批批量抽卡结果里个别图片人物跑偏——那属于 shot-breakdown 的筛选/成本判停范围。"

3. 如果两个 skill 的 trigger 词表继续共用"形象跑偏/形象不对"这类高频短语，建议在**两边**都补充一个前置澄清问句作为 A2 的执行第一步："先确认：跑偏的是角色基准形象图本身（还没锁定成功），还是锁定之后某一批抽出来的具体镜头图（基准图本身没问题）？" 这样即使触发词命中两个 skill，agent 也能在第一步内部收敛到正确的一个。

## 结论

**<80%，按方法论要求需要回炉重做阶段 2（重做 A2/description，而非表面打补丁）**。主要修复对象：`shot-breakdown` 与 `lock-character-reference` 之间"角色形象跑偏"语言信号的相互排除句，两个 skill 都需要补充。
