# -*- coding: utf-8 -*-
"""《山海》v2 —— 39 镜 + 标题卡，约 56 秒，2.39:1。

相对 v1 的三处修正：
  1. 人物镜从 10/30(33%) 砍到 6/39(15%) —— 预告片不该早early交代主角，世界要占主导
  2. 尾巴从 5.4s 拉到 10.2s，并把「腕表还在走」改成「秒针停住」——
     v1 的收尾是余烬飘过，没有重量，观感戛然而止
  3. 总长 37s → 56s，第一幕和收尾都给足呼吸

异兽写法沿用 v1 验证过的三条（v1 三次失败换来的）：
  · 换成模型认识的具体物种（「兽瞳」→「巨蛇的眼」）
  · 只拍后果不画本体（「巨兽的脚」→「地面炸裂 + 上方压下的阴影」）
  · 用运动模糊糊掉形态（「九条尾巴」→「高速残影 + 毛发拖尾」）
"""
W, H = 1376, 576
FRAMES = 49
TRANS = 0.0

MAN = ("三十岁东亚男性，短黑发凌乱湿透，深色现代冲锋衣已经磨破，"
       "脸上有泥污和干涸的血痕，眼神紧绷，皮肤有真实质感，")

LOOK = ("2.39:1 宽银幕电影画面，anamorphic 变形宽荧幕镜头的横向光晕，"
        "低饱和高对比，暗部沉但保留细节，体积光穿过空气中的尘埃与水汽，"
        "35mm 电影胶片颗粒，景深极浅，构图有重量感")
FAST = "，动态模糊明显，画面里有强烈的运动感"

NEG = ("插画, 概念图, 渲染, CG, 3D, 卡通, 动漫, 油画感, 塑料感, 过度锐化, HDR, "
       "明亮, 高饱和, 柔和, 温馨, 可爱, magazine cover, 完美对称, 摆拍感, "
       "招牌, 菜单, 标签, 包装文字, 广告牌, 文字, 水印, 畸形, 多头, 多腿")


def _s(sid, txt, fast=False):
    return (sid, txt + (FAST if fast else "") + "，" + LOOK)


SHOTS = [
 # ═══ 冷开场 3 镜 ═══
 _s("s01", "极特写，雨夜的柏油路面上一部手机屏幕正在龟裂，最后一点冷光熄灭，雨滴砸在碎玻璃上"),
 _s("s02", "大远景，城市天际线上方厚重的积雨云里，某个巨大的东西正在缓慢移动，只见轮廓不见全貌"),
 _s("s03", "中景，暴雨中的柏油路面开始泛起不正常的涟漪，路面下有光在渗出来"),
 # ═══ 第一幕 建立世界 7 镜（只 1 镜有人）═══
 # 原版 AI 味重的四个原因：完美居中对称构图、正面直视镜头、
 # 血迹像化妆师点的斑、湿头发做成了刺猬状定型。
 # 修法：偏侧构图 + 不看镜头 + 头发贴额头 + 用「纪录片抓拍」压掉海报感。
 ("s04", "三十岁东亚男性，湿透的黑色头发一缕缕贴在额头和眼睛上，"
   "深色现代冲锋衣磨破且吸满水后沉重下垂，脸上是被水冲开的泥浆和一道蹭开的血污，"
   "皮肤因为长时间浸水而发白起皱，"
   "中景，他侧身趴在浅水的石滩上，重心在画面偏左，一只手撑地另一只手还垂在水里，"
   "低着头看着地面剧烈咳嗽，完全没有看镜头，"
   "机位很低几乎贴着水面，构图偏斜不居中，"
   "纪录片式的抓拍，35mm 胶片，自然的阴天漫射光没有任何戏剧打光，"
   "轻微暗角，浅景深，像跟拍纪录片里抢到的一格，"
   "2.39:1 宽银幕，低饱和，暗部沉但保留细节，胶片颗粒"),
 _s("s05", "大远景，一个渺小的人影站在山谷底部，四周是高得不合常理的巨树，树干比楼还粗，晨雾沉在林间"),
 _s("s06", "中景，陡峭的山壁上刻满古老的兽形图腾，刻痕很深，苔藓从纹路里长出来"),
 # 原写「肋骨状骨架横跨山谷，像一座天然的桥」→ 出成了真实的木石栈桥。
 # 模型只会照字面画最常见的那个东西，隐喻不成立。去掉「桥」，直接说骨骼。
 _s("s07", "大远景，山谷底部散落着一具巨大动物的白色骨骼，一根根肋骨从土里斜插出来，比树还高，表面风化发白，藤蔓缠在骨缝之间，完全没有任何人造建筑"),
 _s("s08", "中景，一枚巨大的羽毛静静插在地上，比人还高，羽轴上有暗金色的纹路"),
 # 原写「巨大的脊背轮廓」→ 出成了普通山峰。必须写明鳞片和骨刺，否则模型当山画。
 _s("s09", "大远景，翻涌的云海之上露出一段弧形的背脊，表面覆盖着一片片巨大的深色鳞片，脊线上有一排骨质的棘刺，绝不是山峰也不是岩石，是某个活物的身体"),
 # 原写「只有光点看不见身体」→ 模型仍补出了一排穿兜帽的人形。
 # 有眼睛就得有脸是模型的强先验，只能靠「纯黑」「悬浮」把身体的位置占掉。
 _s("s10", "中景，一片纯粹的黑暗中悬浮着七八对成对的暗黄色光点，光点之间是彻底的漆黑，没有任何面部、头部、身体或轮廓，只有浮在虚空里的光点和薄雾"),
 # ═══ 第二幕 推进 9 镜（只 2 镜有人）═══
 _s("s11", "中景，浓雾笼罩的密林间，一道白色的身影正高速掠过树后，速度快到只剩一片拖曳的残影，"
   "身后是一团散开的蓬松白色毛发拖尾，看不清具体形状", True),
 _s("s12", "极特写，一只巨大的鸟爪踩在石头上，爪甲有金属般的暗光，石面被压出裂纹"),
 _s("s13", MAN + "近景，他贴在岩缝后屏住呼吸，只露出半张脸，眼睛看向侧方"),
 _s("s14", "大远景，一只巨大的黑色三足鸟正掠过太阳，羽毛边缘燃着金色的火，整片天空被灼成赤金"),
 _s("s15", "特写，一只手死死攥住一把捡来的青铜短刃，指节发白，刃上有斑驳的铜绿"),
 _s("s16", "中景，从水面之上俯拍，一个巨大的黑色阴影正在水下缓慢游过，水面泛起长长的波纹"),
 _s("s17", "中景，泥地上一个巨大的三趾爪印，深得能积满雨水，人的脚印在旁边显得极小"),
 _s("s18", "中景，一张巨大的半透明蜕皮挂在树枝上，风一吹整片颤动，鳞片的纹路清晰"),
 _s("s19", MAN + "中景，他举着一支简陋的火把走进一个巨大的洞窟，光只照亮很小一圈"),
 # ═══ 第三幕 加速 9 镜（只 1 镜有人，且是背影）═══
 _s("s20", "极特写，黑暗中一只巨大的蛇眼骤然睁开，金红色虹膜上布满细密鳞片纹理，"
   "细长的黑色竖瞳在急剧收缩，眼周覆盖粗糙的深色鳞甲，绝不是人的眼睛", True),
 _s("s21", MAN + "中远景，他在密林中狂奔的背影，枝叶从画面两侧疾速掠过", True),
 _s("s22", "中景，一条巨蛇从水中暴起，九个头同时张开，水花冲天而起", True),
 _s("s23", "中远景，山谷里巨大的立石阵同时亮起，刻纹里迸出刺目的光", True),
 _s("s24", "中景，地面在剧烈撞击中炸裂开来，大块碎石与尘土被震得高高弹起，"
   "一个巨大的黑色阴影正从画面上方压下来遮住光线", True),
 _s("s25", "中远景，漫天的黑色鸟群从林中同时冲天而起，遮蔽了天空", True),
 _s("s26", "中景，湖水正在被某种力量整片抬起，水墙立在半空", True),
 _s("s27", "极特写，青铜刃面反射出跳动的火光", True),
 _s("s28", "大远景，整座山的轮廓在震动中崩落，尘烟顺着山脊翻滚而下", True),
 # ═══ 急停 2 镜（1 镜有人）═══
 _s("s29", MAN + "近景，画面近乎全黑，只有一线光落在他的侧脸上，他在剧烈地喘息"),
 _s("s30", "极特写，一滴汗从下颌滑落，在黑暗里反着一点光"),
 # ═══ 爆发 7 镜（0 镜有人）═══
 _s("s31", "极特写，一只兽瞳占满画面，瞳孔正在急剧收缩", True),
 _s("s32", "中景，一道巨浪正拍向镜头，水墙遮天", True),
 _s("s33", "中景，烈焰从画面下方吞没上来", True),
 _s("s34", "极特写，巨大的鳞片在移动中相互摩擦", True),
 _s("s35", "中景，成片的巨树在某种力量下同时折断", True),
 _s("s36", "大远景，天空从正中裂开一道发光的缝隙", True),
 _s("s37", "极特写，一只巨大的手掌状轮廓在雾中张开，只见剪影", True),
 # ═══ 收尾 4 镜（1 镜有人，背影）═══
 _s("s38", "大远景，一个人影站在山巅背对镜头，面前是一个不可名状的巨大黑色轮廓，只见剪影，雾在两者之间流动"),
 _s("s39", "大远景，那个巨大的黑色轮廓正在雾中缓缓转过头来，只能看到头部的侧影和一点微光"),
 _s("s40", "极特写，一枚现代机械腕表躺在古老的石头上，表蒙碎裂，秒针刚好停住不动"),
 _s("s41", "大远景，山谷里的雾正在缓缓散开，露出更深处层层叠叠的、不属于人间的山峦"),
]

MOVE = {
 "s01": "A cracking phone screen on wet asphalt at night. The cracks spread and the last cold light dies.",
 "s02": "Something enormous shifts slowly inside heavy storm clouds above a city skyline.",
 "s03": "Rain-soaked asphalt ripples unnaturally; light bleeds up through the surface.",
 "s04": "A soaked man lies half in shallow water on a stony bank, head down, coughing hard, not looking at the camera. He keeps coughing; water runs off his hair and jacket. Handheld documentary framing, low to the water.",
 "s05": "A tiny figure at the bottom of a valley of impossibly huge trees. Mist drifts between the trunks.",
 "s06": "Deep carved beast totems on a cliff face. Moss stirs; light creeps across the grooves.",
 "s07": "Enormous weathered ribs jut from the valley floor, taller than trees, vines swaying between them.",
 "s08": "A giant feather stands upright in the ground, taller than a man, its vane rippling in the wind.",
 "s09": "A scaled, spined back breaks the surface of a churning cloud sea, rising and sinking slowly.",
 "s10": "Pairs of dim amber points hover in total blackness, blinking slowly. Nothing else is visible.",
 "s11": "A white shape streaks behind misted trees so fast it is only a smear of motion blur, pale fur trailing.",
 "s12": "A giant bird's talon presses down on stone; cracks spread under the claw.",
 "s13": "A man presses against a rock crevice holding his breath, half his face showing, eyes flicking sideways.",
 "s14": "A huge black three-legged bird crosses the sun, feather edges burning gold, the sky scorched.",
 "s15": "A hand grips a bronze blade, knuckles white. The grip tightens further.",
 "s16": "A vast dark shape glides slowly beneath the water, sending a long wake across the frame.",
 "s17": "A huge three-toed print in mud, filled with rainwater. Raindrops keep landing in it.",
 "s18": "A giant translucent shed skin hangs from a branch, the whole sheet trembling in the wind.",
 "s19": "A man carries a crude torch into a vast cave, the light reaching only a small circle around him.",
 "s20": "A huge serpent eye snaps open in darkness, scaled gold-red iris, thin black vertical pupil contracting.",
 "s21": "A man sprints away through dense forest, branches whipping past the lens at speed.",
 "s22": "A nine-headed serpent erupts from water, all heads opening at once, water exploding upward.",
 "s23": "A ring of standing stones ignites at once, blinding light bursting from the carvings.",
 "s24": "The ground bursts apart under a massive impact, rocks flung upward as a vast shadow drops from above.",
 "s25": "A vast flock of black birds erupts from the forest, filling the sky.",
 "s26": "An entire lake surface lifts into the air, a wall of water standing suspended.",
 "s27": "Firelight leaps across the surface of a bronze blade.",
 "s28": "An entire mountain ridge collapses, dust rolling down the slope.",
 "s29": "A man in near total darkness, one thin line of light on his cheek, breathing hard, shoulders heaving.",
 "s30": "A drop of sweat slides off a jawline, catching a single point of light in the dark.",
 "s31": "An animal pupil fills the frame, contracting sharply.",
 "s32": "A towering wave slams toward the camera.",
 "s33": "Flames surge up and swallow the frame from below.",
 "s34": "Enormous scales grind against each other as something vast moves.",
 "s35": "A stand of giant trees snaps all at once under some force.",
 "s36": "A glowing rift tears open across the sky.",
 "s37": "A colossal hand-like silhouette opens in the fog, only the outline visible.",
 "s38": "A figure on a summit faces a colossal unnameable silhouette. Neither moves; mist flows between them.",
 "s39": "The colossal dark silhouette slowly turns its head in the mist, a faint gleam along the profile.",
 "s40": "A cracked mechanical wristwatch on ancient stone, the second hand frozen, not moving at all.",
 "s41": "Valley mist parts slowly to reveal layer after layer of impossible mountains beyond.",
}

# (成片时长, trim起点, 运镜)
EDIT = {
 "s01": (2.6, 0, "in"),   "s02": (2.6, 0, "out"),  "s03": (2.4, 0, "in"),
 "s04": (2.4, 4, "in"),   "s05": (2.6, 0, "out"),  "s06": (2.2, 0, "up"),
 "s07": (2.6, 0, "out"),  "s08": (2.2, 0, "in"),   "s09": (2.4, 0, "out"),
 "s10": (2.2, 0, "in"),
 "s11": (1.5, 6, "side"), "s12": (1.3, 4, "IN"),   "s13": (1.4, 8, "in"),
 "s14": (1.6, 0, "out"),  "s15": (1.2, 10, "IN"),  "s16": (1.4, 0, "in"),
 "s17": (1.3, 0, "up"),   "s18": (1.4, 0, "in"),   "s19": (1.6, 4, "in"),
 "s20": (0.7, 6, "IN"),   "s21": (0.6, 4, "IN"),   "s22": (0.65, 8, "OUT"),
 "s23": (0.55, 2, "IN"),  "s24": (0.55, 6, "IN"),  "s25": (0.5, 0, "up"),
 "s26": (0.6, 4, "OUT"),  "s27": (0.5, 4, "IN"),   "s28": (0.7, 0, "OUT"),
 "s29": (1.8, 12, "in"),  "s30": (1.2, 8, "IN"),
 "s31": (0.4, 8, "IN"),   "s32": (0.4, 6, "OUT"),  "s33": (0.4, 2, "IN"),
 "s34": (0.35, 4, "IN"),  "s35": (0.4, 0, "OUT"),  "s36": (0.45, 0, "OUT"),
 "s37": (0.5, 4, "IN"),
 "s38": (2.8, 0, "out"),  "s39": (2.6, 0, "in"),
 "s40": (2.4, 6, "in"),   "s41": (3.0, 0, "out"),
}

TITLE = {"text": "山  海", "dur": 3.0, "after": "s37"}

# 一致性：人物镜只剩 6 个
FACE_OUTFIT = ["s04", "s13", "s19", "s29"]
OUTFIT_ONLY = ["s21", "s38"]        # 奔跑背影 / 山巅背影
CONS = {s: ["face", "outfit"] for s in FACE_OUTFIT}
CONS.update({s: ["outfit"] for s in OUTFIT_ONLY})
ATTRS = {s: [("a man in a torn dark modern outdoor jacket",
              "a man in ancient robes or armour")] for s in FACE_OUTFIT + OUTFIT_ONLY}

FILMS = {
 "shanhai2": {
   "name": "山海",
   "shots": SHOTS,
   "move": MOVE,
   "order": [s[0] for s in SHOTS],
   "have": [],
   "neg": NEG,
   "seed": 61000,
   "canvas": (1920, 804),
   "glow": 0.12,
   # v1 的调色叠了两层压暗（eq + curves），整片黑到看不清内容。
   # 这版把对比降到 1.18、亮度不再减，curves 只做温和的 S 型。
   "grade": "eq=saturation=0.86:contrast=1.16",
   "curves": "0/0 0.25/0.21 0.75/0.84 1/1",
   "consistency": CONS,
   "attrs": ATTRS,
   "bgm": r"E:\Projects\AI\popsci-studio\_视频剪辑流水线\bgm\cand_volatile.mp3",
   "bgm_vol": 0.20,
   "dir": "山海",
   "edit": EDIT,
   "title": TITLE,
 },
}
