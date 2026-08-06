# 参考实现 —— 不要直接跑

> **这些脚本是作者那台机器的配置，clone 下来必然跑不起来。**
> 它们的作用是让你看清「这套流程实际是怎么落地的」，不是给你 `python run_films.py` 用的。

## 必须改的地方

| 文件 | 行 | 写死了什么 |
|---|---|---|
| `run_films.py` | 13 | `PY_COMFY` —— conda 环境的 python 路径 |
| `run_films.py` | 14–15 | `CO` / `CI` —— ComfyUI 的 output / input 目录 |
| `run_films.py` | 16 | `ROOT` —— 成片输出根目录 |
| `run_films.py` | 18 | `UNET` —— GGUF 权重文件名 |
| `run_films.py` | 64 | ComfyUI 的 `main.py` 路径与启动参数 |
| `run_films.py` | 128 | z-image 工作流 JSON 路径 |

## 会整个失效的地方

以下不是「改路径」能解决的，**换模型要重写**：

- `gen_keyframes()` 第 140–144 行按节点号改工作流：`wf["67"]` 正向、`wf["71"]` 负向、`wf["70"]` seed、`wf["68"]` 尺寸、`wf["9"]` 文件名前缀。**换一个工作流，这些节点号全错。**
- `build_ltx()` 第 195–206 行依赖 `LTXDirector` 这个 class_type 和它的 `timeline_data` JSON schema。**换 I2V 模型这段整体作废。**

`ui2api.py` 可以把 ComfyUI 的 UI 格式工作流转成 API 格式，帮你找到自己工作流的节点号。三个已修的坑：`COMBO` 在新版 object_info 里是字符串、`forceInput` 输入不占 widget 槽位、widget 转成输入接口后值仍留在 `widgets_values` 里。

## 文件说明

| 文件 | 干什么 |
|---|---|
| `run_films.py` | 主流程：关键帧 → I2V（每镜重启）→ 逐镜后期 → xfade 拼片 |
| `trailer_edit.py` | 预告片专用拼接（硬切 + 逐镜运镜 + 标题卡），通用拼接做不了 |
| `consistency.py` | 人脸/环境/场景一致性校验（InsightFace + CLIP，CPU-only） |
| `regain.py` | 成片音量事后统一调平 |
| `sentinel.py` | 看门狗 |
| `ui2api.py` | ComfyUI UI 工作流 → API 格式 |
| `ltx_gguf_api.json` | LTX 工作流（API 格式） |
| `_example_*.py` | 配置示例：氛围片 / 预告片 / SCP 三部曲 / 标注 |

## 值得直接抄的部分

即使换模型，这几段逻辑是通用的：

- `kill_comfy()` 排除自身 PID 的写法（见 `../../knowledge/pitfalls.md` 坑 ②）
- `post_and_assemble()` 里的柔焦链 `format=gbrp` 写法（坑 ③）
- `regain.py` 的削波保护增益计算
- 断点续跑逻辑：已存在的产物一律跳过
