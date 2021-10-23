# -*- coding: utf-8 -*-
import sys

sys.path.append("..")

from AviationGraph.utils.neo4j_models import Neo4j_Handle

# 预加载Neo4j图数据库
neo4jconn = Neo4j_Handle()
neo4jconn.connectDB()
#print('--Neo4j connecting--')

#print('neo4j数据库已启动！！！')
