# -*- coding: utf-8 -*-
import math

from AviationGraph.Text_Classification.src.model import TextCNN


def generate_dataset(x, res_list):
    filename = "train" + str(x) + ".txt"
    #生成前x%的数据集
    with open("F:\\01-科研资料\\03-项目工程\\AviationGraph\\AviationGraph\\Text_Classification\\result\\" + filename, "w", encoding='utf-8') as f:
        for key, value in res_list[0:len(res_list) * x // 100]:
            f.write(str(key).replace('。', '') + "\n")

if __name__ == '__main__':
    CNN_model = TextCNN()
    CNN_model.train(200)
    result_list, sentence_list = CNN_model.predict("F:\\01-科研资料\\03-项目工程\\AviationGraph\\AviationGraph\\Text_Classification\\data\\sentence.txt")
    score_list = []
    for result in result_list:
        sum = 0
        for data in result:
            num_list = data.tolist()
            for num in num_list:
                if num > 0:
                    sum = sum - num * math.log2(num)
        score_list.append(float(sum))

    # 将文本 和 信息熵封装成字典
    d = dict(zip(sentence_list, score_list))
    res_list = sorted(d.items(), key=lambda x: x[1], reverse=True)
    for idx in [1, 2, 3, 4, 5, 6]:
        generate_dataset(idx * 10, res_list)