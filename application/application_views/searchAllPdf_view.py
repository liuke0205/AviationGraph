# -*- coding: utf-8 -*-
import datetime
import os
import re

import jieba
import pdfplumber
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import threading
import AviationGraph.utils.create_index
from AviationGraph.utils.MySqlConn import MySqlConn

'''
跳转到全文搜索界面
'''
def toSearchAllPdf(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'application/login.html')
    filename_list = list()
    # 连接mysql数据库
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "select file_name from upload_file"
    cnt = cursor.execute(sql)
    conn.commit()
    if cnt != 0:
        data = cursor.fetchone()
        filename_list.append(data[0])
    conn.close()
    return render(request, "application/searchAllPdf.html", {"filename_list": filename_list})

# 建立索引的线程
class myThread (threading.Thread):
    def __init__(self, threadID, name, path):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.path = path
    def run(self):
        print("开始线程：" + self.name)
        # 建立索引
        creat_index(self.path)
        print("退出线程：" + self.name)


@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        #将文件名转换成字符串
        str_filename = str(path)
        if str_filename.endswith(".pdf"):
            if path:
                file_path = str("upload_file/search/" + str(path))
                with open(file_path, 'wb') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)

                file_type = request.POST.get('file_type')
                user_name = request.session.get('username')
                # 连接mysql数据库
                conn = MySqlConn('source').connectMySql()
                cursor = conn.cursor()

                remote_dir = 'upload_file/search/'  # 服务器文件夹
                remote_path = remote_dir + str(path)  # 服务器文件路径

                sql = "INSERT INTO upload_file(file_name, file_road, create_time, username, file_type) VALUES ('%s','%s', '%s', '%s', '%s')" % (
                    path, remote_path, datetime.datetime.now(), user_name, file_type)
                cursor.execute(sql)
                conn.commit()
                # creat_index(path)
                conn.close()

                #开启一个线程去创建索引
                thread1 = myThread(1, "Thread-1", path)
                thread1.start()

                return redirect('/application/toSearchAllPdf/')
        else:
            messages.success(request, "上传失败，请上传PDF文件！")
            return redirect('/application/toSearchAllPdf/')

from AviationGraph.utils.create_index import filesearch, txt_write, is_title, del_punctuation, word_seg
def creat_index(filename):
    file_result = filesearch(filename)
    pdf_filename = file_result[1]  # 文档绝对路径
    file_id = file_result[0]  # 文档id
    file_type = file_result[2]  # 文档类型
    pdfreader = pdfplumber.open(pdf_filename)
    conn = MySqlConn('source').connectMySql()
    for pages in range(pdfreader.pages.__len__()):
        page_text = pdfreader.pages[pages]
        page_content = page_text.extract_text()
        if page_content is not None:
            txt_filename = txt_write(page_content)
            with open(txt_filename, "r", encoding='utf8') as f:
                for line in f.readlines():
                    location = 0  # 判断标题 0--不是标题 1--是标题
                    title = is_title(line)
                    if title:
                        location = 1
                    # 删除干扰
                    str_del1 = del_punctuation(line)
                    str_del2 = re.sub(r'cid\d', '', str_del1)
                    wordlist = word_seg(str_del2)  # 分词
                    for j in range(len(wordlist)):
                        # 页码 page_number   标题 location  关键词wordlist[j]
                        page_number = pages + 1
                        keywords = wordlist[j]
                        if wordlist[j].strip() == "":
                            continue
                        cursor = conn.cursor()
                        sql = "INSERT INTO index_table(id, keyword, page_number, location, file_type) VALUES ('%s','%s', '%s', '%s', '%s')" % (
                            file_id, keywords, page_number, location, file_type)
                        print(sql)
                        cursor.execute(sql)
                        conn.commit()
        else:
            pass
    conn.close()



def searchAllPdf(request):
    key = request.POST.get("keywords")
    if len(key) == 0 or key is None:
        messages.success(request, "请输入您要查询的内容再点击查询")
        return redirect("/application/toSearchAllPdf")
    else:
        jieba.load_userdict("AviationGraph/sourceFile/hkbk.dic")
        word_list = jieba.cut(key)
        result_list = list()
        for word in word_list:
            result = keywordsearch(word)
            for i in result:
                result_list.append(i)
        sort_list = result_sort(result_list)
        print(sort_list)
        res = []
        conn = MySqlConn('source').connectMySql()
        for data in sort_list:
            temp = []
            pdf_id = data[0]
            ## 根据文章id来查找文件绝对路径，进而获得文件内容
            # 连接关系数据库
            cursor = conn.cursor()
            # 根据查询条件编写的查询语句
            sql = "select * from upload_file where id = %s " % (pdf_id)
            cnt = cursor.execute(sql)
            for i in range(cnt):
                result = cursor.fetchone()
                # 将查询结果转换成列表存储
                result = list(result)
                # 文件路径
                file_road = result[2]

                pdfReader = pdfplumber.open(file_road)
                page_text = pdfReader.pages[data[1] - 1]
                page_content = page_text.extract_text()
                '''
                temp列表中存储[文件路径，文件页码，文件内容]
                '''
                temp.append(result[1])
                temp.append(data[1])
                temp.append(page_content)
                res.append(temp)
        if len(res) == 0:
            messages.success(request, "抱歉！未搜索到！")
            return render(request, 'application/searchAllPdf.html')
        conn.close()
        return render(request, "application/searchAllPdf.html", {"res": res, "keywords": key})


def keywordsearch(str_word):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "select id, page_number, location, file_type from index_table where keyword = '%s'" % str_word
    count = cursor.execute(sql)
    result_list = list()
    if count != 0:
        for i in range(count):
            result = cursor.fetchone()
            result_list.append(result)
    conn.commit()
    conn.close()
    return result_list


def bookcut(orList):
    orList.sort()
    newList = []

    n = 0
    for k in range(len(orList)):
        if orList[k][0] == orList[-1][0]:
            newList.append(orList[n:])
            break
        if orList[k][0] != orList[k + 1][0]:
            subList = orList[n:k + 1]
            newList.append(subList)
            n = k + 1

    return newList


def pagecut(orList):
    orList = sorted(orList, key=lambda x: x[1])
    newList = []

    n = 0
    for k in range(len(orList)):
        if orList[k][1] == orList[-1][1]:
            newList.append(orList[n:])
            break
        if orList[k][1] != orList[k + 1][1]:
            subList = orList[n:k + 1]
            newList.append(subList)
            n = k + 1
    return newList


def cut(orList):
    orList = sorted(orList, key=lambda x: x[2])
    newList = []

    n = 0
    for k in range(len(orList)):
        if orList[k][2] == orList[-1][2]:
            newList.append(orList[n:])
            break
        if orList[k][2] != orList[k + 1][2]:
            subList = orList[n:k + 1]
            newList.append(subList)
            n = k + 1

    return newList


def pagecount(page_list):
    pagelist = list()
    if type(page_list[0]) == tuple:
        num = len(page_list)
        id = page_list[0][0]
        page = page_list[0][1]
    else:
        num = 1
        id = page_list[0][0]
        page = page_list[0][1]
    page_lists = sorted(page_list, key=lambda x: x[2])  # 列表排序。1-0
    location = 10
    for i in range(num):
        if page_lists[i][2] == 0:  # 有正文
            location = 2
        if page_lists[i][2] == 1 and location == 2:  # 有正文有标题
            location = 0
            break
        if page_lists[i][2] == 1 and location == 10:  # 只有标题
            location = 1
    pagelist.append(id)
    pagelist.append(page)
    pagelist.append(location)
    pagelist.append(num)
    return pagelist


def result_sort(result_list):
    # id   page    title/content   num
    sortlist = list()
    tosortlist = list()
    book_list = bookcut(result_list)  # 按照文档分开
    for i in range(len(book_list)):
        page_list = pagecut(book_list[i])  # 按照页码分开
        for j in range(len(page_list)):
            nnlist = pagecount(page_list[j])  # 计算出现次数
            tosortlist.append(nnlist)
    flists = sorted(tosortlist, key=lambda x: x[2])  # 按照位置排序  正文/标题-0  标题-1 正文-2
    lllist = cut(flists)  # 按照位置分开
    for k in range(len(lllist)):
        fflists = sorted(lllist[k], key=lambda x: x[3], reverse=True)  # 按照次数排序
        for m in range(len(fflists)):
            sortlist.append(fflists[m])
    return sortlist