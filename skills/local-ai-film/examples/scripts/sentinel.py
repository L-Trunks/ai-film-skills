# -*- coding: utf-8 -*-
"""哨兵：盯着独立跑批进程，它一结束就退出。

为什么需要：跑批用 Start-Process 起的独立进程（为了不被会话杀掉），
但独立进程结束时 harness 不会通知我，导致每次都要用户来问「跑完没」。
哨兵由 harness 托管，只做轮询 + 退出，它一退出我就收到完成通知。

用法：Bash 工具 run_in_background=true 启动本脚本。
"""
import os, sys, time, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PID_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "b3_run.pid")
LABEL = sys.argv[2] if len(sys.argv) > 2 else "跑批"
MAX_H = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0


def alive(pid):
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "if (Get-Process -Id %d -ErrorAction SilentlyContinue) {'1'} else {'0'}" % pid],
                       capture_output=True, text=True)
    return r.stdout.strip() == "1"


if __name__ == "__main__":
    try:
        pid = int(open(PID_FILE).read().strip())
    except Exception as e:
        print("读不到 PID 文件: %r" % e); sys.exit(1)
    print("哨兵盯住 %s PID %d" % (LABEL, pid), flush=True)
    t0 = time.time()
    while time.time() - t0 < MAX_H * 3600:
        if not alive(pid):
            print("%s 已结束（耗时 %.0f 分钟）" % (LABEL, (time.time() - t0) / 60), flush=True)
            sys.exit(0)
        time.sleep(45)
    print("%s 超过 %.1f 小时仍在运行，哨兵退出" % (LABEL, MAX_H), flush=True)
