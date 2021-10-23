from AviationGraph.utils.bm25data import similarity
from django.contrib import messages
from django.shortcuts import render, redirect

from AviationGraph.utils.MySqlConn import MySqlConn


def toAnswer(request):
    return render(request, "application/answer.html")


def simqa(question, file_corpus):
    list = similarity.initbm(question, file_corpus)
    print(type(list[1]))
    print(list)
    if list[1] == 0:
        return -10000
    quest = list[0].strip()
    # 连接mysql数据库
    conn = MySqlConn("source").connectMySql()
    cursor = conn.cursor()

    sql = "select * from fault where phenomenon = '%s'" % (quest)
    count = cursor.execute(sql)
    result_list = []
    if count != 0:
        for i in range(count):
            result = cursor.fetchone()
            result_list.append(result)
    # 将查询结果转换成列表存储
    return result_list[0]


def answer_question(request):
    if request.POST:
        question = request.POST.get("question", None)
        request.session["s_question"] = question

        print(question)
        if question:
            file_corpus = "AviationGraph/utils/bm25data/故障信息.txt"
            bm25 = simqa(question, file_corpus)
            if bm25 == -10000:
                messages.success(request, "抱歉没有答案！")
                return redirect("/application/toAnswer/")

            """将问题插入数据库表中"""
            conn = MySqlConn("source").connectMySql()
            cursor = conn.cursor()
            insert_sql = (
                "INSERT INTO answer_score(s_question, s_score) VALUES('%s',%s)"
                % (question, 1.0)
            )
            cursor.execute(insert_sql)
            conn.commit()
            select_sql = "SELECT id FROM answer_score ORDER BY id DESC LIMIT 1"
            cursor.execute(select_sql)
            conn.commit()
            result = cursor.fetchone()
            id = result[0]
            request.session["id"] = id
            request.session["bm25"] = bm25
            sql_select = "SELECT * FROM answer_score"
            cnt = cursor.execute(sql_select)
            conn.commit()
            score = 0
            for data in range(cnt):
                temp = cursor.fetchone()[2]
                score += float(temp)
            accuracy_rate = 0
            if cnt > 0:
                accuracy_rate = round(score / cnt * 100, 2)
            else:
                accuracy_rate = 0
            score = round(score, 3)

            return render(
                request,
                "application/answer.html",
                {
                    "question_sum": cnt,
                    "score": score,
                    "accuracy_rate": accuracy_rate,
                    "answer": bm25,
                    "question": question,
                },
            )
        else:
            messages.success(request, "问题为空！")
            return redirect("/application/toAnswer/")


# 点击错误按钮更改分数
def answer_error(request):
    conn = MySqlConn("source").connectMySql()
    cursor = conn.cursor()
    s_question = request.session.get("s_question")
    update_sql = (
        "update source.answer_score set s_score = 0.0 WHERE id = '%s'"
        % request.session.get("id")
    )
    cursor.execute(update_sql)
    conn.commit()
    toAnswer(request)
    return render(
        request,
        "application/answer.html",
        {
            "question_sum": request.session.get("question_sum"),
            # "score": request.session.get('score'),
            "accuracy_rate": request.session.get("accuracy_rate"),
            "answer": request.session.get("bm25"),
        },
    )


# 点击正确按钮
def answer_right(request):
    toAnswer(request)
    return render(
        request,
        "application/answer.html",
        {
            "question_sum": request.session.get("question_sum"),
            "accuracy_rate": request.session.get("accuracy_rate"),
            "answer": request.session.get("bm25"),
            "question": request.session["s_question"],
        },
    )
