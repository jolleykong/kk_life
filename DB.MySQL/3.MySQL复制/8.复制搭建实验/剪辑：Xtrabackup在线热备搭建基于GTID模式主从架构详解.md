# 剪辑：Xtrabackup在线热备搭建基于GTID模式主从架构详解

应用初始阶段都是mysql单库支撑，随着应用的访问量不断增长，数据库压力越来越大，就需要考虑搭建主从架构，从而拓展整个数据库层面的吞吐能力，所以不停mysql服务做从库是DBA必须掌握的基础技能之一，percona提供了xtrabackup实现在线热备做从库,下面就讲解下具体的实现步骤：



## 配置SSH

1. ssh-keygen -t rsa 生成密匙

   ```
   ssh-keygen -t rsa
   ```

2. 用ssh-copy-id将公钥复制到远程机器中

   ```
   ssh-copy-id -i .ssh/id_rsa.pub  root@remoteIP
   ```

    拷贝过程中需要输入一次密码。成功之后就可以直接ssh remoteIP.

   



## 初始化备份工具xtrabackup以及qpress

- 工具包准备以及安装
  - 这里我用的官方的二进制包：
		
		> qpress:http://www.quicklz.com/qpress-11-linux-x64.tar

- 执行初始化安装脚本
    ```
    #!/bin/bash 
    #install xtrabackup 
    cd /home
    tar -zxvf percona-xtrabackup-2.4.12-Linux-x86_64.libgcrypt145.tar.gz
    mv percona-xtrabackup-2.4.12-Linux-x86_64 /usr/local/xtrabackup
    ln -sf /usr/local/xtrabackup/bin/* /usr/bin/ 
    xtrabackup --version

    #install qpress 
    tar xvf qpress-11-linux-x64.tar
    cp qpress /usr/bin
    qpress --help
    123456789101112
    ```



## 检查文件句柄数设置

经常由于之前没有设置足够大的值，导致报too many file err错误。



### 句柄设置方式

- 永久生效方式：

```
vim /etc/security/limits.conf
#添加两行：
* soft nofile 65535  
* hard nofile 65535
1234
```

- 临时修改方案：

```
ulimit -SHn 65535
1
```



## 开发备份脚本

```
#!/bin/bash 
#数据库用户名
dbuser='bakup'
#数据库用密码
dbpasswd='123456'
#hosts
dbhost='127.0.0.1'
#日志备份路径
logpath='/home/xtrabackup'
#日志记录头部
tmpdir='/home/xtrabackuptmp'
#远程机器目标位置
remoteDir='/home/databack/'
#远程机器目标位置
remoteIp='192.168.1.1'
#远程机器账户
remoteUser='root'

xtrabackuplogpath='/home/xtrabackuplog1.log'
backtime=`date +%Y%m%d%H%M%S`
dirName=${dbhost}${backtime}
echo "--${backtime},${dbhost}备份数据库开始--" >> ${logpath}/xtrabackuplog.log
echo "--${backtime},${dbhost}备份数据库开始--" >> ${xtrabackuplogpath}
#远程创建文件夹
ssh ${remoteUser}@${remoteIp} "mkdir ${remoteDir}/${dirName}"
#远程备份
xtrabackup --host=${dbhost} --user=${dbuser} --password=${dbpasswd} --backup --no-timestamp --ftwrl-wait-timeout=10 --tmpdir=${tmpdir}  --compress  --compress-threads=8 --stream=xbstream --parallel=8  | ssh ${remoteUser}@${remoteIp} "xbstream -x -C ${remoteDir}/${dirName}"
endtime=`date +%Y%m%d%H%M%S`
lastStr=$(tail -n -1 ${xtrabackuplogpath})
successStr='completed OK'
result=$(echo $lastStr | grep "${successStr}")
if [[ "$result" != "" ]]
then
  echo "--${endtime},${dbhost}数据库备份完成--" >> ${logpath}/xtrabackuplog.log
else
  echo "--${endtime},${dbhost}数据库备份失败!!--" >> ${logpath}/xtrabackuplog.log
fi
echo "--${endtime},${dbhost}备份数据库结束--" >> ${logpath}/xtrabackuplog.log
关于xtrabackup参数这里就不在过多讲解，其他就是一些备份账户 dbuser dbpasswd dbhost 远程目标机器账户remoteUser remoteIp以及存放数据的文件路径remoteDir，一定要注意远程目标机器上必须存在remoteDir，不然会找不到远程机器上的路径。
123456789101112131415161718192021222324252627282930313233343536373839
```



## 开始备份

```
sh /home/shellscript/xtrabackup_back.sh >> /home/xtrabackup/xtrabackuplog1.log 2>&1
1
```

这里 >>后的路径就是备份脚本中xtrabackuplogpath变量的值。



## 恢复备份

```
#decompress
xtrabackup  --parallel=8  --decompress --remove-original --target-dir=/data/mysqlback/20190701155002
#/data/mysqlback/20190701155002即备份文件所在的路径
#prepare:
xtrabackup --prepare --target-dir=/data/mysqlback/20190701155002

#backup 原有mysql文件 以备失败恢复：
mv mysql mysql_bak

#copy-back：
xtrabackup --copy-back --parallel=8 --target-dir=/data/mysqlback/20190701155002
#给最新的mysql数据目录授权 不然可能存在启动mysql失败 提示操作文献权限不足
chown -R mysql:mysql /home/mysqldata/mysql/
# start
service mysqld start
123456789101112131415
```



## 搭建主从关系

- 查看已经执行过的GTID(在mysql datadir同目录下)

```
[root@localhost mysql]# cat xtrabackup_info |grep binlog_pos
binlog_pos = filename 'mysql-bin.000012', position '19559', GTID of the last change 'f2d0efd6-6ab7-11e8-8fdd-fa163eda7360:1-41'
12
```

- 连接mysql执行

```
mysql>SET @MYSQLDUMP_TEMP_LOG_BIN=@@SESSION.SQL_LOG_BIN;
mysql> SET @@SESSION.SQL_LOG_BIN= 0;
mysql> SET @@GLOBAL.GTID_PURGED='f2d0efd6-6ab7-11e8-8fdd-fa163eda7360:1-41';
#这里的f2d0efd6-6ab7-11e8-8fdd-fa163eda7360:1-41就是从xtrabackup_info中查询到的已执行过的GTID值。
mysql> SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
mysql>change master to master_host='192.168.1.2', master_port=3306, master_user='repl_user', master_password='123456', master_auto_position=1;
mysql> start status; #启动slave
mysql> show slave status\G; #查看从库状态
#确认IO Thread yes以及SQL Thread yes 即搭建成
123456789
```

至此就完成了在线热备以及整个备份恢复和搭建GTID主从关系。