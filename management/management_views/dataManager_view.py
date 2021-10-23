import csv

from django.contrib import messages
from django.shortcuts import render, redirect

from AviationGraph.utils.MySqlConn import MySqlConn
from application.models import User, Temp
from AviationGraph.utils.pre_load import neo4jconn


# 跳转到数据管理页面
def toDataManager(request):

    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "SELECT * FROM corpus"
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    if len(data) == 0:
        messages.success(request, "亲，现在没有任何数据，请先进行数据标注工作！")
        return redirect('/management/toAnnotation/')
    return render(request, 'management/data_manager.html', {'tempList': data})


# 将一条数据插入到Neo4j数据库
def importNeo4j(request):
    # 获取id
    id = request.GET.get('id')

    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    select_sql = "SELECT * FROM corpus where id = '%s'" % (id)
    cursor.execute(select_sql)
    # 返回第一条数据即可（信息熵最大的那条数据）
    data = cursor.fetchone()
    conn.commit()

    print(data)
    print(type(data))

    headEntity = data[1]
    tailEntity = data[3]
    relationshipCategory = data[2]

    headEntityType = "无"
    tailEntityType = "无"

    # 连接数据库
    db = neo4jconn

    # 查询出来头实体和尾实体是否已经存在
    result1 = db.findEntity(headEntity)
    result2 = db.findEntity(tailEntity)

    #插入完，在数据库中删除原数据
    delete_sql = "delete from corpus where id = '%s'" % (id)
    cursor.execute(delete_sql)
    conn.commit()

    if result1 and result2:
        # 判断是否存在关系
        if db.findRelationByEntities(headEntity, tailEntity):  # 如果存在关系，更新关系
            db.modifyRelation(headEntity, tailEntity, relationshipCategory, id)
        else:  # 如果两个实体不存在关系，则直接创建关系
            db.insertRelation(headEntity, headEntityType, relationshipCategory,
                              tailEntity, tailEntityType, id)
    elif result1:
        # 创建尾实体
        db.createNode2(tailEntity, tailEntityType)
        # 插入一条neo4j数据库信息
        db.insertRelation(headEntity, headEntityType, relationshipCategory,
                          tailEntity, tailEntityType, id)
    elif result2:
        # 创建头实体
        db.createNode2(headEntity, headEntityType)
        # 插入一条neo4j数据库信息
        db.insertRelation(headEntity, headEntityType, relationshipCategory,
                          tailEntity, tailEntityType, id)
    else:
        # 创建头实体
        db.createNode2(headEntity, headEntityType)
        # 创建尾实体
        db.createNode2(tailEntity, tailEntityType)
        # 插入一条neo4j数据库信息
        db.insertRelation(headEntity, headEntityType, relationshipCategory,
                          tailEntity, tailEntityType, id)
    return redirect('/management/toDataManager/')


# 批量导入Neo4j数据库
def importNeo4jMuilt(request):
    boxList = request.POST.getlist('boxList')
    # 连接数据库
    db = neo4jconn

    #连接MySQL数据库
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    if boxList:
        print(boxList)
        print(type(boxList))
        for id in boxList:

            select_sql = "SELECT * FROM corpus where id = '%s'" % (id)
            cursor.execute(select_sql)
            # 返回第一条数据即可（信息熵最大的那条数据）
            data = cursor.fetchone()
            conn.commit()

            headEntity = data[1]
            tailEntity = data[3]
            relationshipCategory = data[2]

            headEntityType = "无"
            tailEntityType = "无"

            # 查询出来头实体和尾实体是否已经存在
            result1 = db.findEntity(headEntity)
            result2 = db.findEntity(tailEntity)

            # 插入完，在数据库中删除原数据
            delete_sql = "delete from corpus where id = '%s'" % (id)
            cursor.execute(delete_sql)
            conn.commit()

            if result1 and result2:
                # 判断是否存在关系
                if db.findRelationByEntities(headEntity, tailEntity):  # 如果存在关系，更新关系
                    db.modifyRelation(headEntity, tailEntity, relationshipCategory, id)
                else:  # 如果两个实体不存在关系，则直接创建关系
                    db.insertRelation(headEntity, headEntityType, relationshipCategory,
                                      tailEntity, tailEntityType, id)
            elif result1:
                # 创建尾实体
                db.createNode2(tailEntity, tailEntityType)
                # 插入一条neo4j数据库信息
                db.insertRelation(headEntity, headEntityType, relationshipCategory,
                                  tailEntity, tailEntityType, id)
            elif result2:
                # 创建头实体
                db.createNode2(headEntity, headEntityType)
                # 插入一条neo4j数据库信息
                db.insertRelation(headEntity, headEntityType, relationshipCategory,
                                  tailEntity, tailEntityType, id)
            else:
                # 创建头实体
                db.createNode2(headEntity, headEntityType)
                # 创建尾实体
                db.createNode2(tailEntity, tailEntityType)
                # 插入一条neo4j数据库信息
                db.insertRelation(headEntity, headEntityType, relationshipCategory,
                                  tailEntity, tailEntityType, id)
        return redirect('/management/toDataManager/')
    else:
        messages.success(request, "未选中任何数据！")
    return redirect('/management/toDataManager/')



# 删除一条Neo4j数据
def deleteNeo4j(request):
    # 获取前端传过来的temp_id
    id = request.GET.get('id')
    # 连接MySQL数据库
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    # 插入完，在数据库中删除原数据
    delete_sql = "delete from corpus where id = '%s'" % (id)
    cursor.execute(delete_sql)
    conn.commit()
    return redirect('/management/toDataManager/')


# 导出Neo4J数据库
def download(request):
    db = neo4jconn
    searchResult = {}
    tableData = []
    searchResult = db.findAll()
    tableData = Screen(searchResult)
    if tableData:
        for data in tableData:
            with open("exload_all_relation.csv", "a", newline="") as csvfile:
                write = csv.writer(csvfile)
                write.writerow(data)
        messages.success(request, "下载成功！")
        return redirect('/management/toDataManager/')
    else:
        messages.success(request, "Neo4j数据库为空！")
        return redirect('/management/toDataManager/')

def Screen(searchResult):
    tableData = []
    for i in range(0, len(searchResult)):
        relationData = []
        relationData.append(searchResult[i]['n1']['name'])
        relationData.append(searchResult[i]['rel']['type'])
        relationData.append(searchResult[i]['n2']['name'])
        relationData.append((searchResult[i]['rel']['id']))
        tableData.append(relationData)
    return tableData