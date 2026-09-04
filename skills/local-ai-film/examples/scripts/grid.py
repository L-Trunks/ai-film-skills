# -*- coding: utf-8 -*-
"""镜头格子 —— 每一格要么盖过章，要么还在重跑。**全部盖章之前不许进下游。**

配套 `knowledge/grid-review.md`。⛔ 那份文档第一条：**这套默认不开，要先问用户** ——
每一轮盖章都要把联络表当图片喂进上下文，token 用量和上下文占用会明显上去。

验收不是「跑完看一遍」，而是一格一格填：
  ① 看 seg（超分前）→ ② 满意就 --过，不满意 --退 并写清楚为什么
  ③ 退的改提示词 → 按指纹清场重跑 → 回 ①
  ④ 全格盖满才进下游（超分 / 剪辑 / 混音）

⛔ 盖章要连**当时那一版的提示词指纹**一起记。提示词一改，章自动失效 ——
   否则两三轮之内就退化回「只看文件在不在」那个病。

⛔ 拿不准的那一格要单独放大重截再判，不要在联络表的缩图上定罪。

    python grid.py                          看格子：还差哪些镜
    python grid.py --过 A04,D07             盖章
    python grid.py --退 E22 "台阶方向反了"   打回并记原因

依赖：同目录下有一份 `shots.py`，提供 `SHOTS`（每项含 `key`）和 `build_prompt(sh)`。
      产物按 `seg/<key>.mp4` 命名。两处都按你自己的片子改。
"""
import argparse
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shots as SB                                            # noqa: E402

账 = os.path.join(HERE, "work", "验收.json")
产物 = lambda k: os.path.join(HERE, "seg", k + ".mp4")        # noqa: E731


def 指纹(sh):
    return hashlib.md5(SB.build_prompt(sh).encode("utf-8")).hexdigest()[:12]


def 读():
    return json.load(open(账, encoding="utf-8")) if os.path.exists(账) else {}


def 写(d):
    os.makedirs(os.path.dirname(账), exist_ok=True)
    json.dump(d, open(账, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--过", default="")
    ap.add_argument("--退", nargs=2, default=None, metavar=("镜号", "原因"))
    a = ap.parse_args()

    表 = {s["key"]: s for s in SB.SHOTS}
    d = 读()

    if getattr(a, "过"):
        for k in getattr(a, "过").split(","):
            k = k.strip()
            d[k] = {"判": "过", "指纹": 指纹(表[k])}
        写(d)
        print("盖章 %s" % getattr(a, "过"))
    if getattr(a, "退"):
        k, why = getattr(a, "退")
        d[k] = {"判": "退", "指纹": 指纹(表[k]), "因": why}
        写(d)
        print("打回 %s：%s" % (k, why))

    过, 退, 缺 = [], [], []
    for s in SB.SHOTS:
        k = s["key"]
        r = d.get(k)
        if not os.path.exists(产物(k)):
            缺.append(k + "（没段）")
        elif not r or r.get("指纹") != 指纹(s):
            缺.append(k)                      # 没看过，或看过之后提示词又改了
        elif r["判"] == "过":
            过.append(k)
        else:
            退.append((k, r.get("因", "")))

    print("\n格子 %d/%d 已盖章" % (len(过), len(SB.SHOTS)))
    if 退:
        print("\n打回重跑 %d 镜：" % len(退))
        for k, why in 退:
            print("  %-5s %s" % (k, why))
    if 缺:
        print("\n还没看 %d 镜：%s" % (len(缺), " ".join(缺)))
    if not 退 and not 缺:
        print("⭐ 全部盖章 —— 可以进下游了。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
