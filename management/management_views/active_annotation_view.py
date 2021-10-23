import csv
import os
import re
import threading
import docx
import math


from django.contrib import messages
from django.shortcuts import render, redirect
from AviationGraph.utils.MySqlConn import MySqlConn
from application.models import Log, Annotation, User, Dictionary, Temp, Relation
from AviationGraph.Text_Classification.src.model import TextCNN
from AviationGraph.utils.cosine_similarity import similarity
from AviationGraph.utils.snowFlake import IdWorker



# 跳转到文本标注页面
def toActiveAnnotation(request):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "SELECT count(*) FROM active_annotation"
    cursor.execute(sql)
    conn.commit()
    count = cursor.fetchone()
    return render(request, 'management/active_annotation.html', {"count": count[0]})


# 上传文件，并且将数据保存到数据库中
def activeAnnotationUpload(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')

        str_filename = str(path)
        if str_filename.endswith(".docx") or str_filename.endswith(".doc"):
            if path:
                with open('upload_file/active_annotation/active_annotation_word.docx', 'wb+') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)
                # 获取当前用户的id
                user = User.objects.get(username="admin")
                user_id = user.user_id

                new_data = []
                file = docx.Document("upload_file/active_annotation/active_annotation_word.docx")
                for p in file.paragraphs:
                    data = p.text.replace('\n', '').replace('\t', '')
                    new_data.append(data)
                all_word = "".join(new_data).replace(" ", "")

                pattern = r'。|！'
                senetence_list = re.split(pattern, str(all_word))
                new_senetence_list = []
                for data in senetence_list:
                    if len(data) > 0:
                        new_senetence_list.append(data + "。\n")

                if os.path.isfile("upload_file/active_annotation/test.txt"):
                    os.remove("upload_file/active_annotation/test.txt")

                # 将上传的文件，分句后存到txt文件中，作为分类模型的测试数据
                with open("upload_file/active_annotation/test.txt", "w", encoding="utf8") as f:
                    for senetence in new_senetence_list:
                        f.write(senetence)
                f.close()

                #调用深度学习模型->预测所有数据分类的概率
                file_path = "F:\\01-科研资料\\03-项目工程\\AviationGraph\\upload_file\\active_annotation\\test.txt"
                # 开启一个线程 将结果保存到xlsx文件中
                thread1 = myThread(1, "Thread-1", file_path)
                thread1.start()

                # 读取完毕后，删除word文件
                if os.path.isfile("upload_file/active_annotation/active_annotation_word.docx"):
                    os.remove("upload_file/active_annotation/active_annotation_word.docx")

                messages.success(request, "上传成功！")

                #第一次预测结束后，向用户推送一条待标注数据
                #跳转到 向管理员推荐下一条待标注的数据
                return redirect('/management/recommendNextData/')
            else:
                messages.success(request, "文件为空！")
                return redirect('/management/toActiveAnnotation/')
        else:
            messages.success(request, "上传失败，请上传Word文件！")
            return redirect('/management/toActiveAnnotation/')


categories = ['别名关系', '定义关系', '参照关系', '上下位关系', '使用关系', '位置关系', '性能提升关系', '性能需求关系', '选型关系', '组成关系',
                            '作用或影响关系']

# 将抽取结果写入到excel文件的线程
class myThread (threading.Thread):
    def __init__(self, threadID, name, file_path):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.file_path = file_path
    def run(self):
        print("开始线程，去写入文件：" + self.name)
        CNN_model = TextCNN()
        result_list, sentence_list = CNN_model.predict(self.file_path)
        score_list = []
        for result in result_list:
            sum = 0
            for data in result:
                num_list = data.tolist()
                for num in num_list:
                    if num > 0:
                        sum = sum - num * math.log2(num)
            score_list.append(float(sum))

        #将文本 和 信息熵封装成字典
        d = dict(zip(sentence_list, score_list))
        #将字典按照信息熵降序排列
        # sorted(d.items(), key=lambda x: x[1], reverse=True)
        #将排序好的待标注数据存放到mysql数据库中
        # 下面代码作用：根据字段创建表，根据数据执行插入语句
        conn = MySqlConn('source').connectMySql()
        cursor = conn.cursor()
        for key, value in d.items():
            insert_sql = "INSERT INTO active_annotation(text,score) VALUES('%s','%s')" % (
                key.replace("-", "").replace("'", ""), value
            )
            print(insert_sql)
            cursor.execute(insert_sql)
        conn.commit()

        print("退出线程，结束写文件：" + self.name)


# 向管理员推荐下一条待标注的数据
def recommendNextData(request):
    if request.method == 'POST':
        conn = MySqlConn('source').connectMySql()
        cursor = conn.cursor()
        #检查relation_list是否有数据，如果有数据将其存到已标注数据库表中(corpus)
        relation_list = request.session.get('relation_list')
        if relation_list is not None:
            for data in relation_list:
                insert_sql = "INSERT INTO corpus(head_entity, tail_entity, relation, text) VALUES('%s','%s', '%s','%s')" % (
                    data[0], data[2], data[4], data[5]
                )
                cursor.execute(insert_sql)
            conn.commit()

        sql = "SELECT count(*) FROM active_annotation"
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchone()
        count = data[0]
        recommend_text = ""

        if count == 0:
            messages.success(request, "当前没有待标注的数据！")
            return render(request, 'management/text_annotation.html',
                          {"current_text": recommend_text, 'count': 0})

        select_sql = "SELECT text FROM active_annotation ORDER BY score DESC LIMIT 1"
        cursor.execute(select_sql)
        # 返回第一条数据即可（信息熵最大的那条数据）
        data = cursor.fetchone()
        conn.commit()
        recommend_text = data[0]

        # 推荐完之后，这条待标注语句就要删除
        delete_sql = "delete from active_annotation where text = '%s'" % (recommend_text)
        cursor.execute(delete_sql)
        conn.commit()

        '''
        使用相似度算法去除和 本次推荐的待标注数据相似度达到阈值的数据
        '''
        all_text_list = []
        sql = "SELECT text FROM active_annotation"
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()

        for d in data:
            all_text_list.append(d[0])

        # 开启一个线程 计算推荐文本的相似度并且去除相似度达到阈值的数据
        thread1 = simThread(1, "Thread-1", recommend_text, all_text_list)
        thread1.start()

        '''
        判断是否需要重新训练模型
        '''


        #设置session域
        request.session['recommend_text'] = recommend_text
        request.session['relation_list'] = []
        request.session['count'] = count

        return render(request, 'management/active_annotation.html', {"current_text": recommend_text, "count": count, "resultList" : []})



# 开启一个新的线程去计算相似度，并且删除相似的数据
class simThread (threading.Thread):
    def __init__(self, threadID, name, target_text, all_text_list):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.target_text = target_text
        self.all_text_list = all_text_list
    def run(self):
        print("开始线程，计算相似度：" + self.name)
        # 调用相似度计算算法，得到本次推荐的文本 和 所有文本的相似度
        sim_list = similarity(self.target_text, self.all_text_list)
        for idx in range(len(sim_list)):
            if sim_list[idx] > 0.5:
                conn = MySqlConn('source').connectMySql()
                cursor = conn.cursor()
                # 推荐完之后，这条待标注语句就要删除
                delete_sql = "delete from active_annotation where text = '%s'" % (self.all_text_list[idx])
                print(delete_sql)
                cursor.execute(delete_sql)
                conn.commit()
        print("退出线程，相似度计算结束：" + self.name)


# 增加一条标注信息
def addAnnotation(request):
    new_headEntity = request.POST.get('headEntity')
    new_headEntityType = request.POST.get('headEntityType')
    new_tailEntity = request.POST.get('tailEntity')
    new_tailEntityType = request.POST.get('tailEntityType')
    new_relationshipCategory = request.POST.get('relationshipCategory')


    relation_list = request.session.get('relation_list')
    recommend_text = request.session.get('recommend_text')
    count = request.session.get('count')

    snowWorker = IdWorker(1, 1)
    id = snowWorker.get_id()
    print(id)
    relation_list.append([new_headEntity, new_headEntityType, new_tailEntity, new_tailEntityType, new_relationshipCategory, recommend_text, id])
    request.session['relation_list'] = relation_list

    return render(request, 'management/active_annotation.html',
                  {"current_text": recommend_text, "count": count, "resultList": relation_list})


def deleteAnnotation(request):
    id = request.GET.get('id')
    recommend_text = request.session.get('recommend_text')
    count = request.session.get('count')
    relation_list = request.session.get('relation_list')
    for idx in range(len(relation_list)):
        relation = relation_list[idx]
        if str(relation[5]) == str(id):
            del relation_list[idx]
            break

    request.session['relation_list'] = relation_list
    return render(request, 'management/active_annotation.html',
                  {"current_text": recommend_text, "count": count, "resultList": relation_list})


def modifyAnnotation(request):
    recommend_text = request.session.get('recommend_text')
    count = request.session.get('count')
    relation_list = request.session.get('relation_list')

    id = request.POST.get('id')
    headEntity = request.POST.get('headEntity')
    headEntityType = request.POST.get('headEntityType')
    tailEntity = request.POST.get('tailEntity')
    tailEntityType = request.POST.get('tailEntityType')
    relationshipCategory = request.POST.get('relationshipCategory')


    for idx in range(len(relation_list)):
        relation = relation_list[idx]
        if str(relation[5]) == str(id):
            relation[0] = headEntity
            relation[1] = headEntityType
            relation[2] = tailEntity
            relation[3] = tailEntityType
            relation[4] = relationshipCategory
            break

    request.session['relation_list'] = relation_list
    return render(request, 'management/active_annotation.html',
                  {"current_text": recommend_text, "count": count, "resultList": relation_list})