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


# ��ת��������ҳ��
def toD2rq(request):
    return render(request, 'management/d2rq.html')


# ����ǰ���ύ�Ĺ�ϵ���ݿ�������Ϣ�����ص���ҳ��
def commitDatabase(request):
    database = request.POST['database']
    request.session['database'] = database

    return render(request, 'management/d2rq.html', {"database": database})


# ����ǰ���ύ�����ݿ�����������Ϣ
def commitConfiguration(request):
    # ��ȡǰ���ύ��������Ϣ
    host = request.POST['host']
    port = request.POST['port']
    username = request.POST['username']
    password = request.POST['password']
    db_name = request.POST['db_name']
    database = request.session.get('database')
    # ��������Ϣ���浽session��
    request.session['host'] = host
    request.session['port'] = port
    request.session['username2'] = username
    request.session['password'] = password
    request.session['db_name'] = db_name
    request.session['database'] = database
    # ���ݲ�ͬ���͵Ĺ�ϵ���ݿ����ֱ�����
    if database == 'MySQL':
        # ���ӹ�ϵ���ݿ�
        conn = connDB(database, host, int(port), username, password, db_name).connectDB()
        # ��ȡ�����α�
        cursor = conn.cursor()
        # �����������ݿ��
        count = cursor.execute("show tables")
        tableList = list()
        for i in range(count):
            result = cursor.fetchone()
            tableList.append(result[0])
    return render(request, 'management/d2rq.html', {"tableList": tableList, "database": database})


# ��ǰ�˻�ȡ������
def getTable(request):
    # ��ȡ����
    table = request.POST['databaseTable']
    # �����ݿ��������session
    request.session['table'] = table
    # ��ȡsession�е����ݿ�������Ϣ
    database = request.session.get('database')
    host = request.session.get('host')
    username = request.session.get('username2')
    password = request.session.get('password')
    db_name = request.session.get('db_name')
    port = request.session.get('port')
    # ���ӹ�ϵ���ݿ�
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # ��ȡ���ű�������ֶ�
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

    cursor.close()  # �ر��α�
    conn.close()  # �ر�����

    return render(request, 'management/d2rq.html',
                  {'tableList': tableList, 'aList': aList, 'table': table, 'table1_result': table1_result,
                   'bList': bList, 'table2_result': table2_result, 'primary': primary[0],
                   'primary2': primary2})


# �ӹ�ϵ���ݿ��г�ȡ֪ʶ
def d2neo4j(request):
    # ��session�����ȡ��Ϣ
    table = request.session.get('table')
    entity_name = request.POST.get('entity_name')
    entity_property = request.POST.getlist('entity_property')

    database = request.session.get('database')
    host = request.session.get('host')
    username = request.session.get('username2')
    password = request.session.get('password')
    db_name = request.session.get('db_name')
    port = request.session.get('port')

    # �����һ���ڵ���Ϣ
    insertNode(table, entity_name, entity_property, database, host, username, password, db_name, port)

    # ��session�����ȡ�ڶ���ʵ�����������б�
    entity_name2 = request.POST.get('entity_name2')
    entity_property2 = request.POST.getlist('entity_property2')

    # ������ڵڶ����ڵ���Ϣ
    if entity_name2:
        table2 = request.session.get('table2')
        insertNode(table2, entity_name2, entity_property2, database, host, username, password, db_name, port)

        re_name = request.session.get('re_name')
        # ����֪ʶ��Ϣ
        insertKnow(table2, entity_name2, re_name, database, host, username, password, db_name, port)

    messages.success(request, "success!")
    return redirect('/management/toD2rq/')


def insertNode(table, entity_name, entity_property, database, host, username, password, db_name, port):
    # �������ݿ�
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # ƴ�������б�
    str = ','.join(entity_property)
    # print(str)
    # ���ݲ�ѯ������д�Ĳ�ѯ���
    sql = "select %s, %s from %s" % (entity_name, str, table)
    count = cursor.execute(sql)
    # �洢��ѯ��������ֵ�洢��
    dict = {}
    # ѭ���������α�ָ��
    for i in range(count):
        result = cursor.fetchone()
        # ����ѯ���ת�����б�洢
        result = list(result)
        # ��ѯ���ĵ�һ��ֵ��ʵ����
        name = result[0]
        # ����neo4j���ݿ�
        db = neo4jconn
        # ����ʵ����������neo4j���ݿ��Ƿ��Ѿ�����ʵ��
        result1 = db.findEntity(name)
        if result1:
            pass
        # ���û�д��ڽ�����������
        else:
            # ��ȡ�ֵ��ȫ����Ϣ
            dictionary_entity = Dictionary.objects.all()
            # ʵ������
            type = ""
            for entity in dictionary_entity:
                if entity.entity == name:
                    type = entity.entity_type
                    break
            # �������ʵ������
            if type:
                # ����ʵ��ڵ�
                result.remove(name)
                for i in range(len(entity_property)):
                    dict.update({entity_property[i]: result[i]})
                db = neo4jconn
                db.createNode(name, type, dict)
    cursor.close()  # �ر��α�
    conn.close()  # �ر�����


sum = 300


def insertKnow(table2, entity_name2, re_name, database, host, username, password, db_name, port):
    global sum

    # ���ӹ�ϵ���ݿ�
    conn = connDB(database, host, int(port), username, password, db_name).connectDB()
    cursor = conn.cursor()
    # ��ѯ���
    sql = "select %s, %s from %s" % (entity_name2, re_name, table2)

    count = cursor.execute(sql)
    for i in range(count):
        result = cursor.fetchone()
        # ��ȡ��ͷʵ���βʵ�������
        headEntityType = Dictionary.objects.get(entity=result[0]).entity_type
        tailEntityType = Dictionary.objects.get(entity=result[1]).entity_type
        # ����ͷʵ���βʵ������ѯ֮��Ĺ�ϵ
        relation = Relation.objects.get(head_entity=headEntityType, tail_entity=tailEntityType)
        # ��ȡ�ֵ��ȫ����Ϣ
        dictionary_entity = Dictionary.objects.all()
        # ʵ������
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
    cursor.close()  # �ر��α�
    conn.close()  # �ر�����