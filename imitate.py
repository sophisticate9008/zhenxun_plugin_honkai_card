from .Process import Process
from .Cards import Cards
from typing import TYPE_CHECKING, List
from .pic_make import *
if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import Bot,GroupMessageEvent
from .msg_util import *
    
import random
star_and_luck = ["垒之护","绚烂.星霞","跃增.运时","矛之突","灼灼.星熠","复加.得时","幸运一掷","时来运转","好运加护",
                 "魔阵.星数","焰力.星数","幻记.星数","盾之守","烁烁.星电","倍加.巧时","术士.魔阵","骑士.魔运","医者.魔运",
                 "战车.魔运","伤.星数","灵.星数","赐.星数","势.星数"]

light_and_night = [
    "光羽夜蝶", "收割.夜蝶", "复原.光羽", "夜影光烁", "血疗.夜蝶", "神愈.光羽", "渴血.夜蝶",
    "血噬.夜蝶", "晨昏", "裂伤.夜蝶", "清心.光羽", "神罚.光羽", "神赐.光羽", "光夜交织",
    "血镰.夜蝶", "静心.光羽", "以血换血.夜蝶", "灵愈.光羽", "回愈.光羽", "狂宴.夜蝶",
    "拂晓", "刃舞.夜蝶", "血阵.夜蝶", "血清.夜蝶", "倾泻.光羽", "倾泻.光羽", "神助.光羽"
]

song_and_light = [
   "鏖战.蓄力","乐符狂热", "音律强击","争锋.蓄力","交续之时","奇攻.贮力", "闪攻.贮力",
   "速攻.贮力","乐符积蓄","额外音符", "回梦旋律","捷速谐乐","魔文乐谱","激决.蓄力",
   "搏战.集力","破袭.集力","威势.集力","瞬袭.集力","突袭.集力","延时乐曲","音符预演",
   "肆意.小调","安神.小调","甜美.小调","四重.小调","激昂.小调"
]


role_dict = {"特丽丽": star_and_luck, "西琳": star_and_luck, "芙乐艾": light_and_night,
             "布洛洛": light_and_night, "学园长": song_and_light, "绮罗老师": song_and_light}

async def sel_card(my_dict, bot: 'Bot', event: 'GroupMessageEvent'):
    card_instance_list: List[Cards] = []
    card_pack_list: List[List[str]] = []
    sel =  random.choice(list(role_dict.keys()))
    sel_card_pack: List[str] = []
    for j in range(8):
        order = 0
        card_pack = ["_".join((i, f"{random.randint(1,3)}")) for i in random.sample(role_dict[sel], k=3)]
        card_pack_list.append(card_pack)
        for i in card_pack:
            temp = i.split("_")
            card_name = temp[0]
            card_level = int(temp[1])
            order += 1
            card_instance_list.append(Cards(None, card_name, order, card_level))
    
    pic = pic2b64(make_card_sel(card_instance_list), 25)
    await push_image(bot, event, pic)
    await bot.send(event,"选择卡牌一行选择一个 例如(01110022),不满足条件不响应",at_sender=True)
    response = await get_answer(my_dict,3, 8)
    for idx, i in enumerate(response):
        sel_card_pack.append(card_pack_list[idx][int(i)])
    
    await bot.send(event,"接下来对卡牌进行排序 例如(01234567)")
    condition = True
    result = []
    while condition:
        response = await get_answer(my_dict, 8, 8)
        for i in response:
            condition = False
            if i not in "01234567":
                condition = True
                await bot.send(event, "不满足条件请重新输入", at_sender=True)
                break

    for i in response:
        result.append(sel_card_pack[int(i)])
    await bot.send(event, "配置完毕")
    my_dict["cards"] = result
    my_dict["role_name"] = sel
    my_dict["block"] = False


def imitate(my_dict, sys_random=False):
    if not sys_random:
        p = Process(my_dict[0]["role_name"], my_dict[0]["cards"],my_dict[1]["role_name"], my_dict[1]["cards"])
        return p.fighting()
    else:
        sel =  random.choice(list(role_dict.keys()))
        p = Process(my_dict[0]["role_name"], my_dict[0]["cards"], sel, random.choices(role_dict[sel], k=8), sys_random=True)
        return p.fighting()
        
    





    