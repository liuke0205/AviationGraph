import jieba
import math


def run(s1, s2):
    # s1 = "周杰伦是一个歌手,也是一个叉叉"
    # s2 = "周杰伦不是一个叉叉，但是是一个歌手"

    s1_list = [x for x in jieba.cut(s1, cut_all=True) if x != '']
    s2_list = [x for x in jieba.cut(s2, cut_all=True) if x != '']
    s1_set = set(s1_list)
    s2_set = set(s2_list)
    word_dict = dict()
    i = 0
    for word in s1_set.union(s2_set):
        word_dict[word] = i
        i += 1

    # 词频向量化函数
    def word_to_vec(word_dict, lists):
        word_count = dict()
        result = [0] * len(word_dict)
        for word in lists:
            if word_count.get(word, -1) == -1:
                word_count[word] = 1
            else:
                word_count[word] += 1
        for word, freq in word_count.items():
            wid = word_dict[word]
            result[wid] = freq
        return result

    # 计算2个向量的余弦相似度
    def cos_dist(a, b):
        if len(a) != len(b):
            return None
        part_up = 0.0
        a_sq = 0.0
        b_sq = 0.0
        for a1, b1 in zip(a, b):
            part_up += a1 * b1
            a_sq += a1 ** 2
            b_sq += b1 ** 2
        part_down = math.sqrt(a_sq * b_sq)
        if part_down == 0.0:
            return None
        else:
            return part_up / part_down

    s1_vec = word_to_vec(word_dict, s1_list)
    s2_vec = word_to_vec(word_dict, s2_list)
    num = cos_dist(s1_vec, s2_vec)
    return num


def similarity(target_text, all_text_list):
    all_text_list.append(target_text)
    result_list = []
    for other in all_text_list:
        sim = run(target_text, other)
        result_list.append(sim)
    return result_list


if __name__ == '__main__':
    similarity("", [])
