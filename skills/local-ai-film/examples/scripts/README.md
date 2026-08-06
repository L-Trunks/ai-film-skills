# examples/scripts

**这些是参考实现，不是 skill 的必需品。**
skill 本体（`SKILL.md` + `knowledge/` + `directing/` + `profiles/`）拷进
`~/.claude/skills/` 就能用，跟这个目录没有关系。

这里的脚本是我这台机器跑那几部片时真实用的代码，放出来是为了让你看到
「知识库里那些话具体落成代码长什么样」。

---

## 先跑体检

```bash
python doctor.py
```

逐项检查 ComfyUI 目录、python 解释器、ffmpeg、模型文件、ComfyUI 是否在跑、显存够不够。
缺哪项它会直接告诉你改哪个变量。

## 改配置

所有机器相关的路径都在 `config.py`，脚本正文里不写绝对路径。三种改法任选：

| 方式 | 怎么做 | 适合 |
|---|---|---|
| 环境变量 | `set AIFILM_COMFY=D:\ComfyUI` | 不想改文件 |
| 本地覆盖 | `cp config.py config_local.py` 后改 | 长期使用（已 gitignore） |
| 直接改 | 编辑 `config.py` 默认值 | 图省事 |

必填只有三项：

```python
COMFY = r"D:\ComfyUI"                                  # AIFILM_COMFY
PY    = r"D:\conda\envs\comfyui_env\python.exe"        # AIFILM_PY
ROOT  = r"E:\我的短片"                                  # AIFILM_ROOT
```

其余（`CI` / `CO` / `MAIN`）都由 `COMFY` 推导，一般不用管。

---

## 文件说明

| 文件 | 干什么 |
|---|---|
| `config.py` | **机器配置，先改这个** |
| `doctor.py` | 环境体检 |
| `run_films.py` | 跑批主程序（LTX 短单镜路线） |
| `minimax_h3.py` | H3 长单镜路线的跑批 |
| `consistency.py` | 可选的人物/环境一致性自动校验 |
| `sentinel.py` | 跑批看门狗 |
| `bgm_fetch.py` / `bgm_pick.py` | 无版权 BGM 抓取与频谱筛选 |
| `trailer_edit.py` | 预告片剪辑 |
| `ui2api.py` | ComfyUI 界面导出的 workflow 转 API 格式 |
| `_example_*.py` | 那几部片的真实配置，当模板抄 |
| `*_api.json` | ComfyUI 工作流（API 格式） |

`_` 开头的是示例配置，直接复制改成你自己的片子。

---

## 一定会踩的两件事

**跑批必须独立进程 + 看门狗。** 普通后台任务实测 8 分钟就被会话回收。

**长跑脚本要加互斥锁。** 没有锁的话，一次失败的「杀掉重启」就会变成两条流水线
抢同一个 GPU 端口，两边互相踩输出文件名。详见 `knowledge/pitfalls.md` 坑 ⑭。
