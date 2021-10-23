# -*- coding: utf-8 -*-
import datetime

from django.contrib import messages
from django.shortcuts import render, redirect

from AviationGraph.utils.MySqlConn import MySqlConn
from application.models import User, Log

# 跳转到登录界面
def toLogin(request):
    return render(request, "login.html")

# 用户登录
def login(request):
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        print(password)
        print(role)
        if role == "admin":
            if username == "admin" and password == "admin":
                return redirect("/management/toHome/")
            messages.success(request, '不存在该用户，登录失败！')
            return render(request, 'login.html')
        elif role == "user":
            result = User.objects.filter(username=username)
            # 连接关系数据库
            conn1 = MySqlConn('source').connectMySql()
            cursor = conn1.cursor()
            for user in result:
                if user.password == password:
                    request.session['username'] = username
                    sql = "INSERT INTO login_log(username, login_time) VALUES ('%s','%s')" % (
                    username, datetime.datetime.now())
                    cnt = cursor.execute(sql)
                    conn1.commit()

                    sql_select = "SELECT * FROM login_log"
                    cursor.execute(sql_select)
                    conn1.commit()
                    number = len(cursor.fetchall())
                    request.session['number'] = number
                    conn1.close()
                    return redirect("/application/toHome/")
        messages.success(request, '不存在该用户，登录失败！')
        return render(request, 'login.html')
    return render(request, 'login.html')

def exit(request):
    return render(request, 'login.html')