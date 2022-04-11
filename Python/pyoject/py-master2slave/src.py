import pymysql
import os
import sys
import subprocess
import getopt
import logging


logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='test.log',  
                    filemode='w')  

# 创建数据库连接 conn_db
def conn_db(host,port,user,pwd):
    # mysql_host
    # mysql_port
    # mysql_user
    # mysql_pwd
    newdb = pymysql.connect(host=host,
                        user=user,
                        password=pwd,
                        port=port)
    return newdb


# SQL语句
sql_get_matserstatus = "show master status;"
sql_getslave = "show slave hosts;"
sql_isslave = "show slave status;"
sql_slavestatus = "show slave status;"

# 获取数据库身份 get_role
def get_role(db):
    with db.cursor() as cursor:
        # 判定是否为slave
        cursor.execute(sql_isslave)
        result = cursor.fetchone()

        if result:
            # print('is slave.')
            role = 'slave'
        else:
            # is master or not a replica struction.
            # 判定是否为master
            cursor.execute(sql_getslave)
            result = cursor.fetchone()
            if result:
                # print('# is master')
                role = 'master'
            else:
                # print(' is only one node.')
                role = 'onestand'

    return role # 返回role标识。
    '''
    if master -> check_slaves ->vote_slave -> report -> ask switch?
              -> switch -> read only & get gtid -> compare gtid on per slave -> the first slave mark new_master  -> switch to new_master.
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
# 获取slave信息
def get_slaves(db):
    slaves_list = []
    with db.cursor() as cursor:
        # 获取slaves
        cursor.execute(sql_getslave)
        result = cursor.fetchall()

        for slave in result:
            slaves_list.append(str(slave[1])+':'+str(slave[2]))

        print('---->slave:port<----')
        print(slaves_list)  # 或者用dict？
        
    return slaves_list  # 返回一个slaves的列表

# 检查slave状态，check_slave
def check_slave(s_host,s_port,user,pwd):
    # 访问slave，获取show slave status 结果并返回
    # slave = conn_db(s_host,int(s_port),user,pwd)

    # 测试期间临时使用127.0.0.1：48206
    conn_slave = conn_db('127.0.0.1',48206,user,pwd)

    cursor = pymysql.cursors.DictCursor(conn_slave)
    cursor.execute(sql_slavestatus)
    slave_status = cursor.fetchall()
    # print(slave_status)

    # 废弃，转用 pymysql.cursors.DictCursor()
    # with slave.DictCursor() as cursor:
    #     cursor.execute(sql_slavestatus)
    #     result1 = cursor.fetchone()

    return slave_status     # 返回检查slave的slave status dict



# 判定slave存活状态，并计算slave延迟 scan_slaves
def scan_slaves(slaves_list,user,pwd):
    # 存放各slave的 slave status 结果的dict
    slave_status_dict = {}
    for slave in slaves_list:
        host = slave.split(':')[0]
        port = slave.split(':')[1]
        result = check_slave(host,port,user,pwd)            # 这块后续需要使用subprocess等模块实现同时并行check
        slave_status_dict[ host+':'+port ] = result[0]
    return slave_status_dict # 返回这各存放了各slave状态的结果字典


    



# 选举最适合的slave vote_slave
def vote_slave(slave_status_dict):
    # 思路：拿到当前的master的uuid，从Executed_Gtid_Set中截取该UUID对应的GTID，以slave host:GTID 的结构存入dict，
    # 然后做比较，最大的slave被选举出来，并返回最大的slave地址。
    slave_gtid = {}


    for host in slave_status_dict:
        # print(host)
#         print(          # 这一块思路可以以后做主从复制状态检查的report来使用。
# f"""slave_host: {host}
# master_host: {slave_status_dict[host]['Master_Host']}
# slave_io_state: {slave_status_dict[host]['Slave_IO_State']}
# io_thread: {slave_status_dict[host]['Slave_IO_Running']}
# sql_thread: {slave_status_dict[host]['Slave_SQL_Running']}
# rev_gtid: {slave_status_dict[host]['Retrieved_Gtid_Set']}
# exe_gtid: {slave_status_dict[host]['Executed_Gtid_Set']}
# master_uuid: {slave_status_dict[host]['Master_UUID']}
#        """ )


        # 获取属于master 的GTID
        exe_gtid = slave_status_dict[host]['Executed_Gtid_Set'].split('\n')
        for gtid in exe_gtid:
            if gtid.split(':')[0] == slave_status_dict[host]['Master_UUID']:
                slave_gtid[ host ] = gtid.split(':')[1].split(',')[0]       # 如果gtid后面有逗号，处理掉。
                # print(gtid)

    # 根据slave_gtid dict 选择最大的slave
        # 根据value排序dict方法：sorted(key_value.items(), key = lambda kv:(kv[1], kv[0]))
    biggest = sorted(slave_gtid.items(), key = lambda kv:(kv[1], kv[0]))[0]
    # print(biggest)
    return biggest[0]    # final slave host.

# 执行切换 swicth_main

    # 思路：
    #   拿到选举出来的slave地址
    #   master只读，然后记录master的GTID
    #   去选举出来的slave检查rev_gtid，exec。 等exec gtid相等后，reset slave all
    #   去各slave检查exec_GTID，达到master的GTID，reset slave， change master to new master
    #

# 检查slave gtid是否相等master gtid，返回第一个匹配成功的slave地址，及new master
def check_slave_gtid(master_gtid,slave_status_dict,slave_user,slave_pwd):
    pass

def switch_reset_slave(cursor):
    cursor.execute("reset slave all;")

def switch_new_matser(cursor,nm_host,nm_port,nm_user,nm_pwd):
    cursor.execute(f"change master to master_host={nm_host},\
                master_port={nm_port},\
                master_user={nm_user},\
                master_password={nm_pwd},\
                master_auto_position=1;")



def switch_old_master_gtid(master_host,master_port,user,pwd): 
    # take master read only ,and return newest GTID set.
    db = conn_db(master_host,master_port,user,pwd)
    with db.cursor() as cursor:
        cursor.execute("select @@read_only;")
        result_readonly = cursor.fetchone()[0]
        print(result_readonly)

        cursor.execute("set global read_only=0;")

        cursor.execute("show master status;")
        master_gtid_set = cursor.fetchone()[4].split()      # 将gtid转为数组


        cursor.execute("select @@server_uuid;")         # 获取master自己的UUID，用来筛选GTID
        master_uuid = cursor.fetchone()[0]

        # 获取属于master 的GTID set
        for gtid in master_gtid_set:
            # print(gtid)
            if gtid.split(':')[0] == master_uuid:
                master_gtid = gtid.split(':')[1].split(',')[0]       # 如果gtid后面有逗号，处理掉。
                # print(result)
    return master_gtid      # 返回master自己的GTID set，ex: 1-5

def swicth_main(newmaster,user,pwd,oldmaster,slaves):
    
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

for best exprience， use the common username of master and slave.
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
    role = get_role(db)

# 根据role采取行动
# '''
#     if master -> check_slaves ->vote_slave -> report -> ask switch?
#     if slave -> check delay (get master host -> login master -> check_slaves -> vote_slave -> compare with self -> report deference.)
#              -> auto switch (same to if master)
#              -> etc...
# '''
    print(role)
    if role == 'slave':
        pass
    elif role == 'master':
        res = get_slaves(db)
        # for slave in res:
        #     host = slave.split(':')[0]
        #     port = slave.split(':')[1]
        # check_slave(host,port,mysql_user,mysql_pwd)
        slave_status = scan_slaves(res,mysql_user,mysql_pwd)
        # print(slave_status)
        voted_slave = vote_slave(slave_status)      # 选出的slave地址
        print(voted_slave)

        old_master_gtid = switch_old_master_gtid(mysql_host,mysql_port,mysql_user,mysql_pwd)    # 获取到当前master的gtid set


    elif role == 'onestand':
        pass
    else:
        pass


# 主函数执行。
main(sys.argv[1:])