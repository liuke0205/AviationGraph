import codecs

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
import jieba
from AviationGraph.utils.pre_load import neo4jconn

stop_words = 'AviationGraph/sourceFile/stopword.txt'
stopwords = codecs.open(stop_words, 'r', encoding='utf8').readlines()
stopwords = [w.strip() for w in stopwords]
stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']

def GetWordCloud():
    cut_text = ""
    db = neo4jconn
    entity_list = db.findAllEntityNoLimit()
    for data in entity_list:
        cut_text = cut_text + " ".join(jieba.cut(data['n.name']))
        # cut_text.append(data['n.name'])
    # cut_text = " ".join(cut_text)

    for f in corpus_data:
        words = pseg.cut(f)  # 词性标注
        result = []
        for word, flag in words:
            if flag not in stop_flag and word not in stopwords:
                result.append(word)
        corpus.append(result)


    print(cut_text)

    # path_txt = 'E:/硕士毕业论文/04-项目工程/AviationGraph/AviationGraph/DeepLearning/data/train2.txt'
    # # 结巴分词，生成字符串，如果不通过分词，无法直接生成正确的中文词云,感兴趣的朋友可以去查一下，有多种分词模式
    # # Python join() 方法用于将序列中的元素以指定的字符连接生成一个新的字符串。
    # f = open(path_txt, 'r', encoding='UTF-8').read()
    # cut_text = " ".join(jieba.cut(f))
    # print(cut_text)


    path_img = "E:/硕士毕业论文/04-项目工程/AviationGraph/static/img/wordCloud.png"
    background_image = np.array(Image.open(path_img))

    wordcloud = WordCloud(
        # 设置字体，不然会出现口字乱码，文字的路径是电脑的字体一般路径，可以换成别的
        font_path="C:/Windows/Fonts/simfang.ttf",
        background_color="white",
        # mask参数=图片背景，必须要写上，另外有mask参数再设定宽高是无效的
        mask=background_image).generate(cut_text)
    # 生成颜色值
    image_colors = ImageColorGenerator(background_image)
    # 下面代码表示显示图片
    plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    plt.savefig("examples.jpg")  # 必须在plt.show之前，不是图片空白
    plt.show()


if __name__ == '__main__':
    GetWordCloud()