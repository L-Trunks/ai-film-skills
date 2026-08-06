# -*- coding: utf-8 -*-
"""第二批四部片。核心变化：去 AI 味。

燃系翻车总结 →
1. 不堆「史诗/IMAX/大场面/电影感/masterpiece」，这类词直接把模型推向概念图
2. 换成具体摄影参数：焦段、胶片型号、光源是什么灯
3. 允许不完美：暗角、手持轻微不稳、构图不居中
4. 题材去戏剧化 —— 火山冰川闪电是 AI 过拟合区，普通瞬间才真
5. 辉光从 0.35~0.40 降到 0.18，不再炸星芒
"""
W, H = 1280, 704
FRAMES = 49
TRANS = 0.30

HOLD = (" Locked-off camera with only the faintest handheld drift. The shot is a photograph that "
        "barely breathes. No zoom, no pan, no dramatic camera move.")

REAL = ("35mm 胶片摄影，柯达金 200 的颗粒与偏暖发色，轻微暗角，"
        "手持拍摄的轻微不稳，浅景深但不是刻意虚化，"
        "构图略微随意不居中，像随手抓拍下来的一张照片")

NEG = ("插画, 概念图, 渲染, CG, 3D, 动漫脸, cartoon, 2D, 塑料感, 过度锐化, "
       "HDR, 星芒, 光芒四射, 史诗, magazine cover, 完美对称, 摆拍感, 表情夸张, "
       "文字, 水印, 畸形, 多手多脚")

# ══════════ 片 1《夜班》 ══════════
N_GIRL = ("二十五岁东亚年轻女性，黑色中长发有些散乱，深灰色连帽卫衣，"
          "脸上有一点疲惫，没有化妆，皮肤真实，")
NIGHT = [
 ("n01", N_GIRL + "近景，她坐在深夜便利店靠窗的高脚椅上低头看手机，头顶是冷白色 LED 灯管，"
  "面前一碗吃了一半的关东煮正冒热气，窗外是被雨打湿的街道，" + REAL),
 ("n02", "中景，雨后的柏油路面，路灯和店招的霓虹在积水里拉成模糊的竖条倒影，"
  "一个人的腿和伞的下半截从画面右侧走过，" + REAL),
 ("n03", "近景，末班地铁车厢的窗户，玻璃上有水汽和乘客模糊的反光，"
  "窗外隧道的灯一盏盏掠过拉成光带，" + REAL),
 ("n04", "中景，深夜无人的天桥上一台自动贩卖机亮着，冷白的光洒在地面，桥下是车流的红色尾灯，" + REAL),
 ("n05", N_GIRL + "中景，她站在便利店门口的屋檐下等雨停，手里拎着一个塑料袋，"
  "身后是便利店的暖白灯光，面前是被路灯照亮的雨丝，" + REAL),
 ("n06", "特写，一只手推开便利店的玻璃门，门上贴着营业时间的旧贴纸，"
  "门内的暖光和门外的冷蓝夜色在玻璃上重叠，" + REAL),
 ("n07", "中景，深夜的十字路口，红绿灯在空无一人的马路上变换，"
  "斑马线被雨水泡得反光，远处只有一辆出租车的车灯，" + REAL),
 ("n08", N_GIRL + "近景侧脸，她在地铁站台上等车，头顶的日光灯把她的脸照得有点白，"
  "身后是空荡的站台和黑洞洞的隧道口，" + REAL),
 ("n09", "特写，一杯便利店的热咖啡放在窗台上，塑料盖上凝着水珠，热气往上飘，"
  "背景是虚化的夜街灯光，" + REAL),
 ("n10", "中景，老小区楼下的路灯，光晕里能看见细密的雨丝，"
  "自行车棚里停着一排落灰的自行车，" + REAL),
 ("n11", N_GIRL + "中景背影，她走在深夜的巷子里，只有远处一盏路灯，"
  "影子被拉得很长投在湿漉漉的地面上，" + REAL),
 ("n12", "特写，公交站牌被雨打湿，上面的线路号在灯光下泛着水光，"
  "站牌下的长椅空着，积着一小滩水，" + REAL),
 ("n13", "中景，深夜写字楼的外立面，只有零星几个窗还亮着，"
  "在整片黑色的玻璃幕墙上像几粒亮点，" + REAL),
 ("n14", N_GIRL + "近景，她在电梯里靠着轿厢的墙闭上眼休息了一秒，"
  "电梯顶灯是很平的白光，不锈钢墙面上有她模糊的倒影，" + REAL),
 ("n15", "特写，钥匙插进门锁转动，门牌号是掉了漆的旧金属数字，"
  "楼道的声控灯刚刚亮起来，" + REAL),
 ("n16", N_GIRL + "中景，她坐在自家窗边的地板上，没开灯，"
  "只有窗外城市的光照进来落在她身上和地板上，" + REAL),
 ("n17", "大远景，从高处看深夜的城市，成片的居民楼里零星亮着窗，"
  "远处主干道的车流拉成一条流动的光带，天边开始泛起一点点灰蓝，" + REAL),
]
NIGHT_MOVE = {
 "n01": "A tired young woman sits at a convenience store window counter looking at her phone. She keeps "
        "looking down, expression unchanged. Steam rises steadily from the bowl beside her and rain runs "
        "down the window behind." + HOLD,
 "n02": "Wet asphalt at night with neon reflections stretched across the puddles. A person's legs and the "
        "lower half of an umbrella pass through the right of frame. The reflections ripple faintly." + HOLD,
 "n03": "The window of a late-night subway car with condensation and passenger reflections. The tunnel "
        "lights outside streak past continuously in bands." + HOLD,
 "n04": "A lit vending machine on a deserted pedestrian bridge at night. Nothing moves except the red "
        "tail lights of traffic flowing below and a faint flicker in the machine's light." + HOLD,
 "n05": "A young woman waits out the rain under a convenience store awning, a plastic bag in her hand. "
        "She stays where she is. Rain falls in visible threads through the streetlight behind her." + HOLD,
 "n06": "A hand pushes open a convenience store glass door. The hand stays on the door. Warm interior "
        "light and cold blue night overlap in the glass, and a reflection shifts slightly." + HOLD,
 "n07": "An empty crossroads at night. The traffic lights change from red to green over an empty road. "
        "Rain-soaked crosswalk stripes glisten. A single taxi's headlights approach far away." + HOLD,
 "n08": "A young woman waits on an empty subway platform under flat fluorescent light. She stands still. "
        "A faint draft lifts a few strands of her hair from the dark tunnel mouth behind her." + HOLD,
 "n09": "A hot coffee cup on a window ledge, condensation on the plastic lid. Steam curls upward slowly "
        "and the blurred street lights behind it shimmer." + HOLD,
 "n10": "A streetlight in an old residential compound, fine rain visible in the halo. The rain keeps "
        "falling steadily. The parked bicycles below do not move." + HOLD,
 "n11": "A young woman walks away down a narrow alley at night, seen from behind. She keeps walking at "
        "the same pace. Her long shadow slides across the wet ground." + HOLD,
 "n12": "A rain-soaked bus stop sign glinting under a streetlight. Nothing moves. Drops slide down the "
        "sign and the puddle on the bench below trembles as drops land in it." + HOLD,
 "n13": "The facade of an office tower at night with only a few windows still lit. The building is "
        "motionless. A single light in one window flickers off." + HOLD,
 "n14": "A young woman leans against an elevator wall and closes her eyes for a moment. She stays still. "
        "The flat ceiling light hums and her reflection wavers faintly in the steel wall." + HOLD,
 "n15": "A key turns in an old door lock beside a worn metal apartment number. The hand stays on the key. "
        "The corridor's sound-activated light glows and slowly dims." + HOLD,
 "n16": "A young woman sits on the floor by her window in the dark, lit only by the city outside. "
        "She stays still. The light on her and the floor shifts very slowly." + HOLD,
 "n17": "A high view over the city late at night, scattered lit windows across apartment blocks and a "
        "river of traffic light in the distance. The traffic flows and the sky slowly lightens." + HOLD,
}

# ══════════ 片 2《手上的活》 ══════════
HAND = [
 ("h01", "特写俯拍，一双沾满湿陶泥的手在拉坯，陶轮在转，泥浆顺着手指往下淌，"
  "侧窗的自然光斜照在泥坯上，工作台上散落着工具和干泥屑，" + REAL),
 ("h02", "特写，一把刨子在木板上推过，刨花从刨口卷出来，"
  "阳光从侧面照进木工房，空气里飘着细小的木屑，" + REAL),
 ("h03", "特写，一双手在案板上揉面，面粉扬起在清晨的窗光里，案板边缘有旧的刀痕，" + REAL),
 ("h04", "中景，铁匠铺里通红的铁块夹在铁砧上，锤子刚落下，火星四溅，"
  "唯一的光源是炉火和飞起的火星，背景是昏暗的工棚，" + REAL),
 ("h05", "特写俯拍，一双手在缝纫机前引导布料，机针快速上下，线轴在转，"
  "台灯的光只照亮针脚周围一小块，" + REAL),
 ("h06", "特写，一把刻刀在木头上推出一道弧线，木屑卷起，"
  "刀刃反着窗外的光，手指稳稳压住木料，" + REAL),
 ("h07", "中景，陶艺工作室的架子上摆满了晾着的素坯，窗光斜射进来，"
  "空气里能看见细小的粉尘，" + REAL),
 ("h08", "特写，一双手把一块面团摔在案板上，面粉腾起一小团，" + REAL),
 ("h09", "特写，铁钳夹着烧红的铁件浸入水中，大团白色蒸汽轰然升起，"
  "红光在蒸汽里透出来，" + REAL),
 ("h10", "特写俯拍，一支毛笔蘸墨，笔尖在砚台边缘刮出多余的墨，"
  "宣纸铺在旁边，窗光从左侧来，" + REAL),
 ("h11", "中景，木工房的角落，各种手工具挂在墙上的钉板上，"
  "每一把都有使用过的包浆，阳光斜切过一半的墙面，" + REAL),
 ("h12", "特写，一双布满老茧和细小伤口的手摊开在深色的工作台上休息，"
  "指缝里还留着洗不掉的颜色，" + REAL),
 ("h13", "特写，釉料被浇在素坯上，多余的釉顺着坯体流下滴进盆里，" + REAL),
 ("h14", "中景，烤箱门被拉开，热气和暖黄的光一起涌出来，里面是一排烤好的面包，" + REAL),
 ("h15", "特写，一把锉刀在金属件上来回，细小的金属粉末落在台面上，"
  "台灯的光很硬，在金属面上拉出高光，" + REAL),
 ("h16", "特写俯拍，成品陶碗排成一列放在木板上，还带着窑温，"
  "釉面反着窗户的形状，" + REAL),
 ("h17", "中景，工作日结束的工坊，工具都归位了，夕阳从窗户斜射进来，"
  "空气里的浮尘在光柱里缓缓浮动，没有人，" + REAL),
]
HAND_MOVE = {
 "h01": "Clay-covered hands shape a spinning pot on a potter's wheel. The hands stay in contact with the "
        "clay, the wheel keeps turning steadily, and slip runs down the fingers." + HOLD,
 "h02": "A hand plane pushes along a board and a shaving curls out of the throat. The plane keeps moving "
        "at an even pace and fine dust drifts in the side light." + HOLD,
 "h03": "Hands knead dough on a board. The kneading continues in the same steady rhythm and flour puffs "
        "up into the morning window light." + HOLD,
 "h04": "A glowing hot iron bar on an anvil, sparks flying from a hammer strike. Sparks keep scattering "
        "and the metal's glow pulses in the dark workshop." + HOLD,
 "h05": "Hands guide fabric under a sewing machine needle. The needle keeps punching up and down at the "
        "same rate and the spool turns steadily." + HOLD,
 "h06": "A carving knife pushes a curl of wood off a block. The cut continues at an even pace and light "
        "slides along the blade." + HOLD,
 "h07": "Shelves of unfired pots in a pottery studio, side light through the window. Nothing moves except "
        "fine dust drifting slowly through the light." + HOLD,
 "h08": "Hands slap a lump of dough down onto a board and a small cloud of flour bursts up. The flour "
        "drifts and settles slowly." + HOLD,
 "h09": "Tongs lower a red-hot iron piece into water and a huge cloud of white steam erupts. The steam "
        "keeps boiling upward with red light glowing through it." + HOLD,
 "h10": "A brush is loaded with ink and drawn along the edge of an inkstone. The hand keeps the motion "
        "steady and the ink surface ripples." + HOLD,
 "h11": "Hand tools hanging on a pegboard in a workshop corner. Nothing moves. The bar of sunlight on the "
        "wall creeps very slowly and dust floats through it." + HOLD,
 "h12": "Calloused hands with small cuts rest open on a dark workbench. They stay still. Only the "
        "breathing of the fingers and a slow shift of light." + HOLD,
 "h13": "Glaze is poured over an unfired pot, the excess running down and dripping into a basin. The "
        "pouring continues and drips fall steadily." + HOLD,
 "h14": "An oven door opens and heat and warm light pour out over rows of finished bread. The door stays "
        "open and the heat shimmer rises." + HOLD,
 "h15": "A file works back and forth across a metal part, fine metal dust falling on the bench. The "
        "filing continues at an even rhythm under hard lamp light." + HOLD,
 "h16": "Finished ceramic bowls in a row on a wooden board, still warm from the kiln. Nothing moves. "
        "Reflections of the window sit still on the glaze and heat shimmers faintly above them." + HOLD,
 "h17": "An empty workshop at the end of the day, tools put away, low sun through the window. No one is "
        "there. Dust drifts slowly through the shaft of light." + HOLD,
}

# ══════════ 片 3《北方的冬天》 ══════════
W_MAN = ("二十五岁东亚年轻男性，黑色短发，厚重的深色羽绒服和灰色粗针围巾，"
         "鼻头和耳朵被冻得发红，皮肤真实，")
WINTER = [
 ("w01", "中景，清晨雪街上的早点摊，蒸笼掀开的瞬间大团白色蒸汽涌出，"
  "逆着刚升起的太阳被照得透亮，摊主的身影在蒸汽里只剩轮廓，" + REAL),
 ("w02", "特写，结满冰花的玻璃窗，一根手指刚在上面划开一道，"
  "透过缝能看见外面模糊的雪和树，" + REAL),
 # 探针里「手放嘴边呵气、白雾从手心炸开」物理不对，改成对着手哈气搓手
 ("w03", W_MAN + "近景，他在雪地里把两只手拢在嘴前哈气取暖，"
  "一小股白气从他嘴里呼出后散开，睫毛和围巾上挂着霜，冷冽的侧逆光，" + REAL),
 ("w04", "中景，一扇掉漆的红色铁门，门口雪地上有杂乱的脚印，"
  "旁边晾衣绳上挂着冻得硬邦邦的衣服，" + REAL),
 ("w05", "特写俯拍，雪地上一双旧棉鞋踩下去，雪被压出清晰的纹路，" + REAL),
 ("w06", "中景，一条覆着薄雪的小巷，两侧是低矮的砖房，屋檐下挂着一排冰凌，"
  "阳光只照亮巷子的一侧，" + REAL),
 ("w07", "特写，一只手端着一碗热汤面，热气糊住了整个画面上半部分，" + REAL),
 ("w08", W_MAN + "中景背影，他缩着脖子走在雪路上，双手插在羽绒服口袋里，"
  "身后是一串新踩出的脚印，" + REAL),
 ("w09", "特写，一棵光秃秃的树枝上积着一层雪，一只麻雀落下又飞走，"
  "雪被震落下来一小撮，" + REAL),
 ("w10", "中景，结冰的河面，几个孩子的身影在远处滑冰，冰面反着冷白的天光，" + REAL),
 ("w11", "特写，暖气片上搭着一双湿手套，正在慢慢冒出细小的水汽，"
  "窗玻璃上是厚厚的雾气，" + REAL),
 ("w12", W_MAN + "近景侧脸，他坐在有暖气的屋里，手捧着一个搪瓷缸子，"
  "窗外是白茫茫的雪，窗玻璃的雾气让光变得柔软，" + REAL),
 ("w13", "中景，路边一堆被铲到一起的脏雪，混着煤灰和落叶，"
  "旁边是一辆盖着雪的旧自行车，" + REAL),
 ("w14", "特写，一只手在结霜的车窗上写字又擦掉，只留下一片模糊的水痕，" + REAL),
 ("w15", "中景，黄昏的雪街，路灯刚刚亮起来，雪花在灯光里飘，"
  "远处小卖部的窗户透出暖黄的光，" + REAL),
 ("w16", W_MAN + "中景，他站在自家楼下抬头看正在下的雪，"
  "雪花落在他的围巾和睫毛上，路灯从侧后方照过来，" + REAL),
 ("w17", "大远景，入夜后的北方小城，成片的平房屋顶盖着雪，"
  "烟囱里冒出的白烟笔直上升，天空是深蓝色的，零星几扇窗亮着暖黄的灯，" + REAL),
]
WINTER_MOVE = {
 "w01": "Steam bursts from a steamer basket at a street breakfast stall on a snowy morning, backlit by "
        "the low sun. The steam keeps billowing and the vendor's silhouette moves within it." + HOLD,
 "w02": "A finger has just drawn a line through the frost on a window. The finger stays. The frost "
        "crystals glitter and the blurred snow outside shifts faintly." + HOLD,
 "w03": "A young man cups both hands in front of his mouth and breathes to warm them in the snow. "
        "A small stream of white breath leaves his mouth and disperses. Frost on his lashes and scarf." + HOLD,
 "w04": "A peeling red iron door with messy footprints in the snow and frozen laundry on a line. "
        "Nothing moves except the stiff clothes swaying very slightly in the cold wind." + HOLD,
 "w05": "An old cotton shoe presses into snow, leaving a clear tread pattern. The foot stays down. "
        "Loose snow crumbles slowly at the edges." + HOLD,
 "w06": "A snow-dusted alley of low brick houses with icicles under the eaves. Nothing moves. A drop of "
        "meltwater gathers and falls from one icicle." + HOLD,
 "w07": "A hand holds a bowl of hot noodle soup, steam fogging the upper half of the frame. The hand "
        "stays still and the steam keeps rolling upward." + HOLD,
 "w08": "A young man walks away down a snowy road, shoulders hunched, hands in his pockets. He keeps "
        "walking at the same pace, leaving fresh footprints behind him." + HOLD,
 "w09": "Snow on a bare branch. A sparrow lands and takes off again, shaking loose a small fall of snow "
        "that drifts down through the light." + HOLD,
 "w10": "A frozen river with distant figures skating. They keep gliding slowly. The ice reflects the "
        "flat white sky." + HOLD,
 "w11": "Wet gloves drying on a radiator, faint steam rising from them. Nothing moves except the steam "
        "and the fog creeping across the window glass behind." + HOLD,
 "w12": "A young man sits indoors holding an enamel mug, snow visible through a fogged window. He stays "
        "still. Steam rises from the mug and the fog on the glass shifts." + HOLD,
 "w13": "A heap of dirty ploughed snow mixed with coal ash and leaves beside a snow-covered old bicycle. "
        "Nothing moves. A little loose snow slides off the bicycle seat." + HOLD,
 "w14": "A hand writes on a frosted car window and wipes it away, leaving a smear. The hand stays on the "
        "glass and the smear slowly refogs." + HOLD,
 "w15": "A snowy street at dusk as the streetlights come on, snowflakes drifting through the light. "
        "The snow keeps falling and the warm shop window glows steadily." + HOLD,
 "w16": "A young man stands below his building looking up at falling snow. He holds the look. Snowflakes "
        "land on his scarf and lashes and drift past the streetlight behind him." + HOLD,
 "w17": "A northern town at nightfall, snow on the rooftops, straight columns of white chimney smoke "
        "rising into a deep blue sky. The smoke keeps rising and a window light flickers." + HOLD,
}

# ══════════ 片 4《唯美治愈 v2》 ══════════
H_GIRL = ("二十岁东亚女孩，齐下巴黑色波波头，白色棉质短袖衬衫，面容清秀干净，皮肤真实，")
H_BOY = ("二十岁东亚男孩，利落黑色短发，白色棉质短袖衬衫，眉眼清朗，皮肤真实，")
HEAL2 = [
 # 探针里两人啃冰棍表情尴尬，改成女孩递冰棍、两人都低着头，不做正脸表情
 ("s01", "近景，一个齐下巴波波头的女孩和一个短发男孩并排坐在便利店门口的台阶上，"
  "两人都穿白衬衫低着头，女孩把一根冰棍递过去，男孩伸手来接，看不清完整表情，"
  "夏天傍晚的斜阳把台阶照成暖橙色，" + REAL),
 ("s02", "中景，公交车最后一排，一个齐下巴波波头的女孩靠着窗睡着了，"
  "旁边的男孩低头看窗外，午后阳光透过车窗在他们身上移动，车厢的扶手椅背都有使用痕迹，" + REAL),
 ("s03", "中景，老居民楼的楼梯间，光从上方窗户斜射下来切出一道明亮的光柱，"
  "扶手掉了漆，墙上有旧水渍，一个女孩的背影正在往上走，" + REAL),
 ("s04", "中景，老式阳台上晾着几件白衬衫被风吹得鼓起，午后阳光穿过衣料让它们半透明，"
  "栏杆是旧铁艺，远处是居民楼的屋顶，" + REAL),
 ("s05", H_GIRL + "近景，她趴在教室的窗台上看外面，风把窗帘吹起来扫过她的手臂，"
  "阳光在课桌上投下窗框的影子，" + REAL),
 ("s06", "特写俯拍，两只手在课桌下悄悄交叠在一起，桌面边缘有涂改液画的痕迹，" + REAL),
 ("s07", "中景，雨后的操场，地上的水洼映着天空和远处的球门，"
  "一个男孩正踩着水洼边缘走过，鞋边溅起小水花，" + REAL),
 ("s08", H_BOY + "近景，他站在小卖部的冰柜前弯腰挑东西，冰柜的冷光从下面照上来，"
  "白衬衫被照得有点发蓝，" + REAL),
 ("s09", "特写，一台老式电风扇在转，扇叶后面是被吹得晃动的窗帘和午后的光，" + REAL),
 ("s10", H_GIRL + "中景，她骑着自行车在两旁是梧桐树的路上，"
  "阳光穿过树叶在她身上洒下流动的光斑，衬衫下摆被风吹起，" + REAL),
 ("s11", "特写俯拍，两双穿着白球鞋的脚并排坐在天台边缘晃着，脚下是居民楼的屋顶，" + REAL),
 ("s12", "中景，夏天傍晚的天台，两个人的背影并排坐着看远处，"
  "天边是渐变的橙紫色，晾衣绳和水塔的剪影在前景，" + REAL),
 ("s13", "特写，一瓶汽水放在水泥台上，瓶身上全是水珠，"
  "阳光从侧面照过来让玻璃瓶透出琥珀色，" + REAL),
 ("s14", H_BOY + "近景，他坐在路边的台阶上低头系鞋带，"
  "夕阳从侧后方照过来在他后颈和手臂上勾出亮边，" + REAL),
 ("s15", "中景，蝉鸣的午后，树干上停着一只蝉，阳光透过密集的叶子形成大片光斑，" + REAL),
 ("s16", H_GIRL + "近景，她在洒了水的水泥地上蹲着看蚂蚁，头发垂下来遮住半张脸，"
  "傍晚的光很低很暖，" + REAL),
 ("s17", "大远景，夏天的黄昏，两个人的身影并排走在长长的堤坝上，"
  "远处是城市的轮廓和正在落下的太阳，草在风里起伏，" + REAL),
]
HEAL2_MOVE = {
 "s01": "A girl passes an ice lolly to a boy as they sit on convenience store steps in evening sun. "
        "The exchange is slow and both keep their heads down. Their shirts stir in a warm breeze." + HOLD,
 "s02": "A girl sleeps against the window in the back row of a bus while a boy beside her looks out. "
        "Neither moves much. Afternoon light slides across them as the bus travels." + HOLD,
 "s03": "A girl climbs the stairs of an old apartment block through a shaft of window light, seen from "
        "behind. She keeps climbing at the same pace. Dust drifts through the beam." + HOLD,
 "s04": "White shirts on an old balcony line billow in the afternoon wind, sunlight glowing through the "
        "fabric. The shirts keep swaying and lifting." + HOLD,
 "s05": "A girl leans on a classroom window sill looking out. She holds the look. The curtain lifts in "
        "the breeze and brushes her arm, and the window shadow shifts on the desk." + HOLD,
 "s06": "Two hands quietly rest overlapped under a school desk. They stay still. Only the faintest "
        "movement of fingers and a slow shift of light." + HOLD,
 "s07": "A boy walks along the edge of a puddle on a playground after rain, small splashes at his shoes. "
        "He keeps walking. The reflection of the sky ripples in the water." + HOLD,
 "s08": "A boy leans over a shop freezer choosing something, cold light glowing up from below onto his "
        "white shirt. He keeps looking down and the freezer light flickers faintly." + HOLD,
 "s09": "An old electric fan turns, the curtain behind it swaying in the afternoon light. The fan keeps "
        "rotating steadily and the curtain lifts and falls." + HOLD,
 "s10": "A girl rides a bicycle down a plane-tree avenue, dappled light flowing over her. She keeps "
        "riding at an even pace, her shirt hem fluttering." + HOLD,
 "s11": "Two pairs of white sneakers dangle side by side over a rooftop edge. The feet swing slowly and "
        "evenly. The rooftops below stay still." + HOLD,
 "s12": "Two figures sit side by side on a rooftop at dusk, seen from behind, looking into the distance. "
        "They stay seated. The laundry line sways and the sky's gradient shifts slowly." + HOLD,
 "s13": "A soda bottle covered in condensation on a concrete ledge, glowing amber in side light. "
        "Nothing moves except a drop sliding slowly down the glass." + HOLD,
 "s14": "A boy sits on a kerb tying his shoelace, rim light on his neck and arms. The tying continues "
        "slowly and his hair stirs in the breeze." + HOLD,
 "s15": "A cicada clings to a tree trunk in dappled afternoon light. It stays still, wings trembling "
        "faintly, while the leaf shadows shift over the bark." + HOLD,
 "s16": "A girl crouches on wet concrete watching ants, hair hanging over half her face. She stays "
        "crouched, unmoving, and the low warm light shifts on the ground." + HOLD,
 "s17": "Two figures walk side by side along a long embankment at summer dusk. They keep walking at the "
        "same pace. The grass ripples in the wind and the sun sinks." + HOLD,
}

FILMS = {
 "night": {"name": "夜班", "shots": NIGHT, "move": NIGHT_MOVE, "order": [s[0] for s in NIGHT],
           "neg": NEG, "seed": 9200, "glow": 0.18,
           "grade": "eq=saturation=1.02:contrast=1.05",
           "bgm": r"E:\Projects\AI\popsci-studio\_视频剪辑流水线\bgm\Aitech.mp3",
           "bgm_vol": 0.34, "dir": "夜班"},
 "hand":  {"name": "手上的活", "shots": HAND, "move": HAND_MOVE, "order": [s[0] for s in HAND],
           "neg": NEG, "seed": 9300, "glow": 0.18,
           "grade": "eq=saturation=1.04:contrast=1.04",
           "bgm": r"E:\Projects\AI\reddit-video-cn\舒缓.mp3",
           "bgm_vol": 0.30, "dir": "手上的活"},
 "winter": {"name": "北方的冬天", "shots": WINTER, "move": WINTER_MOVE, "order": [s[0] for s in WINTER],
           "neg": NEG, "seed": 9400, "glow": 0.20,
           "grade": "eq=saturation=0.98:contrast=1.06",
           "bgm": r"E:\Projects\AI\reddit-video-cn\assets\audioknap-free-background-music-for-everyone-454587.mp3",
           "bgm_vol": 0.16, "dir": "北方的冬天"},
 "heal2": {"name": "唯美治愈v2", "shots": HEAL2, "move": HEAL2_MOVE, "order": [s[0] for s in HEAL2],
           "neg": NEG, "seed": 9500, "glow": 0.18,
           "grade": "eq=saturation=1.06:contrast=1.03",
           "bgm": r"E:\Projects\AI\reddit-video-cn\music\monume-calm-nature-background-music-456360.mp3",
           "bgm_vol": 0.26, "dir": "唯美治愈v2"},
}
for c in FILMS.values():
    c["have"] = []
