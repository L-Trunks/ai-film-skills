# test-results.md — material-driven-storyboard

## 通过率

**7/8 = 87.5%**

评测方式：独立 sub-agent 盲测（未看到 type/expected_behavior/notes），给定 8 个 skill 的 name+description，逐条判断该触发哪个 skill 或 none。

## 逐条结果

| id | 预期 | 盲测结果 | 判定 |
|---|---|---|---|
| should-trigger-01 | material-driven-storyboard | material-driven-storyboard | PASS |
| should-trigger-02 | material-driven-storyboard | material-driven-storyboard | PASS |
| should-trigger-03 | material-driven-storyboard | material-driven-storyboard | PASS |
| should-trigger-04 | material-driven-storyboard | material-driven-storyboard | PASS |
| should-not-trigger-01 | lock-character-reference（跨 skill 混淆诱饵，硬性要求） | lock-character-reference | PASS |
| should-not-trigger-02 | none（云端算力充足边界） | none | PASS |
| should-not-trigger-03 | emotion-to-camera-language（诱饵） | emotion-to-camera-language | PASS |
| edge-01 | 预期：素材细节不完全匹配（分辨率/景别不同但动作类型对得上）不算"没有素材"，应转 shot-breakdown 做二次修正，而非本 skill 的三选一决策 | material-driven-storyboard（agent 判定这仍属于本 skill"从素材反推能写什么"的核心判据） | **FAIL** |

## 失败分析

### edge-01：素材"有但细节不对" vs "完全没有" 的边界未被区分

- **失败表现**：盲测 agent 认为"分辨率/景别不太一样，其他都对得上"仍应触发 material-driven-storyboard，而预期是这种情况素材本质是存在的，应该转给 shot-breakdown 做"景别不对改景别、机位不对改机位"的二次修正。
- **根因判断**：这是一条**边界确实模糊、诱饵设计可能偏严**的场景，不是 description 有明显歧义句可指认。material-driven-storyboard 的描述通篇讲"没有对应驱动视频/本地工作流做不出来"，"分辨率/景别不太一样"仍可以被合理解读为"没有完全对应的素材"，agent 的判断有一定道理。
- **是否属于"为了凑诱饵而设计过狠的场景"**：是，部分符合。这条 edge case 的措辞（"分辨率和景别跟我想要的不太一样，其他都对得上"）没有明确到"动作类型和大致机位都对得上、只是清晰度/裁切不同"这种更纯粹的 shot-breakdown 场景，留下了让 agent 合理选择 material-driven-storyboard 的空间。

### 建议

- 优先**修测试**：把 edge-01 的 prompt 改得更明确，例如"驱动视频库里这段素材动作、机位、时长都对得上，只是分辨率偏低需要超分，这个还需要走三选一吗？"——更清楚地把"素材本质可用，只需后处理"和"素材类型不存在"分开。
- 如果后续判定这个边界确实是常见真实困惑（本地生产中"素材有但不完美"是高频场景），可以考虑给 material-driven-storyboard 的 B 段加一句：「素材库中已有动作/机位大致匹配、仅分辨率或细微观感需要后处理（超分/裁切）的情况，不算'没有素材'，应转 `shot-breakdown` 做二次修正，而非在此处走三选一」。但这不是必须项，因为通过率 87.5% ≥ 80% 门槛，不构成回炉理由。

## 结论

不需要回炉重做阶段 2。核心 should_trigger 场景和跨 skill 混淆诱饵（should-not-trigger-01，指向 lock-character-reference）全部通过，唯一失败项是一个可能设计过严的边界用例，建议先修测试观察下一轮结果。
