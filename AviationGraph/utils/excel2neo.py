#将excel数据按照特定格式存储到neo4j数据库中
import xlrd

from AviationGraph.utils.pre_load import neo4jconn

def excel2neo4j(filepath):
    #1.读取excel文件
    excel = xlrd.open_workbook(filepath)
    sheet = excel.sheet_by_index(0)
    row_number = sheet.nrows
    relationList = []
    #2.将数据转换成二维列表的形式
    for i in range(1, row_number):
        relationList.append(sheet.row_values(i))
    #3.连接neo4j数据库
    db = neo4jconn
    #4.批量导入
    for data in relationList:
        if len(data[0]) > 10 or len(data[2]) > 10:
            continue
            # 两个实体都不存在，创建节点和关系

        head_entity_value = data[0]
        head_entity_typename = data[1]
        tail_entity_value = data[2]
        tail_entity_typename = data[3]
        relation = data[4]
        # 根据头实体名来查找neo4j数据库是否已经存在实体
        select_head_entity = db.findEntity(head_entity_value)
        # 根据尾实体名来查找neo4j数据库是否已经存在实体
        select_tail_entity = db.findEntity(tail_entity_value)
        print(select_head_entity)
        print(select_tail_entity)
        if len(select_head_entity) == 0 and len(select_tail_entity) == 0:
            db.createNode2(head_entity_value, head_entity_typename)
            db.createNode2(tail_entity_value, tail_entity_typename)
            db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                   relation)

        # 头实体已经存在，创建尾实体和关系
        elif len(select_head_entity) != 0 and len(select_tail_entity) == 0:
            db.createNode2(tail_entity_value, tail_entity_typename)
            db.insertExcelRelation(head_entity_value, head_entity_typename, tail_entity_value, tail_entity_typename,
                                   relation)

        # 尾实体已经存在，创建头实体和关系
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
    print("导入结束")
if __name__ == '__main__':
    excel2neo4j("E:/硕士毕业论文/06-数据/关系表2.xlsx")