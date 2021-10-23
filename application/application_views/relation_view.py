import json

from django.shortcuts import render
from AviationGraph.utils.pre_load import neo4jconn

# 跳转到关系查询页面
def toRelationSearch(request):
    return render(request, 'application/relation_search.html')

def getRelation(searchResult):
    tableData = []
    for i in range(0, len(searchResult)):
        tableData.append(searchResult[i]['rel']['type'])
    return tableData

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

def relation_search(request):
    ctx = {}
    if request.method == 'POST':
        entity1 = request.POST['entity1_text']
        relation = request.POST['relation_text']
        entity2 = request.POST['entity2_text']

        # 将信息存储在session里面
        request.session['entity1'] = entity1
        request.session['relation'] = relation
        request.session['entity2'] = entity2

        db = neo4jconn

        tableData = []  # 列表   存格式化后的数据
        searchResult = {}
        # 若只输入entity1,则输出与entity1有直接关系的实体和关系
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) == 0):
            searchResult = db.findRelationByEntity1(entity1)

        # 若只输入entity2则,则输出与entity2有直接关系的实体和关系
        if (len(entity2) != 0 and len(relation) == 0 and len(entity1) == 0):
            searchResult = db.findRelationByEntity2(entity2)

        # 若输入entity1和relation，则输出与entity1具有relation关系的其他实体
        if (len(entity1) != 0 and len(relation) != 0 and len(entity2) == 0):
            searchResult = db.findOtherEntities(entity1, relation)

        # 若输入entity2和relation，则输出与entity2具有relation关系的其他实体
        if (len(entity2) != 0 and len(relation) != 0 and len(entity1) == 0):
            searchResult = db.findOtherEntities2(entity2, relation)

        # 若输入entity1和entity2,则输出entity1和entity2之间的关系
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) != 0):
            searchResult = db.findRelationByEntities(entity1, entity2)

        # 若输入entity1,entity2和relation,则输出entity1、entity2是否具有相应的关系
        if (len(entity1) != 0 and len(entity2) != 0 and len(relation) != 0):
            searchResult = db.findEntityRelation(entity1, relation, entity2)
        # 若只输入relation,则输出entity1、entity2是否具有相应的关系
        if (len(entity1) == 0 and len(entity2) == 0 and len(relation) != 0):
            searchResult = db.findOthersByRelation(relation)
        # 全为空
        if (len(entity1) == 0 and len(relation) == 0 and len(entity2) == 0):
            searchResult = db.findAll()

        tableData = Screen(searchResult)
        print(tableData)
        if (len(searchResult) > 0):
            print(tableData)
            return render(request, 'application/relation_search.html',
                          {'searchResult': json.dumps(searchResult, ensure_ascii=False), 'tableData': tableData,
                           'entity1': entity1, 'entity2': entity2, 'relation': relation})
        ctx = {'title': '<h1>暂未找到相应的匹配</h1>'}
        return render(request, 'application/relation_search.html', {'ctx': ctx})

    return render(request, 'application/relation_search.html', {'ctx': ctx})

