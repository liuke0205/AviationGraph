import os
import re
import threading
import docx
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect


def toJointExtraction(request):
    return render(request, 'application/joint_extraction.html')


def jointExtraction_upload(request):
    if request.method == 'POST':
        # 获取文件名
        from builtins import str
        path = request.FILES.get('file')
        str_filename = str(path)
        data_type = request.POST.get('data_type')
        request.session['data_type'] = data_type

        # 数据 ->  E:\01-科研资料\03-项目工程\Joint-Extract\data\delu\根据数据集\predict\predict.txt

        if str_filename.endswith(".docx") or str_filename.endswith(".doc"):
            if path:
                if os.path.isfile("upload_file/relation_extraction_word.docx"):
                    os.remove("upload_file/relation_extraction_word.docx")
                with open('upload_file/relation_extraction_word.docx', 'wb+') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)
                '''
                先将所有语句取出换行和\t 去除，然后合到一起，最后再按照句号分句
                '''
                new_data = []
                for p in docx.Document("upload_file/relation_extraction_word.docx").paragraphs:
                    data = p.text.replace('\n', '').replace('\t', '')
                    new_data.append(data)
                all_word = "".join(new_data).replace(" ", "")
                request.session['all_word'] = all_word
                return render(request, 'application/joint_extraction.html', {'str': all_word})
            else:
                messages.success(request, "文件为空！")
                return redirect('/application/toJointExtraction/')
        else:
            messages.success(request, "上传失败，请上传Word文件！")
            return redirect('/application/toJointExtraction/')


# 读取待识别文本并转化成所要形式
def joint_extraction(request):
    data_type = request.session.get('data_type')
    print(data_type)
    # 1.先读取upload_file/relation_extraction_word.docx 看是否存在
    import os.path
    if os.path.isfile("upload_file/relation_extraction_word.docx"):
        # 3.如果已经上传进行抽取，抽取完后删除
        new_data = []
        for p in docx.Document("upload_file/relation_extraction_word.docx").paragraphs:
            data = p.text.replace('\n', '').replace('\t', '')
            new_data.append(data)
        all_word = "".join(new_data).replace(" ", "")

        pattern = r'。|！|；|;'
        senetence_list = re.split(pattern, str(all_word))
        new_senetence_list = []
        for data in senetence_list:
            if len(data) > 0:
                new_senetence_list.append(data + "。")

        # 将session域初始化
        request.session['resultList'] = []

        # 开启一个线程去执行预测任务
        thread = predictThread(1, data_type=data_type)
        thread.start()

        return redirect('/application/display_re_text/')
    # 2.如果不存在提示还没上传文件
    else:
        messages.success(request, "请上传Word文件！")
        return redirect('/application/toJointExtraction/')

# 建立索引的线程
class predictThread (threading.Thread):
    def __init__(self, threadID, data_type):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.data_type = data_type
    def run(self):
        print("开始线程：" + self.name)

        if os.path.isfile("upload_file/relation_extraction_word.docx"):
            os.remove("upload_file/relation_extraction_word.docx")

        if os.path.isfile("download_file/jointExact.xls"):
            os.remove("download_file/jointExact.xls")

        # 代码 ->  E:\01-科研资料\03-项目工程\Joint-Extract\predict.py
        # resultList.append(['头实体', '关系', '尾实体', '原文本'])
        os.system("conda activate joint-extract && python E:\\01-科研资料\\03-项目工程\\Joint-Extract\\predict.py " + self.data_type)
        # os.system("python E:\\01-科研资料\\03-项目工程\\Joint-Extract\\predict.py " + self.data_type)
        # os.system("conda deactivate joint-extract")

        print("退出线程：" + self.name)


def download_jointExtract_result(request):
    if os.path.isfile("download_file/jointExact.xls"):
        file = open('download_file/jointExact.xls', 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="jointExact.xls"'
        return response
    else:
        messages.success(request, "请先进行联合抽取！")
        return redirect('/application/toJointExtraction/')


import xlrd as xd
def display_re_text(request):
    # 读取 E:\01-科研资料\03-项目工程\AviationGraph\download_file\jointExtract.xls 文件，将其转化为二维列表的形式
    if os.path.isfile("download_file/jointExact.xls"):
        data = xd.open_workbook('download_file/jointExact.xls')  # 打开excel表所在路径
        sheet = data.sheet_by_name('jointExact')  # 读取数据，以excel表名来打开
        resultList = []
        for r in range(sheet.nrows):  # 将表中数据按行逐步添加到列表中，最后转换为list结构
            data1 = []
            for c in range(sheet.ncols):
                data1.append(sheet.cell_value(r, c))
            resultList.append(list(data1))
            return render(request, 'application/joint_extracting_result.html', {'resultList': resultList})
    else:
        messages.success(request, "请先进行联合抽取！")
        return redirect('/application/toJointExtraction/')
