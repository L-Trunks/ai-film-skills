"""ComfyUI UI-格式工作流 → API-格式。用 /object_info 推断 widget 名字与顺序。"""
import json, sys, urllib.request

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
API = "http://127.0.0.1:8188"
SKIP = {"MarkdownNote", "Note", "PrimitiveNode", "Reroute"}
BASIC = {"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"}


def is_widget(spec):
    t = spec[0]
    if isinstance(t, list):          # 旧版 object_info：选项直接是列表
        return True
    if t in BASIC:
        return True
    # 兜底：带 options 的一律当 combo widget
    return len(spec) > 1 and isinstance(spec[1], dict) and "options" in spec[1]


def convert(ui, oi):
    links = {l[0]: (l[1], l[2]) for l in ui.get("links", [])}
    api = {}
    warn = []
    for n in ui.get("nodes", []):
        t = n.get("type")
        if t in SKIP or n.get("mode") in (2, 4):
            continue
        s = oi.get(t)
        if not s:
            warn.append("未知节点 %s (#%s)" % (t, n.get("id")))
            continue
        req = s["input"].get("required", {})
        opt = s["input"].get("optional", {})
        allin = dict(req); allin.update(opt)
        order = list(req.keys()) + list(opt.keys())

        conn = {}
        for inp in (n.get("inputs") or []):
            lk = inp.get("link")
            if lk is not None and lk in links:
                src, slot = links[lk]
                conn[inp["name"]] = [str(src), slot]

        def forced(k):
            sp = allin[k]
            return len(sp) > 1 and isinstance(sp[1], dict) and sp[1].get("forceInput")

        # widget 即使被转成输入接口，仍然占着 widgets_values 里的位置，
        # 所以先按全部 widget 槽位对齐，最后再把已连线的丢掉（链接优先）。
        # 只有 forceInput 的输入从来没有 widget 槽位。
        wnames = [k for k in order if is_widget(allin[k]) and not forced(k)]
        wvals = list(n.get("widgets_values") or [])

        if isinstance(n.get("widgets_values"), dict):
            wmap = dict(n["widgets_values"])
        else:
            wmap = {}
            i = 0
            for name in wnames:
                if i >= len(wvals):
                    break
                wmap[name] = wvals[i]; i += 1
                # seed/noise_seed 后面跟一个 control_after_generate，UI 存但 API 不要
                spec = allin[name]
                extra = len(spec) > 1 and isinstance(spec[1], dict) and spec[1].get("control_after_generate")
                if extra or name in ("seed", "noise_seed"):
                    if i < len(wvals) and isinstance(wvals[i], str) and wvals[i] in (
                            "fixed", "increment", "decrement", "randomize"):
                        i += 1

        node = {"class_type": t, "inputs": {}}
        for k, v in wmap.items():
            if k in allin and k not in conn:   # 已连线的 widget：链接优先，丢掉存盘值
                node["inputs"][k] = v
        node["inputs"].update(conn)
        title = (n.get("title") or t)
        node["_meta"] = {"title": title}
        api[str(n["id"])] = node
    return api, warn


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    oi = json.load(urllib.request.urlopen(API + "/object_info", timeout=180))
    ui = json.load(open(src, encoding="utf-8"))
    api, warn = convert(ui, oi)
    json.dump(api, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("节点 %d -> API %d" % (len(ui.get("nodes", [])), len(api)))
    for w in warn:
        print("  !", w)
