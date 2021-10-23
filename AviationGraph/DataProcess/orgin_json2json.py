import os
import json

def json2csv(file_path):
    cnt = 0
    final_list = []

    for json_file in os.listdir(file_path):
        with open(os.path.join(file_path, json_file), "r", encoding="utf8") as jf:
            j = json.load(jf)
            entity_list = j['outputs']['annotation']['T']
            relation_list = j['outputs']['annotation']['R']
            content = j['content']

            result_list = []
            for relation in relation_list:
                if isinstance(relation, dict) and relation is not None:
                    result = [0, 0, 0, 0, 0]
                    head_entity = relation['from']
                    tail_entity = relation['to']
                    for entity in entity_list:
                        if isinstance(entity, dict):
                            if head_entity == entity['id']:
                                result[0] = entity['value']
                                result[1] = entity['name']
                            if tail_entity == entity['id']:
                                result[2] = entity['value']
                                result[3] = entity['name']

                    result[4] = relation['name']
                    if result[0] != 0 and result[1] != 0 and result[2] != 0 and result[3] != 0:
                        result_list.append(result)
            #根据全文获取单个句子列表
            content_list = (str)(content).split("。")

            #从句子中匹配 头实体 和 尾实体
            for result in result_list:
                for content in content_list:
                    if content.find(result[0]) != -1 and content.find(result[2]) != -1:
                        result.append(content.replace("\r\n", ""))
                        final_list.append(result)
                        cnt = cnt + 1
                        break
    ##将列表信息 转换成 json文件存储到本地
    list2json(final_list)
    print(cnt)

def list2json(result_list):

    text_set = set()
    for result in result_list:
        text_set.add(result[5])

    f = open('F:/01-科研资料/03-项目工程/AviationGraph/AviationGraph/DataProcess/out/train_json.json', 'w', encoding='utf-8')
    for text in text_set:
        spo_list = []
        for data in result_list:
            if data[5] == text:
                spo_dict = {}
                spo_dict["object"] = data[0]
                spo_dict["object_type"] = data[1]
                spo_dict["subject"] = data[2]
                spo_dict["subject_type"] = data[3]
                spo_dict["predicate"] = data[4]
                spo_list.append(spo_dict)

        s = json.dumps({
            "text": text,
            "spo_list": spo_list
        }, ensure_ascii=False)
        f.write(s + "\n")
    print("写入结束！")
    f.close()
'''
将标注精灵助手的json数据转成csv数据
头实体 头实体类型 尾实体 尾实体类型 关系类型 原始句子
'''
if __name__ == '__main__':
    json2csv("F:/01-科研资料/03-项目工程/AviationGraph/AviationGraph/DataProcess/json/")