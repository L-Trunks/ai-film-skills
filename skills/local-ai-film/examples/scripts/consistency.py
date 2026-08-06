# -*- coding: utf-8 -*-
"""关键帧一致性自动判定 —— 生成即验，不一致就重抽。

三类一致性，按需启用（在 shot 里声明才检查，不声明零开销）：
  face   人物一致性  InsightFace 人脸嵌入余弦
  env    环境一致性  CLIP 图像嵌入（同一个世界/季节/时段）
  scene  场景一致性  CLIP 图像嵌入（同一个具体地点，阈值更严）

为什么必须自动判定：跑批无人值守，模型看不到中间产物。
靠事后抽帧发现不一致，意味着几小时素材已经跑完才返工。

CPU-only：跑批时 GPU 被 LTX 占满，判定绝不能抢卡。
InsightFace 约 0.3s/张，CLIP ViT-B-32 约 0.06s/张，可忽略。

═══ 阈值标定（本机实测，z-image 出的图）═══
face   同一角色跨镜头 0.338 / 0.344 / 0.402 / 0.417
       不同角色       0.116 / 0.137 / 0.141 / 0.244   → 取 0.28
       ⚠ 别照搬真人照片经验值(0.5+)，AI 生成的同一角色相似度天然偏低
env    同片跨地点 0.500 / 0.504 / 0.615 / 0.710 / 0.882
       跨片       0.428 / 0.434 / 0.482 / 0.531       → 取 0.55（宽松，只拦跑飞）
scene  同一具体地点应达 0.70+（实测同片同调子可到 0.882）→ 取 0.65

⚠ 试过但不可用的方案（别再走回头路）：
  · 色彩直方图交集 —— 跨片相似度反而高于同片，无区分度
  · 色温/明度/饱和标量差 —— 雪街 vs 夏天阳台的明度差(0.064)
    竟小于同环境两镜(0.176)，色彩统计判断不了「是不是同一个地方」
  · 网格结构+梯度能量 —— 同上，跨片 0.809 > 同片 0.797
"""
import os
import numpy as np
from PIL import Image

_FACE_APP = None
_CLIP = None
_FAIL = {"face": False, "clip": False}


# ────────────────────────── 人物 ──────────────────────────
def _face_app():
    global _FACE_APP
    if _FACE_APP is not None or _FAIL["face"]:
        return _FACE_APP
    try:
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _FACE_APP = app
    except Exception as e:
        print("   [一致性] InsightFace 不可用，人物检查跳过: %s" % str(e)[:120])
        _FAIL["face"] = True
    return _FACE_APP


def face_embeddings(path):
    """画面里所有人脸的嵌入（按脸的大小降序）。
    必须返回全部而非最大的那张 —— 双人镜里最大的脸未必是目标角色，
    只比最大脸会得到接近随机的分数（实测 0.078，改成全比后 0.320）。"""
    app = _face_app()
    if app is None:
        return []
    import cv2
    img = cv2.imread(path)
    if img is None:
        return []
    fs = app.get(img)
    fs.sort(key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
    return [np.asarray(f.normed_embedding, dtype=np.float32) for f in fs]


def face_embedding(path):
    """锚点用：取最大那张脸。锚点图应当是单人清晰肖像。"""
    es = face_embeddings(path)
    return es[0] if es else None


def best_face_similarity(path, ref):
    """画面里任意一张脸匹配上锚点即算通过，取最高分。"""
    if ref is None:
        return None
    es = face_embeddings(path)
    return max((float(np.dot(e, ref)) for e in es), default=None)


# ────────────────────────── 环境 / 场景 ──────────────────────────
def _clip():
    global _CLIP
    if _CLIP is not None or _FAIL["clip"]:
        return _CLIP
    try:
        os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")
        os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
        import open_clip, torch
        model, _, prep = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k", device="cpu")
        model.eval()
        _CLIP = (model, prep, torch)
    except Exception as e:
        print("   [一致性] CLIP 不可用，环境/场景检查跳过: %s" % str(e)[:120])
        _FAIL["clip"] = True
    return _CLIP


def clip_embedding(path):
    c = _clip()
    if c is None:
        return None
    model, prep, torch = c
    try:
        with torch.no_grad():
            v = model.encode_image(prep(Image.open(path).convert("RGB")).unsqueeze(0))
        v = v[0].numpy()
        return v / (np.linalg.norm(v) + 1e-8)
    except Exception:
        return None


def clip_similarity(a, b):
    if a is None or b is None:
        return None
    return float(np.dot(a, b))


def color_delta(pa, pb):
    """辅助信息：色温/明度/饱和差。不作判据，只在日志里提示调色是否断层。"""
    def sig(p):
        im = Image.open(p).convert("RGB").resize((160, 160))
        a = np.asarray(im, dtype=np.float32) / 255.0
        hsv = np.asarray(im.convert("HSV"), dtype=np.float32) / 255.0
        return a[..., 0].mean() - a[..., 2].mean(), a.mean(), hsv[..., 1].mean()
    wa, ba, sa = sig(pa); wb, bb, sb = sig(pb)
    return {"warm": abs(wa - wb), "bright": abs(ba - bb), "sat": abs(sa - sb)}


# ────────────────────────── 服装（细节一致性）──────────────────────────
def _torso_crop(path):
    """从人脸框推出躯干区域 —— 下巴以下 2.2 倍脸高、3 倍脸宽。
    ⚠ 只有躯干可用，头部区域实测无区分度：
      同人同装头部 0.715-0.849，异人异装 0.478-0.727，完全重叠
      （「东亚脸+黑发」太通用，帽子/发型的差异被淹没）。"""
    app = _face_app()
    if app is None:
        return None
    import cv2
    img = cv2.imread(path)
    if img is None:
        return None
    H, W = img.shape[:2]
    fs = app.get(img)
    if not fs:
        return None
    f = max(fs, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    x1, y1, x2, y2 = [float(v) for v in f.bbox]
    w, h = x2 - x1, y2 - y1
    cx = (x1 + x2) / 2
    tx1, ty1 = max(0, int(cx - w * 1.5)), min(H - 1, int(y2 + h * 0.1))
    tx2, ty2 = min(W, int(cx + w * 1.5)), min(H, int(y2 + h * 2.3))
    if ty2 <= ty1 + 8 or tx2 <= tx1 + 8:
        return None
    c = img[ty1:ty2, tx1:tx2]
    if c.size == 0:
        return None
    return Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB))


def _clip_pil(im):
    c = _clip()
    if c is None:
        return None
    model, prep, torch = c
    with torch.no_grad():
        v = model.encode_image(prep(im.convert("RGB")).unsqueeze(0))
    v = v[0].numpy()
    return v / (np.linalg.norm(v) + 1e-8)


def outfit_embedding(path):
    """躯干区域的 CLIP 嵌入 —— 判断「衣服换没换」。"""
    c = _torso_crop(path)
    return _clip_pil(c) if c is not None else None


# ────────────────────────── 属性文本探针 ──────────────────────────
_TOK = None


def text_probe(path, pos, neg):
    """CLIP 零样本二分：返回「符合 pos」的概率。
    实测服装类很准（白衬衫 0.999、灰卫衣→非白衬衫 0.000、连帽衫 0.994）；
    ⚠ 帽子这类小配饰会误报（雪地里的深色头发被读成毛线帽 0.923），
      要查小配饰建议同时看 outfit 分数，别单凭探针下结论。"""
    global _TOK
    c = _clip()
    if c is None:
        return None
    model, prep, torch = c
    if _TOK is None:
        import open_clip
        _TOK = open_clip.get_tokenizer("ViT-B-32")
    try:
        im = prep(Image.open(path).convert("RGB")).unsqueeze(0)
        tt = _TOK([pos, neg])
        with torch.no_grad():
            iv = model.encode_image(im); tv = model.encode_text(tt)
        iv = iv / iv.norm(dim=-1, keepdim=True)
        tv = tv / tv.norm(dim=-1, keepdim=True)
        return float((100 * iv @ tv.T).softmax(dim=-1)[0][0])
    except Exception:
        return None


# ────────────────────────── 统一入口 ──────────────────────────
# outfit 实测：同人同装 0.682/0.702/0.715/0.738，异装 0.485/0.502/0.568 → 取 0.62
TH = {"face": 0.28, "env": 0.55, "scene": 0.65, "outfit": 0.62, "attr": 0.60}


def build_refs(path, need):
    """从锚点图提取参考特征。env 与 scene 共用一份 CLIP 嵌入。"""
    refs = {}
    if "face" in need:
        refs["face"] = face_embedding(path)
    if "outfit" in need:
        refs["outfit"] = outfit_embedding(path)
    if "env" in need or "scene" in need:
        v = clip_embedding(path)
        if "env" in need:
            refs["env"] = v
        if "scene" in need:
            refs["scene"] = v
    return refs


def check(path, refs, need, attrs=None):
    """返回 (是否通过, 各项得分dict, 人类可读原因)。
    参考特征缺失的项自动跳过（比如锚点图里没脸）。
    attrs: [(正向描述, 反向描述), ...] 角色的固定属性，用文本探针逐条查。"""
    scores, bad = {}, []
    clip_v = None
    for kind in need:
        ref = refs.get(kind)
        if ref is None:
            continue
        if kind == "face":
            s = best_face_similarity(path, ref)
            if s is None:
                scores["face"] = None
                bad.append("未检出人脸")
                continue
        elif kind == "outfit":
            v = outfit_embedding(path)
            s = clip_similarity(v, ref)
            if s is None:
                scores["outfit"] = None
                bad.append("取不到躯干区域")
                continue
        else:
            if clip_v is None:
                clip_v = clip_embedding(path)
            s = clip_similarity(clip_v, ref)
            if s is None:
                continue
        scores[kind] = s
        if s < TH[kind]:
            bad.append("%s %.3f<%.2f" % (kind, s, TH[kind]))

    for i, ap in enumerate(attrs or []):
        pos, neg = ap[0], ap[1]
        p = text_probe(path, pos, neg)
        if p is None:
            continue
        scores["attr%d" % i] = p
        if p < TH["attr"]:
            bad.append("属性「%s」%.2f<%.2f" % (pos[:24], p, TH["attr"]))

    return (len(bad) == 0), scores, "; ".join(bad)


def fmt(scores):
    return " ".join("%s=%s" % (k, "无" if v is None else "%.3f" % v)
                    for k, v in scores.items())
