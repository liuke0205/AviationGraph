# -*- coding: utf-8 -*-
import random

import xlrd
from django.contrib import messages
from django.shortcuts import render, redirect
import xlwt
from django.http import FileResponse

from AviationGraph.utils.MySqlConn import MySqlConn
from AviationGraph.utils.pre_load import neo4jconn


# 跳转到excel界面
def toExcel(request):
    return render(request, 'management/excel.html')


def upload_excel(request):
    if request.method == 'POST':
        # 获取文件名
        file = request.FILES.get('excel_file')
        # 获取文件名
        str_filename = str(file)
        if str_filename.endswith(".xlsx") or str_filename.endswith(".xls"):
            if file:

                with open('upload_file/excel_import.xlsx', 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # 下面代码作用：获取到excel中的字段和数据
                excel = xlrd.open_workbook("upload_file/excel_import.xlsx")
                sheet = excel.sheet_by_index(0)
                row_number = sheet.nrows
                field_list = sheet.row_values(0)
                data_list = []
                for i in range(1, row_number):
                    data_list.append(sheet.row_values(i))

                # 下面代码作用：根据字段创建表，根据数据执行插入语句
                conn = MySqlConn('source').connectMySql()
                cursor = conn.cursor()
                drop_sql = "drop table if exists {}".format('excel_data')
                cursor.execute(drop_sql)
                conn.commit()

                cursor = conn.cursor()
                create_sql = "create table {}(".format('excel_data')
                for field in field_list[:-1]:
                    create_sql += "{} text,".format(field)
                create_sql += "{} text)".format(field_list[-1])
                cursor.execute(create_sql)
                conn.commit()
                for data in data_list:
                    data =format(data)
                    new_data = ["'{}'".format(i) for i in data]
                    insert_sql = "insert into {} values({})".format('excel_data', ','.join(new_data))
                    print(insert_sql)
                    cursor.execute(insert_sql)
                conn.commit()

                sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s' and TABLE_SCHEMA = 'source' " % ('excel_data')
                count = cursor.execute(sql)
                conn.commit()
                name_list = []
                for i in range(count):
                    rr = cursor.fetchone()[0]
                    if rr not in name_list:
                        name_list.append(rr)
                conn.commit()

                request.session['name_list'] = name_list
                filename = str(file.name)
                return render(request, 'management/excel.html', {'name_list': name_list, 'filename': filename})
        else:
            messages.success(request, "上传失败，请上传Excel文件！")
            return redirect('/management/toExcel/')
    return redirect('/management/toExcel/')

def format(list):
    res = []
    for data in list:
        data = str(data).replace("\"", "").replace("'", "").replace(" ", "")
        res.append(data)
    return res

def flag(string, name_list) -> bool:
    for data in name_list:
        if string == data:
            return True
    return False

def commit_properties(request):
    if request.method == 'POST':
        '''
        后期在前端限定   实体名只能选择一个
        '''
        # 获取到前端选择的字段
        head_entity_list = request.POST.getlist('select2')
        head_property_list = request.POST.getlist('select3')
        tail_entity_list = request.POST.getlist('select22')
        tail_property_list = request.POST.getlist('select33')

        if len(head_entity_list) == 0 or len(tail_entity_list) == 0:
            messages.success(request, "规则为空，请重新添加规则！")
            return redirect('/management/toExcel/')
        tableData = request.session.get('tableData')
        name_list = request.session.get('name_list')

        if len(head_entity_list) > 1 or len(tail_entity_list) > 1:
            messages.success(request, '选择的头实体个数或者尾实体个数大于1！')
            return render(request, 'management/excel.html', {'name_list': name_list, 'tableData': tableData})

        head_property_list = ','.join(head_property_list)
        tail_property_list = ','.join(tail_property_list)
        id = random.randint(100000, 200000)
        temp = [head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id]
        '''
        将新的规则插入到规则表中  将属性列表转换成  A,B,C 格式进行存储
        '''
        # 连接数据库
        conn = MySqlConn('source').connectMySql()
        cursor = conn.cursor()
        sql = "INSERT INTO excel_relation VALUES('%s','%s','%s','%s','%s')" % (
        head_entity_list[0], head_property_list, tail_entity_list[0], tail_property_list, id)
        cursor.execute(sql)
        conn.commit()
        if tableData is None:
            tableData = []
        tableData.append(temp)
        request.session['tableData'] = tableData
        return render(request, 'management/excel.html', {'name_list': name_list, 'tableData': tableData})

resultList_excel=[]

def excel_extract(request):
    if request.method == 'POST':
        # 获取session域中的tableData
        tableData = request.session.get('tableData')
        if len(tableData) == 0 or tableData is None:
            return redirect('/management/toExcel/')
        # 对每个规则进行抽取
        for data in tableData:
            # 获取到前端选择的字段
            head_entity = data[0]
            head_property_list = data[1]
            tail_entity = data[2]
            tail_property_list = data[3]

            # 根据表的字段名进行抽取，判断头实体和尾实体的属性表是否为空
            if len(head_property_list) != 0 and len(tail_property_list) != 0:
                create_relation(head_entity, head_property_list, tail_entity, tail_property_list)
            elif len(head_property_list) == 0 and len(tail_property_list) != 0:
                create_relation1(head_entity, tail_entity, tail_property_list)
            elif len(head_property_list) != 0 and len(tail_property_list) == 0:
                create_relation2(head_entity, head_property_list, tail_entity)
            else:
                create_relation3(head_entity, tail_entity)
    global resultList_excel
    write_excel_xls("upload_file/fault_excel_data.xls", "fault_excel_data", resultList_excel)
    resultList_excel = []
    # 获取session域中的name_list
    name_list = request.session.get('name_list')

    # 抽取完之后将session置为空
    request.session['tableData'] = []
    return render(request, 'management/excel.html', {'name_list': name_list})

def write_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿

def download_fault_data(request):
    file = open('upload_file/fault_excel_data.xls', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="fault_excel_data.xls"'
    return response

def create_relation(head_entity, head_property_list, tail_entity, tail_property_list):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    head_property_list_last = head_property_list.split(',')
    tail_property_list_last = tail_property_list.split(',')

    # 获取头实体属性列表的个数
    head_property_num = len(head_property_list_last)

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s,%s,%s from excel_data" % (
    head_entity_typename, tail_entity_typename, head_property_list, tail_property_list)
    count = cursor.execute(sql)

    # 连接neo4j数据库
    db = neo4jconn

    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询出来的头实体名的value
        head_entity_value = result[0]
        # 查询出来的尾实体名的value
        tail_entity_value = result[1]
        # 查询出来的头实体的属性列表的value
        head_property_list_value = result[2:head_property_num + 2]
        # 查询出来的尾实体的属性列表的value
        tail_property_list_value = result[head_property_num + 2:]
        # 存储头实体属性结果集（字典存储）
        head_property_dict = {}
        # 存储尾实体属性结果集（字典存储）
        tail_property_dict = {}

        # 生成头实体属性字典 例如：{“故障件”：显示器}
        for k in range(len(head_property_list_last)):
            head_property_dict.update({head_property_list_last[k]: head_property_list_value[k]})
        # 生成尾实体属性字典 例如：{“故障件”：显示器}
        for j in range(len(tail_property_list_last)):
            tail_property_dict.update({tail_property_list_last[j]: tail_property_list_value[j]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        resultList_excel.append([head_entity_value, head_entity_typename, str(head_property_dict), tail_entity_value, tail_entity_typename, str(tail_property_dict), tail_entity_typename])
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，更新头实体属性，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.updateNode(head_entity_value, head_property_dict)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，更新尾实体属性，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.updateNode(tail_entity_value, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                db.updateNode(head_entity_value, head_property_dict)
                db.updateNode(tail_entity_value, tail_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation1(head_entity, tail_entity, tail_property_list):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    tail_property_list_last = tail_property_list.split(',')

    # 获取头实体属性列表的个数
    tail_property_num = len(tail_property_list_last)

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s, %s from excel_data" % (head_entity_typename, tail_entity_typename, tail_property_list)
    count = cursor.execute(sql)

    # 连接neo4j数据库
    db = neo4jconn

    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询出来的头实体名的value
        head_entity_value = result[0]
        # 查询出来的尾实体名的value
        tail_entity_value = result[1]
        # 查询出来的尾实体的属性列表的value
        tail_property_list_value = result[2:tail_property_num + 2]
        # 存储尾实体属性结果集（字典存储）
        tail_property_dict = {}

        # 生成尾实体属性字典 例如：{“故障件”：显示器}
        for j in range(len(tail_property_list_last)):
            tail_property_dict.update({tail_property_list_last[j]: tail_property_list_value[j]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)
        resultList_excel.append([head_entity_value, head_entity_typename, "", tail_entity_value, tail_entity_typename, str(tail_property_dict), tail_entity_typename])

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.createNode(tail_entity_value, tail_entity_typename, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，更新尾实体属性，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.updateNode(tail_entity_value, tail_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新尾实体的属性
            else:
                db.updateNode(tail_entity_value, tail_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation2(head_entity, head_property_list, tail_entity):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    # ['故障件','故障件编号']
    head_property_list_last = head_property_list.split(',')

    # 获取头实体属性列表的个数
    head_property_num = len(head_property_list_last)

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s, %s from excel_data" % (head_entity_typename, tail_entity_typename, head_property_list)
    count = cursor.execute(sql)

    # 连接neo4j数据库
    db = neo4jconn

    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询出来的头实体名的value
        head_entity_value = result[0]
        # 查询出来的尾实体名的value
        tail_entity_value = result[1]
        # 查询出来的头实体的属性列表的value
        head_property_list_value = result[2:head_property_num + 2]
        # 存储头实体属性结果集（字典存储）
        head_property_dict = {}

        # 生成头实体属性字典 例如：{“故障件”：显示器}
        for k in range(len(head_property_list_last)):
            head_property_dict.update({head_property_list_last[k]: head_property_list_value[k]})

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)
        resultList_excel.append([head_entity_value, head_entity_typename, str(head_property_dict), tail_entity_value, tail_entity_typename, "", tail_entity_typename])

        '''
            创建并更新节点和关系【先判断两个节点是否相同，再判断一下节点是否已经存在】
        '''
        # 两个实体名不一样
        if head_entity_value != tail_entity_value:
            # 两个实体都不存在，创建节点和关系
            if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 头实体已经存在，更新头实体属性，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.updateNode(head_entity_value, head_property_dict)
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode(head_entity_value, head_entity_typename, head_property_dict)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                db.updateNode(head_entity_value, head_property_dict)
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


def create_relation3(head_entity, tail_entity):
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()

    # 头实体类型名
    head_entity_typename = head_entity
    # 尾实体类型名 / 关系名
    tail_entity_typename = tail_entity

    # 根据查询条件编写的查询语句
    sql = "select %s, %s from excel_data" % (head_entity_typename, tail_entity_typename)
    count = cursor.execute(sql)

    # 连接neo4j数据库
    db = neo4jconn

    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询出来的头实体名的value
        head_entity_value = result[0]
        # 查询出来的尾实体名的value
        tail_entity_value = result[1]

        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)
        resultList_excel.append([head_entity_value, head_entity_typename, "", tail_entity_value, tail_entity_typename, "", tail_entity_typename])

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
                                       tail_entity_typename)

            # 头实体已经存在，创建尾实体和关系
            elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
                db.createNode2(tail_entity_value, tail_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 尾实体已经存在，创建头实体和关系
            elif len(select_head_entity) == 0 and len(select_tail_entity) != 0:
                db.createNode2(head_entity_value, head_entity_typename)
                db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                       tail_entity_typename)

            # 两个实体都已经存在，更新两个实体的属性
            else:
                # 判断两个实体间是否已存在关系，若不存在则创建关系
                if db.findRelationByEntities(head_entity_value, tail_entity_value) or db.findRelationByEntities(
                        tail_entity_value, head_entity_value):
                    continue
                else:
                    db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value,
                                           tail_entity_typename,
                                           tail_entity_typename)
        else:
            continue
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接