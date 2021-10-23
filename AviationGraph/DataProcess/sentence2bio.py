# -*- coding: utf-8 -*-

from AviationGraph.utils.MySqlConn import MySqlConn

#生成中文关系 和 关系英文缩写的 映射字典
relation_chinese = ['别名关系', '定义关系', '参照关系', '上下位关系', '使用关系', '位置关系', '性能提升关系', '性能需求关系', '选型关系', '组成关系', '作用或影响关系']
relation_english = ['ALI', 'DEF', 'REF', 'SAI', 'USE', 'LOC', 'PPR', 'PRR', 'SEL', 'CON', 'FOI']
relation_dict = dict(zip(relation_chinese, relation_english))
print(relation_dict)

# 存儲所有的标签
tags = set()


# 获取数据库中的三元组信息
conn = MySqlConn('aviationgraph').connectMySql()
cursor = conn.cursor()
sql_select = "SELECT * FROM relation"
cnt = cursor.execute(sql_select)
relation_list = []
for i in range(cnt):
    relation = cursor.fetchone()
    relation_list.append(list(relation))

data_list = [] #存储原始句子的列表
#读取原始句子信息
with open("/AviationGraph/DeepLearning/data/valieddata.txt", encoding="utf8", errors="ignore") as f:
    data_list = f.readlines()



def get_BIO_RE_HT():
    data_relation_list = []
    relation_temp_list = []
    for data in data_list:
        temp_list = []
        for relation in relation_list:
            head_entity_index = data.find(relation[0])
            tail_entity_index = data.find(relation[2])
            if head_entity_index != -1 and tail_entity_index != -1 and head_entity_index < tail_entity_index\
                    and len(relation[0]) <= 10 and len(relation[2]) <= 10:
                temp_list.append(relation)
        '''
        如果一个句子中只有一条关系->普通标注方法
        data ： 本章中未定义的术语则按GJB451《可靠性维修性术语》及本手册后续章节中的定义。
        relation : ['GJB451', '文档', '《可靠性维修性术语》', '文档', '别名关系']
        annotation_list : []
        '''
        annotation_list = get_O(len(data))
        if len(temp_list) == 1:
            relation = temp_list[0]
            annotation_list = get_bio_1head_1tail(relation[0], relation[2], relation[4], data, annotation_list)
        '''
        如果一个句子中有多条关系
        data ： 本章中未定义的术语则按GJB451《可靠性维修性术语》及本手册后续章节中的定义。
        temp_list : [['加速度', '性能参数', '模态位移', '性能参数', '作用或影响关系'], ['加速度', '性能参数', '模态加速度', '性能参数', '作用或影响关系']]
        annotation_list : []
        '''
        if len(temp_list) > 1:
            head_dict = {}
            tail_dict = {}
            for relation in temp_list:
                if relation[0] in head_dict.keys():
                    head_dict[relation[0]] = head_dict.get(relation[0]) + 1
                else:
                    head_dict[relation[0]] = 1

                if relation[2] in tail_dict.keys():
                    tail_dict[relation[2]] = tail_dict.get(relation[2]) + 1
                else:
                    tail_dict[relation[2]] = 1

            for relation in temp_list:
                if head_dict.get(relation[0]) == 1 and tail_dict.get(relation[2]) == 1:
                    annotation_list = get_bio_1head_1tail(relation[0], relation[2], relation[4], data, annotation_list)
                elif head_dict.get(relation[0]) > 1:
                    annotation_list = get_bio_nhead_1tail(relation[0], relation[2], relation[4], data, annotation_list)
                elif tail_dict.get(relation[2]) > 1:
                    annotation_list = get_bio_1head_ntail(relation[0], relation[2], relation[4], data, annotation_list)
        if len(temp_list) >= 1:
            print(annotation_list)
            print(temp_list)
            print(data)
        f = open('/AviationGraph/DeepLearning/out/word.txt', 'a+', encoding="utf8")
        for i in range(len(data)):
            if data[i] == "" or data[i] == "\n" or data[i] == "\t":
                continue
            f.write(str(data[i]) + " " + annotation_list[i] + "\n")
            tags.add(annotation_list[i])
        f.write("end" + "\n")

        f.close()

        # f = open('F:/硕士毕业论文/04-项目工程/AviationGraph/DeepLearning/out/BIO.txt', 'a+', encoding="utf8")
        # for word in annotation_list:
        #     f.write(word + "\n")
        # f.write("\n")
        # f.close()

def get_bio_1head_1tail(headEntity, tailEntity, relation, data, annotation_list):
    english_relation = relation_dict[relation]
    head_start_idx = data.find(headEntity)
    tail_start_idx = data.find(tailEntity)
    for idx in range(len(headEntity)):
        annotation_list[idx + head_start_idx] = "I-" + english_relation + "-H"

    for idx in range(len(tailEntity)):
        annotation_list[idx + tail_start_idx] = "I-" + english_relation + "-T"

    annotation_list[head_start_idx] = "B-" + english_relation + "-H"
    annotation_list[tail_start_idx] = "B-" + english_relation + "-T"
    return annotation_list

def get_bio_nhead_1tail(headEntity, tailEntity, relation, data, annotation_list):
    english_relation = relation_dict[relation]
    head_start_idx = data.find(headEntity)
    tail_start_idx = data.find(tailEntity)

    for idx in range(len(headEntity)):
        annotation_list[idx + head_start_idx] = "I-OVE-H"

    for idx in range(len(tailEntity)):
        annotation_list[idx + tail_start_idx] = "I-" + english_relation + "-T"

    annotation_list[head_start_idx] = "B-OVE-H"
    annotation_list[tail_start_idx] = "B-" + english_relation + "-T"
    return annotation_list

def get_bio_1head_ntail(headEntity, tailEntity, relation, data, annotation_list):
    english_relation = relation_dict[relation]
    head_start_idx = data.find(headEntity)
    tail_start_idx = data.find(tailEntity)
    # 首先全部填充上O

    for idx in range(len(headEntity)):
        annotation_list[idx + head_start_idx] = "I-" + english_relation + "-H"

    for idx in range(len(tailEntity)):
        annotation_list[idx + tail_start_idx] = "I-OVE-T"

    annotation_list[head_start_idx] = "B-" + english_relation + "-H"
    annotation_list[tail_start_idx] = "B-OVE-T"
    return annotation_list


'''
输入一个长度，返回一个长度为len的全是O的列表
'''
def get_O(len):
    o_list = []
    for i in range(len):
        o_list.append('O')
    return o_list
# f = open('F:/硕士毕业论文/04-项目工程/AviationGraph/DeepLearning/data/valieddata.txt', 'w', encoding="utf8")
# for data in data_relation_list:
#     f.write(data)
# f.close()

# f = open('F:/硕士毕业论文/04-项目工程/AviationGraph/DeepLearning/data/relation.txt', 'w', encoding="utf8")
# for data in relation_temp_list:
#     f.write(str(data) + '\n')
# f.close()

if __name__ == '__main__':
    get_BIO_RE_HT()
    print(tags)
    print(len(tags))