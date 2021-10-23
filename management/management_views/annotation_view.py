import csv
import os
import re

import docx
from django.contrib import messages
from django.shortcuts import render, redirect

from application.models import Log, Annotation, User, Dictionary, Temp, Relation


# 跳转到文本标注页面
def toAnnotation(request):
    user = User.objects.get(username="admin")
    user_id = user.user_id
    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))
    return render(request, 'management/text_annotation.html', {'username': "admin", 'count': count})


# 上传文件，并且将数据保存到数据库中
def upload(request):
    if request.method == 'POST':
        # 获取文件名
        path = request.FILES.get('file')

        str_filename = str(path)
        if str_filename.endswith(".docx") or str_filename.endswith(".doc"):
            if path:
                with open('upload_file/annotation_word.docx', 'wb+') as destination:
                    for chunk in path.chunks():
                        destination.write(chunk)
                # 获取当前用户的id
                user = User.objects.get(username="admin")
                user_id = user.user_id

                new_data = []
                file = docx.Document("upload_file/annotation_word.docx")
                for p in file.paragraphs:
                    data = p.text.replace('\n', '').replace('\t', '')
                    new_data.append(data)
                all_word = "".join(new_data).replace(" ", "")

                pattern = r'。|！|；|;'
                senetence_list = re.split(pattern, str(all_word))
                new_senetence_list = []
                for data in senetence_list:
                    if len(data) > 0:
                        new_senetence_list.append(data + "。")
                        q = Annotation(content=str(data + "。"), file_name=file, flag=False, user_id_id=user_id)  # 将数据插入到数据库中
                        q.save()

                # 读取完毕后，删除word文件
                if os.path.isfile("upload_file/annotation_word.docx"):
                    os.remove("upload_file/annotation_word.docx")
                messages.success(request, "上传成功！")
                return redirect('/management/toAnnotation/')
            else:
                messages.success(request, "文件为空！")
                return redirect('/management/toAnnotation/')
        else:
            messages.success(request, "上传失败，请上传Word文件！")
            return redirect('/management/toAnnotation/')
result = []


# 展示待标注文本信息
def display_text(request):
    global text_current
    ctx = {}
    if request.method == 'POST':
        # 获取当前用户的ID
        user = User.objects.get(username="admin")
        user_id = user.user_id

        # 获取用户的annotation的ID
        log = Log.objects.get(user_id=user_id)
        annotation_id = log.annotation_id

        # 获取当前用户的未标注信息
        annotation_list = Annotation.objects.filter(user_id_id=user_id, flag=False)
        count = len(annotation_list)

        # 获取当前用户的所有标注信息
        if annotation_list:
            # 获取获取当前用户的所有标注信息的最后一个annotation_id
            annotation_last_id = Annotation.objects.filter(user_id_id=user_id).last().annotation_id
            if int(annotation_last_id) == int(annotation_id):
                messages.success(request, '已经到最后一条数据啦，没有可标注的数据啦！')
                return render(request, 'management/text_annotation.html')
            elif int(annotation_id) == 0:
                # 当前“待标注信息”为列表中的第一条数据
                text_current = annotation_list.first()
                text_current.flag = 1
                text_current.save()
                # 更新log表中的annnotation_id的值
                log = Log.objects.get(user_id=user_id)
                log.annotation_id = text_current.annotation_id
                log.save()
            else:
                for data in annotation_list:
                    if data.flag == 0:
                        text_current = data
                        text_current.flag = 1
                        text_current.save()
                        break
                # 更新log表中的annnotation_id的值
                log = Log.objects.get(user_id=user_id)
                log.annotation_id = text_current.annotation_id
                log.save()

            entityList = {}
            # 获取字典的全部信息
            dictionary_entity = Dictionary.objects.all()
            # 获取当前文本的头实体和尾实体
            for entity in dictionary_entity:
                if text_current.content.find(entity.entity) != -1:
                    entityList[entity.entity] = entity.entity_type
            return render(request, 'management/text_annotation.html',
                          {"current_text": text_current.content, 'entityList': entityList, 'ctx': ctx, 'count': count})
        else:
            messages.success(request, '当前用户没有可标注的数据！')
            return render(request, 'management/text_annotation.html')


# 自动标注
def text_annotation(request):
    if request.method == 'POST':
        # 获取当前用户的ID
        user = User.objects.get(username="admin")
        user_id = user.user_id

        # 获取用户的annotation的ID
        log = Log.objects.get(user_id=user_id)
        annotation_id = log.annotation_id
        text_current = Annotation.objects.get(annotation_id=annotation_id)

        # 获取未标注数据的数量
        count = len(Annotation.objects.filter(user_id=user_id, flag=False))

        # 获取当前标注信息的文档名称
        filename = text_current.file_name

        '''
        自动标注 start         ---数据输入：text----
        '''
        # 获取字典的全部信息
        dictionary_entity = Dictionary.objects.all()

        entityList = {}
        # 获取当前文本的头实体和尾实体
        for entity in dictionary_entity:
            if text_current.content.find(entity.entity) != -1:
                entityList[entity.entity] = entity.entity_type

        # headEntity = entityList[0]
        entity_list = []
        for entity in entityList.keys():
            entity_list.append(entity)

        print(entity_list)
        # 对实体进行排列组合
        head_entity = entity_list[0]
        for i in range(1, len(entity_list)):

            # 获取到头实体和尾实体的类型
            headEntityType = Dictionary.objects.get(entity=head_entity).entity_type
            tailEntityType = Dictionary.objects.get(entity=entity_list[i]).entity_type

            # 根据头实体和尾实体来查询之间的关系
            relationList = Relation.objects.filter(head_entity=headEntityType, tail_entity=tailEntityType)

            for relation in relationList:
                # 将数据插入到Temp表
                temp = Temp(headEntity=head_entity, headEntityType=headEntityType, tailEntity=entity_list[i],
                            tailEntityType=tailEntityType, relationshipCategory=relation.relation,
                            annotation_id_id=text_current.annotation_id, filename=filename, user_id=user_id)
                temp.save()
        '''
        自动标注 end ---数据输出：resultList（从数据库中查询出来的一个结果集）   写入到数据库的Temp表中---
        '''
        # 根据annotation_id查询自动识别的数据集合
        resultList = Temp.objects.filter(annotation_id_id=text_current.annotation_id)
        return render(request, 'management/text_annotation.html',
                      {'resultList': resultList, 'current_text': text_current.content, 'entityList': entityList,
                       'count': count})


# 增加一条标注信息
def addTemp(request):
    # 获取当前用户的ID
    user = User.objects.get(username="admin")
    user_id = user.user_id

    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))

    # 获取用户的annotation的ID
    log = Log.objects.get(user_id=user_id)
    annotation_id = log.annotation_id

    # 获取当前文本信息
    current_text = Annotation.objects.get(annotation_id=annotation_id)
    filename = current_text.file_name

    new_headEntity = request.POST.get('headEntity')
    new_headEntityType = request.POST.get('headEntityType')
    new_tailEntity = request.POST.get('tailEntity')
    new_tailEntityType = request.POST.get('tailEntityType')
    new_relationshipCategory = request.POST.get('relationshipCategory')
    temp = Temp(headEntity=new_headEntity, headEntityType=new_headEntityType, tailEntity=new_tailEntity,
                tailEntityType=new_tailEntityType, relationshipCategory=new_relationshipCategory,
                annotation_id_id=annotation_id, filename=filename, user_id=user_id)
    temp.save()

    # 获取字典的全部信息
    dictionary_entity = Dictionary.objects.all()

    entityList = {}
    # 获取当前文本的头实体和尾实体
    for entity in dictionary_entity:
        if current_text.content.find(entity.entity) != -1:
            entityList[entity.entity] = entity.entity_type

    # 获取修改之后的Temp
    resultList = Temp.objects.filter(annotation_id_id=annotation_id)

    return render(request, 'management/text_annotation.html',
                  {'resultList': resultList, 'current_text': current_text.content, 'entityList': entityList,
                   'count': count})


# 删除选中的Temp一条信息
def deleteTemp(request):
    # 获取前端传过来的temp_id
    id = request.GET.get('temp_id')

    # 删除temp_id
    temp = Temp.objects.get(temp_id=id)
    temp.delete()

    # 获取当前用户的ID
    user = User.objects.get(username="admin")
    user_id = user.user_id

    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))

    # 获取用户的annotation的ID
    log = Log.objects.get(user_id=user_id)
    annotation_id = log.annotation_id

    # 获取当前文本信息
    current_text = Annotation.objects.get(annotation_id=annotation_id)

    # 获取删除之后的Temp
    resultList = Temp.objects.filter(annotation_id_id=annotation_id)
    # 获取字典的全部信息
    dictionary_entity = Dictionary.objects.all()

    entityList = {}
    # 获取当前文本的头实体和尾实体
    for entity in dictionary_entity:
        if current_text.content.find(entity.entity) != -1:
            entityList[entity.entity] = entity.entity_type
    return render(request, 'management/text_annotation.html',
                  {'resultList': resultList, 'current_text': current_text.content, 'entityList': entityList,
                   'count': count})


# 修改Temp信息
def modifyTemp(request):
    temp_id = request.POST.get('temp_id')
    new_headEntity = request.POST.get('headEntity')
    new_headEntityType = request.POST.get('headEntityType')
    new_tailEntity = request.POST.get('tailEntity')
    new_tailEntityType = request.POST.get('tailEntityType')
    new_relationshipCategory = request.POST.get('relationshipCategory')

    # 获取前端传过来的信息
    temp = Temp.objects.get(temp_id=temp_id)
    temp.headEntity = new_headEntity
    temp.headEntityType = new_headEntityType
    temp.tailEntity = new_tailEntity
    temp.tailEntityType = new_tailEntityType
    temp.relationshipCategory = new_relationshipCategory
    temp.save()

    # 获取当前用户的ID
    user = User.objects.get(username="admin")
    user_id = user.user_id

    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))

    # 获取用户的annotation的ID
    log = Log.objects.get(user_id=user_id)
    annotation_id = log.annotation_id

    # 获取当前文本信息
    current_text = Annotation.objects.get(annotation_id=annotation_id)

    # 获取修改之后的Temp
    resultList = Temp.objects.filter(annotation_id_id=annotation_id)

    # 获取字典的全部信息
    dictionary_entity = Dictionary.objects.all()

    entityList = {}
    # 获取当前文本的头实体和尾实体
    for entity in dictionary_entity:
        if current_text.content.find(entity.entity) != -1:
            entityList[entity.entity] = entity.entity_type

    return render(request, 'management/text_annotation.html',
                  {'resultList': resultList, 'current_text': current_text.content, 'entityList': entityList,
                   'count': count})


# 增加一条词典信息
def addDictionary(request):
    if request.method == 'POST':
        entity = request.POST.get('entity')
        entity_type = request.POST.get('entity_type')

        # 获取当前用户的ID
        user = User.objects.get(username='admin')
        user_id = user.user_id

        # 获取未标注数据的数量
        count = len(Annotation.objects.filter(user_id=user_id, flag=False))

        # 获取用户的annotation的ID
        log = Log.objects.get(user_id=user_id)
        annotation_id = log.annotation_id

        # 获取当前文本信息
        current_text = Annotation.objects.get(annotation_id=annotation_id)

        # print(entity, entity_type)
        d = Dictionary(entity=entity, entity_type=entity_type)
        d.save()
        # 获取字典的全部信息
        dictionary_entity = Dictionary.objects.all()

        entityList = {}
        # 获取当前文本的头实体和尾实体
        for entity in dictionary_entity:
            if current_text.content.find(entity.entity) != -1:
                entityList[entity.entity] = entity.entity_type

        return render(request, 'management/text_annotation.html',
                      {'current_text': current_text.content, 'entityList': entityList, 'count': count})


def deleteDictionary(request):
    entity = request.GET.get('entity')

    dictionary = Dictionary.objects.get(entity=entity)
    dictionary.delete()

    # 获取当前用户的ID
    user = User.objects.get(username="admin")
    user_id = user.user_id

    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))

    # 获取用户的annotation的ID
    log = Log.objects.get(user_id=user_id)
    annotation_id = log.annotation_id

    # 获取当前文本信息
    current_text = Annotation.objects.get(annotation_id=annotation_id)

    # 获取字典的全部信息
    dictionary_entity = Dictionary.objects.all()

    entityList = {}
    # 获取当前文本的头实体和尾实体
    for entity in dictionary_entity:
        if current_text.content.find(entity.entity) != -1:
            entityList[entity.entity] = entity.entity_type

    return render(request, 'management/text_annotation.html',
                  {'current_text': current_text.content, 'entityList': entityList, 'count': count})


def modifyDictionary(request):
    entity = request.POST.get('entity1')
    entity_type = request.POST.get('entity_type1')

    dictionary = Dictionary.objects.get(entity=entity)
    dictionary.delete()

    # 获取当前用户的ID
    user = User.objects.get(username="admin")
    user_id = user.user_id

    # 获取未标注数据的数量
    count = len(Annotation.objects.filter(user_id=user_id, flag=False))
    # 获取用户的annotation的ID
    log = Log.objects.get(user_id=user_id)
    annotation_id = log.annotation_id
    # 获取当前文本信息
    current_text = Annotation.objects.get(annotation_id=annotation_id)

    # 获取字典的全部信息
    dictionary_entity = Dictionary.objects.all()

    entityList = {}
    # 获取当前文本的头实体和尾实体
    for entity in dictionary_entity:
        if current_text.content.find(entity.entity) != -1:
            entityList[entity.entity] = entity.entity_type

    return render(request, 'management/text_annotation.html',
                  {'current_text': current_text.content, 'entityList': entityList, 'count': count})
