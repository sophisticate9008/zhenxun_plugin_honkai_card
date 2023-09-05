
from typing import TYPE_CHECKING, List, Tuple, Dict, Optional, Union, Callable,NewType
import random
from .Roles import Roles 
import copy
from .pic_make import *
Card_Pack = NewType("Card_Pack", List[str])
print_attr = ["role_name", "life_max", "life_now", "shield", "power", "coin", "mana", "weak", "easy_hurt", "bleed", "heal", "recover_count"]
class Process:
    winner = 2
    def __init__(self, role1_name: str, card_pack1: Card_Pack, role2_name: str, card_pack2: Card_Pack, sys_random = False):
        self.role_list: List[Roles]  = []
        self.color_map = {
            "迅捷": "#55D1A7",
            "法力": "#499ACD",
            "魔阵": "#A855F1",
            "唯一": "#252C81",
            "流血": "#B3082F",
            "护盾": "#A74722",
            "力量": "#B2381E",
            "自愈": "#458F31",
            "幸运币": "#EEB34D",
            "虚弱": "#2E503F",
            "易伤": "#A774AC",
            "乐符": "#A1BEDC",
        }
        if sys_random:
            card_pack2 = ["_".join((i, f"{random.randint(1,3)}")) for i in card_pack2]
        print(card_pack1)
        print(card_pack2)
        Roles(role1_name, card_pack1, self)
        Roles(role2_name, card_pack2, self)
        self.pic_list: List[Image.Image] = []
        
    def fighting(self):
        for i in range(2):
            self.role_list[i].role_load()
        for i in range(2):
            self.role_list[i].get_attr_backup()
            self.role_list[i].get_attr_now()
        count = 0
        
        while True:
            
            count += 1
            for i in range(2):
                self.role_list[i].cal_bleed_harm()
                self.role_list[i].cal_life()
                self.role_list[i].track_go()
                self.role_list[i].harm_to_life_next = False
            pic = make_turn_process(self,count) 
            for i in range(2):
                if i == 1:
                    self.role_list[i].logs += "敌方效果&\n魔阵效果:\n"
                role_self = self.role_list[i]
                role_enemy = self.role_list[(i + 1) % 2]
                role_self.turn_count += 1
                role_self.turn_begin()
                role_self.merge_accumulate()
                pic = append_accumulate_show(pic, self)

                
                if role_self.life_now <= 0:
                    self.winner = role_enemy.role_index
                    return self.gameover()
                
                role_self.turn_end()
                
                if role_enemy.life_now <= 0:
                    self.winner = role_self.role_index
                    return self.gameover()
                
            for i in range(2):
                if i == 0:
                    self.role_list[i].logs += "敌方效果&\n回合结算:\n"
                else:
                    self.role_list[i].logs += "回合结算:\n"
                if not self.role_list[i].harm_to_life_next:
                    self.role_list[i].harm_to_life -= 1 if self.role_list[i].harm_to_life > 0 else 0   #伤害转治疗回合-1
                self.role_list[i].cal_life()
                self.role_list[i].track_go()
                self.role_list[i].log_handle()
                self.role_list[i].get_states()
            pic = append_logs_and_states(pic, self)
            self.pic_list.append(pic)
            if count >= 96:
                self.winner = 2
                return self.gameover()
 
    def gameover(self):
        num = len(self.pic_list)
        result = Image.new("RGBA", (0,0))
        pic_list = []
        for idx, i in enumerate(self.pic_list):
            result = append_images(result, i, 1,0)
            i.close()
            if (idx + 1) % 8 == 0:
                result = convert_png_to_jpg_with_lower_quality(result, 1)
                pic_list.append(pic2b64(result, 50))
                result.close()
                result = Image.new("RGBA", (0,0))
            elif idx == len(self.pic_list) - 1:
                result = convert_png_to_jpg_with_lower_quality(result, 1)
                pic_list.append(pic2b64(result, 50))
                result.close()
                result = Image.new("RGBA", (0,0))
                
            

            
        return {
            "winner": f"{'平局' if  self.winner == 2 else (self.role_list[self.winner].role_name + '获胜')}",
            "0": self.role_list[0],
            "1": self.role_list[1],
            "pics": pic_list
        }

        
    
        
        
        
    
    
        
        



        
    

                
            
