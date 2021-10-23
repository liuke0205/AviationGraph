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
from application.application_views import home_view, searchAllPdf_view, relation_view, classification_view, QA_view, jointExtraction_view
from application import views

urlpatterns = [
    # 用户注册
    path('register/', views.register),

    # 跳转到 应用系统的主界面
    path('toHome/', home_view.toHome),

    # 联合抽取模块
    path('toJointExtraction/', jointExtraction_view.toJointExtraction),
    path('jointExtraction_upload/', jointExtraction_view.jointExtraction_upload),
    path('joint_extraction/', jointExtraction_view.joint_extraction),
    path('display_re_text/', jointExtraction_view.display_re_text),
    path('download_jointExtract_result/', jointExtraction_view.download_jointExtract_result),
    path('show_progress/', jointExtraction_view.show_progress),

    # 全文搜索功能
    path('toSearchAllPdf/', searchAllPdf_view.toSearchAllPdf),
    path('upload_pdf/', searchAllPdf_view.upload_pdf),
    path('searchAllPdf/', searchAllPdf_view.searchAllPdf),


    # 问答系统
    path('toAnswer/', QA_view.toAnswer),
    path('answer_question/', QA_view.answer_question),

    # 知识搜索 模块
    path('toRelationSearch/', relation_view.toRelationSearch),
    #进行关系查询操作
    path('relation_search/', relation_view.relation_search),

    # 故障信息融合 模块
    path('toClassification/', classification_view.toClassification),
    path('confirmClassication/', classification_view.confirmClassication),
    path('download_classication_file/', classification_view.download_classication_file),

    path('addReason/', classification_view.addReason),
    path('confirmClassication_recommend/', classification_view.confirmClassication_recommend),
    path('upload_classification_train_file/', classification_view.upload_classification_train_file),
    path('upload_classification_test_file/', classification_view.upload_classification_test_file),
    path('display_classication_result/', classification_view.display_classication_result),
]
app_name = "application"