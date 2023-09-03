import asyncio
from utils.message_builder import image

async def get_answer(my_dict,up_limit,count):
    time_count = 0
    condition = True
    while condition and time_count <= 180:
        await asyncio.sleep(1)
        time_count += 1
        id = my_dict["answer_id"]
        if my_dict["answer"].get(id):
            id += 1
            my_dict["answer_id"] = id
            answer_list = []
            for i in range(up_limit):
                answer_list.append(str(i))
            print(my_dict["answer"][id - 1])
            if len(my_dict["answer"][id - 1]) != count:
                condition = True
                continue
            
            for i in my_dict["answer"][id - 1]:
                condition = False
                if i not in answer_list:
                    condition = True
                    continue
            if condition:
                continue
            return my_dict["answer"][id - 1]

async def push_image(bot, event, _image):
    try:    
        await bot.send(event,image(b64=_image))
    except:
        pass
