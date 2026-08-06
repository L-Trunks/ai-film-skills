# -*- coding: utf-8 -*-
"""按频谱目标档抓无版权 BGM —— 内容 → 搜索词 → 下载 → 频谱体检 → 只留贴合的。

解决的问题：曲库只有 5 首、三档频谱里有一档挤了 3 首另两档各 1 首，
导致 9 部片的 audio 维全是「BGM通铺」—— 不是不想变，是没得选。

源：
  openverse  无需 key，聚合 CC0 / CC-BY，已实测可用
  pixabay    需 PIXABAY_API_KEY 环境变量（免费申请），CC0 类许可，未实测

⚠ key 一律走环境变量，不写进任何配置文件。

用法：
  python bgm_fetch.py deep  --n 8
  python bgm_fetch.py fresh --n 6 --out D:\bgm
"""
import argparse, json, os, subprocess, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bgm_pick import analyze, score, TARGETS      # noqa: E402

UA = {"User-Agent": "ai-film-skills/0.1 (royalty-free BGM sourcing)"}

# 三档各自的搜索词。挑词的原则：描述「声音质地」而不是「情绪」——
# 搜 "sad" 拿到的是人声民谣，搜 "low drone minor" 才拿到能当底的东西。
#
# ⚠ Openverse 的 category=music 只对单词查询生效，多词短语加上它会 0 命中
#   （实测 "ambient"+category → 195 条，"cinematic ambient drone"+category → 0）。
#   所以不发 category 参数，改在客户端过滤。搜索词也尽量短。
TERMS = {
    "fresh": ["ambient", "pad", "piano ambient", "acoustic loop", "chimes"],
    "deep":  ["cinematic", "drone", "atmospheric", "underscore", "dark pad"],
    "dark":  ["dark ambient", "drone dark", "eerie pad", "suspense ambient", "cinematic dark"],
}

# 成片是无对白氛围片时，BGM 是唯一音轨 → 目标 RMS 0.075（见 knowledge/bgm-spectral.md）
MIN_DUR = 30.0          # 太短的循环起来接缝明显
MAX_KEEP_SCORE = 1.2    # 与目标档的距离上限，超过就不是这一档的曲子

# 曲名流派排除表。
# 频谱三项只量音色，量不到「有没有明确节拍」—— 一段 140BPM 的 hip-hop loop
# 可以和氛围 pad 有完全相同的质心/滚降/低频占比（实测踩过：抓 deep 档抓回来一首
# 「Hip-Hop Rap Lead Loop BPM 140」）。
# 试过用谱通量自相关做节拍检测，全频段和低频段两版都无法区分，已放弃 ——
# 这个笨办法反而可靠：有节拍的曲子，作者基本都会在标题里写明流派或 BPM。
#
# ⚠ 非英文标题会绕过纯英文的排除表 —— 实测漏掉过一首 "Batería y pads"
#   （batería = 西班牙语「鼓」）。Openverse 聚合多语种来源，务必带上常见外语词。
GENRE_BLOCK = [
    # 英文流派 / 节拍标记
    "bpm", "hip hop", "hip-hop", "hiphop", "rap", "trap", "drill",
    "edm", "dance", "house", "techno", "dubstep", "dnb", "drum and bass",
    "beat", "drums", "drum", "percussion", "groove", "funk", "disco",
    "rock", "metal", "punk", "jazz", "swing", "reggae", "latin",
    "pop song", "vocal", "singing", "acapella", "choir",
    "loop pack", "sample pack", "riff", "solo", "guitar", "bass line",
    # 西班牙语 / 葡萄牙语
    "batería", "bateria", "tambor", "percusión", "percussão", "ritmo",
    "guitarra", "canción", "voz",
    # 法语 / 德语 / 意大利语
    "batterie", "tambour", "rythme", "chanson",
    "schlagzeug", "trommel", "rhythmus", "gitarre",
    "batteria", "ritmo italiano", "chitarra",
    # 日文 / 中文
    "ドラム", "リズム", "ギター", "ボーカル",
    "鼓", "节拍", "吉他", "人声",
]


def genre_blocked(title):
    t = title.lower()
    return next((w for w in GENRE_BLOCK if w in t), None)


# ⚠ Openverse 的 license_type=commercial 只保证「可商用」，**不排除 ND**。
#   ND = NoDerivatives，禁止演绎 —— 把音乐配到视频上通常构成演绎作品，
#   用 ND 曲目当 BGM 有法律风险。实测抓回来过一首 by-nd 2.0。
#   SA = ShareAlike，会传染许可到整条片子，同样不适合。
LICENSE_BLOCK = ("nd", "sa", "nc")


def license_blocked(lic):
    """lic 形如 'by-nd 2.0' / 'cc0 1.0' / 'by 4.0'。"""
    code = (lic or "").split()[0].lower()
    parts = code.replace("cc-", "").split("-")
    return next((p for p in parts if p in LICENSE_BLOCK), None)


def openverse(term, page_size=20):
    # ⚠ 匿名访问 page_size 上限就是 20，填 40 会直接 401 Unauthorized（不是限流，实测
    #   requests_today=2 时照样 401）。要更大页需去 Openverse 注册拿 token。
    q = urllib.parse.urlencode({
        "q": term, "license_type": "commercial", "page_size": page_size,
    })
    req = urllib.request.Request("https://api.openverse.org/v1/audio/?" + q, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as f:
        d = json.load(f)
    out = []
    for r in d.get("results", []):
        u = r.get("url")
        if not u:
            continue
        # 客户端过滤：明确标了非 music 的直接扔；duration 是毫秒
        if r.get("category") not in (None, "music"):
            continue
        dur_ms = r.get("duration") or 0
        if dur_ms and dur_ms < MIN_DUR * 1000:
            continue
        out.append({
            "title": (r.get("title") or "untitled")[:60],
            "url": u,
            "license": "%s %s" % (r.get("license", "?"), r.get("license_version") or ""),
            "creator": r.get("creator") or "",
            "source": r.get("source") or "openverse",
            "detail": r.get("foreign_landing_url") or "",
        })
    return out


def pixabay(term, page_size=20):
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return []
    q = urllib.parse.urlencode({"key": key, "q": term, "per_page": page_size})
    req = urllib.request.Request("https://pixabay.com/api/audio/?" + q, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            d = json.load(f)
    except Exception as e:
        print("  pixabay 查询失败（端点可能与文档不符）: %r" % e)
        return []
    out = []
    for r in d.get("hits", []):
        u = r.get("audio") or r.get("previewURL")
        if not u:
            continue
        out.append({"title": (r.get("tags") or "untitled")[:60], "url": u,
                    "license": "Pixabay Content License", "creator": r.get("user") or "",
                    "source": "pixabay", "detail": r.get("pageURL") or ""})
    return out


def slug(s):
    keep = "".join(c if c.isalnum() or c in " -_" else "" for c in s).strip()
    return (keep or "track").replace(" ", "_")[:48]


def download(url, dst):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as f, open(dst, "wb") as o:
        o.write(f.read())
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=list(TARGETS))
    ap.add_argument("--n", type=int, default=6, help="每档要留几首")
    ap.add_argument("--out", default=r"E:\Projects\AI\popsci-studio\_视频剪辑流水线\bgm")
    a = ap.parse_args()

    stage = os.path.join(a.out, "_staging")
    os.makedirs(stage, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    manifest_p = os.path.join(a.out, "LICENSES.jsonl")
    seen = set()
    if os.path.exists(manifest_p):
        for line in open(manifest_p, encoding="utf-8"):
            try:
                seen.add(json.loads(line)["url"])
            except Exception:
                pass

    tc, tr, tl, tm = TARGETS[a.target]
    print("目标档 %s：质心~%d 滚降~%d 低频~%.0f%% %s\n"
          % (a.target, tc, tr, tl * 100, tm or "调性不限"))

    cands = []
    for term in TERMS[a.target]:
        for fn in (openverse, pixabay):
            try:
                got = fn(term)
            except Exception as e:
                print("  %s('%s') 失败: %r" % (fn.__name__, term, e)); continue
            for g in got:
                if g["url"] not in seen:
                    seen.add(g["url"]); cands.append(g)
        time.sleep(0.5)
    print("候选 %d 条\n" % len(cands))

    kept, rows = 0, []
    for c in cands:
        if kept >= a.n:
            break
        bad = genre_blocked(c["title"])
        if bad:
            print("  [排除] %-40s 标题含「%s」" % (c["title"][:40], bad)); continue
        lbad = license_blocked(c["license"])
        if lbad:
            print("  [排除] %-40s 许可 %s 含 %s" % (c["title"][:40], c["license"], lbad.upper()))
            continue
        ext = os.path.splitext(urllib.parse.urlparse(c["url"]).path)[1] or ".mp3"
        tmp = os.path.join(stage, slug(c["title"]) + ext)
        try:
            download(c["url"], tmp)
            an = analyze(tmp)
        except Exception as e:
            print("  跳过 %-40s %s" % (c["title"][:40], str(e)[:50])); continue
        if an["dur"] < MIN_DUR:
            print("  太短 %-40s %.0fs" % (c["title"][:40], an["dur"])); os.remove(tmp); continue
        s = score(an, a.target)
        mark = "留" if s <= MAX_KEEP_SCORE else "弃"
        print("  [%s] %-40s 质心%5.0f 滚降%5.0f 低频%3.0f%% %-9s 距离%.2f"
              % (mark, c["title"][:40], an["centroid"], an["rolloff"],
                 an["low"] * 100, an["key"], s))
        if s > MAX_KEEP_SCORE:
            os.remove(tmp); continue
        dst = os.path.join(a.out, "%s_%s%s" % (a.target, slug(c["title"]), ext))
        os.replace(tmp, dst)
        c.update(file=os.path.basename(dst), band=a.target,
                 centroid=round(an["centroid"]), rolloff=round(an["rolloff"]),
                 low=round(an["low"], 3), key=an["key"], dur=round(an["dur"], 1))
        rows.append(c); kept += 1

    with open(manifest_p, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\n留下 %d 首 -> %s" % (kept, a.out))
    print("许可与署名已追加到 %s" % manifest_p)
    if any("by" in r["license"].lower() and "cc0" not in r["license"].lower() for r in rows):
        print("⚠ 其中有 CC-BY 曲目，发布时必须在视频描述里署名，见 LICENSES.jsonl")


if __name__ == "__main__":
    main()
