from collections import defaultdict
import time

from typing import Tuple, Dict, Optional, Union, Callable,NewType, TYPE_CHECKING, List
import random

from .pic_make import make_card
if TYPE_CHECKING:
    from .Process import Process
    from PIL import Image
from .Cards import Cards
import math
exclude_types = (dict, list, tuple)

beilv = 30
Card_Pack = NewType("Card_Pack", List[str])
class Roles:
    life_max = 100000
    life_now = 100000
    life_recover = 0
    shield = 0
    power = 0
    coin = 0
    bleed = 0
    heal = 0
    note = 0
    mana = 10
    rampart = 0
    weak = 0
    easy_hurt = 0
    coin_judge_min = 1
    attack = 0
    effect_count_even = 1
    effect_count_next = 1
    coin_throw_beilv = 1
    card_odd = 0
    card_even = 0
    card_accumulate = 0
    card_use_count = 0
    coin_get_beilv = 1
    coin_get_count = 0
    attack_count = 0
    card_use_index = 0
    no_limit = False
    all_fast_card = False
    fast_card_limit = 0
    harm_to_life = 0
    turn_count = 0
    harm = 0
    bleed_harm = 0
    harm_to_life_next = False
    bleed_to_life = 0
    heal_beilv = 1
    bleed_harm_to_life = 0
    push_bleed = 0
    recover_count = 0
    life_change = 0
    again = False
    logs = ""
    states = ""
    log_harm = ""
    log_recover = ""
    role_describe = ""
    return_note = False
    sum_harm = 0
    def __init__(self, role_name: str, card_pack: Card_Pack, process: "Process"):
        self.accumulate_list: List[str] = []
        self.card_pack_instance: List[Cards] = []
        self.attr_backup: Dict[str, int] = {}
        self.attr_now: Dict[str, int] = {}
        self.track_list: List[str] = []
        self.only_list: List[str] = []
        self.accumulate = []
        self.role_name = role_name
        self.process = process
        self.card_pack_instance_backup: List[Cards] = []
        self.card_pic_pool: List['Image.Image'] = []
        self.name_args: Dict[str, str] = {"shield":"护盾", "power": "力量", "mana": "法力", "coin":"幸运币", 
                                          "heal":"自愈", "bleed": "流血", "weak": "虚弱", "easy_hurt": "易伤",
                                          "note": "乐符"}
        #角色加载入process并分配index

        process.role_list.append(self)
        if len(process.role_list) == 1:
            self.role_index = 0
        else:
            self.role_index = 1

        #卡组
        order = 0
        for i in card_pack:
            temp = i.split("_")
            card_name = temp[0]
            card_level = int(temp[1])
            self.card_pack_instance.append(Cards(self, card_name, order, card_level))
            self.card_pack_instance_backup.append(Cards(self, card_name, order, card_level))
            order += 1
        self.get_attr_now()
        self.get_attr_backup()
        self.make_card_pool()            

       
    def record_state(self):
        pass
    
    def throw_coin(self, num: int):
        num = num if self.coin >= num else self.coin
        self.coin -= num
        attack = 0
        for i in range(int (num * self.coin_throw_beilv)):
            attack += random.randint(self.coin_judge_min, 6)
        return attack
    
    def get_attr_backup(self):
        backup = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
            and not isinstance(getattr(self, attr), exclude_types)
            and not hasattr(getattr(self, attr), "__module__")
        }
        self.attr_backup = backup

        
    def get_attr_now(self):
        attr_now = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
            and not isinstance(getattr(self, attr), exclude_types)
            and not hasattr(getattr(self, attr), "__module__")
        }
        self.attr_now = attr_now

    
    def merge_track(self):
        if self.turn_count == 9:
            self.track_list = merge_strings(self.track_list)
                

    def track_go(self):
        self.get_attr_now()
        for i in self.attr_now:
            if i in self.name_args:
                num = self.attr_now[i] - self.attr_backup[i]
                if abs(num) > 0:
                    opstr = " + " if num > 0 else " "
                    self.logs += (self.name_args[i] + opstr + str(int(num))) + "\n"       
        for j in range(len(self.track_list)):            
            change_list: List[str] = []
            for i in self.track_list:
                temp = i.replace(" ", "").split("<") if "<" in i else i.replace(" ", "").split(">")
                num = self.attr_now[temp[0]] - self.attr_backup[temp[0]]
                if (num < 0 and "<" in i) or (num > 0 and ">" in i):
                    var = getattr(self, temp[1])
                    var_change = abs(num * float(temp[2])) if "coin" != temp[1] else abs(num * int(float(temp[2]))) * self.coin_get_beilv
                    var += var_change
                    setattr(self, temp[1], var)
                    if temp[1] in self.name_args:
                        if int(var_change) > 0:
                            self.logs += self.name_args[temp[1]] + " + " +  str(int(var_change)) + "\n"
                    change_list.append(temp[0])   
            if len(change_list) == 0:
                break
            for i in change_list:
                self.attr_backup[i] = self.attr_now[i]
            self.get_attr_now()
        self.get_attr_backup()
        
        for i in self.attr_now:
            if i in self.name_args:
                num = self.attr_now[i] - self.attr_backup[i]
                if num > 0:
                    opstr = " + " if num > 0 else " - "
                    self.logs += (self.name_args[i] + opstr + str(int(num)))  


    def log_handle(self):
        for i in self.name_args:
            self.logs = self.logs.replace(i, self.name_args[i])
    
    def get_states(self):
        for i in self.attr_now:
            if i in list(self.name_args.keys()):
                if int(self.attr_now[i]) > 0:
                    self.states += self.name_args[i] + " : " + str(int(self.attr_now[i])) + " "
                
    
    def turn_begin(self):
        
        self.merge_track()
        if not self.rampart and self.turn_count != 1:
            self.shield = int(self.shield / 2)
            self.rampart -= 1 if self.rampart > 0 else 0
        self.accumulate_accelerate()
        self.cal_harm()
        self.cal_life()
        self.track_go() #回合
        self.life_recover += self.bleed * self.bleed_to_life
        self.life_recover += self.heal
        self.track_go()
        self.cal_life() #流血伤害结算 ，血量回复结算
        self.track_go()
        self.use_card() #使用卡片
        self.track_go() 
        self.cal_harm() #计算伤害
        self.track_go() 
        self.cal_life() #结算
        self.track_go() #追踪


    def turn_end(self):
        
        enemy = self.process.role_list[(self.role_index + 1) % 2]
        enemy.bleed += self.push_bleed
        self.push_bleed = 0 #
          #魔阵的对敌方流血生效

        
        self.weak -= 1 if self.weak > 0 else 0
        self.easy_hurt -= 1 if self.easy_hurt > 0 else 0
        

        

    
    def cal_bleed_harm(self,num=0):
        enemy = self.process.role_list[(self.role_index + 1) % 2]
        if num == 0:
            self.bleed_harm += enemy.bleed * 30
            self.life_recover += int(self.bleed_harm * self.bleed_harm_to_life / 100 / 30)
        else:
            self.bleed_harm += num
            self.life_recover += int(num * self.bleed_harm_to_life / 100 / 30)
        self.sum_harm += self.bleed_harm
    
    def cal_harm(self):
        if self.attack_count or self.attack != 0:
            enemy = self.process.role_list[(self.role_index + 1) % 2]
            self.harm += self.attack * 30
            self.harm += self.attack_count * (int(self.power) + self.note) * 30
            backup = self.note
            if self.attack_count > 0:
                self.note = 0
                self.track_go()
                if self.return_note:
                    self.return_note = False
                    self.note = backup
                    self.track_go()            
            self.attack = 0
            self.attack_count = 0
            if self.weak:
                self.harm *= 0.6
            if enemy.easy_hurt:
                self.harm *= 1.5
        
        self.sum_harm += self.harm

                

        
    def cal_life(self):
        
        
        if self.life_recover > 0:
            self.recover_count += 1
            
        enemy = self.process.role_list[(self.role_index + 1) % 2]
        if not enemy.harm_to_life_next and enemy.harm_to_life > 0:
            enemy.life_recover += self.harm / 30
            enemy.life_recover += self.bleed_harm / 30
        else:
            enemy.life_now -= (self.harm - enemy.shield) if enemy.shield <= self.harm else 0
            enemy.shield -= self.harm if self.harm <= enemy.shield else enemy.shield
            enemy.life_now = round(enemy.life_now, 0)
            enemy.life_now -= self.bleed_harm
            
        self.life_max += self.life_recover * 30 * self.heal_beilv
        self.life_now += self.life_recover * 30 * self.heal_beilv
        if int(self.harm + self.bleed_harm) > 0:
            self.log_harm += str(int(self.harm + self.bleed_harm)) + "\n"
        if int(self.life_recover * 30 * self.heal_beilv) > 0:
            self.log_recover += str(int(self.life_recover * 30 * self.heal_beilv)) + "\n"
        self.life_recover = 0
        self.bleed_harm = 0
        self.harm = 0
        if self.attr_backup["life_now"] != self.life_now:
            self.life_change += 1
    
    def use_card(self):
        if self.fast_card_limit == 0:
            self.logs += "使用卡牌:\n"
        card_use = self.card_pack_instance[self.card_use_index]
        if self.mana >= card_use.mana:
            self.mana -= card_use.mana
            self.card_use_count += 1
            for i in range(self.effect_count_next):
                self.effect_count_next = 1
                card_use.use()
                
            if card_use.odd and (card_use.index % 2 == 0 or self.no_limit):
                self.card_odd += 1
            if card_use.even and (card_use.index % 2 == 1 or self.no_limit):
                self.card_even += 1
                for i in range(self.effect_count_even - 1):
                    card_use.use()

            if card_use.broken:
                self.card_pack_instance.remove(card_use)
                self.card_use_index = (self.card_use_index) % len(self.card_pack_instance)
            else:
                self.card_use_index = (self.card_use_index + 1) % len(self.card_pack_instance)
            if (card_use.fast_card or self.all_fast_card) and self.fast_card_limit == 0:
                self.fast_card_limit = (self.fast_card_limit + 1) % 2
                self.use_card()
                self.fast_card_limit = (self.fast_card_limit + 1) % 2
        else:
            self.logs += "\n法力不足, 法力加1\n"
            self.mana += 1

    def get_accumulate_num(self):
        num = 0
        for idx, i in enumerate(self.accumulate_list[:]):
            temp = i.replace(" ","").split(">")
            color = temp[4] 
            if color != 'none':
                num += 1 
        return num   

    def merge_accumulate(self):
        self.accumulate_list = merge_strings(self.accumulate_list)
    
    def get_accumulate_min(self):
        num_list = []
        for idx, i in enumerate(self.accumulate_list[:]):
            temp = i.replace(" ","").split(">")
            count_now = int(temp[3])   
            num_list.append(count_now)
        return min(num_list)
        
    
    
    def accumulate_accelerate(self, accelerate_num = 1, effect_num = 1, no_limit = False, min = 0):
        #20 > {name} > num > count_now > color > accu_num
        remove_list = []
        for idx, i in enumerate(list(self.accumulate_list[:])):
            temp = i.replace(" ","").split(">")
            count_max = int(temp[0])
            attr_name = temp[1]
            num = eval(temp[2])
            count_now = int(temp[3])
            color = temp[4]
            accu_num = int(float(temp[5]))
            if min != 0:
                count_now = min
            else:
                count_now -= count_now if count_now < accelerate_num else accelerate_num
            if count_now <= 0 or no_limit:
                attr_value = getattr(self, attr_name)
                attr_value += effect_num * num * accu_num
                setattr(self, attr_name, attr_value)
                if not no_limit:
                    if not self.again:
                        remove_list.append(i)
                    else:
                        
                        str_new = " > ".join([str(count_max), attr_name, temp[2], str(count_max), color, str(accu_num)])
                        self.accumulate_list[idx] = str_new
            else:
                str_new = str_new = " > ".join(map(str, [count_max, attr_name, temp[2], count_now, color, str(accu_num)]))
                self.accumulate_list[idx] = str_new
        
        for i in remove_list:
            self.accumulate_list.remove(i)
        
    
    #角色属性加载
    def role_load(self):
        
        if self.role_name == "西琳":
            self.role_describe = "西琳:开始获得2层力量,10护盾,使用奇数牌增加1点护盾,偶数牌增加1点生命"
            self.shield += 300
            self.power += 2
            self.track_list.append("card_odd > shield > 30")
            self.track_list.append("card_even > life_recover > 1")
        if self.role_name == "特丽丽":
            self.role_describe = "特丽丽:开始获得一个幸运币,判定不小于3,每获得一个幸运币,回复1生命"
            self.coin += 1
            self.coin_judge_min = 3
            self.track_list.append("coin > life_recover > 1")
        
        if self.role_name == "芙乐艾":
            self.role_describe = "芙乐艾:开始获得2层法力并为敌方施加1层虚弱,2层流血"
            self.process.role_list[(self.role_index + 1) % 2].weak += 1
            self.process.role_list[(self.role_index + 1) % 2].bleed += 2
            self.mana += 2
        if self.role_name == "布洛洛":
            self.role_describe = "布洛洛:开始获得2层自愈,每消耗1层自愈,增长3生命,生命变化时,增加1护盾"
            self.track_list.append("heal < life_recover < 3")
            self.track_list.append("life_change > shield > 30")
            self.heal += 2
        if self.role_name == "绮罗老师":
            self.role_describe = "绮罗老师:开始获得1乐符,4法力,每获得8枚乐符,获得1层力量"
            self.note += 1
            self.mana += 4
            self.track_list.append("note > power > 0.125")
        if self.role_name == "学园长":
            self.role_describe = "学园长:开始获得1法力,5点护盾,15点生命上限,每次释放积蓄卡牌,获得3护盾"
            self.track_list.append("card_accumulate > shield > 90")
            self.mana += 1
            self.shield += 5 * 30
            self.life_now += 15 * 30
            self.life_max += 15 * 30
    def make_card_pool(self):
        self.card_pic_pool = [make_card(i) for i in self.card_pack_instance_backup]
            
            
def merge_strings(strings):
    merged_dict = defaultdict(float)  # 使用默认工厂函数为float

    for string in strings:
        if ">" in string:
            parts = string.split(" > ")
            key = " > ".join(parts[:-1])
            value = float(parts[-1])  # 解析为浮点数
            merged_dict[key] += value
        else:
            parts = string.split(" < ")
            key = " < ".join(parts[:-1])
            value = float(parts[-1])  # 解析为浮点数
            merged_dict[key] += value
            
    merged_strings = []
    for key, value in merged_dict.items():
        if ">" in key:
            merged_strings.append(f"{key} > {value}")
        else:
            merged_strings.append(f"{key} < {value}")

    return merged_strings


        