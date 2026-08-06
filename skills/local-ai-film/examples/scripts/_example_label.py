# -*- coding: utf-8 -*-
"""《奇形怪状》纪录片化：右下角楷体物种名 + 换更沉的 BGM 重新拼片。

BGM 换 cand_volatile：质心 1196Hz（最暗）、节奏强度 1.33（小调里最低）、
低频 33%。比原来的 audioknap（1385/1.41）更沉、更不流行化，符合纪录片气质。
"""
import os, sys, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["FILMS_MODULE"] = "films4"
import films4 as F

BASE = r"E:\Projects\AI\popsci-studio\_短片\奇形怪状"
BR, LB, OUT = os.path.join(BASE, "broll"), os.path.join(BASE, "broll_labeled"), os.path.join(BASE, "out")
FONT_SRC = r"C:\Windows\Fonts\simkai.ttf"
FONT = os.path.join(HERE, "kai.ttf")
BGM = r"E:\Projects\AI\popsci-studio\_视频剪辑流水线\bgm\cand_volatile.mp3"
BGM_VOL = 0.19          # 由 audioknap@0.23→RMS 0.0685 反推，目标 RMS 0.06

D, T = F.FRAMES / 24.0, F.TRANS
FADE_IN, FADE_OUT, SIZE = 0.35, 0.40, 36

NAMES = {
 "m01": "星鼻鼹", "m02": "鸭嘴兽", "m03": "三趾树懒", "m04": "穿山甲", "m05": "裸鼹鼠",
 "m06": "指猴", "m07": "长鼻猴", "m08": "眼镜猴", "m09": "大食蚁兽", "m10": "犰狳", "m11": "蜜獾",
 "s01": "独角鲸", "s02": "海牛", "s03": "水滴鱼", "s04": "鮟鱇鱼", "s05": "皇带鱼",
 "s06": "叶海龙", "s07": "海蛞蝓", "s08": "鹦鹉螺", "s09": "螳螂虾", "s10": "翻车鱼",
 "s11": "管虫", "s12": "鲎", "s13": "椰子蟹", "s14": "招潮蟹", "s15": "海百合",
 "b01": "鲸头鹳", "b02": "军舰鸟", "b03": "蓝脚鲣鸟", "b04": "极乐鸟", "b05": "犀鸟",
 "b06": "巨嘴鸟", "b07": "秘书鸟", "b08": "几维鸟", "b09": "鹤鸵",
 "i01": "兰花螳螂", "i02": "竹节虫", "i03": "叶䗛", "i04": "角蝉", "i05": "长颈鹿象鼻虫",
 "i06": "蓝闪蝶", "i07": "蜂鸟鹰蛾", "i08": "水熊虫", "i09": "马陆", "i10": "蚁狮",
 "r01": "玻璃蛙", "r02": "伞蜥", "r03": "飞蜥", "r04": "变色龙", "r05": "蓝箭毒蛙",
 "r06": "加拉帕戈斯象龟", "r07": "角蝰",
 "p01": "大王花", "p02": "猪笼草", "p03": "捕蝇草", "p04": "茅膏菜", "p05": "生石花",
 "p06": "猴面小龙兰", "p07": "蜂兰", "p08": "鹤望兰", "p09": "巨魔芋", "p10": "王莲",
 "p11": "猴面包树", "p12": "千岁兰", "p13": "龙血树", "p14": "绞杀榕", "p15": "发光蘑菇",
 "p16": "鹿角蕨", "p17": "含羞草", "p18": "红树林",
}
ORDER = F.FILMS["odd"]["order"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("失败:", (r.stderr or "")[-600:]); return False
    return True


def label(sid):
    src, dst = os.path.join(BR, sid + ".mp4"), os.path.join(LB, sid + ".mp4")
    if not os.path.exists(src):
        print("  %s 源缺失" % sid); return False
    if sid not in NAMES:
        print("  %s 无名称" % sid); return False
    alpha = ("if(lt(t,{fi}),t/{fi},if(lt(t,{ho}),1,max(0,({d}-t)/{fo})))"
             .format(fi=FADE_IN, ho=D - FADE_OUT, d=D, fo=FADE_OUT))
    vf = ("drawtext=fontfile=kai.ttf:text='%s':x=w-tw-64:y=h-th-56:"
          "fontsize=%d:fontcolor=white:shadowcolor=black@0.45:shadowx=2:shadowy=2:"
          "alpha='%s'" % (NAMES[sid], SIZE, alpha))
    return run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", vf,
                "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                "-pix_fmt", "yuv420p", dst])


def assemble(shots):
    ins = []
    for s in shots:
        ins += ["-i", os.path.join(LB, s + ".mp4")]
    parts, cur, off = [], "[0:v]", D - T
    for i in range(1, len(shots)):
        lbl = "[x%d]" % i
        parts.append("%s[%d:v]xfade=transition=dissolve:duration=%.2f:offset=%.2f%s"
                     % (cur, i, T, off, lbl))
        cur = lbl; off += D - T
    total = D * len(shots) - T * (len(shots) - 1)
    raw = os.path.join(OUT, "_raw_labeled.mp4")
    if not run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(parts),
                "-map", cur, "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-r", "24", raw]):
        return
    final = os.path.join(OUT, "成片_奇形怪状.mp4")
    af = ("[1:a]volume=%.2f,afade=t=in:st=0:d=2,afade=t=out:st=%.1f:d=2.5[a]"
          % (BGM_VOL, total - 2.5))
    if run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-stream_loop", "-1", "-i", BGM,
            "-filter_complex", af, "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final]):
        d = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
        print("成片 %d 镜 / %.2fs -> %s" % (len(shots), float(d), final))


if __name__ == "__main__":
    os.makedirs(LB, exist_ok=True)
    if not os.path.exists(FONT):
        shutil.copyfile(FONT_SRC, FONT)
    os.chdir(HERE)
    miss = [s for s in ORDER if s not in NAMES]
    if miss:
        print("缺名称:", miss); sys.exit(1)
    ok = [s for s in ORDER if label(s)]
    print("已标注 %d/%d 镜" % (len(ok), len(ORDER)))
    if len(ok) == len(ORDER):
        assemble(ok)
