import re
import jieba
import pdfplumber
import string
from AviationGraph.utils.MySqlConn import MySqlConn


def filesearch(filename):
    # 根据文件名查表得到文件路径、类型、id
    conn = MySqlConn('source').connectMySql()
    cursor = conn.cursor()
    sql = "select id, file_road, file_type from upload_file where file_name = '%s'" % filename
    cursor.execute(sql)
    result = cursor.fetchone()

    return result


def title_judge(str_judge):
    result_1 = re.findall("(第)+(一|二|三|四|五|六|七|八|九|十)+(一|二|三|四|五|六|七|八|九|十)+(章|节|篇)", str_judge)
    result_2 = re.findall("(第)+(一|二|三|四|五|六|七|八|九|十)+(章|节|篇)", str_judge)
    result_3 = re.findall(r"\d\.\d", str_judge)
    result_4 = re.findall(r"\d\d\.\d", str_judge)
    result_5 = re.findall(r"(第)+(\d)+(章|节|篇)", str_judge)
    result_6 = re.findall(r"(第)+(\d\d)+(章|节|篇)", str_judge)
    result_7 = re.findall(r"(第)+(\s\d\s)+(章|节|篇)", str_judge)
    result_8 = re.findall(r"(第)+(\s\d\d\s)+(章|节|篇)", str_judge)
    if (result_1.__len__() == 0 and result_2.__len__() == 0 and result_3.__len__() == 0 and result_4.__len__() == 0
            and result_5.__len__() == 0 and result_6.__len__() == 0 and result_7.__len__() == 0
            and result_8.__len__() == 0):
        return False
    else:
        return True


def is_title(str_del):
    # 排除干扰
    i = 0
    tem_result = re.findall(r"[\u4e00-\u9fa5]\d", str_del)
    tem_result_ti = re.findall(r"第\d", str_del)
    tem_result_1 = re.findall(r"(章|节|篇)[\u4e00-\u9fa5]", str_del)
    tem_result_2 = re.findall(r"[a-zA-Z]\s\d", str_del)
    tem_result_3 = re.findall(r"\w第", str_del)
    tem_result_4 = re.findall(r"\d\s[a-zA-Z]", str_del)
    tem_result_5 = re.findall(r"[\[\]]", str_del)
    # tem_result_6 = re.findall("\s\d", str)
    tem_result_6 = re.findall(r"[\(\)]", str_del)
    # tem_result_7 = re.findall(r"\d[a-zA-Z]", str)
    tem_result_7 = re.findall(r"[a-zA-Z]\d", str_del)
    tem_result_8 = re.findall(r"\s\d\.\d", str_del)
    tem_result_9 = re.findall(r"\s\d\d\.\d", str_del)
    if tem_result.__len__() != 0 and tem_result_ti.__len__() == 0:
        i = 1
    if i != 0 or tem_result_1.__len__() != 0 or tem_result_2.__len__() != 0 or tem_result_3.__len__() != 0 \
        or tem_result_4.__len__() != 0 or tem_result_5.__len__() != 0 or tem_result_6.__len__() != 0 \
            or tem_result_7.__len__() != 0 or tem_result_8.__len__() != 0 or tem_result_9.__len__() != 0:
        return False
    result = title_judge(str_del)

    return result


def txt_write(str_write):
    # 将PDF一页内容写到TXT
    filename = r"upload_file/out.txt"
    with open(filename, "w", encoding='utf-8') as f:
        f.write(str_write)
        f.close()

    return filename


def word_seg(str_seg):
    # 分词
    jieba.load_userdict(r"AviationGraph/sourceFile/hkbk.dic")
    seg_list = jieba.lcut_for_search(str_seg, HMM=False)

    return seg_list


def del_punctuation(str_delpunc):
    # 删除文本中中英标点
    punctuation_string = string.punctuation
    for i in punctuation_string:
        str_delpunc = str_delpunc.replace(i, '')
    punctuation_str = string.punctuation
    for i in punctuation_str:
        str_delpunc = str_delpunc.replace(i, '')

    return str_delpunc


