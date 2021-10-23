import pymysql
from django.contrib import messages
from django.shortcuts import render, redirect

from application.models import Dictionary, Relation
from AviationGraph.utils.pre_load import neo4jconn


class connDB(object):
    def __init__(self, DB_Name, host, port, user, password, database):
        self._DB_Name = DB_Name
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

    def connectDB(self):
        if self._DB_Name == "MySQL":
            conn = pymysql.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                   database=self._database)
            return conn


# 跳转到管理主页面
def toD2rq(request):
    return render(request, 'management/d2rq.html')


# 接收前端提交的关系数据库类型信息，返回到主页面
def commitDatabase(request):
    database = request.POST['database']
    request.session['database'] = database

    return render(request, 'management/d2rq.html', {"database": database})


# 接收前端提交的数据库连接配置信息
def commitConfiguration(request):
    # 获取前端提交的配置信息
    host = request.POST['host']
    port = request.POST['port']
    username = request.POST['username']
    password = request.POST['password']
    db_name = request.POST['db_name']
    database = request.session.get('database')
    # 将配置信息保存到session中
    request.session['host'] = host
    request.session['port'] = port
    request.session['username2'] = username
    request.session['password'] = password
    request.session['db_name'] = db_name
    request.session['database'] = database
    # 根据不同类型的关系数据库来分别连接
    if database == 'MySQL':
        # 连接关系数据库
        conn = connDB(database, host, int(port), username, password, db_name).connectDB()
        # 获取操作游标
        cursor = conn.cursor()
        # 查找所有数据库表
        count = cursor.execute("show tables")
        tableList = list()
        for i in range(count):
            result = cursor.fetchone()
            tableList.append(result[0])
    return render(request, 'management/d2rq.html', {"tableList": tableList, "database": database})


# 从前端获取到表名
def getTable(request):
    # 获取表名
    table = request.POST['databaseTable']
    # 将数据库表名存入session
    request.session['table'] = table
    # 获取session中的数据库配置信息
    database = request.session.get('database')
    host = request.session.get('host')
    username = request.session.get('username2')
    password = request.session.get('password')
    db_name = request.session.get('db_name')
    port = request.session.get('port')
    # 连接关系数据库
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # 获取本张表的所有字段
    sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s'" % (table)
    count = cursor.execute(sql)
    aList = list()
    for i in range(count):
        rr = cursor.fetchone()[0]
        if rr not in aList:
            aList.append(rr)

    count = cursor.execute("show tables")
    tableList = list()
    for i in range(count):
        result = cursor.fetchone()
        tableList.append(result[0])
    sql4 = "SELECT  COLUMN_NAME FROM INFORMATION_SCHEMA.`KEY_COLUMN_USAGE` WHERE table_name='%s' AND constraint_name='PRIMARY'" % (
        table)
    count = cursor.execute(sql4)
    primary = cursor.fetchone()

    table1_result = []
    sql_1 = "select * from %s" % (table)
    sum_1 = cursor.execute(sql_1)
    for data in range(sum_1):
        result_1 = cursor.fetchone()
        table1_result.append(result_1)

    sql = "select TABLE_NAME,COLUMN_NAME,CONSTRAINT_NAME from INFORMATION_SCHEMA.KEY_COLUMN_USAGE where CONSTRAINT_SCHEMA ='source' AND REFERENCED_TABLE_NAME = '%s';" % (
        table)
    count = (cursor.execute(sql))
    bList = list()
    primary2 = []

    table2_result = []
    if count > 0:
        re = cursor.fetchone()

        request.session['table2'] = re[0]
        request.session['re_name'] = re[1]
        table2 = re[0]

        sql2 = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s'" % (table2)
        count = cursor.execute(sql2)
        for i in range(count):
            rr = cursor.fetchone()[0]
            if rr not in bList:
                bList.append(rr)

        sql3 = "SELECT  COLUMN_NAME FROM INFORMATION_SCHEMA.`KEY_COLUMN_USAGE` WHERE table_name='%s' AND constraint_name='PRIMARY'" % (
            table2)
        count = cursor.execute(sql3)
        primary2 = cursor.fetchone()[0]

        sql_2 = "select * from %s" % (table2)
        sum_2 = cursor.execute(sql_2)
        for data in range(sum_2):
            result_2 = cursor.fetchone()
            table2_result.append(result_2)

    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接

    return render(request, 'management/d2rq.html',
                  {'tableList': tableList, 'aList': aList, 'table': table, 'table1_result': table1_result,
                   'bList': bList, 'table2_result': table2_result, 'primary': primary[0],
                   'primary2': primary2})


# 从关系数据库中抽取知识
def d2neo4j(request):
    # 从session里面获取信息
    table = request.session.get('table')
    entity_name = request.POST.get('entity_name')
    entity_property = request.POST.getlist('entity_property')

    database = request.session.get('database')
    host = request.session.get('host')
    username = request.session.get('username2')
    password = request.session.get('password')
    db_name = request.session.get('db_name')
    port = request.session.get('port')

    # 插入第一个节点信息
    insertNode(table, entity_name, entity_property, database, host, username, password, db_name, port)

    # 从session里面获取第二个实体名和属性列表
    entity_name2 = request.POST.get('entity_name2')
    entity_property2 = request.POST.getlist('entity_property2')

    # 如果存在第二个节点信息
    if entity_name2:
        table2 = request.session.get('table2')
        insertNode(table2, entity_name2, entity_property2, database, host, username, password, db_name, port)

        re_name = request.session.get('re_name')
        # 生成知识信息
        insertKnow(table2, entity_name2, re_name, database, host, username, password, db_name, port)

    messages.success(request, "success!")
    return redirect('/management/toD2rq/')


def insertNode(table, entity_name, entity_property, database, host, username, password, db_name, port):
    # 连接数据库
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # 拼接属性列表
    str = ','.join(entity_property)
    # print(str)
    # 根据查询条件编写的查询语句
    sql = "select %s, %s from %s" % (entity_name, str, table)
    count = cursor.execute(sql)
    # 存储查询结果集（字典存储）
    dict = {}
    # 循环来遍历游标指针
    for i in range(count):
        result = cursor.fetchone()
        # 将查询结果转换成列表存储
        result = list(result)
        # 查询到的第一个值是实体名
        name = result[0]
        # 连接neo4j数据库
        db = neo4jconn
        # 根据实体名来查找neo4j数据库是否已经存在实体
        result1 = db.findEntity(name)
        if result1:
            pass
        # 如果没有存在进行下述操作
        else:
            # 获取字典的全部信息
            dictionary_entity = Dictionary.objects.all()
            # 实体类型
            type = ""
            for entity in dictionary_entity:
                if entity.entity == name:
                    type = entity.entity_type
                    break
            # 如果存在实体类型
            if type:
                # 生成实体节点
                result.remove(name)
                for i in range(len(entity_property)):
                    dict.update({entity_property[i]: result[i]})
                db = neo4jconn
                db.createNode(name, type, dict)
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接


sum = 300


def insertKnow(table2, entity_name2, re_name, database, host, username, password, db_name, port):
    global sum

    # 连接关系数据库
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # 查询语句
    sql = "select %s, %s from %s" % (entity_name2, re_name, table2)

    count = cursor.execute(sql)
    for i in range(count):
        result = cursor.fetchone()
        # 获取到头实体和尾实体的类型
        headEntityType = Dictionary.objects.get(entity=result[0]).entity_type
        tailEntityType = Dictionary.objects.get(entity=result[1]).entity_type
        # 根据头实体和尾实体来查询之间的关系
        relation = Relation.objects.get(head_entity=headEntityType, tail_entity=tailEntityType)
        # 获取字典的全部信息
        dictionary_entity = Dictionary.objects.all()
        # 实体类型
        type0 = ""
        for entity in dictionary_entity:
            if entity.entity == result[0]:
                type0 = entity.entity_type
                break
        type1 = ""
        for entity in dictionary_entity:
            if entity.entity == result[1]:
                type1 = entity.entity_type
                break
        db = neo4jconn
        sum += 1
        if db.findRelationByEntities(result[0], result[1]):
            continue
        else:
            db.insertRelation(result[0], type0, relation.relation, result[1], type1, str(sum))
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接