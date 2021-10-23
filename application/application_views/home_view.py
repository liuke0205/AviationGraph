import json

from django.shortcuts import render

from AviationGraph.utils.pre_load import neo4jconn


def entity_relation_cnt(request):
    entity_cnt = request.POST.get('entity_cnt')
    relation_cnt = request.POST.get('relation_cnt')
    if len(entity_cnt) == 0:
        entity_cnt = str(100)
    if len(relation_cnt) == 0:
        relation_cnt = str(100)
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    db = neo4jconn
    searchResult = db.findAllByCnt(relation_cnt)
    searchEntity = db.findAllEntityByCnt(entity_cnt)

    entity_amount = db.getAllEntityAmount()
    entity_amount = entity_amount[0]['COUNT(n)']
    relation_amount = db.getAllRelationAmount()
    relation_amount = relation_amount[0]['COUNT(r)']
    print(entity_amount)
    print(relation_amount)
    number = request.session.get('number')
    return render(request, 'application/home.html',
                  {'searchResult': json.dumps(searchResult, ensure_ascii=False), 'relation_amount': relation_amount,
                   'searchEntity': json.dumps(searchEntity, ensure_ascii=False), 'entity_amount': entity_amount,
                   'number': number, 'entity_cnt':entity_cnt, 'relation_cnt': relation_cnt})

# 跳转到主页面
def toHome(request):
    username = request.session.get('username')
    if username is None:
        return render(request, 'login.html')
    db = neo4jconn
    searchResult = db.findAll()
    searchEntity = db.findAllEntity()
    number = request.session.get('number')
    entity_amount = db.getAllEntityAmount()
    entity_amount = entity_amount[0]['COUNT(n)']
    relation_amount = db.getAllRelationAmount()
    relation_amount = relation_amount[0]['COUNT(r)']
    return render(request, 'application/home.html',
                  {'searchResult': json.dumps(searchResult, ensure_ascii=False), 'relation_amount': relation_amount,
                   'searchEntity': json.dumps(searchEntity, ensure_ascii=False), 'entity_amount': entity_amount,
                   'number': number, 'entity_cnt': 100, 'relation_cnt':100})
