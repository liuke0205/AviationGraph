# -*- coding: utf-8 -*-
import json

from AviationGraph.bm25data import similarity
from django.contrib import messages
from django.shortcuts import render, redirect
import jieba.posseg as pseg
import codecs
from AviationGraph.utils.pre_load import neo4jconn
import redis

stop_words = 'AviationGraph/sourceFile/stopword.txt'
stopwords = codecs.open(stop_words, 'r', encoding='utf8').readlines()
stopwords = [w.strip() for w in stopwords]
stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']

def toAnswer(request):
    return render(request, "application/answer.html")


def answer_question(request):
    if request.POST:
        question = request.POST.get('question')
        request.session['s_question'] = question

        if question is None:
            messages.success(request, "问题为空，请重新输入问题！")
            return redirect('/application/toAnswer/')
        else:
            try:
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                answer = r.get(question)
                if answer is not None:
                    print("通过缓存查出答案")
                    ctx = {'title': '<h1>通过缓存查出答案，没有查询路径图！</h1>'}
                    return render(request, "application/answer.html", {'ctx': ctx, 'answer': r.get(question), 'question': question})
            except Exception:
                messages.success(request, "Redis异常，请检查！")

            file_corpus = 'AviationGraph/bm25data/QA.txt'
            # result_list = [最相似问题， 最相似问题的得分，第二相似问题，第二相似问题的得分]
            result_list = similarity.initbm(question, file_corpus)
            # 判断最相似问题的得分是否为0
            if float(result_list[1]) == 0:
                messages.success(request, "抱歉，暂时还不能给您一个完美的答案！")
                return redirect('/application/toAnswer/')
            else:
                template_question = result_list[0]
                # 1.首先匹配到规则问题属于哪一类问题
                row_id = match_template(template_question, file_corpus)
                if row_id == -1:
                    raise RuntimeError('出现程序错误！')
                # 2.从原问题中根据规则问题 找出关键字（升级版本：进行实体识别）
                words = pseg.cut(question)  # 词性标注
                result = []
                for word, flag in words:
                    if flag not in stop_flag and word not in stopwords:
                        result.append(word)
                print(row_id)
                print(result)
                # 3.根据问题类别+关键字 搜索Neo4j数据库
                answer, searchResult = getAnswer(row_id, result)
                print(answer)
                #如果neo4j数据库中没有答案，那么返回一句话
                if answer is True:
                    messages.success(request, "抱歉，暂时还不能给您一个完美的答案！")
                    return redirect('/application/toAnswer/')
                # 5.将问题缓存到Redis数据库
                try:
                    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                    # 将question的答案进行缓存，并且设置60分钟的失效时间
                    r.set(question, answer, 60)
                except Exception:
                    messages.success(request, "Redis异常，请检查！")
                print(searchResult)
                if (len(searchResult) > 0):
                    return render(request, 'application/answer.html',
                                  {'answer': answer, 'question': question, 'searchResult': json.dumps(searchResult, ensure_ascii=False)})

#查找问题所在的行号
def match_template(question, file_corpus):
    question_list = codecs.open(file_corpus, 'r', encoding='utf8').readlines()
    for i in range(len(question_list)):
        if question_list[i] == question:
            return i
    return -1

#根据问题模板的行号 + 分词结果 得到图数据库的信息
def getAnswer(row_id, result):
    db = neo4jconn
    # 别名关系
    if row_id >= 0 and row_id <= 1:
        answer, answer2 = db.findAliasName(result[0], "别名关系")
        print(type(answer), "000000")
        print(answer)
        if answer is None or len(answer) == 0:
            return True, []
        else:
            return_res = answer[0]['n1.name'] + "的别名是：" + answer[0]['alias.name'] + "。"
            return return_res, answer2

    # 组成关系
    elif row_id > 1 and row_id <= 2:
        answer, answer2 = db.findComposition(result[0], "组成关系")
        if len(answer) < 1:
            return True, []
        else:
            return_res = result[0] + "由"
            for data in range(len(answer) - 1):
                return_res = return_res + answer[data]['n.name'] + "、"
            return return_res + answer[len(answer) - 1]['n.name'] + "组成。", answer2

    # 定义关系
    elif row_id > 2 and row_id <= 3:
        answer, answer2 = db.findDefinition(result[0], "定义关系")
        if len(answer) < 1:
            return True, []
        else:
            return answer[0]['n1.name'] + "可以定义为：" + answer[0]['n.name'], answer2

    '''
    其他关系模板
    '''