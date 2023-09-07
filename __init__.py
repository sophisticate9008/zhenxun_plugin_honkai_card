import asyncio
import random
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import (
    GROUP,
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    )

from utils.http_utils import AsyncHttpx
from utils.message_builder import custom_forward_msg
from nonebot_plugin_apscheduler import scheduler
from utils.data_utils import init_rank, _init_rank_graph
from utils.utils import scheduler
from nonebot import on_command,on_message
from nonebot.adapters.onebot.v11.exception import ActionFailed
from utils.utils import get_message_text
from utils.message_builder import image
from .json_util import *
from models.bag_user import BagUser
from .imitate import imitate, sel_card
get_url = 'https://honkai-card-honkai-card-rhbdvhegec.cn-hangzhou.fcapp.run/get_data'
post_url = 'https://honkai-card-honkai-card-rhbdvhegec.cn-hangzhou.fcapp.run/send_data'
group_hook = {}
wait_time = 360
__zx_plugin_name__ = "模拟模拟宇宙"
__plugin_usage__ = f"""
usage:
    卡bug 发送 崩三卡牌强制刷新
    发送模拟 崩三卡牌 挑选完进入等待时间{wait_time}s(60s配置时间在内),时间到无第二个人将进入人机对战, 一个群同时只有一场对战,角色随机发放,绑定对应体系卡组
    人人对战输赢伤害皆录入排行,发送崩三卡牌排行榜,可查看前10排名,一周刷新一次,按照排行每天晚上进行奖励发放,
    发送崩三卡牌排行榜云端 可查看前50名总体排行 ，伤害数据每晚上传云数据库，只传前10名，
""".strip()
__plugin_des__ = "崩三卡牌"
__plugin_cmd__ = ["崩三卡牌", "崩三卡牌排行榜", "崩三卡牌强制刷新"]
__plugin_type__ = ("群内小游戏",)
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": __plugin_cmd__,
}

honkai_card = on_command("崩三卡牌", permission=GROUP,priority=5, block=True)

def get_status(event:GroupMessageEvent):
    global group_hook
    group = str(event.group_id)
    if group_hook.get(group) and (group_hook[group][0]["uid"] == str(event.user_id) or 
                                  (group_hook[group].get(1) and group_hook[group][1]["uid"] == str(event.user_id))
                                  ):
        
        return True
    else:
        return False
input_arg = on_message(permission=GROUP,priority=996,rule=get_status)

@input_arg.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global group_hook
    group = str(event.group_id)
    
    text = get_message_text(event.json())
    text.strip()
    if group_hook[group][0]["uid"] == str(event.user_id):    
        id = group_hook[group][0]["answer_id"]       
        group_hook[group][0]["answer"][id] = text
    else:
        id = group_hook[group][1]["answer_id"]       
        group_hook[group][1]["answer"][id] = text        
    await input_arg.finish()
 
async def jishiqi(group):
    global group_hook
    group_hook[group]["sys_random"] = False
    cd = wait_time
    while cd > 0:
        cd -= 1
        await asyncio.sleep(1)
    group_hook[group]["sys_random"] = True 


@honkai_card.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global group_hook
    text = get_message_text(event.json())
    text.strip()
    data = read_json_file(record_dir)
    group = str(event.group_id)
    if "排行榜" in text:
        if "云端" in text:
            cloud_data = []
            for i in range(3):
                try:
                    cloud_data =  await AsyncHttpx.get(get_url + "?n=50",timeout = 15).json()
                    print(cloud_data)
                    break
                except:
                    await asyncio.sleep(5)
            if len(cloud_data) == 0:
                await honkai_card.finish("暂时无法获取云端排行")
            else:
                _uname_lst = [i["user_name"] for i in cloud_data]
                _num_lst = [i["harm"] for i in cloud_data]
            rank_image = await asyncio.get_event_loop().run_in_executor(None, _init_rank_graph, "崩三卡牌总伤害云端排行榜", _uname_lst, _num_lst)
        else:
            rank_image = await init_rank("崩三卡牌总伤害排行榜", [int(item) for item in list(data[group]["rank"].keys())], list(data[group]["rank"].values()),group, 10)
        if rank_image:
            await honkai_card.finish(image(b64=rank_image.pic2bs4()))
    elif "强制刷新" in text:
        group_hook[group] = {}
    else:
        if group_hook.get(group):
            if group_hook[group][0]["block"]:
                await honkai_card.finish("请先等第一位玩家配置完毕")
            elif group_hook[group][0]["uid"] == str(event.user_id):
                await honkai_card.finish("你已经参与了",at_sender = True)
            else:
                group_hook[group][1] = {}
                group_hook[group][1]["uid"] = str(event.user_id)
                group_hook[group][1]["answer_id"] = 0
                group_hook[group][1]["answer"] = {}
                group_hook[group][1]["block"] = True
                await sel_card(group_hook[group][1],bot,event)
        else:
            group_hook[group] = {}
            group_hook[group]["sys_random"] = False
            group_hook[group][0] = {}
            group_hook[group][0]["uid"] = str(event.user_id)
            group_hook[group][0]["answer_id"] = 0
            group_hook[group][0]["answer"] = {}
            group_hook[group][0]["block"] = True
        try:
            task1 = asyncio.create_task(jishiqi(group))
            task2 = asyncio.create_task(sel_card(group_hook[group][0], bot, event))
            task3 = asyncio.create_task(fighting(bot, event))
            
            await asyncio.gather(task1, task2, task3)
        except Exception as e:
            print(f"An error occurred: {e}")
            task1.cancel()
            task2.cancel()
            task3.cancel()
            await honkai_card.send("未及时配置，取消操作")
            group_hook[group] = {}
            

async def fighting(bot:Bot, event:GroupMessageEvent):
    global group_hook
    group = str(event.group_id)
    while group_hook.get(group):
        if group_hook[group].get(1) and not group_hook[group][1]["block"]:
            await bot.send(event, "双方就绪,开始战斗")
            try:
                result = imitate(group_hook[group])
            except Exception as e:
                await bot.send(event, f"模拟过程出错,{e}")
            await bot.send(event, f"{result['winner']}\n{result['0'].role_name}\n{result['1'].role_name}\n总伤害:{result['0'].sum_harm}\n总伤害:{result['1'].sum_harm}")
            record_harm(group, group_hook[group][0]["uid"], result["0"].sum_harm)
            record_harm(group, group_hook[group][1]["uid"], result["1"].sum_harm)
            msg_list = [image(pic) for pic in result["pics"]]
            group_hook[group] = {}
            await bot.send_group_forward_msg(
                group_id=event.group_id, messages=custom_forward_msg(msg_list, bot.self_id)
            ) 
            

        elif group_hook[group]["sys_random"]:
            await bot.send(event,"无人应战,将开始人机对战")
            try:
                result = imitate(group_hook[group],sys_random=True)
            except Exception as e:
                await bot.send(event, f"模拟过程出错,{e}")
            await bot.send(event, f"{result['winner']}\n{result['0'].role_name}\n{result['1'].role_name}\n总伤害:{result['0'].sum_harm}\n总伤害:{result['1'].sum_harm}")
            record_harm(group, group_hook[group][0]["uid"], result["0"].sum_harm)
            msg_list = [image(pic) for pic in result["pics"]]
            group_hook[group] = {}
            await bot.send_group_forward_msg(
                group_id=event.group_id, messages=custom_forward_msg(msg_list, bot.self_id)
            ) 
            

        await asyncio.sleep(1)
                  
        
async def get_nickname(user_id: int, group_id: int = None):
    bot = get_bot()
    
    if group_id is None:
        # 获取陌生人信息
        stranger_info = await bot.get_stranger_info(user_id=user_id)
        nickname = stranger_info['nickname']
    else:
        # 获取群组成员信息
        member_info = await bot.get_group_member_info(user_id=user_id, group_id=group_id)
        nickname = member_info['card'] if member_info['card'] else member_info['nickname']
    
    return nickname





@scheduler.scheduled_job("cron", day_of_week='mon', hour=6)
async def _():
    data = read_json_file(record_dir)
    for i in data:
        data[i] = {}
    write_json_file(record_dir)
@scheduler.scheduled_job(
    "cron",
    hour=22,
    minute=1,
)
async def _():
    data = read_json_file(record_dir)
    data_send = []
    for i in data:
        gold_add = 150
        for j in data[i]["rank"]:
            group = int(i)
            id = int(j)
            await BagUser.add_gold(id, group, gold_add)
            gold_add -= 10
            try:
                nickname = await get_nickname(int(j), int(i))
                data_send.append({"user_name": nickname, 'group_id': i, 'uid': j, "harm": data[i]["rank"][j]})
            except:
                pass
    time_delay = random.randint(0, 3500)
    count = 0
    while count < time_delay:
        count += 1
        await asyncio.sleep(1)
        
    try_count = 0
    while try_count < 6:
        try:
            if len(data_send) > 0:
                await AsyncHttpx.post(post_url, data=data_send)
                
            break
        except:
            try_count += 1
            await asyncio.sleep(10)
    
        

            
