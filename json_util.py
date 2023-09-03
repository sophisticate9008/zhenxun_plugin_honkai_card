import json
import os
current_path = os.path.abspath(__file__)
directory = os.path.dirname(current_path)
record_dir = directory + "/record.json"


def record_harm(group: str, id:str, harm):
    data = read_json_file(record_dir)
    if data.get(group):
        if data.get(id):
            data[group][id].append(harm)
        else:
            data[group][id] = [harm]
    else:
        data[group] = {}
        data[group][id] = [harm]
    data[group] = rank_lists_max_values(data[group])
    write_json_file(record_dir, data)
    
            
            
def read_json_file(file_path):
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    return data

def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)            

def rank_lists_max_values(dictionary):
    rank = {}

    for key, value in dictionary.items():
        if isinstance(value, list):
            max_value = max(value)
            rank[key] = max_value

    sorted_rank = dict(sorted(rank.items(), key=lambda item: item[1], reverse=True))
    top_10 = dict(list(sorted_rank.items())[:10])

    # 更新原始字典，添加排名信息
    dictionary.update({"rank": top_10})

    return dictionary



