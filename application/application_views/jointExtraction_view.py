import os
import threading
import docx
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect
import xlrd as xd


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

        if str_filename.endswith(".docx") or str_filename.endswith(".doc"):
            if path:
                if os.path.isfile("upload_file/relation_extraction_word.docx"):
                    os.remove("upload_file/relation_extraction_word.docx")
                with open('upload_file/relation_extraction_word.docx', 'wb+') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)
                '''
                数据 ->  E:\01-科研资料\03-项目工程\Joint-Extract\data\delu\根据数据集\predict\predict.txt && []
                '''
                new_data = []
                with open("E:\\01-科研资料\\03-项目工程\\Joint-Extract\\data\\delu\\" + data_type[5:] + "\\\predict\predict.txt", "w", encoding="utf-8") as f:
                    for p in docx.Document("upload_file/relation_extraction_word.docx").paragraphs:
                        f.write(p.text + "\n")
                        new_data.append(p.text)
                f.close()
                all_word = "\n".join(new_data)
                request.session['all_word'] = all_word
                return render(request, 'application/joint_extraction.html', {'str': all_word, 'data_type' : data_type})
            else:
                messages.success(request, "文件为空！")
                return redirect('/application/toJointExtraction/')
        else:
            messages.success(request, "上传失败，请上传Word文件！")
            return redirect('/application/toJointExtraction/')


# 读取待识别文本并转化成所要形式
def joint_extraction(request):
    data_type = request.session.get('data_type')
    # 1.先读取upload_file/relation_extraction_word.docx 看是否存在
    import os.path
    if os.path.isfile("upload_file/relation_extraction_word.docx"):
        # 开启一个线程去执行预测任务
        thread = predictThread(1, data_type=data_type)
        thread.start()
        return redirect('/application/display_re_text/')
    # 2.如果不存在提示还没上传文件
    else:
        messages.success(request, "请上传待抽取的文件！")
        return redirect('/application/toJointExtraction/')

# 使用深度学习预测
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
        # os.system(
        #     "cd E:\\01-科研资料\\03-项目工程\\Joint-Extract &&  conda activate joint-extract && python predict.py " + self.data_type)
        os.system(
            "cd E:\\01-科研资料\\03-项目工程\\Joint-Extract &&  conda activate joint-extract && python predict.py " + self.data_type + " && conda deactivate joint-extract")

        print("退出线程：" + self.name)


def download_jointExtract_result(request):
    if os.path.isfile("download_file/jointExact.xls"):
        file = open('download_file/jointExact.xls', 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="jointExact.xls"'
        return response
    else:
        messages.success(request, "抱歉，当前没有抽取结果！")
        return redirect('/application/toJointExtraction/')


def display_re_text(request):
    # 读取 download_file/jointExtract.xls 文件，将其转化为二维列表的形式
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
        messages.success(request, "抱歉，当前没有抽取结果！")
        return redirect('/application/toJointExtraction/')