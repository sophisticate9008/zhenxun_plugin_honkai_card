from typing import TYPE_CHECKING, List, Tuple
from .pic_util import *
if TYPE_CHECKING:
    from .Process import Process
    from .Cards import Cards
    from .Roles import Roles
import copy

def make_card_sel(card_list: List['Cards'], num: int):
    pic_row_list: List[Image.Image] = []
    pic = Image.new('RGBA',(0,0))
    for idx, i in enumerate(card_list):
        pic = append_images(pic,make_card(i),0,0)
        if (idx + 1) % num == 0:
            pic_row_list.append(copy.deepcopy(pic))
            pic = Image.new('RGBA',(0,0))
    
    for i in pic_row_list:
        pic = append_images(pic, i,1,0)
    
    return convert_png_to_jpg_with_lower_quality(pic, 1)
            

def make_card(card: 'Cards', mask=False):
    back = res_dir + card.color + ".jpg"
    font = yuanshen_ttf
    color_map = {
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
        "乐符": "#A1BEDC"
    }
    result = add_colored_text_to_image(back, card.describe, (17, 190), (180, 300), 20, font, color_mapping=color_map)
    result = add_colored_text_to_image(result, card.card_name, (0,139),(195,177), 20, font,default_color=(255,255,255))
    result = add_colored_text_to_image(result, str(card.mana), (0,0),(40,40), 19, font,default_color="#0076B8")
    result = add_colored_text_to_image(result, "★" * card.level, (0, 0), (195, 40), 17, font, default_color="#F5D9C7")
    if mask:
        result = apply_transparent_mask(result, (0,0,0,128))
    result = convert_png_to_jpg_with_lower_quality(result, 1)
    return result


def make_card_pack(role: 'Roles', reverse_order: bool = False):
    have_card_list: List[str] = [i.index for i in role.card_pack_instance]
    card_pic_list: List[Image.Image] = []
    if reverse_order:
        align = 0
    else:
        align = 1
    
    
    card_pack_to_iterate = role.card_pack_instance_backup
    if reverse_order:
        card_pack_to_iterate = reversed(card_pack_to_iterate)
    
    for i in card_pack_to_iterate:
        if i.index not in have_card_list:
            card_pic_list.append(make_card(i, mask=True))
        else:
            temp = make_card(i)
            if (i.index == role.card_pack_instance[role.card_use_index].index 
                or ((role.card_pack_instance[role.card_use_index].fast_card or role.all_fast_card)
                    and i.index == role.card_pack_instance[(role.card_use_index + 1) % len(role.card_pack_instance)].index)):
                blank = Image.new("RGBA", (temp.size[0], temp.size[1] // 5), (0,0,0,0))
                if reverse_order:
                    temp = append_images(blank, temp, 1, 1)
                else:
                    temp = append_images(temp, blank, 1, 0)
            card_pic_list.append(temp) 
    
    result = Image.new('RGBA', (0,0),(255,255,255,1))
    for i in card_pic_list:
        result = append_images(result, i, 0, align)
        i.close()

    return result


def make_turn_process(process: 'Process', count):
    back = Image.new("RGBA", (1560, 1200),(0,0,0,255))
    result1 = make_card_pack(process.role_list[0])
    result2 = make_card_pack(process.role_list[1], reverse_order=True)
    back = paste_image(back, result2, (0,0), (result2.size), 1,1)
    back = paste_image(back, result1, (0,back.size[1] - result1.size[1]), (back.size), 1,1)
    back = add_colored_text_to_image(back, f"回合{count}", (0,0), back.size, 15, yuanshen_ttf, default_color=(255,255,255))
    return back


def append_accumulate_show(pic: Image.Image, process: 'Process'):
    for i in range(2):
        width = 24
        border_x = 3
        broder_y = 3
        height = 36
        if i == 0:
            start_x = 150
            start_y = 420
        else:
            start_x = 1560 - 150 - width
            start_y = 420          
        role_self = process.role_list[i]
        x = start_x
        y = start_y
        count = 0
        line_count = 8

        for j in role_self.accumulate_list:
            temp = j.replace(" ","").split(">")
            count_now = temp[3]
            color = temp[4]
            accu_num = str(int(float(temp[5])))
            if color != 'none':
                count += 1
                if i == 0:
                    pic = apply_transparent_mask(pic, color, [(x, y, x + width, y + height)])
                    pic = add_colored_text_to_image(pic, count_now + "\n" + accu_num, (x, y), (x + width, y + height), 15, yuanshen_ttf)
                    x += width + border_x
                else:
                    pic = apply_transparent_mask(pic, color, [(x - width, y, x, y + height)])
                    pic = add_colored_text_to_image(pic, count_now + "\n" + accu_num, (x - width, y), (x, y + height), 15, yuanshen_ttf)
                    x -= width + border_x
                if count % line_count == 0:
                    x = start_x
                    y += height + broder_y
                
    return pic

def append_logs_and_states(pic: Image.Image, process: 'Process'):
    for i in range(2):
        
        role_self = process.role_list[i]
        if i == 0:
            pic = add_colored_text_to_image(pic, role_self.role_describe, (10, 740), (390, 760), 20, yuanshen_ttf, alignment=(0,0),
                                            color_mapping=process.color_map, default_color=(255,255,255))             
            pic = add_colored_text_to_image(pic, role_self.logs, (10, 400), (390, 700), 20, yuanshen_ttf, alignment=(0,1),
                                            color_mapping=process.color_map, default_color=(255,255,255))    
            pic = add_colored_text_to_image(pic, role_self.states, (10, 700), (520, 720), 20, yuanshen_ttf, alignment=(0,2),
                                            color_mapping=process.color_map,default_color=(255,255,255) )                
            render_self = render_progress_bar(role_self.life_now, role_self.life_max, width=380, corner_radius=8)
            pic = paste_image(pic, render_self, (10, 720), (390, 740), 1, 1)
            pic = add_colored_text_to_image(pic, str(int(role_self.life_now)) + " / " + str(int(role_self.life_max)), 
                                            (395, 720), (560,740), 15, yuanshen_ttf,alignment=(0,1), 
                                            color_mapping= process.color_map,default_color=(255,255,255))
            
            if len(role_self.log_harm.split("\n")) > 0:
                pic = add_colored_text_to_image(pic, role_self.log_harm.lstrip('0'),
                                            (450, 400), (660,500), 25, yuanshen_ttf,alignment=(0,1), 
                                            color_mapping= process.color_map,default_color="#B6230F")         
            if len(role_self.log_recover.split("\n")) > 0:
                pic = add_colored_text_to_image(pic, role_self.log_recover.lstrip('0'),
                                            (450, 500), (660,600), 25, yuanshen_ttf,alignment=(0,1), 
                                            color_mapping= process.color_map,default_color="#B8F87A")
        else:
            pic = add_colored_text_to_image(pic, role_self.role_describe, (pic.size[0] - 390, 740), (pic.size[0] - 10, 760), 20, yuanshen_ttf, alignment=(2,0),
                                            color_mapping=process.color_map, default_color=(255,255,255)) 
            pic = add_colored_text_to_image(pic, role_self.logs, (pic.size[0] - 390, 400), (pic.size[0] - 10, 700), 20, yuanshen_ttf, alignment=(2,1),
                                            color_mapping=process.color_map, default_color=(255,255,255))    
            pic = add_colored_text_to_image(pic, role_self.states, (pic.size[0] - 520, 700), (pic.size[0] - 10, 720), 20, yuanshen_ttf, alignment=(2,2),
                                            color_mapping=process.color_map,default_color=(255,255,255) )                
            render_self = render_progress_bar(role_self.life_now, role_self.life_max, width=380, corner_radius=8)
            render_self = rotate_image(render_self, 180)
            pic = paste_image(pic, render_self, (pic.size[0] - 390, 720), (pic.size[0] - 10, 740), 1, 1)
            pic = add_colored_text_to_image(pic, str(int(role_self.life_now)) + " / " + str(int(role_self.life_max)), 
                                            (pic.size[0] - 560, 720), (pic.size[0] - 395,740), 15, yuanshen_ttf,alignment=(2,1), 
                                            color_mapping= process.color_map,default_color=(255,255,255) )
            if len(role_self.log_harm.split("\n")) > 0:
                pic = add_colored_text_to_image(pic, role_self.log_harm.lstrip('0'),
                                (pic.size[0] - 660, 400), (pic.size[0] - 450,500), 25, yuanshen_ttf,alignment=(2,1), 
                                color_mapping= process.color_map,default_color="#B6230F" )

            if len(role_self.log_recover.split("\n")) > 0:
                pic = add_colored_text_to_image(pic, role_self.log_recover.lstrip('0'),
                                (pic.size[0] - 660, 500), (pic.size[0] - 450,600), 25, yuanshen_ttf,alignment=(2,1), 
                                color_mapping= process.color_map,default_color="#B8F87A" )                
        role_self.logs = ""
        role_self.states = ""
        role_self.log_harm = ""
        role_self.log_recover = ""
    
    return pic