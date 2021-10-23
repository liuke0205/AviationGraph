from django.contrib import messages
from django.shortcuts import render, redirect
from application.models import User, Log

# 注册用户
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        result = User.objects.filter(username=username)
        for user in result:
            if user.username == username:
                messages.success(request, '用户已存在')
                return render(request, 'application/register.html')

        q = User(username=username, password=password)
        q.save()

        # 注册用户的之后，在log表中插入一条“文本标注记录信息”   annotation_id默认值为0
        current_user = User.objects.get(username=username)
        user_id_id = current_user.user_id
        q2 = Log(annotation_id=0, user_id=user_id_id)
        q2.save()

        messages.success(request, '注册成功')
        return render(request, 'login.html', {'username': username, 'password': password})
    return render(request, 'application/register.html')