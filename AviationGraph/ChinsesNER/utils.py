# -*- coding:utf-8 -*-
from AviationGraph.utils.snowFlake import IdWorker

relation_chinese = [
    "别名",
    "定义",
    "参照",
    "上下位",
    "使用",
    "位置",
    "性能提升",
    "性能需求",
    "选型",
    "组成",
    "作用或影响",
]
relation_english = [
    "ALI",
    "DEF",
    "REF",
    "SAI",
    "USE",
    "LOC",
    "PPR",
    "PRR",
    "SEL",
    "CON",
    "FOI",
]
relation_dict = dict(zip(relation_english, relation_chinese))
tail_data = [
    "B-ALI-T",
    "B-FOI-T",
    "B-DEF-T",
    "B-SAI-T",
    "B-USE-T",
    "B-PRR-T",
    "B-LOC-T",
    "B-SEL-T",
    "B-CON-T",
    "B-REF-T",
    "B-PPR-T",
]
head_data = [
    "B-ALI-H",
    "B-FOI-H",
    "B-DEF-H",
    "B-SAI-H",
    "B-USE-H",
    "B-PRR-H",
    "B-SEL-H",
    "B-CON-H",
    "B-LOC-H",
    "B-REF-H",
    "B-PPR-H",
]


# 判断是否存在重叠关系
"""
@:return 0：不存在重叠关系；1：存在头实体重叠；2：存在尾实体重叠
"""
def isOVE(id2BIO):
    for BIO in id2BIO:
        if BIO == "B-OVE-H":
            return 1
        elif BIO == "B-OVE-T":
            return 2
    return 0


def get_result(BIO, text, map):
    id2BIO = []
    for id in BIO:
        for k, v in map.items():
            if v == id:
                id2BIO.append(k)

    relation = []

    # 使用雪花算法生成id
    # worker = IdWorker(1, 2, 0)

    # 存在头实体重叠关系情况
    if isOVE(id2BIO) == 1:
        head_entity_start = get_idx(id2BIO, "B-OVE-H")
        # 不正确，应该找最后一个=====================================================
        head_entity_end = get_idx_last(id2BIO, head_entity_start, "I-OVE-H")
        head_entity = text[head_entity_start: head_entity_end + 1]
        for idx in range(len(id2BIO)):
            if id2BIO[idx] in tail_data:
                relation_english_sigleon = id2BIO[idx][2:-2]
                global j, kk
                tail = "I" + id2BIO[idx][1:]

                for j in range(idx + 1, len(id2BIO)):
                    if tail == id2BIO[j]:
                        continue
                    else:
                        break
                tail_entity = text[idx:j]
                relation.append(
                    [
                        head_entity,
                        relation_dict[relation_english_sigleon],
                        tail_entity,
                        text
                    ]
                )
    # 存在尾实体重叠关系情况
    elif isOVE(id2BIO) == 2:
        # relation = get_OVE_RELATION(id2BIO, text, "B-OVE-T", "I-OVE-T")
        tail_entity_start = get_idx(id2BIO, "B-OVE-T")
        tail_entity_end = get_idx_last(id2BIO, tail_entity_start, "I-OVE-T")
        tail_entity = text[tail_entity_start : tail_entity_end + 1]
        for idx in range(len(id2BIO)):
            if id2BIO[idx] in head_data:
                global m
                head = "I" + id2BIO[idx][1:]
                for m in range(idx + 1, len(id2BIO)):
                    if head == id2BIO[m]:
                        continue
                    else:
                        break
                head_entity = text[idx:m]
                relation_english_sigleon = id2BIO[idx][2:-2]
                relation.append(
                    [
                        head_entity,
                        relation_dict[relation_english_sigleon],
                        tail_entity,
                        text
                    ]
                )
    # 没有重叠关系
    else:
        # 考虑[[37, 38, 0, 39, 40, 40, 40, 0, 39, 40, 40, 40, 0, 39, 40, 0, 0, 0]]
        # 能够正确识别  但是没有将重叠关系识别为OVE
        """
        在单元可靠性是时间t的函数时，若所有单元的寿命都服从指数分布，则式中：λi——第z个单元的故障率(1/h);λs——产品的故障率(1/h)。
        [['可靠性', '作用或影响关系', '时间']]

        飞机由起落装置、机身、机翼组成。
        [['飞机', '组成关系', '起落装置'], ['飞机', '组成关系', '机翼']]
        这种情况就是重叠关系，但是没有识别成重叠关系，解码的时候可以根据这种情况进行设计。
        """
        head_list = []
        head_entity_chinese = []

        tail_list = []
        tail_entity_chinese = []
        for idx in range(len(id2BIO)):
            if id2BIO[idx] in head_data:
                head_list.append(id2BIO[idx])
                head = "I" + id2BIO[idx][1:]
                global kk
                for kk in range(idx + 1, len(id2BIO), 1):
                    if head == id2BIO[kk]:
                        continue
                    else:
                        break
                head_entity_chinese.append(text[idx:kk])
            if id2BIO[idx] in tail_data:
                tail_list.append(id2BIO[idx])
                tail = "I" + id2BIO[idx][1:]
                global pp
                for pp in range(idx + 1, len(id2BIO), 1):
                    if tail == id2BIO[pp]:
                        continue
                    else:
                        break
                tail_entity_chinese.append(text[idx:pp])

        for i in range(len(head_list)):
            rel_head = head_list[i][2:-2]
            for j in range(len(tail_list)):
                rel_tail = tail_list[j][2:-2]
                if rel_head == rel_tail:
                    relation.append(
                        [
                            head_entity_chinese[i],
                            relation_dict[rel_head],
                            tail_entity_chinese[j],
                            text
                        ]
                    )
    return relation


"""
查找str在id2BIO中的位置
"""


def get_idx(id2BIO, char):
    for idx in range(len(id2BIO)):
        if id2BIO[idx] == char:
            return idx
    return -1


def get_idx_last(id2BIO, start, char):
    global idx
    for idx in range(start + 1, len(id2BIO)):
        if id2BIO[idx] == char:
            continue
        else:
            break
    return idx - 1


def format_result(result, text, tag):
    entities = []
    print(result)
    print(text)
    print(tag)
    for i in result:
        begin, end = i
        entities.append(
            {
                "start": begin,
                "stop": end + 1,
                "word": text[begin : end + 1],
                "type": tag,
            }
        )
    return entities


def get_tags(path, tag, tag_map):
    print(path)
    print(tag)
    print(tag_map)
    begin_tag = tag_map.get("B-" + tag)
    mid_tag = tag_map.get("I-" + tag)
    end_tag = tag_map.get("E-" + tag)
    single_tag = tag_map.get("S")
    o_tag = tag_map.get("O")
    begin = -1
    end = 0
    tags = []
    last_tag = 0
    for index, tag in enumerate(path):
        if tag == begin_tag and index == 0:
            begin = 0
        elif tag == begin_tag:
            begin = index
        elif tag == end_tag and last_tag in [mid_tag, begin_tag] and begin > -1:
            end = index
            tags.append([begin, end])
        elif tag == o_tag or tag == single_tag:
            begin = -1
        last_tag = tag
    return tags

import operator
from tqdm import tqdm
def f1_score(input_str, pre_result, rel_result):
    origin = 0.0
    found = 0.0
    right = 0.0
    if len(rel_result) != 0:
        origin = len(rel_result)
    if len(pre_result) != 0:
        found = len(pre_result)

    for rel_relation in rel_result:
        for pre_relation in pre_result:
            if operator.eq(pre_relation, rel_relation):
                right += 1

    recall = 0.0 if origin == 0 else (right / origin)
    precision = 0.0 if found == 0 else (right / found)
    f1 = (
        0.0
        if recall + precision == 0
        else (2 * precision * recall) / (precision + recall)
    )

    pbar = tqdm()
    pbar.update()
    pbar.set_description(
        'f1: %.5f, precision: %.5f, recall: %.5f' % (f1, precision, recall)
    )
    # print(
    #     "\t{}\trecall {:.2f}\tprecision {:.2f}\tf1 {:.2f}".format(
    #         input_str, recall, precision, f1
    #     )
    # )
    return recall, precision, f1