import math
from six import iteritems
from six.moves import xrange
import jieba.posseg as pseg
import codecs

stop_words = 'AviationGraph/sourceFile/stopword.txt'
stopwords = codecs.open(stop_words, 'r', encoding="utf-8").readlines()
stopwords = [w.strip() for w in stopwords]
stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']

# BM25 parameters.
PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25

#数据处理
class DataProcess(object):
    def __init__(self, file_corpus):
        self.file_corpus = file_corpus
        self.corpus_data = self.load_corpus()

    def load_corpus(self):
        input_data = codecs.open(self.file_corpus, 'r', encoding="utf-8")
        return input_data.readlines()

    def preproccess(self):
        corpus = []
        for f in self.corpus_data:
            words = pseg.cut(f)  # 词性标注
            result = []
            for word, flag in words:
                if flag not in stop_flag and word not in stopwords:
                    result.append(word)
            corpus.append(result)
        return corpus

#计算相似度
class BM25(object):

    def __init__(self, corpus):
        self.corpus_size = len(corpus)
        self.avgdl = sum(map(lambda x: float(len(x)), corpus)) / self.corpus_size   #文档平均长度
        self.corpus = corpus
        self.f = []  #列表的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数
        self.df = {}  #储存每个词以及该词出现的次数
        self.idf = {}  #储存每个词的idf值
        self.initialize() #idf

    def initialize(self):
        for document in self.corpus:
            frequencies = {}
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.f.append(frequencies)

            for word, freq in iteritems(frequencies):  #iteritems()返回一个迭代器
                if word not in self.df:
                    self.df[word] = 0
                self.df[word] += 1

        for word, freq in iteritems(self.df):
            self.idf[word] = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)


    def get_score(self, document, index, average_idf):
        score = 0
        for word in document:
            if word not in self.f[index]:
                continue
            idf = self.idf[word] if self.idf[word] >= 0 else EPSILON * average_idf
            score += (idf * self.f[index][word] * (PARAM_K1 + 1)
                      / (self.f[index][word] + PARAM_K1 * (1 - PARAM_B + PARAM_B * self.corpus_size / self.avgdl)))
        return score

    def get_scores(self, document, average_idf):
        scores = []
        for index in xrange(self.corpus_size):
            score = self.get_score(document, index, average_idf)
            scores.append(score)

        return scores


def initbm(question, file_corpus):
    data = DataProcess(file_corpus).preproccess()
    query = []
    q_words = pseg.cut(question)  # 词性标注
    for word, flag in q_words:
        if flag not in stop_flag and word not in stopwords:
            query.append(word)
    bm25 = BM25(data)
    average_idf = sum(map(lambda k: float(bm25.idf[k]), bm25.idf.keys())) / len(bm25.idf.keys())

    scores = bm25.get_scores(query, average_idf)

    file = DataProcess(file_corpus).load_corpus()
    print(scores)
    result = dict(zip(file, scores))

    res = (sorted(result.items(), key=lambda kv: kv[1], reverse=True))
    list = [res[0][0], res[0][1], res[1][0], res[1][1]]
    print(list)
    return list