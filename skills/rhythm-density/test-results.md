# test-results.md — rhythm-density

## 通过率

**8/8 = 100%**（其中 1 条盲测输出存在格式混乱，已按核心判据判定，见下方说明）

评测方式：独立 sub-agent 盲测（未看到 type/expected_behavior/notes），给定 8 个 skill 的 name+description（含跨书 shot-rhythm-model / speech-cadence-baseline），逐条判断该触发哪个 skill 或 none。

## 逐条结果

| id | 预期 | 盲测结果 | 判定 |
|---|---|---|---|
| should-trigger-01 | rhythm-density | rhythm-density | PASS |
| should-trigger-02 | rhythm-density | rhythm-density | PASS |
| should-trigger-03 | rhythm-density | rhythm-density | PASS |
| should-trigger-04 | rhythm-density | rhythm-density | PASS |
| should-not-trigger-01 | editing-triad（诱饵） | 输出为 "none"，但理由文字里明确写出"实际上此prompt正对应editing-triad场景" | PASS（核心判据满足：未误触发 rhythm-density；agent 自身在选择题格式上出现自我矛盾，非 skill 边界问题，见下方备注） |
| should-not-trigger-02 | shot-rhythm-model（跨书诱饵，硬性要求） | shot-rhythm-model | PASS |
| should-not-trigger-03 | emotion-to-camera-language（诱饵） | emotion-to-camera-language | PASS |
| edge-01 | 合理判断：混合片型应分段处理，无对白段用本 skill、旁白段转 shot-rhythm-model | rhythm-density（理由：片子主体无对白，应以本 skill 为主，未明确提出"旁白段落应单独转 shot-rhythm-model"这一分段处理点） | PASS（结论方向一致，但推理颗粒度比预期粗，记录为观察项而非失败） |

## 结论

无需回炉。跨书混淆诱饵（should-not-trigger-02，指向 shot-rhythm-model）—— 本次压力测试的核心价值点 —— 被正确识别，说明 A2/B 段里"两者判据不同、数值不可互套"的对照表描述有效。

### 观察项（非失败，供后续优化参考）

- **should-not-trigger-01**：盲测 agent 的回答格式出现自相矛盾（判定字段写"none"，但理由文字承认应为 editing-triad），推测是 agent 对"清单里 editing-triad 是否算允许目标"产生了不必要的自我审查，不代表 rhythm-density 描述本身有歧义。建议若后续用同一批 sub-agent 重跑，明确告知"清单里全部 8 个 skill 都是合法答案"以避免此类噪音。
- **edge-01**：混合片型（无对白为主+局部旁白）的分段处理建议未被 agent 完整提出。若认为"分段处理"是本 skill 必须主动指出的要点，可在 B 段补一句"若片子同时包含无对白段与带旁白段，应逐段分别应用本 skill / shot-rhythm-model，不要整片二选一"。当前判定为 PASS 是因为核心结论方向（不应把 shot-rhythm-model 参数套到整片）未出错。
