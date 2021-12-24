import os
import configparser

######## 检查vip 配置
appconf='/data/mha/app1/app1.conf'
defaultconf='/data/mha/app1/default.conf'
vip='192.168.188.50'


######### 读取default配置文件，获取mysql_user\replication_user\os_ssh_user
conn_default = configparser.ConfigParser()
conn_default.read(defaultconf)
items_default = conn_default.items('server default')
items_default = dict(items_default)

    #### default.conf key helper ####
    ##           ITEM : KEY
    ##
    ##        os root : ssh_user
    ##     mysql root : user
    ## mysql root pwd : password
    ## mysql rep user : repl_user
    ##  mysql rep pwd : repl_password
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
#print(node_ip)

# 检查vip绑定在哪个节点上，确定当前master节点
is_vip={}

    # 拿到kv，通过ssh连接验证，返回结果Y/N
for i in node_ip :
    node_result = os.system("ssh root@"+node_ip[i][0]+ " ip addr | grep 'inet 192' | awk -F '[/]' '{print $1}' | awk '{print $2}' | grep "+ vip +" >/dev/null")
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


# 查看VIP相对于配置文件的绑定结果，结果并不能说明节点mysql是否存活，所以已经down掉的slave也会显示在N中。。
for k in is_vip:
    print( "[is vip?] " + k + " , node(s):" + str(is_vip[k]) )
# 如果没有vip绑定在节点上， 那么说明vip绑定存在问题，需要管理员介入。
if is_vip.get('Y') is None :
    print('There is not any node has been bond vip, Needed check the cluster status and vip status!')



# 生成以当前master节点为目标的change master 命令
master_host = "".join( node_ip[ ''.join(is_vip['Y']) ][0])
master_port = "".join( node_ip[ ''.join(is_vip['Y']) ][1])
rep_user = items_default['repl_user']
rep_pwd = items_default['repl_password']
# print("change master to master_host='"+ master_host +"',master_port=" + str(master_port) +" , master_user='" + rep_user +"', master_password='" + rep_pwd + "', master_auto_position=1;" )

# 生成change master SQL语句
change_master_sql = "change master to master_host='"+ master_host +"',master_port=" + str(master_port) +" , master_user='" + rep_user +"', master_password='" + rep_pwd + "', master_auto_position=1;" 
# print(change_master_sql)



# 