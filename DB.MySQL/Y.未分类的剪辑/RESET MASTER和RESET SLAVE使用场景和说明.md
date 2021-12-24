# RESET MASTER和RESET SLAVE使用场景和说明

【前言】在配置主从的时候经常会用到这两个语句，刚开始的时候还不清楚这两个语句的使用特性和使用场景。 经过测试整理了以下文档，希望能对大家有所帮助；    ###【一】RESET MASTER参数 功能说明：删除所有的binglog日志文件，并将日志索引文件清空，重新开始所有新的日志文件。用于第一次进行搭建主从库时，进行主库binlog初始化工作；  注意reset master 不同于purge binary log的两处地方 1\. reset master 将删除日志索引文件中记录的所有binlog文件，创建一个新的日志文件 起始值从000001  开始，然而purge binary log 命令并不会修改记录binlog的顺序的数值 2\. reset master 不能用于有任何slave 正在运行的主从关系的主库。因为在slave 运行时刻 reset master  命令不被支持，reset master 将master 的binlog从000001 开始记录,slave 记录的master log  则是reset master 时主库的最新的binlog,从库会报错无法找的指定的binlog文件。 测试如下：

```
未删除前

[root@mysql01 mysql]# pwd
/data/mysql

[root@mysql01 mysql]# ls1234567
```

![img](http://blog.itpub.net/attachment/201506/16/12679300_1434436974vQ02.png)

```
mysql> show master status\G;
*************************** 1\. row ***************************
            File: <span style="color:#ff0000;">mysql-bin.000025
</span>        Position: <span style="color:#ff0000;">107
</span>    Binlog_Do_DB:
Binlog_Ignore_DB:
1 row in set (0.01 sec)1234567
```

**当前有25个binlong日志，且Position的位置为107**

运行RESET MASTER

```
mysql> reset master;
Query OK, 0 rows affected (0.03 sec)

mysql> show master status\G;
*************************** 1\. row ***************************
            File: mysql-bin.000001
        Position: 107
        Binlog_Do_DB:
Binlog_Ignore_DB:
1 row in set (0.00 sec)12345678910
```

![img](http://blog.itpub.net/attachment/201506/16/12679300_1434436975spvn.png)

**显示所有的binlog已经被删除掉，且binlog从000001 开始记录**

注：当数据库要清理binlog文件的时候，可以通过操作系统进行删除，也可以运行reset master进行删除。但是如果当前是主数据库，且主从数据库正常的时候，千万不能用这种方式删除。

【使用场景】第一次搭建主从数据库时，用于主库的初始化binglog操作；

### 【二】RESET SLAVE

功能说明：用于删除SLAVE数据库的relaylog日志文件，并重新启用新的relaylog文件；

reset slave 将使slave 忘记主从复制关系的位置信息。该语句将被用于干净的启动, 它删除master.info文件和relay-log.info 文件以及所有的relay log 文件并重新启用一个新的relaylog文件。

使用reset slave之前必须使用stop slave 命令将复制进程停止。

**登录从数据库，未删除前**

```
mysql> show slave status\G;
*************************** 1\. row ***************************
               Slave_IO_State: Connecting to master
                  Master_Host: 192.168.47.167
                  Master_User: server
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File: mysql-bin.000019
          Read_Master_Log_Pos: 12992
              Relay_Log_File: mysql02-relay-bin.000004
                Relay_Log_Pos: 4
        Relay_Master_Log_File: mysql-bin.000019123456789101112
```

![img](http://blog.itpub.net/attachment/201506/16/12679300_1434436977427p.png)

当前relaylog为0004；

删除后

```
mysql> stop slave;                
先停止slave
Query OK, 0 rows affected (0.01 sec)

mysql> reset slave;               
Query OK, 0 rows affected (0.04 sec)

mysql> show slave status\G;
*************************** 1\. row **************************
               Slave_IO_State:
                  Master_Host: 192.168.47.167
                  Master_User: server
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File:
          Read_Master_Log_Pos: 4
           Relay_Log_File: mysql02-relay-bin.000001
                Relay_Log_Pos: 4123456789101112131415161718
```

![image](http://blog.itpub.net/attachment/201506/16/12679300_1434436979p3eA.png)

RESET SLAVE将使SLAVE忘记主从复制关系的位置信息。该语句将被用于干净的启动, 它删除master.info文件和relay-log.info 文件以及所有的relay log 文件并重新启用一个新的relaylog文件。

使用场景：当原来的主从关系被破坏之后，从库经过重新初始化后直接连接会报 ERROR 1201的错误，运行reset slave后，重新配置主从连接就可以了；

```
mysql> CHANGE MASTER TO MASTER_HOST='192.168.0.167',MASTER_USER='test',MASTER_PASSWORD='test', MASTER_LOG_FILE='mysql-bin.000001',MASTER_LOG_POS=176658;

ERROR 1201 (HY000): Could not initialize master info structure; more error messages can be found in the MySQL error log123
```

总结：如果是需要删除mysql binlog和relaylog文件的时候，那么通过操作系统的删除或者PURGE命令都可以，但是涉及到mysql主从配置的时候便需要使用RESET MASTER和RESET SLAVE解决问题；

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

本文作者：JOHN，某上市公司DBA，业余时间专注于数据库的技术管理，从管理的角度去运用技术。

技术博客：猎人笔记                        数据库技术群：367875324 （请备注数据库类型）

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

转自：https://blog.csdn.net/yabingshi_tech/article/details/50736735