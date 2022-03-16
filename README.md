# AviationGraph

> 本项目是基于航空领域的知识图谱管理系统。

---

## QuickStart

1. 开启Neo4j服务：neo4j.bat console
2. 开启Redis服务：运行redis-server.exe
3. 项目运行环境在requirements.txt中
   1. 生成requriements.txt： pip freeze > requirements.txt
   2. 生成requriements.txt： pip freeze > requirements.txt
   3. 注意：py2neo版本 2020.0.0
4. 数据库SQL文件：/database文件夹下面


## 文件路径

```html
AviationGraph
|      README.md
|      requirements.txt              运行环境
|      manage.py                     项目启动入口
|      search.py                     查询程序
|
|------AviationGraph                  
|    |    bm25data                  存放bm25程序
|    |    ChinsesNER                NER程序
|    |    DataProcess               数据处理程序
|    |    sourceFile                
|    |    Text_Classification       文本分类
|    |    utils                     工具程序
|
|
|------application                   应用系统
|    |    application_views          应用管理系统的视图
|    |    __init__.py
|    |    admin.py                   
|    |    apps.py                    app配置文件
|    |    models.py                  模型文件
|    |    urls.py                    路由
|    |    views.py                   主视图
|
|
|------management                    管理系统
|    |    application_views          管理系统的视图
|    |    __init__.py
|    |    admin.py
|    |    apps.py                    app配置文件
|    |    models.py                  模型文件
|    |    urls.py                    路由
|    |    views.py                   主视图
|
|
|------staic                         存放页面的静态文件
|------database                      存放数据库文件
|------templates                     存放前端页面文件
|------upload_file                   存放上传的文件
|------download_file                 存放下载的文件

```
## 模块介绍