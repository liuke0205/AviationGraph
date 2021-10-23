# -*- coding: utf-8 -*-

import json

import docx
from django.contrib import messages
from django.shortcuts import render, redirect
from AviationGraph.utils.pre_load import neo4jconn

'''
跳转到基于规则的word知识提取
'''


def toWord(request):
    return render(request, "management/word.html")

'''
关系：【组成关系】
对表格进行解析
'''


def table(line: str) -> list:
    result_list = []
    data = line.split()
    for i in range(len(data) - 1):
        temp_list = [data[i], "组成关系", data[i + 1], line.replace("\n", "")]
        result_list.append(temp_list)
    return result_list


'''
关系：【组成关系】
由...组成、由...构成
sring = 组成 | 构成
'''


def made_of_1(string: str, line: str) -> list:
    start0 = line.find("，")
    start1 = line.find("由")
    start2 = line.find(string)
    result_list = []
    if start1 != -1 and start2 != -1 and start2 > start1:
        list1 = line[start1 + 1:start2]
        for data in list1.split("、"):
            temp_list = [line[start0 + 1:start1], "组成关系", data, line.replace("\n", "")]
            result_list.append(temp_list)
    return result_list


'''
关系：【组成关系】
string = 主要包括|分为
'''


def made_of_2(string: str, line: str) -> list:
    start1 = line.find(string)
    end1 = line.find("。")
    list1 = line[start1 + len(string):end1]
    result_list = []
    if list1.find("、") != -1:
        for data in list1.split("、"):
            if data[-1] == "等":
                temp_list = [line[0:start1], "组成关系", data[0:-1], line.replace("\n", "")]
                result_list.append(temp_list)
            else:
                temp_list = [line[0:start1], "组成关系", data, line.replace("\n", "")]
                result_list.append(temp_list)

    start = line.find(string)
    end = line.find("等")
    headEntity = line[0:start]

    list = line[start + len(string) + 1:end]

    for data in list.split("；"):
        index = data.find('）')
        if index != -1:
            data2 = data[index + 1:]  # 大型客车（3辆），分为铰接式客车，双层客车和多层客车
            for i in range(1, 1000):
                if data2.find(chr(i)) != -1:
                    beg_index = data2.find('（')
                    end_index = data2.find('）')
                    tailEntity = data2[0:beg_index]  # 大型客车
                    in_entity = data2[beg_index + 1:end_index]
                    temp_list = [tailEntity, "数量关系", in_entity]
                    result_list.append(temp_list)

                    temp_list1 = [headEntity, "组成关系", tailEntity]  # , line.replace("\n", "")
                    result_list.append(temp_list1)
                    break
    return result_list


'''
关系：【位置关系】
string  = 位于......
'''


def local(string: str, line: str) -> list:
    # 获取关键字位置
    start = line.find(string)
    # 获取结束位置
    end = line.find("。")
    temp_list = [line[0:start], "位置关系", line[start + len(string):end], line.replace("\n", "")]  # 注意删除换行符
    # print(temp_list)
    return temp_list


'''
关系：【使用关系】
string = 采用|使用
'''


def use(string: str, line: str) -> list:
    # 获取关键字位置
    start = line.find(string)
    # 获取结束位置
    end = line.find("，")
    temp_list = []
    if start != -1:
        if end == -1:
            end = line.find("。")
        temp_list = [line[0:start], "使用关系", line[start + len(string):end], line.replace("\n", "")]
    return temp_list


def main(infile) -> list:
    infopen = open(infile, 'r', encoding="utf-8")
    # 加载json格式的配置文件 => 字典
    with open("AviationGraph/sourceFile/rules.json", 'r', encoding='UTF-8') as f:
        load_dict = json.load(f)

    # 后期读取配置文件或者前端列表
    ###relation = ["位于", "使用", "采用", "主要包括", "分为", "\t", "组成", "构成"]
    relation = ["\t"]
    for k, v in load_dict.items():
        for listData in v:
            relation.append(listData)
    result_list = []

    # 读取格式化之后的文件
    lines1 = infopen.readlines()
    for line in lines1:
        for r in relation:
            if line.find(r) != -1:
                if r == "\t":
                    # print(table(line))
                    temp_list = table(line)
                    for data in temp_list:
                        result_list.append(data)

                for k, v in load_dict.items():
                    for listData in v:
                        if r == listData:
                            if k == "使用关系":
                                temp_list = use(r, line)
                                result_list.append(temp_list)
                            if k == "位置关系":
                                temp_list = local(r, line)
                                result_list.append(temp_list)
                            if k == "组成关系1":
                                temp_list = made_of_2(r, line)
                                for data in temp_list:
                                    result_list.append(data)
                            if k == "组成关系2":
                                if line.find("由") != -1:
                                    # print(made_of_1(r, line))
                                    temp_list = made_of_1(r, line)
                                    for data in temp_list:
                                        result_list.append(data)
    resultList = []
    for data in result_list:
        temp = ["", "", "", "", ""]
        temp[0] = data[0]
        temp[2] = data[1]
        temp[3] = data[2]
        if data[0].find("飞机") != -1:
            temp[1] = "飞机"
        if data[0].find("系统") != -1:
            temp[1] = "系统"
        if data[0].find("框") != -1:
            temp[1] = "框"

        if data[2].find("飞机") != -1:
            temp[4] = "飞机"
        if data[2].find("系统") != -1:
            temp[4] = "系统"
        if data[2].find("框") != -1:
            temp[4] = "框"

        if data[1] == "使用关系":
            temp[1] = "部附件"
            temp[4] = "结构"
        if data[1] == "组成关系" and data[0].find("系统") != -1 and data[2].find("系统") == -1:
            temp[4] = "部附件"
        if data[1] == "组成关系" and data[0].find("飞机") != -1 and data[2].find("系统") == -1:
            temp[4] = "结构"
        if data[1] == "数量关系":
            temp[1] = "部附件"
            temp[4] = "数量"

        if data[1] == "位置关系":
            temp[1] = "结构"
            if temp[4] != "框":
                temp[4] = "位置"
        resultList.append(temp)

    infopen.close()

    return resultList


'''
格式化待处理文件
1.去掉空行
2.去掉数字开头的行
3.将列表形式处理成一行（未完成）
'''


def format_file(infile) -> list:
    outfile = "upload_file/temp.txt"

    infopen = open(infile, 'r', encoding="utf-8")
    outfopen = open(outfile, 'w+', encoding="utf-8")

    lines = infopen.readlines()

    t_list = []
    for j in range(len(lines)):
        if lines[j].split():
            if lines[j].find("主要包括") != -1:
                for i in range(ord("a"), ord("z") + 1):
                    if lines[j + 1].startswith(chr(i)) == True:
                        t_list.append(lines[j].replace("\n", ""))
                        t_list.append(lines[j + 1].replace("\n", ""))
                        for k in range(j + 2, len(lines)):
                            for i in range(ord("a"), ord("z") + 1):
                                if lines[k].startswith(chr(i)) == True:
                                    t_list.append(lines[k].replace("\n", ""))
            list_str = ''.join(t_list)
            if list_str:
                # print(list_str)
                outfopen.writelines(list_str + "\n")
            t_list = []
            for i in range(9):
                if lines[j].startswith(str(i)) == True:
                    break
            if i == 8:
                outfopen.writelines(lines[j])
        else:
            outfopen.writelines("")
    infopen.close()
    outfopen.close()
    # 调用主处理函数
    resultList = main(outfile)
    return resultList


def upload_word(request):
    # 上传文件，并且将数据保存到数据库中
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')
        str_filename = str(path)
        if str_filename.endswith(".docx") or str_filename.endswith(".doc"):
            if path:
                with open('upload_file/technical_file_word.docx', 'wb+') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)

                file = docx.Document("upload_file/technical_file_word.docx")

                infile = "upload_file/temp1.txt"
                with open(infile, 'w+', encoding="utf-8") as outfopen:
                    for p in file.paragraphs:
                        data = p.text.strip('\n')
                        outfopen.writelines(data + "\n")
                resultList = format_file(infile)
                messages.success(request, "上传成功！")

                request.session['word_list'] = resultList
                request.session['word_filename'] = str(path.name)
                return redirect('/management/display_word_result/')
            else:
                messages.success(request, "文件为空！")
                return redirect('/management/toWord/')
        else:
            messages.success(request, "上传失败，请上传Word文件！")
            return redirect('/management/toRelation/')

def wordExtractInsertNeo4j(request):
    resultList = request.session.get('word_list')
    print(resultList)
    if len(resultList) == 0:
        messages.success(request, "请抽取后再导入数据！")
        return redirect('/management/toWord/')
    db = neo4jconn
    for data in resultList:
        head_entity_value = data[0]
        head_entity_typename = data[1]
        tail_entity_value = data[3]
        tail_entity_typename = data[4]
        relation = data[2]


        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       relation)

            # 头实体已经存在，更新头实体属性，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       relation)

            # 尾实体已经存在，更新尾实体属性，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       relation)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           relation)
    return render(request, 'management/word.html', {'resultList': resultList})

def display_word_result(request):
    resultList = request.session.get('word_list')
    word_filename = request.session.get('word_filename')
    return render(request, 'management/word.html', {'resultList': resultList, 'word_filename':word_filename})