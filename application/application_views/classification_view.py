# -*- coding: utf-8 -*-
import datetime
import os

import jieba
import xlrd
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect
from sklearn.feature_extraction.text import TfidfVectorizer

from AviationGraph.utils.MySqlConn import MySqlConn

##跳转到分类信息下载界面
from AviationGraph.utils.utils import db2txt
from AviationGraph.bm25data import similarity
from AviationGraph.utils.utils import write_excel_xls



# 下载所有的训练集
def download_classication_file(request):
    # 1.读取训练集
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "select * from classication_train"
    cnt = cursor.execute(sql)
    res = []
    for i in range(cnt):
        data = cursor.fetchone()
        res.append([data[0], data[1], data[2], data[3]])

    if os.path.isfile("download_file/classication_data.xls"):
        os.remove("download_file/classication_data.xls")

    # 2.将训练集数据写入到classication_data.xlsx表   覆盖形式
    write_excel_xls("download_file/classication_data.xls", "classication_data", res)

    file = open('download_file/classication_data.xls', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="classication_data.xls"'
    return response


def excelAddMysql_test(path):
    #################2021.5.28：将excel中的故障信息添加到classication_test表中
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    drop_table = "delete from classication_test"
    cursor.execute(drop_table)
    conn.commit()
    cursor = conn.cursor()
    with open('upload_file/classication/classication_test.xlsx', 'wb+') as destination:
        for chunk in path.chunks():
            destination.write(chunk)
    # 下面代码作用：获取到excel中的字段和数据
    excel = xlrd.open_workbook("upload_file/classication/classication_test.xlsx")
    sheet = excel.sheet_by_index(0)
    row_number = sheet.nrows
    data_list = []
    for i in range(1, row_number):
        data_list.append(sheet.row_values(i))

    for data in data_list:
        sql = "INSERT INTO classication_test(故障现象,createtime) VALUES ('%s','%s')" % (data[0], datetime.datetime.now())
        cursor.execute(sql)
    conn.commit()
    conn.close()


def excelAddMysql_train(path):
    #################2021.5.28：将excel中的故障信息添加到classication_test表中
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    with open('upload_file/classication/classication_train.xlsx', 'wb+') as destination:
        for chunk in path.chunks():
            destination.write(chunk)
    # 下面代码作用：获取到excel中的字段和数据

    excel = xlrd.open_workbook("upload_file/classication/classication_train.xlsx")
    sheet = excel.sheet_by_index(0)
    row_number = sheet.nrows
    data_list = []
    for i in range(1, row_number):
        data_list.append(sheet.row_values(i))

    drop_table = "delete from classication_train"
    cursor.execute(drop_table)
    conn.commit()

    truncate_table = "truncate table classication_train"
    cursor.execute(truncate_table)
    conn.commit()

    drop_table = "delete from classication_mom"
    cursor.execute(drop_table)
    conn.commit()
    truncate_table = "truncate table classication_mom"
    cursor.execute(truncate_table)
    conn.commit()

    for data in data_list:
        sql = "INSERT INTO classication_train(故障现象,标签,解决方案,createtime) VALUES ('%s','%s','%s','%s')" % (
        data[0], data[1], data[2], datetime.datetime.now())
        cursor.execute(sql)
    conn.commit()
    cursor = conn.cursor()
    sql = "select * from classication_train"
    cnt = cursor.execute(sql)
    res = []
    for i in range(cnt):
        data = cursor.fetchone()
        if data[0] == int(data[2].split('同')[1]):
            print(int(data[2].split('同')[1]))
            print(data[1])
            res.append([data[2], data[1], data[3]])
    cursor = conn.cursor()
    for data in res:
        insert_sql = "INSERT INTO classication_mom(标签,故障现象,解决方案) VALUES ('%s','%s','%s')" % (data[0], data[1], data[2])
        cursor.execute(insert_sql)
    conn.commit()


def upload_classification_test_file(request):
    if request.method == 'POST':
        '''
        检查是否已经上传过训练数据
        '''
        conn = MySqlConn('source').connectMySql()
        cursor = conn.cursor()
        sql = "select * from classication_train"
        cnt = cursor.execute(sql)
        conn.commit()
        if cnt == 0:
            messages.success(request, "现在还没有训练数据，请先上传训练数据！")
            return redirect('/application/toClassification/')

        # 获取文件名
        path = request.FILES.get('test_file')
        str_filename = str(path)
        if str_filename.endswith(".xlsx") or str_filename.endswith(".xls"):
            if path:
                excelAddMysql_test(path)
                train_words_list = []
                train_labels = []

                conn = MySqlConn('source').connectMySql()
                cursor = conn.cursor()
                sql = "select * from classication_train"
                cnt = cursor.execute(sql)
                for i in range(cnt):
                    data = cursor.fetchone()
                    train_words_list.append(data[1])
                    train_labels.append(data[2])
                conn.commit()

                test_words_list = []
                sql2 = "select * from classication_test"
                cnt2 = cursor.execute(sql2)
                for i in range(cnt2):
                    data = cursor.fetchone()
                    test_words_list.append(data[0])

                train_words_list = cut_words(train_words_list)
                test_words_list = cut_words(test_words_list)

                stop_words = open('AviationGraph/sourceFile/stopword.txt', 'r', encoding='utf-8').read()
                stop_words = stop_words.encode('utf-8').decode('utf-8-sig')  # 列表头部\ufeff处理
                stop_words = stop_words.split('\n')  # 根据分隔符分隔

                # 计算单词权重
                tf = TfidfVectorizer(stop_words=stop_words, max_df=0.5)

                train_features = tf.fit_transform(train_words_list)
                # 上面fit过了，这里transform
                test_features = tf.transform(test_words_list)

                # 多项式贝叶斯分类器
                from sklearn.naive_bayes import MultinomialNB

                clf = MultinomialNB(alpha=0.001).fit(train_features, train_labels)
                predicted_labels = clf.predict(test_features)

                print(predicted_labels)
                print(len(predicted_labels))

                reason_list = []
                fault_list = []

                conn = MySqlConn('source').connectMySql()
                cursor = conn.cursor()

                for data in predicted_labels:
                    sql = "select * from classication_mom where 标签 = '%s'" % (data)
                    cursor.execute(sql)
                    select_data = cursor.fetchone()
                    reason_list.append(select_data[3])
                    fault_list.append(select_data[2])

                # 将故障现象存储到txt中
                db2txt()
                file_corpus = 'AviationGraph/bm25data/fault.txt'

                cursor = conn.cursor()

                recommend1 = []
                recommend2 = []
                recommend1_reason = []
                recommend2_reason = []
                recommend1_label = []
                recommend2_label = []

                for data in test_words_list:
                    list = similarity.initbm(data, file_corpus)
                    recommend1.append(list[0].replace('\n', '').replace('\r', ''))
                    sql = "select * from classication_mom where 故障现象 = '%s'" % (recommend1[-1])
                    cursor.execute(sql)
                    select_data = cursor.fetchone()
                    # print("----"+select_data[3])
                    recommend1_reason.append(select_data[3])
                    recommend1_label.append(select_data[1])
                    recommend2.append(list[2].replace('\n', '').replace('\r', ''))
                    sql = "select * from classication_mom where 故障现象 = '%s'" % (recommend2[-1])
                    cursor.execute(sql)
                    select_data = cursor.fetchone()
                    # print(select_data[3]+"________")
                    recommend2_reason.append(select_data[3])
                    recommend2_label.append(select_data[1])
                '''
                 对测试数据打标签
                 '''
                resultList_classification = []
                for i in range(len(test_words_list)):
                    resultList_classification.append(
                        [test_words_list[i], predicted_labels[i], reason_list[i], fault_list[i], recommend1[i],
                         recommend2[i], recommend1_reason[i], recommend2_reason[i], recommend1_label[i],
                         recommend2_label[i]])

                conn.commit()
                '''
                将resultList_classification存储到 classication_result_temp
                '''
                for data in resultList_classification:
                    cursor = conn.cursor()
                    insert_sql = "INSERT INTO classication_result_temp(故障现象,标签,解决方案,父_故障现象,推荐一,推荐二,推荐一解决方案,推荐二解决方案,推荐一标签,推荐二标签) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                 (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8],
                                  data[9])
                    cursor.execute(insert_sql)
                conn.commit()

                '''
                将分类好的数据进行导出
                '''
                from AviationGraph.utils.utils import write_excel_xls
                write_excel_xls("download_file/classication_data.xls", "classication_data", resultList_classification)
                conn.close()

                ##############################将分类结果写入新的表   classification_result，同时需要将标签对应的 解决方案插入进去
                return redirect('/application/display_classication_result/')
            else:
                messages.success(request, "文件为空，请重新上传！")
                return redirect('/application/toClassification/')
        else:
            messages.success(request, "上传失败，请上传Excel文件！")
            return redirect('/application/toClassification/')
    return redirect('/application/toClassification/')


def cut_words(list):
    """
    对文本进行切词
    :param file_path: txt文本路径
    :return: 用空格分词的字符串
    """
    resultlist = []
    for data in list:
        textcut = jieba.cut(data)
        text_with_spaces = ''
        for word in textcut:
            text_with_spaces += word + ' '
        resultlist.append(text_with_spaces)
    return resultlist


def upload_classification_train_file(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('train_file')
        print(path)
        if path:
            excelAddMysql_train(path)
            ### 故障现象  解决方案  标签
            messages.success(request, "训练数据上传成功！")
            return render(request, 'application/classification.html')
        else:
            messages.success(request, "文件为空，请重新上传！")
            return redirect('/application/toClassification/')


def jieba_tokenize(text):
    return jieba.lcut(text)


# 跳转到分类界面
def toClassification(request):
    username = request.session.get('username')
    return render(request, 'application/classification.html')


def confirmClassication(request):
    id = 0
    if request.method == 'GET':
        id = request.GET.get('id')
    else:
        id = request.POST.get('fault_id')

    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    sql = "select * from classication_result_temp where id = '%s'" % (id)
    cursor.execute(sql)
    data = cursor.fetchone()
    delete_sql = "delete from classication_result_temp where id = '%s'" % (id)
    cursor.execute(delete_sql)
    conn.commit()

    cursor = conn.cursor()
    insert_sql = "INSERT INTO classication_train(故障现象,标签,解决方案,createtime) VALUES ('%s','%s','%s','%s')" % (
    data[1], data[2], data[3], datetime.datetime.now())
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()
    return redirect('/application/display_classication_result/')


def confirmClassication_recommend(request):
    id = 0
    print(request.method)
    flag = 0
    id = request.POST.get('recommend_id')
    if id == None:
        flag = 1
        id = request.POST.get("recommend2_id")
    print(id)
    print(flag)

    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    sql = "select * from classication_result_temp where id = '%s'" % (id)
    cursor.execute(sql)
    data = cursor.fetchone()
    delete_sql = "delete from classication_result_temp where id = '%s'" % (id)
    cursor.execute(delete_sql)
    conn.commit()

    cursor = conn.cursor()
    if flag == 0:
        insert_sql = "INSERT INTO classication_train(故障现象,标签,解决方案,createtime) VALUES ('%s','%s','%s','%s')" % (
        data[1], data[9], data[7], datetime.datetime.now())
        print("flag=" + str(flag))
    else:
        insert_sql = "INSERT INTO classication_train(故障现象,标签,解决方案,createtime) VALUES ('%s','%s','%s','%s')" % (
        data[1], data[10], data[8], datetime.datetime.now())
        print("flag=" + str(flag))
    cursor.execute(insert_sql)
    conn.commit()
    conn.close()
    return redirect('/application/display_classication_result/')


def display_classication_result(request):
    #读取classification_result表
    resultList_classification = []
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "select * from classication_result_temp"
    cnt = cursor.execute(sql)
    if cnt == 0:
        messages.success(request, "没有待确认数据！")
        return redirect('/application/toClassification/')
    for i in range(cnt):
        data = cursor.fetchone()
        resultList_classification.append(data)
    return render(request, 'application/classification_result.html',
                  {'resultList_classification': resultList_classification})


def addReason(request):
    text = request.POST.get('text')
    reason = request.POST.get('reason')

    conn = MySqlConn('source').connectMySql()

    cursor = conn.cursor()
    sql = "select max(id) from classication_train"
    cnt = cursor.execute(sql)
    data = cursor.fetchone()
    id = data[0] + 1

    cursor = conn.cursor()
    insert_sql = "INSERT INTO classication_train(故障现象,标签,解决方案,createtime) VALUES ('%s','%s','%s','%s')" % (
        text, '同' + str(id), reason, datetime.datetime.now())
    cursor.execute(insert_sql)
    conn.commit()

    cursor = conn.cursor()
    insert_sql = "INSERT INTO classication_mom(标签,故障现象,解决方案) VALUES ('%s','%s','%s')" % ("同" + str(id), text, reason)
    cursor.execute(insert_sql)
    conn.commit()

    delete_sql = "delete from classication_result_temp where 故障现象 = '%s'" % (text)
    cursor.execute(delete_sql)
    conn.commit()

    return redirect('/application/display_classication_result/')