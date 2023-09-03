from typing import TYPE_CHECKING, Dict, Union
if TYPE_CHECKING:
    from .Process import Process
    from .Roles import Roles 
song_and_note = ["鏖战.蓄力", "乐符狂热"]
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

class Cards:
    index: index = 0
    fast_card: bool = False #迅捷卡牌
    broken: bool = False#
    odd = False
    even = False
    mana = 0
    
    def __init__(self, role: "Roles", card_name: str, index: int, level: int):
        self.describe = ""
        self.card_name = card_name
        self.index = index
        self.level = level
        self.role = role
        
        color = "红"
        if card_name == "垒之护":
            self.color = color
            self.describe = f"护盾+{25 + 25 * level},获得99层壁垒"

            def use(self_):
                role.rampart += 99
                role.shield += (25 + 25 * level) * 30

        if card_name == "绚烂.星霞":
            self.color = color
            self.describe = f"现有力量翻{1 + level}倍"

            def use(self_):
                role.power *= 1 + level
                self.describe = f"现有力量翻{1 + level}倍"

        if card_name == "跃增.运时":
            self.color = color
            self.describe = f"幸运币+{10 * level},魔阵:消耗等量幸运币后返还等量幸运币,唯一"
            self.broken = True

            def use(self_):
                role.coin += 10 * level * role.coin_get_beilv
                if card_name not in role.only_list:
                    role.track_list.append("coin < coin < 1")
                    role.only_list.append(card_name)

        color = "金"
        if card_name == "矛之突":
            self.color = color
            self.describe = f"护盾加{5 + 5 * level},然后失去所有护盾,每失去一点造成{2 + level}伤害"

            def use(self_):
                role.shield += (5 + 5 * level) * 30
                shield_num = role.shield
                role.shield = 0
                role.harm += shield_num * (2 + level)
                role.attack_count += 1

        if card_name == "灼灼.星熠":
            self.color = color
            power_add = 2 if level == 1 else 4
            even_count = 3 if level == 3 else 2
            self.describe = f"魔阵:打出奇数牌获得{power_add}力量,偶数牌重复{even_count}次效果,唯一"
            self.broken = True

            def use(self_):
                if card_name not in role.only_list:
                    role.track_list.append(f"card_odd > power > {power_add}")
                    role.effect_count_even = even_count
                    role.only_list.append(card_name)

        if card_name == "复加.得时":
            self.color = color
            self.describe = f"魔阵:投掷的幸运币数量翻{1 + level}倍,唯一"
            self.broken = True

            def use(self_):
                role.coin_throw_beilv = 1 + level


        if card_name == "幸运一掷":
            self.color = color
            self.describe = f"{10 + level * 5}伤害,投掷所有幸运币,造成总点数{round(float(0.7 + level * 0.3), 0)}的伤害"

            def use(self_):
                role.attack += 10 + level * 5
                result = role.throw_coin(role.coin)
                role.attack += float(0.7 + level * 0.3) * result
                role.attack_count += 1

        if card_name == "时来运转":
            self.color = color
            num = 10 if level == 1 else 6 + level * 3
            self.describe = f"幸运币+{num}"

            def use(self_):
                num = 10 if level == 1 else 6 + level * 3
                role.coin += num * role.coin_get_beilv

        if card_name == "好运加护":
            self.color = color
            self.broken = True 
            self.describe = f"幸运币+{1 + level * 2},魔阵:幸运币必投出最大值"

            def use(self_):
                num = 1 + level * 2
                role.coin += num * role.coin_get_beilv
                role.coin_judge_min = 6

        if card_name == "魔阵.星数":
            self.color = color
            self.odd = True  
            self.broken = True

            if level == 2:
                self.describe = f"获得1层力量,奇数-魔阵:每回合获得一层力量"        
            else:
                self.describe = f"奇数-魔阵:每回合获得{2 if level == 3 else 1}层力量"

            def use(self_):
                if level == 2:
                    role.power += 1
                if self.index % 2 == 0 or role.no_limit:
                    num = 2 if level == 3 else 1
                    role.track_list.append(f"turn_count > power > {num}")

        if card_name == "焰力.星数":
            self.color = color
            self.even = True  
            self.describe = f"{level + 3}伤害,偶数:每用过1张牌,追加{level + 3}伤害"

            def use(self_):
                num = 3 + level
                role.attack += num
                role.attack_count += 1
                if self.index % 2 == 1 or role.no_limit:
                    role.attack += num * role.card_use_count

        if card_name == "幻记.星数":
            self.color = color
            self.broken = True 
            self.describe = f"获得{2 + level}层力量,魔阵:奇数偶数无条件触发"

            def use(self_):
                role.power += 2 + level
                role.no_limit = True

        color = "紫"
        if card_name == "盾之守":
            self.color = color
            self.describe = f"护盾+{5 + level},然后护盾翻倍"

            def use(self_):
                role.shield += (5 + level) * 30
                role.shield *= 2


        if card_name == "烁烁.星电":
            self.color = color
            self.describe = f"奇数:施加{3 + level}层易伤,偶数:施加{3 + level}层虚弱"

            if self.index % 2 == 0:
                self.odd = True
            else:
                self.even = True

            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                if self.index % 2 == 0:
                    enemy.easy_hurt += 3 + level
                else:
                    enemy.weak += 3 + level

        if card_name == "倍加.巧时":
            self.color = color
            self.describe = f"幸运币+{-5 + level * 5},魔阵:获得的幸运币数量翻倍,唯一"
            self.broken = True

            def use(self_):
                role.coin += (-5 + level * 5) * role.coin_get_beilv
                role.coin_get_beilv = 2

        if card_name == "术士.魔阵":
            self.color = color
            self.broken = True
            self.describe = f"魔阵:每回合幸运币+{level}"

            def use(self_):
                role.track_list.append(f"turn_count > coin > {level}")

        if card_name == "骑士.魔运":
            self.color = color
            self.describe = f"生效{4 + level * 2}次:2+点数伤害"

            def use(self_):
                num = 4 + level * 2
                role.attack += 2 * num
                result = role.throw_coin(num)
                role.attack += result
                role.attack_count += num

        if card_name == "医者.魔运":
            self.color = color
            self.describe = f"幸运币+{4 if level == 1 else 6}, 每有一个幸运币加{2 if level == 3 else 1}生命"

            def use(self_):
                role.coin += (4 if level == 1 else 6) * role.coin_get_beilv
                role.life_recover += (2 if level == 3 else 1) * role.coin

        if card_name == "战车.魔运":
            self.color = color
            self.describe = f"魔阵:每获得一个幸运币造成{level}伤害"
            self.broken = True

            def use(self_):
                role.track_list.append(f"coin > attack > {level}")

        if card_name == "伤.星数":
            self.color = color
            self.describe = f"5伤害,奇数:施加{2 + level}层易伤"
            self.odd = True
            self.mana = 1

            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.attack += 5
                role.attack_count += 1
                if self.index % 2 == 0 or role.no_limit:
                    enemy.easy_hurt += 2 + level

        if card_name == "灵.星数":
            self.color = color
            self.describe = f"2伤害*{2 + level},偶数:法力加{level}"
            self.even = True

            def use(self_):
                num = 2 + level
                role.attack += 2 * num
                role.attack_count += num
                if self.index % 2 == 1 or role.no_limit:
                    role.mana += level

        if card_name == "赐.星数":
            self.color = color
            self.describe = f"2伤害*{1 + level},偶数:每用过一张牌,生命加{2 + level}"
            self.even = True

            def use(self_):
                role.attack += 2 * (1 + level)
                role.attack_count += (1 + level)
                if self.index % 2 == 1 or role.no_limit:
                    role.life_recover += role.card_use_count * (2 + level)

        if card_name == "势.星数":
            self.color = color
            self.describe = f"获得2层力量,奇数:再获得{level}层力量"
            self.odd = True

            def use(self_):
                role.power += 2
                if self.index % 2 == 0 or role.no_limit:
                    role.power += level
        
        color = "红"
        if card_name == "光羽夜蝶":
            self.color = color
            self.describe = f"魔阵:每回合获得{level}层力量,自愈与法力,敌方获得{level}层流血,虚弱和易伤"
            self.broken = True
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.track_list.append(f"turn_count > power > {level}")
                role.track_list.append(f"turn_count > heal > {level}")
                role.track_list.append(f"turn_count > mana > {level}")
                enemy.track_list.append(f"turn_count > bleed > {level}")
                enemy.track_list.append(f"turn_count > weak > {level}")
                enemy.track_list.append(f"turn_count > easy_hurt > {level}")
            
        if card_name == "收割.夜蝶":
            self.color = color
            self.describe = f"{20 + level *10}伤害,追加等于敌方已损失生命值{level}倍的流血伤害"
            
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.attack_count += 1
                role.attack += 20 + level * 10
                role.cal_bleed_harm(enemy.life_max - enemy.life_now)
                
        
        if card_name == "复原.光羽":
            self.color = color
            self.describe = f"下{2 if level == 3 else 1}回合自身受到的所有伤害转为治疗"
            
            if level == 1:
                self.mana = 2
            def use(self_):
                if role.harm_to_life == 0:
                    role.harm_to_life_next = True
                role.harm_to_life += 2 if level == 3 else 1
                
        
        color = "金"
        if card_name == "夜影光烁":
            self.color = color
            self.describe = f"{10 * level + 15 + (5 if level == 3 else 0)}伤害和生命"

            def use(self_):
                role.attack += 10 * level + 15 + (5 if level == 3 else 0)
                role.life_recover += 10 * level + 15 + (5 if level == 3 else 0)
                role.attack_count += 1
        
        if  card_name == "血疗.夜蝶":
            self.color = color
            self.describe = f"魔阵:自身每有一层流血,回合开始时回复{1 + level}点生命"
            self.broken = True
            
            def use(self_):
                role.bleed_to_life += 1 + level
        
        if card_name == "神愈.光羽":
            self.color = color
            self.describe = f"魔阵:治疗量变为{level + 1}倍,唯一"
            self.broken = True
            
            def use(self_):
                role.heal_beilv = level + 1
        
        if card_name == "渴血.夜蝶":
            self.color = color
            self.describe = f"流血对敌方造成伤害时,回复伤害值{10 * level + 15 + (5 if level == 3 else 0)}%的生命"   
            self.broken = True
            
            def use(self_):
                role.bleed_harm_to_life += 10 * level + 15 + (5 if level == 3 else 0)
                
        if card_name == "血噬.夜蝶":
            self.color = color
            self.describe = f"敌方流血立刻生效{1 + level}次"
            self.mana = 1
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                for i in range(1 + level):
                    role.cal_bleed_harm()
                
        
        if card_name == "晨昏":
            self.color = color
            self.describe = f"双方叠加{2 + level}层流血和自愈 迅捷"   
            self.fast_card = True
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.bleed += 2 + level
                role.heal += 2 + level
                enemy.bleed += 2 + level
                enemy.heal += 2 + level
        
        if card_name == "裂伤.夜蝶":
            self.color = color
            self.broken = True
            self.describe = f"敌方当前流血层数+{75 + level * 25}% 消耗"
            self.mana = 2
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.bleed += int(enemy.bleed * (75 + level * 25) / 100)
                
            
        if card_name == "清心.光羽":
            self.color = color
            self.describe = f"清除自身所有负面状态,每清除一点回复{1 + level}点生命值"
            self.mana = 1
            
            def use(self_):
                num_ = role.bleed + role.weak + role.easy_hurt
                role.bleed = 0
                role.weak = 0
                role.easy_hurt = 0
                role.life_recover += num_ * (1 + level)
                
        if card_name == "神罚.光羽":
            self.color = color
            self.describe = f"获得{level}层自愈 魔阵:治疗时对敌方造成等量伤害"
            self.broken = True
            
            def use(self_):
                role.heal += level
                role.track_list.append(f"life_max > harm > 1")
                            
        
        if card_name == "神赐.光羽":
            self.color = color
            self.describe = f"{12 + level * 4}伤害 自身每有一层自愈,多{4 + level}伤害"
            self.mana = 1
            
            def use(self_):
                role.attack += 16
                role.attack += role.heal * (4 + level)
                role.attack_count += 1
        
        color = "紫"
        if card_name == "光夜交织":
            self.color = color
            self.describe = f"双方叠加{5 + level}层自愈和流血"
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.bleed += 5 + level
                role.heal += 5 + level
                enemy.bleed += 5 + level
                enemy.heal += 5 + level
                
        if card_name == "血镰.夜蝶":
            self.color = color
            self.describe = f"移除敌方所有自愈,并施加{level}倍层数的流血"
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.bleed += enemy.heal * level
                enemy.heal = 0
        
        if card_name == "静心.光羽":
            self.color = color
            self.describe = f"法力加 {0 if level == 1 else 5} 魔阵:自身负面状态减少时,获得{2 if level == 3 else 1}倍减少层数的自愈"
            self.broken = True
            
            def use(self_):
                role.mana += 0 if level == 1 else 5
                role.track_list.append(f"weak < heal < {2 if level == 3 else 1}")
                role.track_list.append(f"easy_hurt < heal < {2 if level == 3 else 1}")
                role.track_list.append(f"bleed < heal < {2 if level == 3 else 1}")
                
        if card_name == "以血换血.夜蝶":
            self.color = color
            self.broken = True
            self.describe = f"法力+{-2 + 2 * level}魔阵:自身被叠加流血时,向敌方叠加相同层数的流血"
            
            def use(self_):
                role.mana += -2 + 2 * level
                role.track_list.append("bleed > push_bleed > 1")
                
        
        if card_name == "灵愈.光羽":
            self.color = color
            self.describe = f"法力+{1 + level}, 每有一点法力加{1 + level}点生命"
            
            def use(self_):
                role.mana += 1 + level 
                role.life_recover += (1 + level) * role.mana
                
        if card_name == "回愈.光羽":
            self.color = color
            self.describe = f"生命+10,每有一点自愈多回{1 + level}点生命 迅捷"
            self.mana = 3
            self.fast_card = True
            
            def use(self_):
                role.life_recover += 10
                role.life_recover += (1 + level) * role.heal
        
        if card_name == "狂宴.夜蝶":
            self.color = color
            self.mana = 3
            self.describe = f"敌方叠加2层流血和{level}层虚弱 迅捷"
            self.fast_card = True
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.bleed += 2
                enemy.weak += level
                
        if card_name == "拂晓":
            self.color = color
            self.describe = f"法力+{2 + 2 * level} 双方叠加{2 + level}层流血和自愈"
            
            def use(self_):
                role.mana += 2 + 2 * level
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.bleed += 2 + level
                enemy.heal += 2 + level
                role.bleed += 2 + level
                role.heal += 2 + level
        
        if card_name == "刃舞.夜蝶":
            self.color = color    
            self.describe = f"法力+{level} 敌方叠加等于自身法力的流血(至多{3 + level * 2})"

            def use(self_):
                role.mana += level
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.bleed += (level * 2 + 3) if role.mana > (level * 2 + 3) else role.mana
                
        if card_name == "血阵.夜蝶":
            self.color = color
            self.describe = f"魔阵:每回合为双方叠加{1 + level}层流血"
            self.broken = True
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.track_list.append(f"turn_count > bleed > {1 + level}")
                enemy.track_list.append(f"turn_count > bleed > {1 + level}")
        
        if card_name == "血清.夜蝶":
            self.color = color
            self.describe = f"{13 + level * 2}伤害 消耗自身至多四层流血,每消耗一层多{4 + level}伤害"
            self.mana = 2
            
            def use(self_):
                role.attack_count += 1
                role.attack += 13 + level * 2
                role.attack += (4 if role.bleed > 4 else role.bleed) * (4 + level)
                role.bleed -= (4 if role.bleed > 4 else role.bleed)
                
        if card_name == "倾泻.光羽":
            self.color = color
            self.describe = f"{7 + 3 * level}伤害 消耗至多3层自愈,每1层加{6 + level * 2}伤害"
            self.mana = 1
            
            def use(self_):
                role.attack_count += 1
                role.attack += 10
                role.attack += (3 if role.heal > 3 else role.heal) * (6 + 2 * level)
                role.heal -= (3 if role.heal > 3 else role.heal)
                
        if card_name == "复苏.光羽":
            self.color = color
            self.describe = f"法力+1,获得{1 + level}层自愈"
            
            def use(self_):
                role.mana += 1
                role.heal += 1 + level
        
        if card_name == "神助.光羽":
            self.color = color        
            self.describe = f"10伤害,每回复过一次生命值,加{1 + level}伤害"
            
            def use(self_):
                role.attack_count += 1
                role.attack += 10
                role.attack += role.recover_count * (1 + level)
        
        color = "红"
        if card_name == "鏖战.蓄力":
            self.color = color
            if level != 1:
                self.describe += f"积蓄(20): {-50 + level * 50}伤害"
            self.describe += "魔阵:积蓄效果触发后将再次开始倒计时"
            self.broken = True
            
            def use(self_):
                role.again = True
                if level != 1:
                    role.card_accumulate += 1
                    role.accumulate_list.append(f"20 > attack > {-50 + level * 50} > 20 > #A21911")
                    role.accumulate_list.append(f"20 > attack_count > 1 > 20 > none")
                    
        if card_name == "乐符狂热":
            self.describe = f"乐符+{5 + 5 * level} 积蓄(5)获得等于乐符数量{0.5 + 0.5 * level}倍的力量"
            self.color = color
            
            def use(self_):
                role.card_accumulate += 1
                role.note += 5 + 5 * level
                role.accumulate_list.append(f"5 > power > self.note * {0.5 + 0.5 * level} > 5 > #B47EC6")
                
        if card_name == "音律强击":
            self.color = color
            self.describe = f"{5 + 5 * level} 受{5 + 5 * level}倍乐符与力量加成"
            
            def use(self_):
                role.attack += 5 + 5 * level
                role.attack += (role.note + role.power) * (4 + 5 * level)
                role.attack_count += 1
        
        color = "金"
            
        if card_name == "争锋.蓄力":
            self.color = color
            self.describe = f"触发{1 + level}次场上的积蓄效果 迅捷"
            self.fast_card = True
            
            def use(self_):
                role.accumulate_accelerate(accelerate_num=0, effect_num= 1 + level, no_limit=True)
        
        if card_name == "交续之时":
            self.color = color
            self.describe = f"生命+{0 if level == 1 else 6} 下一张牌连续生效{3 if level == 3 else 2}"
            
            def use(self_):
                role.effect_count_next = 3 if level == 3 else 2
        
        
        if card_name == "奇攻.贮力":
            self.color = color
            if level == 1:
                self.mana = 2
            
            self.describe = f"复制{2 if level == 3 else 1}份场上的积蓄效果"
            
            def use(self_):
                num = 2 if level == 3 else 1
                backup = role.accumulate_list[:]
                for i in range(num):
                    role.accumulate_list.extend(backup)
        
        if card_name == "闪攻.贮力":
            self.color = color 
            self.describe = f"积蓄(10): {20 + 5 * level}伤害"
            
            def use(self_):
                role.card_accumulate += 1
                role.accumulate_list.append(f"10 > attack > {20 + 5 * level} > 10 > #E7B77B")
                role.accumulate_list.append(f"10 > attack_count > 1 > 10 > none")
        
        if card_name == "速攻.贮力":
            self.color = color 
            self.mana = 1
            self.describe = f"加速{2 * level}次,由该卡触发的积蓄效果生效{1 + level}次"
            
            def use(self_):
                role.accumulate_accelerate(accelerate_num=2 * level, effect_num=1 + level)
            
        if card_name == "乐符积蓄":
            self.color = color 
            self.describe = f"积蓄(5):乐符+{15 + 5 * level}"
            
            def use(self_):
                role.card_accumulate += 1
                role.accumulate_list.append(f"5 > note > {15 + 5 * level} > 5 > #D54582")
                
        if card_name == "额外音符":
            self.color = color 
            self.describe = f"魔阵:每回合乐符+{2 + level}"
            self.broken = True
            
            def use(self_):
                role.track_list.append(f"turn_count > note > {2 + level}")
        
        if card_name == "回梦旋律":
            self.color = color 
            self.describe = f"法力+{-1 + level * 2} 移除对方的护盾 迅捷"
            self.fast_card = True
            
            def use(self_):
                role.mana += -1 + level * 2
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                enemy.shield = 0
        
        if card_name == "捷速谐乐":
            self.color = color 
            self.mana = 3
            self.describe = f"3伤害 * {4 + level}"
            
            def use(self_):
                role.attack += 3 * (4 + level)
                role.attack_count += 4 + level
                
        if card_name == "魔文乐谱":
            self.color = color 
            self.mana = 1
            self.describe = f"现有乐符数量增加{75 + 25 * level}%"
            
            def use(self_):
                role.note += int(role.note * (75 + 25 * level) / 100)
        
        color = "紫"
        
        if card_name == "激决.蓄力":
            self.color = color 
            self.describe = f"场上每有一个积蓄效果, 获得{1 + level}层力量"
            
            def use(self_):
                role.power += role.get_accumulate_num() * (1 + level)
                
        if card_name == "搏战.集力":
            self.color = color
            self.describe = f"法力+{-2 + level * 2}场上所有积蓄倒计时变为其中最小值 迅捷"
            self.fast_card = True
            
            def use(self_):
                if role.get_accumulate_num() > 0:
                    
                    min = role.get_accumulate_min()
                    role.accumulate_accelerate(effect_num=0, min=min)
        
        if card_name == "破袭.集力":
            self.color = color
            self.describe = f"积蓄(8):{15 + 5 * level}"
            
            def use(self_):
                role.card_accumulate += 1
                role.accumulate_list.append(f"8 > attack > {15 + 5 * level} > 8 > #669592")
                role.accumulate_list.append(f"8 > attack_count > 1 > 8 > none")
                
        if card_name == "威势.集力":
            self.color = color
            self.describe = f"法力+{3 + level} 积蓄(7):生命+{2 + level * 3}"
            
            def use(self_):
                role.card_accumulate += 1
                role.mana += 3 + level
                role.accumulate_list.append(f"7 > life_recover > {2 + level * 3} > 7 > #8EBF78")
                
        if card_name == "瞬袭.集力":
            self.mana = 2
            self.color = color
            self.describe = f"场上如果有2个及以上积蓄倒计时则造成{25 + level * 5}伤害"
            
            def use(self_):
                if role.get_accumulate_num() >= 2:
                    role.attack += 25 + level * 5
                    role.attack_count += 1
                    
        if card_name == "突袭.集力":
            self.color = color
            self.describe = f"回复等同于场上积蓄数量{4 + level}倍的生命"
            
            def use(self_):
                role.life_recover += role.get_accumulate_num() * (4 + level)
        
        if card_name == "延时乐曲":
            self.color = color
            self.describe = f"乐符+{1 + 2 * level} 积蓄(5): 1伤害 * {4 + level}"
            
            def use(self_):
                role.card_accumulate += 1
                role.note += 1 + 2 * level
                role.accumulate_list.append(f"5 > attack > {4 + level} > 5 > #62A8F1")
                role.accumulate_list.append(f"5 > attack_count > {4 + level} > 5 > none")
        
        if card_name == "音符预演":
            self.color = color 
            self.describe = f"乐符+{1 + 2 * level}下一次攻击后返还乐符"
            
            def use(self_):
                role.note += 1 + 2 * level
                role.return_note = True
                
        if card_name == "肆意.小调":
            self.color = color
            self.describe = f"法力+{4 if level == 3 else 2} 魔阵:每{2 if level == 1 else 1}回合加1法力"
            self.broken = True
            def use(self_):
                role.mana += 4 if level == 3 else 2
                role.track_list.append(f"turn_count > mana > {0.5 if level == 1 else 1}")
        
        if card_name == "安神.小调":
            self.color = color
            self.mana = 2
            self.describe = f"{7 + 5 * level}伤害 对方法力-2"
            
            def use(self_):
                enemy = role.process.role_list[(role.role_index + 1) % 2]
                role.attack += 7 + 5 * level
                enemy.mana -= 2
                role.attack_count += 1
                
        if card_name == "甜美.小调":
            self.color = color
            self.broken = True
            self.describe = f"魔阵:每获得一枚乐符加{level}护盾"
            
            def use(self_):
                role.track_list.append(f"note > shield > {level * 30}")
                
        if card_name == "四重.小调":
            self.color = color
            self.mana = 2
            self.describe = f"2伤害*{3 + level}"
            
            def use(self_):
                role.attack += 2 * (3 + level)
                role.attack_count += 2 * (3 + level)                
        
        if card_name == "激昂.小调":
            self.color = color
            self.describe = f"护盾+{4 + 4 * level} 获得等同于法力的乐符 至多{4 + 4 * level}"
            
            def use(self_):
                role.shield += (4 + 4 * level) * 30
                role.note += (4 + 4 * level) if (4 + 4 * level) > role.mana else role.mana
            
            
        self.use = use.__get__(self)
        