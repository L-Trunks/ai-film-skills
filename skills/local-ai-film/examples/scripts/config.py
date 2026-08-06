# -*- coding: utf-8 -*-
"""这台机器的配置 —— 所有机器相关的路径都集中在这里，脚本正文不写绝对路径。

三种改法，任选其一：

  ① 环境变量（推荐，不用改文件，也不会被 git 追踪）
       set AIFILM_COMFY=D:\\ComfyUI
       set AIFILM_PY=D:\\conda\\envs\\comfy\\python.exe
       set AIFILM_ROOT=E:\\我的短片

  ② 在同目录建 config_local.py，写同名变量覆盖
       COMFY = r"D:\\ComfyUI"
       ROOT  = r"E:\\我的短片"
     （config_local.py 已在 .gitignore 里，不会被提交）

  ③ 直接改本文件的默认值

跑 `python doctor.py` 可以体检当前配置对不对。
"""
import os
import shutil

def _env(key, default):
    return os.environ.get("AIFILM_" + key, default)


# ── 必填三项 ──────────────────────────────────────────────
COMFY = _env("COMFY", r"D:\ComfyUI")                 # ComfyUI 根目录
PY    = _env("PY", r"D:\Software\conda\envs\comfyui_env\python.exe")   # 跑 ComfyUI 的 python
ROOT  = _env("ROOT", r"E:\Projects\AI\popsci-studio\_短片")            # 成片输出根目录

# ── 由上面推导，通常不用改 ────────────────────────────────
API   = _env("API", "http://127.0.0.1:8188")
CO    = _env("CO", os.path.join(COMFY, "output"))
CI    = _env("CI", os.path.join(COMFY, "input"))
MAIN  = os.path.join(COMFY, "main.py")

# ── 模型文件名（要和你 ComfyUI 里实际的文件名一致）────────
UNET_LTX = _env("UNET_LTX", "LTX-2.3-22B-distilled-1.1-Q4_K_M.gguf")
UNET_H3  = _env("UNET_H3", "minimax_h3_fl2va_pruned_int8_convrot.safetensors")

# ── 可选 ─────────────────────────────────────────────────
T2I_WORKFLOW = _env("T2I_WORKFLOW", "")   # 文生图工作流 json，留空则跳过关键帧生成
FONT = _env("FONT", r"C:\Windows\Fonts\simkai.ttf")
BGM_DIR = _env("BGM_DIR", os.path.join(ROOT, "_bgm"))

# ── 本地覆盖 ─────────────────────────────────────────────
try:
    from config_local import *          # noqa: F401,F403
except ImportError:
    pass


def check():
    """返回 [(项, 值, 是否就绪, 说明)]，供 doctor.py 用。"""
    rows = [
        ("ComfyUI 根目录", COMFY, os.path.isdir(COMFY), "AIFILM_COMFY"),
        ("ComfyUI main.py", MAIN, os.path.isfile(MAIN), "由 COMFY 推导"),
        ("python 解释器", PY, os.path.isfile(PY), "AIFILM_PY"),
        ("输出根目录", ROOT, os.path.isdir(os.path.dirname(ROOT)) or os.path.isdir(ROOT),
         "AIFILM_ROOT，不存在会自动建"),
        ("ComfyUI input", CI, os.path.isdir(CI), "由 COMFY 推导"),
        ("ComfyUI output", CO, os.path.isdir(CO), "由 COMFY 推导"),
        ("ffmpeg", shutil.which("ffmpeg") or "未找到", bool(shutil.which("ffmpeg")), "需在 PATH 里"),
        ("ffprobe", shutil.which("ffprobe") or "未找到", bool(shutil.which("ffprobe")), "需在 PATH 里"),
        ("字体", FONT, os.path.isfile(FONT), "AIFILM_FONT，只有加字幕才用得到"),
    ]
    return rows
