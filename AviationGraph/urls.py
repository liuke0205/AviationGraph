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
from django.contrib import admin
from django.urls import path
from django.conf.urls import include

from AviationGraph import views



urlpatterns = [
    path('admin/', admin.site.urls),

    #跳转到登录界面
    path('', views.toLogin),

    #用户或管理员登录
    path('login/', views.login),
    # 用户或管理员退出
    path('exit/', views.exit),

    # application APP下面所有的接口，访问需要在原来所有URL前面加上application
    # http://127.0.0.1:8888/application/index
    path('application/', include('application.urls', namespace='application')),

    path('management/', include('management.urls', namespace='management')),
]
