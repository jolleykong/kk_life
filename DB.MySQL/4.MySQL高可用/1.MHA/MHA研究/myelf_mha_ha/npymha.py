import os
import time
import configparser

######## 指定MHA配置文件
appconf='/data/mha/app1/app1.conf'
defaultconf='/data/mha/app1/default.conf'

vip='192.168.188.50'


######### 读取global default配置文件，获取mysql_user\replication_user\os_ssh_user
conn_default = configparser.ConfigParser()
conn_default.read(defaultconf)
items_default = conn_default.items('server default')
items_default = dict(items_default)

    #### default.conf key helper ####
    ##           ITEM : KEY
    ##
    ##        os root : ssh_user      : items_default['ssh_user']
    ##     mysql root : user          : items_default['user']
    ## mysql root pwd : password      : items_default['password']
    ## mysql rep user : repl_user     : items_default['repl_user']
    ##  mysql rep pwd : repl_password : items_default['repl_password']
    ##
    ############## END ##############



######### 读取app配置文件，获取node配置的个数
con_app = configparser.ConfigParser()
con_app.read(appconf)
sections_app = con_app.sections()
# 排除[server default] 部分。（这部分用来指定dir）
sections_app.remove('server default')

    ## node members
    # print(sections_app)
    ## node count
    # len(sections_app)


######## 读取每个node的IP，生成node:ip,port 的kv
node_ip={}

for i in sections_app:
    node_ip[i]=dict(con_app.items(i))['hostname'],dict(con_app.items(i))['port']

    ## print(node_ip)

# 检查vip绑定在哪个节点上，确定当前master节点
def check_vip(v_node_ip,v_vip) :
    is_vip={}
    # 拿到kv，通过ssh连接验证，返回结果Y/N
    for i in v_node_ip :
        node_result = os.system("ssh root@"+v_node_ip[i][0]+ " ip addr | grep 'inet 192' | awk -F '[/]' '{print $1}' | awk '{print $2}' | grep "+ v_vip +" >/dev/null")
        if node_result == 0 :
            is_vip['Y']=[i]        
        elif node_result == 256 :
            if 'N' in is_vip :
                cache = []
                for is_v_n in is_vip['N'] :
                    cache.append(is_v_n)
                cache.append(i)
                # print(cache)
                is_vip['N'] = cache
            else :
                is_vip['N']=[i]
        else :
            if 'unknow' in is_vip :
                cache = []
                for is_v_n in is_vip['unknow'] :
                    cache.append(is_v_n)
                cache.append(i)
                # print(cache)
                is_vip['unknow'] = cache
            else :
                is_vip['unknow']=[i]
    return is_vip

# return is_vip dict
# is_vip = check_vip(node_ip,vip)


# # 查看VIP相对于配置文件的绑定结果，结果并不能说明节点mysql是否存活，所以已经down掉的slave也会显示在N中。。
def node_map(v_is_vip) :
    # warning_msg = ''
    node_map_cache = []
    for k in v_is_vip:
        node_map_cache.append( "[is vip?] " + k + " , node(s):" + str(v_is_vip[k]) )
    return node_map_cache

def no_vip_warning(v_is_vip) :
    if v_is_vip.get('Y') is None :
        return 'Y'
    # # return node_map_cache
    # # 如果没有vip绑定在节点上， 那么说明vip绑定存在问题，需要管理员介入。 这部分独立成新函数。
    # 
    #     # warning_msg = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " [ERROR] " + "Cluster VIP is UNAVALIABLE!"
    #     # print(warning_msg)


# return node mapping and msg.
# for line in node_map(is_vip) :
#     print(line)

# if is_vip.get('Y') is not None :
# 生成以当前master节点为目标的change master 命令
# master_host = "".join( node_ip[ ''.join(is_vip['Y']) ][0])
# master_port = "".join( node_ip[ ''.join(is_vip['Y']) ][1])
# rep_user = items_default['repl_user']
# rep_pwd = items_default['repl_password']

# # 生成change master SQL语句
# change_master_sql = "change master to master_host='"+ master_host +"',master_port=" + str(master_port) +" , master_user='" + rep_user +"', master_password='" + rep_pwd + "', master_auto_position=1;" 


def make_change_sql(v_is_vip) :
    master_host = "".join( node_ip[ ''.join(v_is_vip['Y']) ][0])
    master_port = "".join( node_ip[ ''.join(v_is_vip['Y']) ][1])
    rep_user = items_default['repl_user']
    rep_pwd = items_default['repl_password']
    # 生成change master SQL语句
    change_master_sql = "change master to master_host='"+ master_host +"',master_port=" + str(master_port) +" , master_user='" + rep_user +"', master_password='" + rep_pwd + "', master_auto_position=1;" 
    return change_master_sql


###################### 找出并恢复死掉的节点，后续完善，现在不会写。
# # check rpl ,find error node  # + " | tail -5 | grep 'is dead,'"
# rpl_check_command = ("masterha_check_repl --global_conf=" + defaultconf + " --conf=" + appconf  )
# # 如何实现抓取到dead node的IP呢？
# rplchk_out=os.popen( rpl_check_command )

# 改用一种取巧的方式先实现，但是不适合节点太多，以及某些特殊场景。

# 获取 root 密码。 获取 mysql root 密码，获取节点地址

# step 1. 先检测哪个mysql无法访问了
def check_fail_mysql() :
    # node_ip --> section:ip,port
    # sections_app --> sections in app.conf
    for node in sections_app :
        ##        os root : ssh_user      : items_default['ssh_user']
        ##     mysql root : user          : items_default['user']
        ## mysql root pwd : password      : items_default['password']
        ## mysql rep user : repl_user     : items_default['repl_user']
        ##  mysql rep pwd : repl_password : items_default['repl_password']
        # node_ip[node][0] , 获取地址
        fail_list =[]
        print( node_ip[node][0] )
        check_fail_result = os.system("mysql -h " + node_ip[node][0] + " -P " + node_ip[node][1] + " -u " + items_default['user'] + " -p" + items_default['password'] + " -e 'select 1; '"  )
        if check_fail_result == 256 :
            fail_list.append(node)
        return fail_list


# step 2. 再检测这个mysql的server是否可以ssh
def check_fail_server(v_fail_list) :
    # [1]. server dead
    # [2]. mysql dead
    # server_status = server:1|2
    server_status = {}
    for node in v_fail_list :
        check_fail_result = os.system("ssh " + items_default['ssh_user'] + "@" + node_ip[node][0] + " ls" )
        if check_fail_result == 256 :
            # 节点死了
            print('server dead')
            server_status[node] = 1
        else :
            # mysql 死了
            print('mysqld dead')
            server_status[node] = 2
    return server_status

# step 3. 如果可以ssh，通过ssh拉起服务，change master.
def rec_dead_mysql(v_dead_node,v_is_vip) :
    # v_is_vip 用来通过make_change_sql() 生成当前master ip的change语句。
    # v_dead_node 可以是一个list，包含无法访问的节点IP
    if type(v_dead_node) == str :
        v_dead_node = [v_dead_node]
    for node in v_dead_node :
        rec_command = os.system("ssh " + items_default['ssh_user'] + "@" + node_ip[node][0] + " '/usr/local/mysql/bin/mysqld --defaults-file=/data/mysql/mysql3307/my3307.cnf &'" )
        if rec_command == 0 :
            # set read only and change master
            sql = make_change_sql(v_is_vip)
            os.system("mysql -h " + node_ip[node][0] + " -P " + node_ip[node][1] + " -u " + items_default['user'] + " -p" + items_default['password'] + " -e 'set global read_only=1; exit;'"   )
            os.system("mysql -h " + node_ip[node][0] + " -P " + node_ip[node][1] + " -u " + items_default['user'] + " -p" + items_default['password'] + " -e 'reset slave; exit;'"   )
            change_command = os.system("mysql -h " + node_ip[node][0] + " -P " + node_ip[node][1] + " -u " + items_default['user'] + " -p" + items_default['password'] + " -e " + "'" + sql +"'" )
            if change_command == 0 :
                change_command = os.system("mysql -h " + node_ip[node][0] + " -P " + node_ip[node][1] + " -u " + items_default['user'] + " -p" + items_default['password'] + " -e  start slave;" )
                return (0)
            else :
                # print('change master not done.')
                return(1)
        else :
            # print('recover mysql service not done.')
            return(0)
        


# step 4. 如果不可以ssh，说明节点彻底死了，放弃该节点——删除配置. 如果change master 失败，也删除配置。
    # app_file == con_app
# 通过查询找到失败节点的section

# 删除失败的section
def remove_fail_section(fail_server) :
    # 将配置文件赋给临时变量
    new_app_conf = con_app
    new_app_conf.remove_section( fail_server )
    # 写入变更
    new_app_conf.write( open(appconf,'w') )



# # 
mha_check_result = ()


while True :
    masterha_check_status_command = ("masterha_check_status --global_conf=" + defaultconf + " --conf=" + appconf )
    cmdout=os.popen( masterha_check_status_command )
    lines=cmdout.readlines()
    mha_check_result = "".join(lines).strip()
    print(mha_check_result)

    if 'ok' in mha_check_result.lower():
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " [CHECK] " + "Cluster Status Check is OKay!")
        # 执行vip与节点关系、并做有效性检查，输出检查结果
        ok_result = node_map( check_vip(node_ip,vip) )
        # no VIP
            # is_vip=check_vip(node_ip,vip)
            # vip_warning_status = no_vip_warning( is_vip )
        if no_vip_warning( check_vip(node_ip,vip) ) == 'Y' :
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " [ERROR] " + "Cluster VIP unavaliable!")

        # 输出配置文件中的存活节点
        for result in ok_result :
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " [INFOS] " + result.strip())

        
        # 输出集群检查结果及配置文件？
    elif 'stop' in mha_check_result.lower():
        print('maybe stopped.')
        # 找到失败的节点
        # 思路，manager停止就意味着发生了failover，那么去执行检查，结果的最后5行内会有报错信息，如：
            # [error][/usr/share/perl5/vendor_perl/MHA/ServerManager.pm, ln492]  Server 192.168.188.53(192.168.188.53:3307) is dead, but must be alive! Check server settings.
        # 通过这种方式拿到server地址，然后执行ssh操作，拉起节点，change to new_master，然后拉起manager【这块不太严谨】
        #masterha_check_repl --global_conf=/data/mha/app1/default.conf --conf=/data/mha/app1/app1.conf
        # os.popen("masterha_check_repl --global_conf=" + defaultconf + " --conf=" + appconf)
        # 返回vip及node关系
        is_vip = check_vip(node_ip,vip)
        # step 1. 检查无法访问的mysql节点
        fail_list = check_fail_mysql()
        # step 2. 检查1结果中是否可以ssh，返回状态dict，1为服务器dead，2为mysqld dead
        if len(fail_list) == 0 :
            os.system("nohup masterha_manager --global_conf=" + defaultconf + " --conf=" + appconf  + " &" )
            restart_mng_msg = ("masterha_check_status --global_conf=" + defaultconf + " --conf=" + appconf  + " &" )
            ## 这块有问题，需要想想、

        print(fail_list)
        server_status_dict = check_fail_server(fail_list)
        for node in server_status_dict :
            if server_status_dict[node] == 1 :
                None 
                print('jump')
                # 执行清理节点
            elif server_status_dict[node] == 2 :
                # 需要重新拉起mysql
                    # 通过check_vip(),得到is_vip 的node IP，用来生成change 语句
                    # node 为需要重新拉起的节点IP(s)
                rec_stat = rec_dead_mysql(node,is_vip)
                print(rec_stat)
                if rec_stat == 1 :
                    print('恢复失败，需要DBA手动检查')
                elif rec_stat == 0 :
                    # 重新启动MHA manager
                    #   --global_conf=/etc/masterha/masterha_default.cnf  --conf=/etc/masterha/app1.cnf &
                    # 执行manager拉起        
                        # 初期实现目标：拉起mysql，change master to new_master
                        # 远期实现目标：从备份拉起mysql，change master to new_master
                    restart_mng_msg = os.system("nohup masterha_manager --global_conf=" + defaultconf + " --conf=" + appconf  + " &" )
                    if restart_mng_msg == 1 :
                        print('restrat MHA manager successed!')
                    elif restart_mng_msg == 256 :
                        print('restrat MHA manager failed!')
                else :
                    print('Unknown error, code 12.')
            else :
                print('Unknown error, code 11.')
    else :
        print(mha_check_result.lower())
        print('I am SB.')

    time.sleep(10)

