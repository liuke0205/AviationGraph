import os
import json


def json2txt(file_path):
    res_list = []
    with open(file_path, "r", encoding="utf8") as jf:
        j = json.load(jf)
        result_list = j["result"]
        for result in result_list:
            temp = [0, 0]
            temp[1] = result["text"]
            #relation计数
            count_dict = dict()
            for spo in result["spo_list"]:
                relation = spo["predicate"]
                if relation in count_dict:
                    count_dict[relation] += 1
                else:
                    count_dict[relation] = 1
            #取relation最大值作为最终的关系类型
            temp[0] = max(count_dict, key=count_dict.get)
            res_list.append(temp)

    with open("F:/01-科研资料/03-项目工程/AviationGraph/AviationGraph/DataProcess/out/rel_classification.txt", "w", encoding="utf8") as f:
        for data in res_list:
            f.write(data[0] + "\t" + data[1] + "\n")
    with open("/AviationGraph/Text_Classification/data/place/sentence.txt", "w", encoding="utf8") as f:
        for data in res_list:
            f.write(data[1] + "。\n")
    print(res_list)

'''
将标注精灵助手的json数据转成csv数据
头实体 头实体类型 尾实体 尾实体类型 关系类型 原始句子
'''
if __name__ == '__main__':
    json2txt("/AviationGraph/DataProcess/out/train_json.json")