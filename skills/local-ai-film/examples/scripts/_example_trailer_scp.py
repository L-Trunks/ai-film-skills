# -*- coding: utf-8 -*-
"""SCP 三部曲预告片 —— 各 36 镜 + 标题卡，约 53 秒，2.39:1。

为什么 SCP 比山海经适合这套流程：
  · 核心美学就是「不展示异常本身」—— 收容间、防化服、混凝土、监控画质、
    事后现场，全是模型有海量真实照片作底的东西
  · 防化服 / 防毒面具遮脸，一致性风险几乎归零
  · 山海经缺的是异兽数据；SCP 根本不需要异兽出镜

⚠ 文字是本题材的最大陷阱：SCP 满世界都是文件、标牌、编号。
   按坑④，主体描述里绝不能出现任何文字载体 —— 一律改成
   无字的警示灯、纯色色块、几何标记、空白金属牌。
"""
W, H = 1376, 576
FRAMES = 49
TRANS = 0.0

NEG = ("插画, 概念图, 渲染, CG, 3D, 卡通, 动漫, 油画感, 塑料感, 过度锐化, HDR, "
       "明亮, 高饱和, 柔和, 温馨, magazine cover, 完美对称, 摆拍感, "
       "招牌, 标牌, 文件, 文档, 编号, 标签, 包装文字, 警示牌文字, 屏幕文字, "
       "文字, 字母, 数字, 水印, 畸形, 多头, 多腿")

BASE = ("2.39:1 宽银幕电影画面，anamorphic 变形宽荧幕镜头的横向光晕，"
        "低饱和高对比，暗部沉但保留细节，35mm 电影胶片颗粒，景深极浅")
FAST = "，动态模糊明显，画面里有强烈的运动感"


def _mk(look):
    def f(sid, txt, fast=False):
        return (sid, txt + (FAST if fast else "") + "，" + look + "，" + BASE)
    return f


# ═══════════════════ 片1《收容失效》 ═══════════════════
L1 = "地下设施内部，红色警报灯与冷白应急灯交替，混凝土与金属，空气里有烟雾和粉尘"
S1 = _mk(L1)
HAZ = "一名穿着橙色重型防化服的人员，头盔面罩反着光完全看不清脸，"

BREACH = [
 S1("b01", "极特写，一盏红色警报灯在混凝土墙上开始旋转，光扫过粗糙的墙面"),
 S1("b02", "中景，一条空无一人的地下走廊，尽头的应急灯一盏一盏地熄灭"),
 S1("b03", "特写，一扇厚重的金属防爆门上，一排指示灯从绿色跳成红色，没有任何文字"),
 S1("b04", "中景，监控画面的质感，一个空荡的收容间，中央的基座上什么都没有"),
 S1("b05", "特写，厚玻璃观察窗上出现一道裂纹，正在缓慢延伸"),
 S1("b06", HAZ + "中景，他站在走廊尽头背对镜头，手电的光束切开粉尘"),
 S1("b07", "中景，天花板的通风格栅正在被某种力量从内部顶开，螺丝一颗颗弹出"),
 S1("b08", "特写，地面上一道深深的刮痕从画面一端延伸到另一端，边缘的混凝土翻起"),
 S1("b09", "中景，一排储物柜全部被从内部撞变形，金属门板向外鼓出"),
 S1("b10", HAZ + "近景，他的面罩上映着闪烁的红光和他自己模糊的倒影"),
 S1("b11", "中景，控制室里一整面墙的显示器全部只剩雪花噪点"),
 S1("b12", "特写，一只戴着厚手套的手正按下一个红色的圆形按钮，按钮下陷"),
 S1("b13", "中景，厚重的隔离闸门正在缓慢降下，闸门下的缝隙里透出光"),
 S1("b14", "特写，地面积水里倒映着交替闪烁的红光，水面泛起同心的涟漪"),
 S1("b15", "中景，一台仪器的指针疯狂地来回摆动，最后卡在最右端不动了"),
 S1("b16", "中远景，走廊深处的黑暗里，有什么东西的轮廓一闪而过", True),
 S1("b17", HAZ + "中景，他猛地转身举起手电照向身后，光束在粉尘里成柱", True),
 S1("b18", "特写，防化服的面罩玻璃上突然爬满霜花，从中心向外结晶", True),
 S1("b19", "中景，一整排应急灯同时爆裂，玻璃碎片四溅", True),
 S1("b20", "中景，一扇金属门被从另一侧撞出一个巨大的凹陷", True),
 S1("b21", "中远景，一群防化服人员在烟雾中向后撤退，手电光乱晃", True),
 S1("b22", "特写，混凝土墙面上迅速蔓延开蛛网状的裂纹", True),
 S1("b23", "中景，通风管道整段从天花板上被扯落，砸在地上", True),
 S1("b24", "中远景，走廊尽头的黑暗正在向镜头逼近，吞掉沿途的灯光", True),
 S1("b25", "近景，一名研究员摘下眼镜，抬手擦掉额头的汗，脸上全是疲惫，画面近乎全黑只有一线光"),
 S1("b26", "极特写，一滴汗从下颌滑落，在黑暗中反着一点红光"),
 S1("b27", "极特写，警报灯的红光扫过镜头", True),
 S1("b28", "极特写，防化服面罩后一双睁大的眼睛", True),
 S1("b29", "中景，闸门在最后一刻轰然落地，扬起一片尘", True),
 S1("b30", "极特写，一只手掌拍在观察窗的玻璃上，从另一侧", True),
 S1("b31", "中景，整条走廊的灯同时熄灭，只剩一片漆黑", True),
 S1("b32", "极特写，红色指示灯最后闪了一下就灭了", True),
 S1("b33", "中景，一片死寂的走廊，闸门已经完全封死，地上散落着头盔和手电"),
 S1("b34", "特写，一顶被遗落的防化头盔躺在地上，面罩里映着走廊尽头微弱的光"),
 S1("b35", "中远景，从监控视角看这条走廊，画面上什么都没有，只有静止的黑暗"),
 S1("b36", "大远景，设施外部，一片荒野中只有几个不起眼的通风口，风吹过草地"),
]
BREACH_MV = {
 "b01": "A red alarm light begins to rotate on a concrete wall, the beam sweeping across the rough surface.",
 "b02": "An empty underground corridor; the emergency lights go out one by one down its length.",
 "b03": "Indicator lights on a heavy blast door flip from green to red one after another.",
 "b04": "CCTV-quality footage of an empty containment cell, nothing on the central plinth. Dust drifts.",
 "b05": "A crack appears in thick observation glass and slowly spreads outward.",
 "b06": "A figure in an orange hazmat suit stands at the end of a corridor, torch beam cutting the dust.",
 "b07": "A ceiling vent grille is pushed out from inside, screws popping loose one at a time.",
 "b08": "A deep gouge runs the length of the floor, concrete curled up at its edges. Dust settles.",
 "b09": "A row of lockers, every door bulged outward from the inside. The metal creaks and shifts.",
 "b10": "A hazmat visor reflects flashing red light and the wearer's own blurred reflection.",
 "b11": "A wall of control room monitors, all showing nothing but static that keeps rolling.",
 "b12": "A gloved hand presses a large round red button; the button sinks in and stays down.",
 "b13": "A heavy isolation gate descends slowly, light spilling through the closing gap.",
 "b14": "Standing water on the floor reflects the flashing red light; concentric ripples keep spreading.",
 "b15": "An instrument needle swings wildly back and forth, then jams hard against the right stop.",
 "b16": "Something's outline flickers past in the darkness at the far end of the corridor.",
 "b17": "A hazmat figure spins and raises a torch behind him, the beam a solid column in the dust.",
 "b18": "Frost crystals race across a hazmat visor from the centre outward.",
 "b19": "An entire row of emergency lights bursts at once, glass spraying.",
 "b20": "A metal door is punched into a huge dent from the far side.",
 "b21": "Hazmat figures retreat backwards through smoke, torch beams swinging wildly.",
 "b22": "Web-like cracks race across a concrete wall.",
 "b23": "A whole run of ventilation duct is torn from the ceiling and crashes down.",
 "b24": "Darkness advances up the corridor toward the camera, swallowing the lights as it comes.",
 "b25": "A researcher takes off his glasses and wipes sweat from his forehead, exhausted, in near darkness.",
 "b26": "A bead of sweat slides off a jawline, catching a point of red light in the dark.",
 "b27": "The red alarm beam sweeps directly across the lens.",
 "b28": "A pair of wide eyes behind a hazmat visor.",
 "b29": "The gate slams down the last stretch and hits the floor, throwing up dust.",
 "b30": "A palm slaps against observation glass from the far side.",
 "b31": "Every light in the corridor goes out at once, leaving total black.",
 "b32": "A red indicator flickers once and dies.",
 "b33": "A dead-silent corridor, the gate fully sealed, helmets and torches scattered on the floor.",
 "b34": "An abandoned hazmat helmet on the floor, faint corridor light reflected in its visor.",
 "b35": "A CCTV view of the corridor. Nothing happens. Only still darkness and a little grain.",
 "b36": "A wide shot of scrubland with a few unremarkable vent stacks. Wind moves the grass.",
}

# ═══════════════════ 片2《站点档案》 ═══════════════════
L2 = "机构内部的冷静日光灯照明，米灰色墙面与不锈钢，观察窗玻璃的反光，克制的低对比"
S2 = _mk(L2)
COAT = "一名穿着白色实验服的研究人员，戴着口罩只露出眼睛，"

ARCH = [
 S2("a01", "极特写，一只手正在把一枚金属钥匙插进老式的锁孔，缓慢转动"),
 S2("a02", "中景，一条极长的白色走廊，两侧是一模一样的金属门，尽头看不到头"),
 S2("a03", "中景，一间收容室的厚玻璃观察窗，室内是空的，只有一把椅子"),
 S2("a04", COAT + "中景，他站在观察窗前背对镜头，双手背在身后一动不动"),
 S2("a05", "特写，一面墙上排列着几十个一模一样的圆形指示灯，全部是稳定的绿色"),
 S2("a06", "中景，一间陈列室，玻璃柜里摆着若干个日常物件：一只茶杯、一把梳子、一双旧鞋"),
 S2("a07", "极特写，玻璃柜里的那只茶杯，杯壁上有一道细微的裂纹"),
 S2("a08", "中景，一台老式的开盘录音机正在转动，磁带缓慢地绕过磁头"),
 S2("a09", COAT + "近景，他低头在一块无字的金属板上做着什么，只看得见手部动作"),
 S2("a10", "中景，一间空的会议室，长桌两侧的椅子都被整齐地推进去了"),
 S2("a11", "特写，天花板的日光灯管发出极轻微的闪烁"),
 S2("a12", "中景，一扇金属门缓缓打开，门后是一片纯粹的黑暗，什么都看不见"),
 S2("a13", "特写，观察窗的玻璃上出现了一个手掌的印痕，从内侧"),
 S2("a14", "中景，陈列柜里的那双旧鞋，鞋尖的方向和刚才不一样了"),
 S2("a15", COAT + "中景，他停下脚步回头看向长廊深处，只露出侧脸"),
 S2("a16", "特写，一排绿色指示灯中，最右边那一个变成了黄色"),
 S2("a17", "中景，走廊的地面上有一串湿的脚印，从一扇门通向另一扇门"),
 S2("a18", "特写，录音机的磁带突然开始反向转动，转速越来越快", True),
 # 原写「椅子面向同一方向」→ 模型画了一屋子真人在开会。
 # 凡是「某物不在场但留下痕迹」的表达，模型都会把那个「某物」补出来。
 S2("a19", "中景，一间空无一人的会议室，所有椅子都被拉出来整齐地面向同一个方向，画面里没有任何人，没有人影，没有身体，只有空椅子和冷白的日光灯", True),
 S2("a20", "特写，玻璃柜的门内侧结起了一层白霜", True),
 S2("a21", "中景，一整条走廊的日光灯依次熄灭，黑暗从远端逼近", True),
 S2("a22", "特写，那排指示灯从右往左依次变红", True),
 # 原写「坐过的凹陷」→ 模型直接画了个人坐在上面。同上，必须用否定句堵死在场。
 S2("a23", "特写，一把空椅子的坐垫，布面上有一个明显的下陷痕迹，椅子上没有人，画面里没有任何人体、四肢或衣物，只有这把空椅子", True),
 S2("a24", "中景，收容室的厚玻璃从内侧被撞出蛛网状的裂纹", True),
 S2("a25", COAT + "近景，他摘下口罩深吸一口气，画面近乎全黑只有一线光落在脸上"),
 S2("a26", "极特写，他的瞳孔在黑暗中缓缓放大"),
 S2("a27", "极特写，一个指示灯变红", True),
 S2("a28", "极特写，磁带在轴上疯狂旋转", True),
 S2("a29", "中景，那扇门后的黑暗正在向外溢出", True),
 S2("a30", "极特写，玻璃裂纹瞬间爬满整面窗", True),
 S2("a31", "中景，陈列柜里的所有物件同时震动起来", True),
 S2("a32", "极特写，一只眼睛在黑暗中睁开，是人的眼睛，但瞳孔太大了", True),
 S2("a33", "中景，走廊恢复了照明，一切看起来和最初一模一样，只是那把椅子不见了"),
 S2("a34", "特写，玻璃柜里空出了一个位置，其余物件还在原处"),
 S2("a35", "中景，一名研究人员的背影正沿着长廊走远，走廊的尽头依然看不到头"),
 S2("a36", "大远景，一栋毫不起眼的灰色办公楼，周围是普通的停车场和树，日常得过分"),
]
ARCH_MV = {
 "a01": "A hand inserts a metal key into an old lock and turns it slowly.",
 "a02": "An extremely long white corridor lined with identical metal doors, no end in sight. Lights hum.",
 "a03": "Thick observation glass onto an empty containment room with a single chair. Nothing moves.",
 "a04": "A researcher stands at an observation window, hands behind his back, completely still.",
 "a05": "Dozens of identical round indicator lights on a wall, all steady green. One flickers faintly.",
 "a06": "A display room of glass cases holding ordinary objects: a teacup, a comb, a pair of old shoes.",
 "a07": "A teacup in a glass case with a fine crack in its wall. Nothing moves; light shifts on the glaze.",
 "a08": "An old reel-to-reel recorder turns, tape running slowly across the head.",
 "a09": "A researcher works on a blank metal plate, only his hands visible, moving steadily.",
 "a10": "An empty meeting room, all chairs pushed neatly under the long table. Utterly still.",
 "a11": "A ceiling fluorescent tube flickers very slightly, over and over.",
 "a12": "A metal door swings slowly open onto pure darkness. Nothing can be seen inside.",
 "a13": "A handprint appears on observation glass, pressed from the inside.",
 "a14": "The old shoes in the case are pointing a different way than before. Nothing else has moved.",
 "a15": "A researcher stops and looks back down the corridor, only his profile visible.",
 "a16": "In a row of green indicators, the rightmost turns amber.",
 "a17": "A trail of wet footprints crosses the corridor floor from one door to another.",
 "a18": "The recorder's tape suddenly reverses and spins faster and faster.",
 "a19": "An empty meeting room, every chair pulled out and facing the same way. Nobody is present. Dust drifts.",
 "a20": "White frost spreads across the inside of the display case glass.",
 "a21": "A whole corridor of lights goes out in sequence, darkness advancing from the far end.",
 "a22": "The row of indicators turns red one by one from right to left.",
 "a23": "Close on an empty chair seat with a clear depression in the fabric. Nobody is in the chair.",
 "a24": "Thick containment glass cracks into a web from the inside.",
 "a25": "A researcher pulls down his mask and takes a deep breath in near darkness, one line of light on his face.",
 "a26": "His pupil dilates slowly in the dark.",
 "a27": "An indicator light turns red.",
 "a28": "Tape spins wildly on its reel.",
 "a29": "Darkness spills outward from the open doorway.",
 "a30": "Cracks race across the entire window at once.",
 "a31": "Every object in the display cases begins to vibrate at once.",
 "a32": "An eye opens in darkness. It is a human eye, but the pupil is far too large.",
 "a33": "The corridor lights return. Everything looks exactly as before, except the chair is gone.",
 "a34": "One position in the display case is empty. The other objects are undisturbed.",
 "a35": "A researcher walks away down the endless corridor, growing smaller.",
 "a36": "A completely unremarkable grey office building with an ordinary car park and trees.",
}

# ═══════════════════ 片3《异常现场》 ═══════════════════
L3 = "野外封锁现场，强烈的日光与探照灯，黄色封锁带与灰绿色军用装备，空气里全是尘土"
S3 = _mk(L3)
FLD = "一名穿着灰绿色防化服的外勤人员，防毒面具遮住整张脸，"

FIELD = [
 S3("f01", "大远景，一片荒野的正中央，几十顶白色帐篷围成一个圆，圆心是空的"),
 S3("f02", "特写，一条黄色的封锁带在风里绷紧又松开，上面没有任何文字"),
 S3("f03", "中景，一排军用卡车停在土路上，车灯全部朝向同一个方向"),
 S3("f04", FLD + "中景，他背对镜头站在封锁线边缘，手里提着一台仪器"),
 S3("f05", "特写，仪器上的指针在缓慢地、有规律地摆动"),
 S3("f06", "大远景，荒野中央有一个完美的圆形区域，里面的草全部是枯白色的"),
 S3("f07", "中景，圆形区域的边界线，一边是绿草一边是枯草，界限锐利得不自然"),
 S3("f08", "特写，一只手戴着厚手套，捡起边界上一株半绿半枯的草"),
 S3("f09", "中远景，几名防化服人员排成一列缓慢走向圆心，间距完全一致"),
 S3("f10", "中景，一顶帐篷里排着几张空的行军床，床单整齐得像没人睡过"),
 S3("f11", "特写，一台老式收音机放在折叠桌上，指示灯亮着，但没有声音"),
 S3("f12", "大远景，探照灯从四面照向圆心，光柱在尘土里交汇"),
 S3("f13", "中景，圆心的地面上有一个浅浅的凹陷，土是新翻的"),
 S3("f14", FLD + "近景，他的防毒面具镜片上映着探照灯的光和一片空旷"),
 S3("f15", "特写，地上一串脚印走到圆心就消失了，没有折返"),
 S3("f16", "中景，天空中的云在圆形区域正上方形成了一个洞", True),
 S3("f17", "中景，所有的探照灯同时熄灭，只剩月光", True),
 S3("f18", "特写，仪器的指针疯狂旋转起来", True),
 S3("f19", "中远景，防化服人员开始向后奔跑，尘土被踢起", True),
 S3("f20", "中景，帐篷被一股力量整片掀飞，帆布在空中翻卷", True),
 S3("f21", "特写，圆形区域的枯草在瞬间全部化成灰烬", True),
 S3("f22", "中远景，一道尘柱从圆心冲天而起", True),
 S3("f23", "中景，卡车的车灯逐一炸裂", True),
 S3("f24", "大远景，整片荒野的地面在起伏，像水面一样", True),
 S3("f25", FLD + "近景，他跪在地上摘下面具，脸上全是灰，剧烈地喘着气，画面近乎全黑"),
 S3("f26", "极特写，他睁大的眼睛，瞳孔里映着远处的火光"),
 S3("f27", "极特写，探照灯的光扫过镜头", True),
 S3("f28", "极特写，指针撞到刻度尽头", True),
 S3("f29", "中景，尘柱在半空中散开", True),
 S3("f30", "极特写，一只手抓住封锁带", True),
 S3("f31", "大远景，荒野上升起一片刺目的白光", True),
 S3("f32", "极特写，白光吞没画面", True),
 S3("f33", "大远景，天亮了，荒野上什么都没有，帐篷、卡车、封锁带全都不见了"),
 S3("f34", "特写，地上只剩一小截被烧焦的黄色封锁带"),
 S3("f35", "大远景，那个圆形区域已经长满了新的绿草，比周围还要茂盛"),
 S3("f36", "大远景，一条空荡的公路穿过荒野，远处有一辆车正在开走"),
]
FIELD_MV = {
 "f01": "Dozens of white tents ringing an empty centre in open scrubland. Canvas flaps in the wind.",
 "f02": "Yellow cordon tape snaps taut and slack in the wind, continuously.",
 "f03": "A line of military trucks on a dirt road, all headlights aimed the same way. Dust drifts.",
 "f04": "A hazmat field officer stands at the cordon holding an instrument, seen from behind.",
 "f05": "An instrument needle swings slowly and rhythmically back and forth.",
 "f06": "A perfect circle of dead white grass in open scrubland. The grass sways but does not recover.",
 "f07": "The boundary of the circle: green grass on one side, dead on the other, unnaturally sharp.",
 "f08": "A gloved hand picks a stalk that is half green and half dead. The hand holds it up.",
 "f09": "Hazmat figures walk toward the centre in a line at perfectly equal spacing.",
 "f10": "Empty camp beds in a tent, sheets too neat to have been slept in. Canvas breathes in the wind.",
 "f11": "An old radio on a folding table, its indicator lit, producing no sound at all.",
 "f12": "Floodlights converge on the centre from all sides, beams crossing in the dust.",
 "f13": "A shallow depression at the centre, the soil freshly turned. Dust settles into it.",
 "f14": "A gas mask visor reflects floodlights and empty ground.",
 "f15": "A line of footprints crosses to the centre and simply stops. Nothing returns.",
 "f16": "A hole opens in the cloud directly above the circle.",
 "f17": "Every floodlight goes out at once, leaving only moonlight.",
 "f18": "The instrument needle spins wildly around its dial.",
 "f19": "Hazmat figures run backwards away from the centre, kicking up dust.",
 "f20": "A tent is lifted whole and thrown, canvas tumbling through the air.",
 "f21": "The dead grass in the circle turns to ash all at once.",
 "f22": "A column of dust erupts from the centre into the sky.",
 "f23": "Truck headlights burst one after another.",
 "f24": "The whole ground undulates like the surface of water.",
 "f25": "A field officer kneels and pulls off his mask, face covered in ash, breathing hard in near darkness.",
 "f26": "His wide eyes reflect distant firelight.",
 "f27": "A floodlight beam sweeps across the lens.",
 "f28": "The needle slams against the end stop.",
 "f29": "The dust column disperses in mid air.",
 "f30": "A hand grabs the cordon tape.",
 "f31": "Blinding white light rises from the scrubland.",
 "f32": "White light swallows the frame.",
 "f33": "Daylight. The scrubland is completely empty; tents, trucks and tape are all gone.",
 "f34": "A short length of scorched yellow tape lies on the ground. Wind stirs it.",
 "f35": "The circle is now covered in new grass, greener and thicker than the land around it.",
 "f36": "An empty road across the scrubland, one car driving away in the distance.",
}

# ── 共用剪辑骨架（36 镜：3 冷开场 / 6 建立 / 8 推进 / 8 加速 / 2 急停 / 6 爆发 / 3 收尾）──
def _edit(p):
    ids = ["%s%02d" % (p, i) for i in range(1, 37)]
    D = ([(2.6, 0, "in"), (2.6, 0, "out"), (2.4, 0, "in")] +
         [(2.2, 0, "out"), (2.2, 0, "in"), (2.4, 0, "up"),
          (2.0, 0, "in"), (2.2, 4, "in"), (2.2, 0, "out")] +
         [(1.5, 0, "in"), (1.4, 4, "IN"), (1.4, 0, "up"), (1.3, 0, "in"),
          (1.5, 6, "in"), (1.3, 0, "IN"), (1.4, 0, "out"), (1.4, 0, "in")] +
         [(0.7, 6, "IN"), (0.6, 4, "IN"), (0.65, 8, "OUT"), (0.55, 2, "IN"),
          (0.6, 6, "IN"), (0.5, 0, "up"), (0.6, 4, "OUT"), (0.7, 0, "IN")] +
         [(1.8, 12, "in"), (1.2, 8, "IN")] +
         [(0.4, 8, "IN"), (0.4, 6, "OUT"), (0.4, 2, "IN"),
          (0.35, 4, "IN"), (0.4, 0, "OUT"), (0.45, 4, "IN")] +
         [(2.8, 0, "out"), (2.6, 6, "in"), (3.0, 0, "out")])
    return dict(zip(ids, D))


def _film(name, key, shots, mv, seed, grade, curves, bgm, vol, face, outfit, attr):
    cons = {s: ["face"] for s in face}
    cons.update({s: ["outfit"] for s in outfit})
    return {"name": name, "shots": shots, "move": mv, "order": [s[0] for s in shots],
            "have": [], "neg": NEG, "seed": seed, "canvas": (1920, 804),
            "glow": 0.12, "grade": grade, "curves": curves,
            "consistency": cons,
            "attrs": {s: [attr] for s in face + outfit},
            "bgm": bgm, "bgm_vol": vol, "dir": name,
            "edit": _edit(key), "title": {"text": name, "dur": 3.0, "after": key + "33"}}


_M = r"E:\Projects\AI\popsci-studio\_视频剪辑流水线\bgm"
FILMS = {
 # 防化服/面具遮脸 → 只查 outfit；唯一露脸的是急停那镜的研究员
 "breach": _film("收容失效", "b", BREACH, {k: v + " Locked-off camera, minimal drift."
                 for k, v in BREACH_MV.items()}, 71000,
                 "eq=saturation=0.80:contrast=1.18", "0/0 0.25/0.21 0.75/0.85 1/1",
                 _M + r"\cand_volatile.mp3", 0.20,
                 ["b25"], ["b06", "b10", "b17"],
                 ("a person in an orange heavy hazmat suit", "a person in ordinary clothes")),
 "archive": _film("站点档案", "a", ARCH, {k: v + " Locked-off camera, minimal drift."
                  for k, v in ARCH_MV.items()}, 72000,
                  "eq=saturation=0.86:contrast=1.10", "0/0 0.25/0.23 0.75/0.86 1/1",
                  _M + r"\Ambiment.mp3", 0.55,
                  ["a25"], ["a04", "a09", "a15"],
                  ("a researcher in a white lab coat", "a person in ordinary clothes")),
 "field": _film("异常现场", "f", FIELD, {k: v + " Locked-off camera, minimal drift."
                for k, v in FIELD_MV.items()}, 73000,
                "eq=saturation=0.84:contrast=1.16", "0/0 0.25/0.21 0.75/0.85 1/1",
                _M + r"\cand_complex.mp3", 0.26,
                ["f25"], ["f04", "f14"],
                ("a person in a grey-green hazmat suit and gas mask", "a person in ordinary clothes")),
}
