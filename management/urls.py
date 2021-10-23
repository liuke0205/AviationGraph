"""AviationGraph URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from management import views
from management.management_views import d2rq_view, excel_view, word_view, annotation_view, dataManager_view, home_view, \
    jointExtraction_management_view, active_annotation_view
urlpatterns = [
    #管理端-主界面
    path('toHome/', home_view.toHome),

    #数据库抽取界面
    path('toD2rq/', d2rq_view.toD2rq),
    # 选择数据库管理系统名
    path('commitDatabase/', d2rq_view.commitDatabase),
    # 提交数据库连接配置
    path('commitConfiguration/', d2rq_view.commitConfiguration),
    # 获取选中的表名
    path('getTable/', d2rq_view.getTable),
    ##从关系数据库中抽取知识
    path('d2neo4j/', d2rq_view.d2neo4j),


    # 联合抽取模块
    path('toJointExtraction/', jointExtraction_management_view.toJointExtraction),
    path('jointExtraction_upload/', jointExtraction_management_view.jointExtraction_upload),
    path('joint_extraction/', jointExtraction_management_view.joint_extraction),
    path('display_re_text/', jointExtraction_management_view.display_re_text),
    path('download_jointExtract_result/', jointExtraction_management_view.download_jointExtract_result),
    path('show_progress/', jointExtraction_management_view.show_progress),
    path('addCorpus/', jointExtraction_management_view.addCorpus),
    path('deleteCorpus/', jointExtraction_management_view.deleteCorpus),
    path('modifyCorpus/', jointExtraction_management_view.modifyCorpus),

    # 跳转到Excel知识抽取界面
    path('toExcel/', excel_view.toExcel),
    path('upload_excel/', excel_view.upload_excel),
    path('commit_properties/', excel_view.commit_properties),
    path('excel_extract/', excel_view.excel_extract),


    #基于规则的Word提取
    path('toWord/', word_view.toWord),
    path('upload_word/', word_view.upload_word),
    path('display_word_result/', word_view.display_word_result),
    path('wordExtractInsertNeo4j/', word_view.wordExtractInsertNeo4j),



    # 跳转到标注页面
    path('toAnnotation/', annotation_view.toAnnotation),
    # 文本标注文件上传
    path('upload/', annotation_view.upload),
    # 显示待标注文本信息
    path('display_text/', annotation_view.display_text),
    # 自动标注
    path('text_annotation/', annotation_view.text_annotation),
    # 增加一条字典信息
    path('addDictionary/', annotation_view.addDictionary),
    # 删除一条字典信息
    path('deleteDictionary/', annotation_view.deleteDictionary, name='deleteDictionary'),
    # 修改一条字典信息
    path('modifyDictionary/', annotation_view.modifyDictionary),
    # 删除标注文本信息
    path('deleteTemp/', annotation_view.deleteTemp, name='deleteTemp'),
    # 修改文本信息
    path('modifyTemp/', annotation_view.modifyTemp),
    # 增加一条文本信息
    path('addTemp/', annotation_view.addTemp),

    path('toDataManager/', dataManager_view.toDataManager),
    #将一条数据插入到neo4j数据库
    path('importNeo4j/', dataManager_view.importNeo4j),
    #批量导入
    path('importNeo4jMuilt/', dataManager_view.importNeo4jMuilt),
    #删除
    path('deleteNeo4j/', dataManager_view.deleteNeo4j),



    # 跳转到主动学习标注页面
    path('toActiveAnnotation/', active_annotation_view.toActiveAnnotation),
    # 主动学习标注文件上传
    path('activeAnnotationUpload/', active_annotation_view.activeAnnotationUpload),
    # 向管理员推荐下一条待标注的数据
    path('recommendNextData/', active_annotation_view.recommendNextData),
    #增加一条标注信息
    path('addAnnotation/', active_annotation_view.addAnnotation),
    #删除一条标注信息
    path('deleteAnnotation/', active_annotation_view.deleteAnnotation),
    #修改一条标注信息
    path('modifyAnnotation/', active_annotation_view.modifyAnnotation),

]
app_name = "management"