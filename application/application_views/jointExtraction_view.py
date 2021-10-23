import os
import re

import docx
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect

from AviationGraph.ChinsesNER.main import ChineseNER
# 跳转到关系查询页面
from AviationGraph.utils.utils import write_excel_xls


def toJointExtraction(request):
    return render(request, 'application/joint_extraction.html')


def jointExtraction_upload(request):
    if request.method == 'POST':
        # 获取文件名
        from builtins import str
        path = request.FILES.get('file')
        str_filename = str(path)

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
                print(all_word)
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

        resultList = []
        resultList.append(['头实体', '关系', '尾实体', '原文本', '编号'])
        cn = ChineseNER("predict")
        global num_progress
        for i in range(len(new_senetence_list)):
            # 调用深度学习预测模型
            temp_list = cn.predict(new_senetence_list[i])
            for data in temp_list:
                if len(data) > 0:
                    resultList.append(data)
            num_progress = round(i * 100 / len(new_senetence_list), 2)
        # 抽取完毕后，删除word文件
        if os.path.isfile("upload_file/relation_extraction_word.docx"):
            os.remove("upload_file/relation_extraction_word.docx")

        if os.path.isfile("download_file/jointExact.xls"):
            os.remove("download_file/jointExact.xls")

        # 将结果保存到xlsx文件中
        write_excel_xls("download_file/jointExact.xls", "jointExact", resultList)

        request.session['resultList2'] = resultList
        return redirect('/application/display_re_text/')
    # 2.如果不存在提示还没上传文件
    else:
        messages.success(request, "请上传Word文件！")
        return redirect('/application/toJointExtraction/')


def show_progress(request):
    return JsonResponse(num_progress, safe=False)


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


def display_re_text(request):
    resultList = request.session.get('resultList2')
    if resultList is None or len(resultList) == 0:
        messages.success(request, "请先进行联合抽取！")
        return redirect('/application/toJointExtraction/')
    else:
        return render(request, 'application/joint_extracting_result.html', {'resultList': resultList})
