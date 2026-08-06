# test-results.md — lock-character-reference

## 通过率

**8/8 = 100%**

评测方式：独立 sub-agent 盲测（未看到 type/expected_behavior/notes），给定 8 个 skill 的 name+description（本书 6 个 + 跨书 shot-rhythm-model / speech-cadence-baseline 2 个），逐条判断该触发哪个 skill 或 none。

## 逐条结果

| id | 预期 | 盲测结果 | 判定 |
|---|---|---|---|
| should-trigger-01 | lock-character-reference | lock-character-reference | PASS |
| should-trigger-02 | lock-character-reference | lock-character-reference | PASS |
| should-trigger-03 | lock-character-reference | lock-character-reference | PASS |
| should-trigger-04 | lock-character-reference | lock-character-reference | PASS |
| should-not-trigger-01 | emotion-to-camera-language（诱饵） | emotion-to-camera-language | PASS |
| should-not-trigger-02 | none（云端平台边界） | none | PASS |
| should-not-trigger-03 | none（非叙事出图） | none | PASS |
| edge-01 | 合理判断：仅主角需严格锁定，露脸较少的角色可豁免 | lock-character-reference（理由与预期一致：背景角色可豁免，主角需锁） | PASS |

## 结论

无需回炉。跨 skill 混淆诱饵（should-not-trigger-01，指向 emotion-to-camera-language）与角色数量边界（edge-01）均被正确处理，说明本 skill 与 emotion-to-camera-language 之间"形象锁定 vs 单镜提示词"的边界描述清晰有效。
