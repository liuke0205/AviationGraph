import json

def load_data(filename):
    """加载数据
    单条格式：{'text': text, 'spo_list': [(s, p, o)]}
    """
    D = []
    with open(filename,"r", encoding='utf-8') as f:
        for l in f:
            print(l)
            print(type(l))
            l = json.loads(l)
            D.append({
                "text": l["text"],
                "spo_list": [(spo["subject"], spo["predicate"], spo["object"])
                             for spo in l["spo_list"]]
            })
    return D

def text2label(text_label, predicate, s_start, s_end, predicate1, o_start, o_end):
    text_label[s_start] = "B-" + predicate + "-H"
    for idx in range(s_start+1, s_end):
        text_label[idx] = "I-" + predicate + "-H"

    text_label[o_start] = "B-" + predicate1 + "-T"
    for idx in range(o_start + 1, o_end):
        text_label[idx] = "I-" + predicate1 + "-T"
    return text_label

def json2label(origin_data, filename):
    f = open('./out/' + filename, 'w', encoding='utf-8')
    for data in origin_data:
        text, spo_list = data["text"], data["spo_list"]
        subject_dict, object_dict = dict(), dict()

        for spo in spo_list:
            subject, object = spo[0], spo[2]
            if subject in subject_dict:
                subject_dict[subject] = subject_dict[subject] + 1
            else:
                subject_dict[subject] = 1

            if object in object_dict:
                object_dict[object] = object_dict[object] + 1
            else:
                object_dict[object] = 1

        text_label = []
        # 对标签序列初始化为O
        for idx in range(len(text)):
            text_label.append("O")

        for subject in subject_dict.keys():
            for spo in spo_list:
                if spo[0] == subject:
                    object, predicate = spo[2], spo[1]

                    s_start = text.find(subject)
                    s_end = s_start + len(subject)

                    o_start = text.find(object)
                    o_end = o_start + len(object)

                    # 如果头实体只有一个
                    if subject_dict[subject] == 1:
                        # 如果尾实体也只有一个，那么不存在重叠关系，直接正常标注
                        if object_dict[object] == 1:
                            text_label = text2label(text_label, predicate, s_start, s_end, predicate, o_start, o_end)
                        # 如果尾实体的个数大于1，那么说明尾实体是重叠实体，需要将尾实体的关系设置为OVE
                        else:
                            text_label = text2label(text_label, predicate, s_start, s_end, "OVE", o_start, o_end)
                    else:
                        # 直接将头实体的关系标注为OVE，尾实体默认个数为1，不去考虑尾实体也对应多个的情况
                        text_label = text2label(text_label, "OVE", s_start, s_end, predicate, o_start, o_end)
        # s = json.dumps(
        #     {
        #         "text": text,
        #         "label": text_label,
        #         "spo_list":spo_list
        #     },
        #     ensure_ascii=False,
        #     indent=4
        # )
        # f.write(s + "\n")
        for idx in range(len(text)):
            f.write(text[idx] + " " + text_label[idx] + "\n")
        f.write("end" + "\n")
    f.close()


if __name__ == '__main__':
    # # 加载数据集
    # train_data = load_data('../origin_data/train_data.json')
    # valid_data = load_data('../origin_data/dev_data.json')
    # #将训练集根据标注策略转换成可用的数据
    # json2label(train_data, "train.txt")
    # #将测试集根据标注策略转换成可用的数据
    # json2label(valid_data, "dev.txt")


    train_data = load_data('./out/train_json.json')
    json2label(train_data, "train.txt")

else:
    pass