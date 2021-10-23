# -*- coding: utf-8 -*-
import xlrd
import xlwt
import csv

from AviationGraph.utils.MySqlConn import MySqlConn
from AviationGraph.utils.pre_load import neo4jconn


def write_excel_xls_append(path, value):
    with open(path, 'a+', encoding="gbk") as f:
        csv_write = csv.writer(f)
        for data in value:
            csv_write.writerow(data)

# 将列表存储到excel表中
def write_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿

def db2txt():
    conn = MySqlConn('source').connectMySql()
    cur = conn.cursor()
    # 执行数据库的操作cur.execute
    cnt = cur.execute('select * from classication_mom')
    f = open('AviationGraph/bm25data/fault.txt', 'w')
    for i in range(cnt):
        row = cur.fetchone()
        f.write(str(row[2]) + "\n")
    f.close()
    conn.close()