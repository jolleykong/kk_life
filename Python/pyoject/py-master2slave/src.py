import pymysql
import os
import sys
import subprocess
import getopt
import logging

# 创建数据库连接 conn_db
def conn_db(host,port,user,pwd):
    # mysql_host
    # mysql_port
    # mysql_user
    # mysql_pwd
    # host: str | None = ..., user: Any | None = ..., password: str = ..., database: Any | None = ..., port: int 
    newdb = pymysql.connect(host=host,
                            user=user,
                            password=pwd,
                            port=port)
    return newdb


# SQL语句
sql_get_matserstatus = "show master status;"
sql_getslave = "show slave hosts;"
sql_isslave = "show slave status;"

# 获取数据库身份 get_role
def get_role(db):
    with db.cursor() as cursor:
        # 判定是否为slave
        cursor.execute(sql_isslave)
        result = cursor.fetchall()  # 需要后续看下手册
        if result:
            print('is slave.')
        else:
            print('# is master or not a replica struction.')
            # 判定是否为master
            cursor.execute(sql_getslave)
            result = cursor.fetchall()
            if result:
                print('# is master')
            else:
                print(' is only one node.')
    return None # 计划返回role标识。
    '''
    if master -> check_slaves ->vote_slave -> report -> ask switch?
    if slave -> check delay (get master host -> login master -> check_slaves -> vote_slave -> compare with self -> report deference.)
             -> auto switch (same to if master)
             -> etc...
    [X][abandon]if slave -> swicth to self? -> get master host -> login master -> check_slaves -> get other slaves -> change master to self.
    '''

'''
with connection:
    # create db
    with connection.cursor() as cursor:
        sql1 = "show master status;"
        # sql2 = "create database yy"
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        print(result1)
'''
# 判定slave存活状态，并计算slave延迟 check_slaves
def check_slaves():
    pass

# 选举最适合的slave vote_slave
def vote_slave():
    pass

# 执行切换 swicth
def swicth():
    pass


# print(sys.argv[0],sys.argv[1])

def main(argv):
    #argv = sys.argv[1:]

    opts,args = getopt.getopt(argv,"h:p:u:P:")
    # print(opts,len(opts))

    mysql_port = ''
    mysql_host = ''
    mysql_pwd  = ''
    mysql_user = ''

    # 参数数量不够4个则抛出提示。
    if len(opts) != 4:
        print('''
usage:
    -h mysqlhost -P mysqlport -u mysqluser -p mysqlpassword
        ''')
    else:
        # 将命令行参数赋值给参数
        for opt,arg in opts:
            if opt == '-h': mysql_host = arg
            elif opt == '-P': mysql_port = int(arg)
            elif opt == '-u': mysql_user = arg
            elif opt == '-p': mysql_pwd = arg
    # print(mysql_port,mysql_host,mysql_pwd,mysql_user)

# make db connection 创建数据库连接
    db = conn_db(mysql_host,mysql_port,mysql_user,mysql_pwd)

# decide connection db is master/slave. 判定数据库身份
    get_role(db)


# 主函数执行。
main(sys.argv[1:])