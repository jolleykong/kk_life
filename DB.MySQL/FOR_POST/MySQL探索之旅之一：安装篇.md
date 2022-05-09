
# 章节提要：
Part I. 操作系统平台选择
Part II. 更专业的安装MySQL
Part III. 弱水三千，我娶哪个发行版/版本？
Part IV. 环境配置
Part V. 安装
Part VI. 奔跑吧皮卡丘！初始化实例以及启动MySQL服务
Part VII. MySQL最最基础的命令


# 面向阅读对象：
有一丢丢计算机基础知识的爱好者。
会使用Linux。

# Part I. 操作系统平台选择
在接下来的时光里，我们使用CentOS 7.8 x86_64 对MySQL进行学习和探索。

虽然Windows万般好，无他，请独爱Linux。因为在Linux下，你可以获得MySQL更好的性能表现，也可以使用更多的Linux特性来玩转MySQL，Linux值得你拥有。
MySQL支持多种Linux发行版，使用平台较多的大致有Ubuntu(Debian系)、CentOS(RedHat 红帽系)、SUSE Linux等等等等。随着计算机硬件的日益强悍，尽可能选择64位架构的操作系统平台以及的64位的MySQL发行版。

# Part II. 更专业的安装MySQL
如果你使用过Linux，或许安装MySQL对你来说小事一桩—— apt install mysql-server / yum install mysql-server ，一条命令搞定一切的快感令你如沐春风。
不过，这样“智能”的安装方式可以使你快速的使用数据库，却不能让你更好的玩转MySQL——安装过程里对操作系统做了哪些配置？实际安装的是哪一个版本？如何安装特定的版本？
因此，从现在开始，我们使用二进制发行版(Linux Generic)的方式对MySQL进行安装配置和探索。

# Part III. 弱水三千，我娶哪个发行版/版本？
MySQL作为一个开源数据库项目，拥有众多分支版本，在这里我们主要使用官方版本 MySQL 5.7.30 x86_64 进行探索。
在这里我们直接在服务器进行下载： 
```
[root@testsrv ~]# wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.30-linux-glibc2.12-x86_64.tar.gz /root
```
# Part IV. 环境配置
1.建立MySQL用户"mysql"
```
[root@testsrv ~]# useradd -g mysql -u 2000 -s /sbin/nologin -d /usr/local/mysql -MN mysql
```
2.修改sysctl.conf
```
[root@testsrv ~]# echo "vm.swappiness=1" >> /etc/sysctl.conf
[root@testsrv ~]# sysctl -p 
```
无报错则继续。

3.配置limits.conf
```
[root@testsrv ~]# echo '* soft nofile 65535' >> /etc/security/limits.conf
[root@testsrv ~]# echo '* hard nofile 65535' >> /etc/security/limits.conf
```
4.配置ulimit
```
[root@testsrv ~]# echo "ulimit -n 65535" >> /etc/rc.local
[root@testsrv ~]# ulimit -n 65535
```
5.配置IO调度
```
[root@testsrv ~]# echo deadline > /sys/block/sda/queue/scheduler
[root@testsrv ~]# grubby --update-kernel=ALL --args="elevator=deadline" &>/dev/null
```
6.关闭NUMA
```
[root@testsrv ~]# sed -i '/^numa/c numa=off' /etc/default/grub
[root@testsrv ~]# grub2-mkconfig -o /etc/grub2.cfg >/dev/null
```
7.关闭SELinux
```
[root@testsrv ~]# vi /etc/selinux/config
修改内容为SELINUX=disabled
```
8.重启服务器以生效配置
```
[root@testsrv ~]# reboot
```
# Part V. 安装
1. 规划并创建MySQL的BASE DIR和DATA DIR
- BASE DIR：MySQL的程序文件所在目录
在这里选择将MySQL解压到/opt/mysql-5.7.30-linux-glibc2.12-x86_64
```
[root@testsrv ~]# tar zxf /root/mysql-5.7.30-linux-glibc2.12-x86_64.tar.gz -C /opt/

[root@testsrv ~]# ls /opt/mysql-5.7.30-linux-glibc2.12-x86_64 
bin data docs include lib LICENSE man README share support-files
```

- DATA DIR：MySQL实例的数据文件所在目录
由于同一个服务器上极有可能运行多个MySQL实例，在这里将每个实例的目录规划为/data/mysql/{MySQL实例端口号}
我们先建立一个3306实例的目录：
```
[root@testsrv ~]# mkdir -p /data/mysql/mysql3306/{data,logs,tmp}
```
2. 将目录所有者指定为操作系统mysql用户
```
[root@testsrv ~]# chown -R mysql:mysql /data/mysql/mysql3306/{data,logs,tmp}
```

- 目录解释：
```
/data/mysql/
└── mysql3306 #实例端口号作为实例DATA DIR的一部分，便于管理和识别
  ├── data  #实例数据文件的存放目录（datadir就是它）
  ├── logs  #实例日志文件的存放目录
  └── tmp  #实例的临时文件目录
```

3. 为mysql3306实例编写参数文件
同样的，我们也使用实例的端口号来命名实例的参数文件，便于管理和识别。
[root@testsrv ~]# vi /data/mysql/mysql3306/my3306.cnf

将下列参数写入到文件并保存。不同于以往MySQL教程的长篇大论，在这里我们先使用尽可能少的配置来让MySQL运行起来。
```
[mysqld]
user                =mysql
basedir               =/opt/mysql-5.7.30-linux-glibc2.12-x86_64/ 
datadir               =/data/mysql/mysql3306/data/ 
server_id              =1003306
port                =3306
bind-address                =127.0.0.1
character_set_server        =utf8mb4 
explicit_defaults_for_timestamp   =on
log_timestamps           =system
lower_case_table_names       =1 
default_time_zone              ='+08:00' 
socket               =/data/mysql/mysql3306/tmp/mysql.sock 
secure_file_priv          =/data/mysql/mysql3306/tmp/ 

binlog_format            =row
log_bin               =/data/mysql/mysql3306/logs/mysql-bin 
binlog_rows_query_log_events    =on 
log_slave_updates          =on 
 log_error              =/data/mysql/mysql3306/logs/error.log
general_log             =off 
general_log_file          =/data/mysql/mysql3306/logs/general.log 

slow_query_log           =on 
slow_query_log_file         =/data/mysql/mysql3306/logs/slow_query.log 
log_queries_not_using_indexes    =on 
long_query_time           =1.000000 

gtid_mode              =on 
enforce_gtid_consistency      =on 
```
4. 检查MySQL的依赖
```
[root@testsrv ~]# ldd /opt/mysql-5.7.30-linux-glibc2.12-x86_64/bin/mysqld
```
没有提示NOT FOUND 就可以下一步了。 如果发现有依赖组件NOT FOUND，使用yum等方式安装依赖，直到通过检测。

5. 创建软连接并配置PATH
```
[root@testsrv ~]# ln -sf /opt/mysql-5.7.30-linux-glibc2.12-x86_64 /usr/local/mysql
[root@testsrv ~]# echo 'export PATH=/usr/local/mysql/bin:$PATH' >> /etc/profile
```
6. 使PATH生效
```
[root@testsrv ~]# . /etc/profile
[root@testsrv ~]# which mysql
/usr/local/mysql/bin/mysql
```

# Part VI. 奔跑吧皮卡丘！初始化实例以及启动MySQL服务
忙了这么久，做了这么多mysql3306的准备，在这一步都会体现价值。

1.随机密码方式初始化实例

- 使用随机密码方式初始化实例，mysqld初始化过程中会随机为root@localhost创建密码，可以在errorlog中查看密码明文。
- 登陆后强制要求变更密码。
```
[root@testsrv ~]# mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf --initialize
```
- 耐心的等待一会，没有报错的话就是可以啦（没有消息就是最好的消息）！ 
- 如果有报错，根据报错做一下排查：
```
datadir的目录中有文件（目录不为空拒绝初始化）？
是缺依赖包(xxx not found.)？
还是目录权限不对(permisson denied.)？ 
还是配置文件中的datadir目录里存在文件？
亦或是命令选项敲错了(误将 defaults-file 打成了 default-files)？
```
- 查看一下初始化后的结果
```
[root@testsrv ~]# ls /data/mysql/mysql3306/data 
auto.cnf  ca.pem      client-key.pem ibdata1   ib_logfile1 mysql        private_key.pem server-cert.pem sys
ca-key.pem client-cert.pem ib_buffer_pool ib_logfile0 ib_logfile2 performance_schema public_key.pem  server-key.pem

[root@testsrv ~]# cat /data/mysql/mysql3306/logs/error.log 
…
…
2020-07-10T17:43:51.243252+08:00 0 [Warning] CA certificate ca.pem is self signed.
2020-07-10T17:43:51.551619+08:00 1 [Note] A temporary password is generated for root@localhost: QsJqBL+7*;de
```
2.启动mysqld进程以启动实例

- 简单语法：
```
mysqld     --defaults-file=${mycnf_file} &
			--defaults-file 指定mysql cnf 配置文件路径
```

- 完成初始化后，就可以启动实例了
```
[root@testsrv ~]# mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf &
```

- 查看进程
```
[root@testsrv ~]# ps -ef | grep mysqld
mysql   527  465 1 09:20 pts/0  00:00:00 mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf
```

- 启动完成，如果查看不到进程，可以检查一下errorlog，看看是什么问题导致启动失败。

3.登陆mysql3306实例

- 简单语法： mysql -u root     -p123 -h 127.0.0.1 -P 3306 -S xxxx.sock 

```
-u mysql user，不指定则以当前OS username
-p mysql user的密码
-h mysql实例的服务器地址/IP，可能与-P连用
-P mysql实例的服务器端口，默认为3306
-S 本地socket方式登陆时用来指定socket文件地址，用-S就不需要-h 和-P了
```

- 使用本地socket方式登陆（建议）

```
[root@testsrv ~]# mysql -S /data/mysql/mysql3306/tmp/mysql.sock -u root -p 
Enter password:        # 此处密码不会显示，将初始化时errorlog中的临时密码：QsJqBL+7*;de 输入或粘贴进去即可
Welcome to the MySQL monitor. Commands end with ; or \g.
Your MySQL connection id is 4
Server version: 5.7.30-log

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 

先退出
mysql> exit
Bye
```

- 使用TCP方式登陆

```
[root@testsrv ~]# mysql -h 127.0.0.1 -u root -p 
Enter password:       # 此处密码不会显示，将初始化时errorlog中的临时密码：QsJqBL+7*;de 输入或粘贴进去即可
Welcome to the MySQL monitor. Commands end with ; or \g.
Your MySQL connection id is 2
Server version: 5.7.30-log

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```
4.修改root@localhost密码

- 使用临时密码登陆实例后，进行任何操作时都会弹出密码修改的提示，同时操作被阻止。

```
mysql> show databases;
ERROR 1820 (HY000): You must reset your password using ALTER USER statement before executing this statement.
```

- 修改密码为 hellomysql

```
mysql> alter user user() identified by 'hellomysql';
Query OK, 0 rows affected (0.06 sec)
```

- 再进行操作就可以了：

```
mysql> show databases;
+--------------------+
| Database      |
+--------------------+
| information_schema |
| mysql       |
| performance_schema |
| sys        |
+--------------------+
4 rows in set (0.00 sec)
```

- 后续登陆都使用新密码


附.无密码方式初始化实例
mysqld初始化阶段可以使用--initialize-insecure 方式替代--initialize ，这样在实例初始化过程中，root@localhost用户密码为空，方便的同时也存在一些安全隐患。

如果已经使用1.随机密码方式初始化实例，再次进行初始化操作会报错。在这里我们删除掉前面初始化的结果，使用无密码方式重新初始化一遍。

删除前一次初始化的内容
```
[root@testsrv ~]# rm -fr /data/mysql/mysql3306/data/*
[root@testsrv ~]# rm -fr /data/mysql/mysql3306/logs/*
[root@testsrv ~]# rm -fr /data/mysql/mysql3306/tmp/* 
```
无密码方式初始化实例
```
[root@testsrv ~]# mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf --initialize-insecure
```

查看一下初始化后的结果
```
[root@testsrv ~]# ls /data/mysql/mysql3306/data 
auto.cnf  ca.pem      client-key.pem ibdata1   ib_logfile1 mysql        private_key.pem server-cert.pem sys
ca-key.pem client-cert.pem ib_buffer_pool ib_logfile0 ib_logfile2 performance_schema public_key.pem  server-key.pem

[root@testsrv ~]# cat /data/mysql/mysql3306/logs/error.log 
…
…
2020-07-10T17:33:54.606511+08:00 1 [Warning] root@localhost is created with an empty password ! Please consider switching off the --initialize-insecure option.
```

启动实例后可直接无密码登陆
```
[root@testsrv ~]# mysql -S /data/mysql/mysql3306/tmp/mysql.sock -u root
Welcome to the MySQL monitor. Commands end with ; or \g.
Your MySQL connection id is 2
Server version: 5.7.30-log

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```
建议无密码初始化后，手动设定密码，以确保安全。

# Part VII. MySQL最最基础的命令
- 初始化实例
  - 随机密码：
    ```
    mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf --initialize
    ```
  - 无密码：
    ```
    mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf --initialize-insecure
    ```

- 启动实例
```
mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf &
```

- 登陆实例
```
mysql -S /data/mysql/mysql3306/tmp/mysql.sock -u root -p 
```

- 修改密码
```
mysql> alter user username identified by 'newpassword';
如果修改当前用户密码，username可以直接使用user() 函数。
```

- 查看实例状态
```
mysql> \s （清晰简要）
或
mysql> show status\G （长篇大论）
```

- 关闭实例
```
mysql> shutdown ; exit;
```
