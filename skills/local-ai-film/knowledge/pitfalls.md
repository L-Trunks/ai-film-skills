# 工程坑

**全部为本机实测**（RTX 4070Ti 12G / Windows 11 / ComfyUI）。每条标注适用范围：`通用` 的换模型也成立，`profile` 的只对特定组合成立、换模型须重测。

提示词层的坑见 `prompt-craft.md`，声音见 `bgm-spectral.md`。

---

## ① 显存/内存不释放，必须每镜重启 ★最重要

**适用：`profile`（凡是权重大于显存、依赖 offload 的组合）**

LTX 的 17 GB 权重在 12 GB 卡上必然 offload 十几 GB 到系统内存，**ComfyUI 不会在任务结束后释放这部分**。`POST /free` 带 `unload_models` + `free_memory` 返回 200 但内存纹丝不动。跑第二条就 `OSError: [WinError 1450] 系统资源不足` 崩溃。

实测：崩溃时 0.9 GB 空闲 → 杀进程后立刻回到 20.9 GB。**只有进程退出能还内存。**

`examples/scripts/run_films.py` 已内置每镜 kill + restart，别自己写循环绕过它。

**出图侧同样会泄漏，只是慢一些。** z-image 连跑 70 张能把 ComfyUI 撑到 17 GB 常驻，把后续 LTX 的 offload 逼进页面文件 —— 采样从 12s/it 掉到 120s/it。所以出图也要分批重启，本机取 `kf_batch_restart: 15`。

标定方法见 `../profiles/calibration.md` 第 3 步。权重小于显存的组合（比如 SDXL + 8G 以内的 I2V）不需要这条。

---

## ② 跑批脚本自杀

**适用：通用（凡是脚本与被杀进程同环境）**

跑批脚本跑在 `comfyui_env` 下时，`kill_comfy()` **必须排除自身 PID**。一致性校验依赖 `insightface` / `open_clip`，这两个只装在 `comfyui_env`，所以脚本被迫用那个环境的 python —— 而 kill 逻辑按环境路径匹配，不排除自己就会把自己杀掉。

症状极具迷惑性：**静默退出、无 traceback、退出码 255**，看门狗重启后继续自杀。

```python
"Get-Process python | Where-Object {$_.Path -like '*comfyui_env*' -and $_.Id -ne %d}" % os.getpid()
```

反过来，如果用别的环境（如 `zhiyu`）跑批，一致性校验会**静默降级成「不检查」**，跑完才发现全片人物不一致。

### 连带伤害：同环境下的其他任务也会被杀

`kill_comfy()` 按**环境路径**匹配，只排除自身 PID —— 意味着**任何跑在同一个 conda 环境下的
无关进程都会被连坐**。踩过：一个抓 BGM 的脚本跑在 `comfyui_env` 下，探针每次启动都把它杀掉，
表现是「下载莫名其妙中断，日志停在一半，退出码却是 0」。

两条对策：

- **长任务换个环境跑**（本仓库把 BGM 抓取放在 `zhiyu`），从物理上避开匹配范围
- 若必须同环境，改成按**命令行**匹配而不是按环境路径

⚠️ PowerShell 5.1 里 `Get-Process` **不填充 `CommandLine` 字段**，值是 `$null`。
所以下面这种写法是无效的，`$null -notlike '*xxx*'` 恒为真，等于没排除：

```powershell
Get-Process python | Where-Object {$_.CommandLine -notlike '*bgm_fetch*'} | Stop-Process   # ✗ 无效
```

要拿命令行必须走 CIM：

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -notlike '*bgm_fetch*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

### ★ 杀完必须复查残留数量，否则你不知道有没有杀掉

**这条是本仓库代价最高的一次教训：一个 19.5 GB 的下载被三个并发实例写成垃圾。**

三次「杀掉旧实例」全部静默失败，每次都以为成功了：

| 尝试 | 为什么没生效 |
|---|---|
| `pkill -f dl_loop.sh` | Git Bash 下匹配不到 `nohup bash script.sh` 启动的进程 |
| `pkill -f dl_chunk.sh` | 同上 |
| `Stop-Process -Id 27911` | `ps -W` **第一列是 MSYS PID**，`Stop-Process` 要的是**第四列 WINPID** |

累积到 7 个 bash + 4 个 curl 同时向一个文件追加，文件报废。

两条铁律：

```powershell
# ① 杀完立刻复查，数量必须是 0
$n = @(Get-CimInstance Win32_Process -Filter "Name='bash.exe'" |
       Where-Object { $_.CommandLine -like '*dl_*' }).Count
"残留: $n"
```

② **长任务自带互斥锁**，不要依赖「先杀干净」。Git Bash 没有 `flock`，用 `mkdir` —— 目录创建是原子操作：

```bash
LOCKD="${TARGET}.lockdir"
if ! mkdir "$LOCKD" 2>/dev/null; then
  OLD=$(cat "$LOCKD/pid" 2>/dev/null)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then echo "已有实例 pid=$OLD"; exit 1; fi
  echo "陈旧锁，接管"        # 进程已死则接管，避免锁死
fi
echo $$ > "$LOCKD/pid"
trap 'rm -rf "$LOCKD"' EXIT
```

⚠️ 监控长任务时**把实例数一起打出来**。只看进度不看实例数，多实例会一直隐藏到文件被写坏为止。

### ⚠️ 但「数进程」几乎必然误报，要数日志

按命令行匹配数进程会把两类东西算进来，实测两次误报到 6：

| 误报来源 | 说明 |
|---|---|
| **脚本自己 fork 的子壳** | `CODE=$(curl ...)` 这类命令替换会 fork，**子进程命令行与父进程完全相同**。一个 worker 能数出 3 个 |
| **你的检查命令自己** | 检查命令里含有被匹配的字符串（如 `dl_final.sh`），执行它的 shell 也被数进去 |

看父子关系就能分辨：

```powershell
Get-CimInstance Win32_Process -Filter "Name='bash.exe'" |
  Where-Object { $_.CommandLine -like '*你的脚本*' } |
  Select-Object ProcessId, ParentProcessId, CreationDate | Format-List
# 若 B 的 Parent 是 A、C 的 Parent 是 B，那是一条 fork 链，只算 1 个实例
```

**可靠做法：让脚本在成功获锁后打一行 `START`，数日志里的 START 行数。**
每次成功获锁恰好一行，不受 fork 和检查命令干扰。

```bash
mkdir "$LOCKD" 2>/dev/null || { echo "!! 锁已存在"; exit 1; }
echo "START pid=$$"        # ← 数这个
```

### 最后一道保险：SHA256 终验

进程管理再小心也可能有意外。HuggingFace 在 API 里公布了每个文件的 sha256：

```bash
curl -s "https://huggingface.co/api/models/<repo>?blobs=true" \
 | python -c "import json,sys;[print(f['lfs']['sha256'],f['rfilename']) for f in json.load(sys.stdin)['siblings'] if f.get('lfs')]"
```

下载脚本末尾比对一次，**19.5 GB 约 1–2 分钟**。有它兜底，中间过程出没出岔子都能定论 ——
比反复纠结「刚才那次是不是污染了」省事得多。

---

## ③ 柔焦链必须在 RGB 空间

**适用：通用（ffmpeg 的 blend 行为与模型无关）**

`blend=screen` 是逐平面运算，在 YUV 下会把 U/V 色度平面也 screen，色度被推高 → **整片泛品红**。

踩过两次：第一次以为是 `lutyuv` 只清了亮度通道，补 `u=128:v=128` 仍然紫。正解是整条链 `format=gbrp`，出口再 `format=yuv420p`。

```
[0:v]crop=...,scale=...,format=gbrp,split[a][b];
[b]lutrgb=r='if(gt(val,170),val,0)':g='...':b='...',gblur=sigma=24[glow];
[a][glow]blend=all_mode=screen:all_opacity=0.18,eq=...,format=yuv420p[v]
```

---

## ④ ffmpeg 的 stderr 不能用 `text=True` 读

**适用：通用（中文 Windows 环境）**

中文 Windows 上 ffmpeg 的 stderr 会让 GBK 解码抛 `UnicodeDecodeError`，异常在 subprocess 的读取线程里被吞掉，**你只会拿到空字符串或默认值**。

踩过：`volumedetect` 解析不到 `max_volume` → 削波余量取了默认值 → 整批增益被卡在 +0.5 dB，表面上「跑成功了」但实际几乎没调。

```python
r = subprocess.run(cmd, capture_output=True)          # 不要 text=True
err = (r.stderr or b"").decode("utf-8", "replace")
```

同理，**带中文的路径要写在 .py 文件里**，经 `bash -c` 传参会被控制台编码毁掉。

---

## ⑤ `xfade duration=0` 会退化成垃圾文件

**适用：通用**

想要硬切（预告片类）而把 `TRANS` 设成 0，`xfade` 会退化，**产出 2 秒的垃圾文件而且日志显示成功**。

硬切要用专门的拼接路径（`examples/scripts/trailer_edit.py`），不要试图让通用拼片函数通过 `TRANS=0` 兼容。

---

## ⑥ 一致性阈值不能照搬真人经验值

**适用：通用（凡是用嵌入相似度判 AI 生成图）**

**AI 生成的同一角色，相似度天然低于真人照片。** 照搬人脸识别常用的 0.5+ 会把全部合格图判成不合格。

本机标定（InsightFace 人脸嵌入余弦）：

| | 实测值 | 阈值 |
|---|---|---|
| 同一角色 | 0.338 / 0.344 / 0.402 / 0.417 | **0.28**（两侧都有余量） |
| 不同角色 | 0.116 / 0.137 / 0.141 / 0.244 | |

CLIP ViT-B-32 图像嵌入：同环境 0.500–0.882，跨环境 0.428–0.531 → `env` 取 0.55（宽松，只拦「跑到另一个世界去了」），`scene` 取 0.65（严，要求认得出是同一地点）。

**换模型或换嵌入网络必须重新标定**，这几个数只对上述组合成立。

**试过但不可用的方案**（别再走回头路）：色彩直方图交集、色温/明度/饱和标量差、网格结构+梯度能量 —— 三者**跨环境的相似度反而高于同环境**，完全无区分度。色彩统计只能判断「曝光和调色像不像」，判断不了「是不是同一个地方」，必须用语义嵌入。

判定全部 CPU-only（InsightFace 0.3s/张、CLIP 0.06s/张），不抢 GPU。

---

## ⑦ 跑批必须用「独立进程 + Monitor」两件套

**适用：通用（Claude Code 环境）**

普通后台任务实测 8 分钟就被会话回收。必须 detach：

```powershell
$env:FILMS_MODULE="你的配置模块名"
$p = Start-Process -FilePath "<你的 python>" `
  -ArgumentList "-u","<skill>\examples\scripts\run_films.py","片1,片2" `
  -WorkingDirectory <配置目录> -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput ".\run.log" -RedirectStandardError ".\run.err"
$p.Id | Out-File ".\run.pid" -Encoding ascii
```

配 Monitor（`persistent: true`）轮询 PID —— **独立进程结束时 harness 不会通知**，不挂 Monitor 就只能等人来问「跑完没」。

Monitor 的过滤必须覆盖**失败路径**：进程崩了也要发事件，否则「崩了」和「还在跑」看起来一模一样。

---

## ⑧ 负向提示词在 I2V 阶段可能根本不存在 ★

**适用：通用（先查你自己的工作流，多数 I2V 工作流都有这个问题）**

`《自助洗衣店》` 验证片踩到：全片设计零人物，`NEG` 里明明写了 `人, 人影, 人脸, 手, 身体`，
成片末镜却伸进来一只手往滚筒里放衣物。

**关键帧是干净的，人是图生视频阶段自己加的。**

| 阶段 | 帧 0 | 帧 24 | 帧 48 |
|---|---|---|---|
| 关键帧（z-image） | 干净 | — | — |
| I2V（LTX） | 干净 | **手伸入 + 多出一件灰衣物** | 手退出，灰衣物留下 |

根因：LTX 工作流里负向条件的来源是 —

```
node 128 = ConditioningZeroOut     ← 零条件，不是文本编码
```

整条链路**没有任何负向文本节点**。`cfg["neg"]` 只被写进 z-image 的节点 71，
`build_ltx()` 从头到尾没往负向里写过东西 —— 写多少个「人」都是白写。

### 怎么查你自己的工作流

```python
# 顺着 negative 输入回溯，看终点是 ConditioningZeroOut 还是 CLIPTextEncode
for k, v in wf.items():
    if 'negative' in v.get('inputs', {}):
        print(k, v['class_type'], '<-', v['inputs']['negative'])
```

终点是 `ConditioningZeroOut` → **这个工作流的 I2V 阶段没有负向能力**。

### ⚠️ 先说结论：逐项否定压不住，别浪费重抽次数

第一反应是照「缺席表达」那套把否定写全，实测**无效**：

```
The door stays shut and is never opened.
No person, no hand, no arm, no sleeve and no reflection of a person
appears in the frame at any moment.
The clothes inside do not move at all, nothing is added and nothing is removed.
```

| 重抽 | 结果 |
|---|---|
| v1（无否定） | 手伸入，放进一件灰衣物 |
| v2（上面这段全量否定） | **手仍然伸入，而且把舱门拉开了** |

两次错误方向一致（都是「人在操作滚筒」）→ 按坑「概念盲区」的判据，**这是盲区不是概率问题，停止加词。**

否定句在**关键帧阶段**有效（z-image 有真实的负向文本通路），在 **I2V 阶段无效** ——
零条件的负向意味着模型只看正向，而正向里的否定词在扩散模型里本来就是弱信号。

### 根因：运动先验会把动作补完

**「让它动起来」这个指令会把隐含的施动者召唤出来。**

「滚筒里的衣物」在训练数据里几乎总是伴随「有人在装衣服」。静止关键帧不含人，
一旦要求它动，模型就去补那个动作，连带补出施动者。

写运动提示词前自问：**这个画面动起来，隐含着谁在动它？**

### 真正的修法：三选一

| 方案 | 做法 | 代价 |
|---|---|---|
| **改成静止帧**（推荐） | 不跑 I2V，直接用关键帧做极缓 Ken Burns 生成该镜 | 零风险、零 GPU 时间；但该镜完全没有环境微动 |
| 换主体 | 换成没有隐含施动者的物件（地漏、通风口、灯管） | 若该镜是结构关键镜（如循环回扣），换主体等于改结构 |
| 只取前段 | 截取人出现之前的帧 | 可用秒数被压缩，长镜做不了 |

《自助洗衣店》最终走了第一条 —— s14 是循环回扣镜，必须与 s01 同构，换不了主体。
静止帧对这一镜反而更好：末镜给足静止时间，观众才有机会发现那处改变。

参考 `material-driven-storyboard` 的三选一判断（换素材 / 改静态图 + Ken Burns / 改故事），
本条是它在 I2V 阶段的具体化。

---

### PowerShell 处理中文路径会静默失败

`Move-Item "D:\ComfyUI\_废弃6-08-05\本次废片\..."` 报
`Could not find a part of the path`，但同一个目录用 Bash `mv` 完全正常。

**后果不是报错本身，是「以为移走了其实没移」** —— 今天两次踩到：
旧产物没被移走，跑批脚本的断点续跑逻辑把它们当成「已完成」直接跳过，
产出的是上个版本的素材。

**规则：涉及中文路径的文件操作一律走 Bash，不走 PowerShell。**
PowerShell 只用来管进程（`Get-CimInstance` / `Stop-Process`）。

⚠️ 顺带一条：**改了配置参数（分辨率/权重/提示词）后，产物文件名前缀应该带版本号。**
`SHANHAI_00_` 这种跨版本复用的前缀，会让断点续跑把旧版产物当成本版已完成。


## ⑨ 大文件下载：`hf_hub_download` 卡死不会自己恢复

**适用：通用**

下 19.5 GB 的权重时，`hf_hub_download(resume_download=True)` 在 2% 处**完全停住**，
25 秒零字节增长，进程还活着、不报错、不超时 —— 表现和「正在慢慢下」一模一样。

**判断方法：量两次文件大小，不要看进程是否存活。**

```bash
S1=$(stat -c %s "$F"); sleep 25; S2=$(stat -c %s "$F")
[ "$S2" -le "$S1" ] && echo "已卡死"
```

### ⚠️ 但 `curl --retry` + `-C -` 会把文件截断重下

第二次踩：换 curl 后跑到 **8.22 GB**，某次重试后掉回 **0.78 GB** —— 从头开始了。

原因：`--retry` 触发重连时，若服务端返回 `200` 而不是 `206`（区间响应），
curl 会**覆盖重写**整个输出文件。`-C -` 只在进程启动时生效一次，管不住中途的重试。

### 第三次踩：外层 shell 循环 + `curl -C -` 同样不行

以为「每轮全新 curl，启动时重读本地大小定偏移」就安全了。跑到 **10 GB** 时 `rc=56`
（recv 失败）退出，下一轮读到的文件大小变成了 **364 MB**。

**只要还在用 curl 的 `-C` 续传，状态就由 curl 内部维护，异常退出后不可信。**

### 真正的正解：显式分块 + 按 HTTP 状态码判定

根因是 **HF 大文件走 Xet 存储，会间歇性对 Range 请求返回 `200` 而不是 `206`** ——
返回 200 时 body 是**整个文件的开头**，不是你要的区间。

所以必须：自己算区间、下到临时文件、**看状态码决定要不要追加**。

```bash
D=目标文件; U=地址; TOTAL=$(curl -sIL "$U" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
CHUNK=$((256*1024*1024)); TMP="$D.chunk"
while :; do
  S=$(stat -c %s "$D" 2>/dev/null || echo 0)
  [ "$S" -ge "$TOTAL" ] && break
  E=$((S + CHUNK - 1)); [ "$E" -ge "$TOTAL" ] && E=$((TOTAL-1))
  CODE=$(curl -sL --max-time 600 -w '%{http_code}' --range "$S-$E" -o "$TMP" "$U")
  if [ "$CODE" = "206" ]; then
    cat "$TMP" >> "$D"        # 206 → 是从 S 开始的有效前缀，不完整也要
  else
    echo "丢弃 HTTP=$CODE"     # 200 → 是文件开头，追加就会毁掉整个文件
  fi
  rm -f "$TMP"
done
```

两个容易写错的点：

- **不完整的 206 要保留**，它是合法前缀。第一版把它也回退了，白白浪费带宽
- **判据必须是状态码，不是字节数**。收到 30 MB 既可能是「206 但连接断了」（保留），
  也可能是「200 的前 30 MB」（丢弃），光看大小分不出来

⚠️ 先用 `curl -sIL` 取 `content-length` 作为精确终止条件，别用百分比估算。

### 监控要区分「停滞」和「倒退」

这个坑差点被漏掉，因为监控写的是：

```bash
if [ "$S" -le "$PREV" ]; then echo "停滞"; fi     # ✗ 把「变小」也算成停滞
```

**文件变小是完全不同的故障**，必须单独报：

```bash
[ "$S" -lt "$PREV" ] && echo "!! 被截断 $PREV -> $S"
[ "$S" -eq "$PREV" ] && echo "停滞"
```

⚠️ hf 的半成品在 `<模型目录>/.cache/huggingface/download/.../*.incomplete`，
改名到目标位置就能被 `curl -C -` 接上，不用从头下。

---

## ⑩ 验收必须抽帧，不能只看日志

**适用：通用**

拼片成功不等于片子能看。逐条查：

```bash
ffmpeg -v error -y -i 成片.mp4 -vf "select='eq(n\,24)+eq(n\,66)+...',scale=340:-1,tile=3x3" -frames:v 1 检查.png
ffmpeg -v error -i 成片.mp4 -f null -            # 全解码校验
```

| 查什么 | 为什么 |
|---|---|
| 有没有乱码文字 | 见 `prompt-craft.md` 文字载体 |
| 人物是否一致 | 校验可能静默降级（坑 ②） |
| 辉光是否过头 | 高对比素材配 0.40 会炸出星芒 |
| 末帧有没有漂 | `max_shot_sec` 是否标定准确 |
| **指纹是否已写回** | 漏了反同质化机制下次就失效 |

最后一条容易忘，但它是整套机制的闭环。

---

## ⑪ concat 之后必须重建时间戳，否则静默丢帧 ★

**适用：通用（任何多段拼接）**

```
✗ [0:v]<调色链>[v]
✅ [0:v]setpts=N/24/TB,<调色链>[v]
```

concat demuxer 拼接时**每段各自从 PTS 0 起算**，时间戳撞车的帧会被编码器直接丢掉。
实测 6062 帧拼成 6013 帧，少 2 秒，**没有任何报错或警告**。

危险在于它的表现太温和：画面只是"短了一点"，很容易被忽略。
但丢帧是**累积**的 —— 音画会越到后面偏得越多，
片尾那句最重要的旁白就踩空了。

同源问题出现在剪辑阶段：`trim` 之后用 `setpts=PTS-STARTPTS` 也会埋下这个雷，
一律改成 `setpts=N/FPS/TB`（按帧序号重建，严格递增且间隔均匀）。

**验收**：数帧，不要看时长。

```bash
ffprobe -count_frames -select_streams v:0 -show_entries stream=nb_read_frames out.mp4
```

---

## ⑫ 提示词里的文字会被画进画面 ★

**适用：`text_sensitivity: low` 的档（H3 这类）尤其明显**

模型会把提示词里**任何像标签的短语**渲染成画面文字，位置就在标准字幕位
（画面底部居中，y≈0.88）。同一段连撞三次，每次画的都是当时最"可引用"的那句：

| 第几版 | 提示词里有什么 | 画出来的字 |
|---|---|---|
| 1 | `旁白说："他没有拔剑。"` | 「他没有拔剑」 |
| 2 | 删掉旁白，补了配角描述 `二十五六岁` | 「二十五六岁」 |
| 3 | 去掉数字，剩动作描述 `行了个礼` | 「行了个礼」 |

**数字风险最高** —— 年龄是我加进去才出现的，加之前没有，去掉又没了。

### 三条规矩

1. **不需要口型就别把台词写进提示词。** 音轨反正后期重配。
2. **角色描述里不写任何数值**（年龄、身高、数量），改用形容词。
3. **`画面无文字无水印` 完全无效。** 上面三版提示词末尾**都带着这句**。
   这和坑 ⑧ 是同一条规律：负面词压不住，得改画面内容。

### 顽固段用确定性手段

换三次种子还画字的段，别再赌了 —— 裁掉底部 14% 再放大回原尺寸，
物理消除。代价是 1.16 倍推近，夹在切点之间看不出来。

### 怎么扫

肉眼逐帧翻不现实。装个 OCR 自动扫（`rapidocr_onnxruntime`，无需 key）：

```python
# 装到独立目录，别污染 ComfyUI 环境（它自带 numpy，会和 torch 打架）
# pip install --target <tmp>/ocr rapidocr_onnxruntime
# 必须单独起进程跑，不能和 torch/cv2 混在一个进程里
```

判据不是"检出了字"，而是**位置 + 宽度**：
`cy >= 0.78 且 0.3 <= cx <= 0.7` 才是字幕位。
刺绣纹样会被认成单个字母（宽度 0.01-0.05），那是噪声。
**宽度大但只认出一两个字**的最可疑 —— 那是一条乱码文字带。

---

## ⑬ Windows 上的三个静默失败 ★

**适用：通用**

三个都不报错，都让你以为是别的地方出了问题。

### Python 文本模式写文件 → CRLF

```python
✗ open(path, "w", encoding="utf-8")             # \n 被翻成 \r\n
✅ open(path, "w", encoding="utf-8", newline="\n")
```

bash 读出来的每一行都带一个 `\r`，拼出的路径全部对不上。
表现是"文件不存在"，极易误判成上一步生成失败。

防御性做法是两头都修，bash 侧也剥一下：

```bash
while read -r i; do i="${i%$'\r'}"; ... done < order.txt
```

### cv2 遇中文路径静默失败

`cv2.imwrite()` 返回 `False` 而不抛异常，`cv2.imread()` 返回 `None`。

```python
def wr(p, img):
    ok, buf = cv2.imencode(".png", img)
    open(p, "wb").write(buf.tobytes())

def rd(p):
    return cv2.imdecode(np.frombuffer(open(p, "rb").read(), np.uint8), 1)
```

同类：PowerShell 的 `Move-Item` 处理中文路径也会静默失败（坑 ⑧ 末节）。
**中文路径的文件操作一律走 Bash 或 Python 字节流。**

### 片源尺寸不能写死

以为是 736×416，实际模型吐的是 **768×416**（对齐到 32 的倍数）。
被单独裁剪的那一段缩放回了错误尺寸，concat 在那里断掉，成片只剩一半长度。

```python
r = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0:s=x", probe], capture_output=True, text=True)
OW, OH = [int(v) for v in r.stdout.strip().split("x")[:2]]
```

---

## ⑭ 杀进程时会杀到自己 ★

**适用：通用（坑 ② 的补充，这是同一天第四次踩）**

```powershell
# ✗ 这条命令自己的命令行里就含有 'jw_regen.sh'，会把自己的父 shell 杀掉
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*jw_regen.sh*' } | Stop-Process
```

表现是命令返回 exit 255，而你以为是权限问题。

```powershell
# ✅ 用字符串拼接绕开自匹配
$a='jw_'+'regen.sh'
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*$a*" }
```

### 杀完必须验残留，然后才能重启

没验就重启的代价：两条流水线同时跑，**两个 ComfyUI 抢同一个端口**，
互相踩对方的输出文件名。

**给所有长跑脚本加 mkdir 互斥锁**：

```bash
LOCK="$BASE/.regen.lockdir"
if ! mkdir "$LOCK" 2>/dev/null; then
  OLD=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "已有实例 pid=$OLD，退出"; exit 1
  fi
  echo "陈旧锁，接管"
fi
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT
```

---

## ⑮ 通用超分会拧坏小人脸 ★

**适用：通用（任何 ESRGAN 系放大）**

阈值很清晰：**人脸短边 < 110 px 时，超分是破坏性的**。
五官熔成一团、脸上长出十字鳞片伪纹理、眼周出硬边。
脸 > 150 px 则无害。

原理：通用放大模型对小而糊的人脸没有先验，必须"填"出细节 —— 只能编。

**修法要在生成阶段，不在后期** —— 超分补不出生成时就不存在的信息。按代价从小到大：

1. **提高生成分辨率** —— 最直接。脸的像素数正比于画幅，
   0.3 MP 提到 0.5 MP 是 1.30 倍线性放大，86 px 的脸变 112 px，跨过阈值。
   **不必全片都提，只提脸小的那几段** —— 后期反正要统一超分到同一尺寸。
2. **改景别 / 换构图重抽** —— 脸只有 50 px 的镜头，提到 1 MP 也才 91 px，
   参数救不了，只能改构图。
3. **换种子重抽** —— 只对"构图没问题但这一版画糊了"有效。

**上面三条都来不及做，才用按段分治**（脸小的段走 lanczos 原生放大）。
要清楚它做的是"不去编造"而不是"修好"：脸该糊还是糊，
只是从"编错的五官"退回到"看不清的五官"。详见 `post-production.md` 第 3 节。

**人脸修复（CodeFormer / GFPGAN）不是解法**，对奇幻角色反而是负资产：
实测把琥珀金瞳改成灰蓝、加重眼线，`fidelity=0.9` 都拦不住。

---

## ⑯ ffmpeg 的两个本机陷阱

**适用：本机（Windows + Git Bash）**

### drawtext 段错误

`drawtext` 滤镜在本机会 Segmentation fault（fontconfig 找不到字体）。
但 `subtitles` / `ass` 滤镜（libass）正常 —— 显式给 `fontsdir` 即可。

要在图上标序号，改用位置定位（固定列数排布），或者用 PIL 画好再叠。

### cv2 读不了部分 mp4

`VideoHelperSuite` 输出的 mp4 用 `cv2.VideoCapture` 打不开
（`Could not find decoder for codec_id=61`）。
用 ffmpeg 抽帧成 PNG 再读，别在 cv2 里硬啃视频。
