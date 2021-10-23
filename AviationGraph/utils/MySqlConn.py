import pymysql

class MySqlConn():
    def __init__(self, databaseName):
        self.databaseName = databaseName
        print("----------mysql数据库已连接---------")
    def connectMySql(self):
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root',
                               database=self.databaseName)
        return conn