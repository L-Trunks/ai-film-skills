# test-results.md — emotion-to-camera-language

## 通过率

**8/8 = 100%**

评测方式：独立 sub-agent 盲测（未看到 type/expected_behavior/notes），给定 8 个 skill 的 name+description，逐条判断该触发哪个 skill 或 none。

## 逐条结果

| id | 预期 | 盲测结果 | 判定 |
|---|---|---|---|
| should-trigger-01 | emotion-to-camera-language | emotion-to-camera-language | PASS |
| should-trigger-02 | emotion-to-camera-language | emotion-to-camera-language | PASS |
| should-trigger-03 | emotion-to-camera-language | emotion-to-camera-language | PASS |
| should-trigger-04 | emotion-to-camera-language | emotion-to-camera-language | PASS |
| should-not-trigger-01 | shot-breakdown（诱饵：生成后筛选） | shot-breakdown | PASS |
| should-not-trigger-02 | none（风格非情绪） | none | PASS |
| should-not-trigger-03 | lock-character-reference（诱饵：形象未锁定） | lock-character-reference | PASS |
| edge-01 | 已有具体提示词，不需要重新触发翻译 | none | PASS |

## 结论

无需回炉。本 skill 与 shot-breakdown（生成前描述 vs 生成后筛选）、与 lock-character-reference（依赖关系）两条易混边界均被盲测正确识别，描述清晰。
