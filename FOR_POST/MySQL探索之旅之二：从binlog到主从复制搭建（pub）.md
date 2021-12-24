- ## MySQL探索之旅之二：从binlog到主从复制搭建

- 原创 孔个个 [帅萌的杂谈铺](javascript:void(0);) *7月20日*

- ------

- 章节提要

- 1. 神奇的binlog——复制的根源
  2. 初步了解binlog的position
  3. 创建一个新实例
  4. 复制(Replication)简介
  5. 使用position方式搭建全新的异步复制架构
  6. 玩转复制：sql_thread until
  7. 总结，以及些个思考——可能是由浅入深的跳板

- ​      

- 面向阅读对象

- - 有一丢丢计算机基础知识的爱好者
  - 会使用Linux
  - 参与过前面的MySQL探索之旅的小伙伴

-  

- 阅读本文你将收获

- - 对binlog和position有浅层的认识
  - 使用pos方式搭建主从复制
  - 使用pos方式控制主从复制内容


- ------

- MySQL replication，又名主从复制，花名AB复制。或许MySQL replication是导致MySQL火爆的原因，没有之一。

- 目前为止，MySQL replication已经进化了三次了：

- - 异步复制（Asynchronous repliaction）
  - 半同步复制（Semi-synchronous replication）
  - 无损半同步复制（Lossless semi-sync replication）
    

- 在今天的旅途中，我们继续使用《MySQL探索之旅之一：安装篇》的环境，通过异步复制（Asynchronous repliaction）简单认识一下MySQLreplication，并像上一次探索之旅一样，在保证知识连贯性的前提下，我们先搭建一个最简单的异步复制架构，然后以此尝试对replication进行一层探索。

-    

- ​    **准备发车辣！**


- ------

- 1.神奇的binlog——复制的根源

- 我们初始化并启动实例后，从操作系统访问MySQL实例的logs目录，可以看到有类似的文件结构：

```
  [root@testsrv~]# tree /data/mysql/mysql3306├──data                    #DATA DIR├──logs                     #日志目录│  ├── error.log            #错误日志│  ├── mysql-bin.000001      #binlog│  ├── mysql-bin.000002│  ├── mysql-bin.000003│  ├── mysql-bin.000004│  ├── mysql-bin.index       #binlog索引│  └── slow_query.log        #慢查询日志├──my3306.cnf               #自定义的实例参数文件└──tmp                      #临时目录
```

- 我们今天只关注一下binlog。

-    

- - 在MySQL中触摸binlog——登入到MySQL实例，执行查询

- - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql>show master status;+------------------+----------+--------------+------------------+------------------------------------------+|File             | Position |Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                        |+------------------+----------+--------------+------------------+------------------------------------------+|mysql-bin.000004 |      194 |              |                  |85406fb9-c571-11ea-81ff-0242c0a8bc33:1-2 |+------------------+----------+--------------+------------------+------------------------------------------+1row in set (0.00 sec)
  ```

-  

- - 复位binlog，此时会清空所有binlog，从头开始。

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql>reset master;QueryOK, 0 rows affected (0.24 sec)
  mysql>show master status;+------------------+----------+--------------+------------------+-------------------+|File             | Position |Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |+------------------+----------+--------------+------------------+-------------------+|mysql-bin.000001 |      154 |              |                  |                   |+------------------+----------+--------------+------------------+-------------------+1row in set (0.00 sec)
  ```

- 

- - 对应的，binlog文件也消失了。

- - 
  - 
  - 
  - 
  - 

- ```
  [root@testsrv~]# ls -l logs/-rw-r-----1 mysql mysql 21251 Jul 14 17:33 error.log-rw-r-----1 mysql mysql   776 Jul 14 17:32mysql-bin.000001-rw-r-----1 mysql mysql    44 Jul 14 17:30mysql-bin.index-rw-r-----1 mysql mysql   736 Jul 14 12:00slow_query.log
  ```

- 

- - 回到实例，创建一个数据库kk，然后查看一下master status

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql>create database kk;QueryOK, 1 row affected (0.05 sec)
  mysql>show master status;+------------------+----------+--------------+------------------+----------------------------------------+|File             | Position |Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                      |+------------------+----------+--------------+------------------+----------------------------------------+|mysql-bin.000001 |      307 |              |                  |85406fb9-c571-11ea-81ff-0242c0a8bc33:1 |+------------------+----------+--------------+------------------+----------------------------------------+1row in set (0.00 sec)
  ```

- 

- ------

- 2.初步了解binlog的position

-  我们来瞧瞧这些binlog文件里都记录了什么。

- - 
  - 

- ```
  [root@testsrvlogs]# cat mysql-bin.index/data/mysql/mysql3306/logs/mysql-bin.000001             
  ```

- binlog.index文件记录的是目前有效的binlog文件们的完全路径

-  

- 再来看看binlog的内容

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  ## 不了解这个命令的小伙伴不要急，现在只需要知道它用来解析binlog就可以。[root@testsrv logs]# mysqlbinlog -vvv --base64-output=decode-rows mysql-bin.000001 /*!50530 SET @@SESSION.PSEUDO_SLAVE_MODE=1*/; /*!50003 SET @OLD_COMPLETION_TYPE=@@COMPLETION_TYPE,COMPLETION_TYPE=0*/; DELIMITER /*!*/; # at 4 #200714 19:08:22 server id 1003306 end_log_pos 123 CRC32 0xf8334f25 Start: binlog v 4, server v 5.7.30-log created 2 00714 19:08:22 at startup # Warning: this binlog is either in use or was not closed properly. ROLLBACK/*!*/; # at 123 #200714 19:08:22 server id 1003306 end_log_pos 154 CRC32 0x994044b1 Previous-GTIDs # [empty] # at 154 # 事务差不多在这里开始了。注意下面的GTID_NEXT，以及end_log_pos #200714 19:08:25 server id 1003306 end_log_pos 219 CRC32 0x553b7d06 GTID last_committed=0 sequence_number= 1 rbr_only=no SET @@SESSION.GTID_NEXT= '85406fb9-c571-11ea-81ff-0242c0a8bc33:1'/*!*/; # at 219 #200714 19:08:25 server id 1003306 end_log_pos 307 CRC32 0x4e27557f Query thread_id=2 exec_time=0 error_co de=0 SET TIMESTAMP=1594724905/*!*/; SET @@session.pseudo_thread_id=2/*!*/; SET @@session.foreign_key_checks=1, @@session.sql_auto_is_null=0, @@session.unique_checks=1, @@session.autocommit=1/*!*/ ; SET @@session.sql_mode=1436549152/*!*/; SET @@session.auto_increment_increment=1, @@session.auto_increment_offset=1/*!*/; /*!\C utf8 *//*!*/; SET @@session.character_set_client=33,@@session.collation_connection=33,@@session.collation_server=45/*!*/; SET @@session.lc_time_names=0/*!*/; SET @@session.collation_database=DEFAULT/*!*/; create database kk /*!*/; SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/; DELIMITER ; # End of log file /*!50003 SET COMPLETION_TYPE=@OLD_COMPLETION_TYPE*/; /*!50530 SET @@SESSION.PSEUDO_SLAVE_MODE=0*/;
  ```

- 对数据库做一些操作，然后再次解析binlog日志

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql> use kk;Database changedmysql> show master status;+------------------+----------+--------------+------------------+----------------------------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                      |+------------------+----------+--------------+------------------+----------------------------------------+| mysql-bin.000001 |      307 |              |                  | 85406fb9-c571-11ea-81ff-0242c0a8bc33:1 |+------------------+----------+--------------+------------------+----------------------------------------+1 row in set (0.00 sec)
  mysql> create table k1 (id int primary key);Query OK, 0 rows affected (0.03 sec)
  mysql> show master status;+------------------+----------+--------------+------------------+------------------------------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                        |+------------------+----------+--------------+------------------+------------------------------------------+| mysql-bin.000001 |      478 |              |                  | 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-2 |+------------------+----------+--------------+------------------+------------------------------------------+1 row in set (0.00 sec)
  mysql> insert into k1 values (1);Query OK, 1 row affected (0.01 sec)
  mysql> show master status;+------------------+----------+--------------+------------------+------------------------------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                        |+------------------+----------+--------------+------------------+------------------------------------------+| mysql-bin.000001 |      776 |              |                  | 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-3 |+------------------+----------+--------------+------------------+------------------------------------------+1 row in set (0.00 sec)
  ## 这个命令如果不知道意思的话，不要急。## 这个命令用来解析binlog内容。[root@testsrv logs]# mysqlbinlog -vvv --base64-output=decode-rows mysql-bin.000001  …  SET @@session.collation_database=DEFAULT/*!*/;  create database kk  /*!*/;  # at 307  # 这是一个事务  #200714 19:19:14 server id 1003306 end_log_pos 372 CRC32 0x993a25a8 GTID last_committed=1 sequence_number=  2 rbr_only=no  SET @@SESSION.GTID_NEXT= '85406fb9-c571-11ea-81ff-0242c0a8bc33:2'/*!*/;  # at 372  #200714 19:19:14 server id 1003306 end_log_pos 478 CRC32 0xff471106 Query thread_id=2 exec_time=0 error_co  de=0  use `kk`/*!*/;  SET TIMESTAMP=1594725554/*!*/;  create table k1 (id int primary key)  /*!*/;  # at 478  #200714 19:19:23 server id 1003306 end_log_pos 543 CRC32 0x217364c6 GTID last_committed=2 sequence_number=  3 rbr_only=yes  # 这是又一个事务  /*!50718 SET TRANSACTION ISOLATION LEVEL READ COMMITTED*//*!*/;  SET @@SESSION.GTID_NEXT= '85406fb9-c571-11ea-81ff-0242c0a8bc33:3'/*!*/;  # at 543  #200714 19:19:23 server id 1003306 end_log_pos 613 CRC32 0x0a46d048 Query thread_id=2 exec_time=0 error_co  de=0  SET TIMESTAMP=1594725563/*!*/;  BEGIN  /*!*/;  # at 613  #200714 19:19:23 server id 1003306 end_log_pos 662 CRC32 0x071057ce Rows_query  # insert into k1 values (1)  # at 662  #200714 19:19:23 server id 1003306 end_log_pos 705 CRC32 0xe04343f1 Table_map: `kk`.`k1` mapped to number 116  # at 705  #200714 19:19:23 server id 1003306 end_log_pos 745 CRC32 0xb8abbf36 Write_rows: table id 116 flags: STMT_END_F  ### INSERT INTO `kk`.`k1`  ### SET  ### @1=1 /* INT meta=0 nullable=0 is_null=0 */  # at 745  #200714 19:19:23 server id 1003306 end_log_pos 776 CRC32 0x67b87cc8 Xid = 41  COMMIT/*!*/;  SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/;  DELIMITER ;  # End of log file  /*!50003 SET COMPLETION_TYPE=@OLD_COMPLETION_TYPE*/;  /*!50530 SET @@SESSION.PSEUDO_SLAVE_MODE=0*/;
  ```

- 有点乱，不过不要紧，结合前面show master status的查询结果，这段binlog里的内容似乎就是那些操作的记录？

- 

- 我们来尝试分析一下，将每个SQL操作时查询到的position信息和binlog解析后的内容做一下对比。（不知道GTID是什么的同学今天可以先不用管它。）

- | SQL                                            | show-GTID        | show-POS | binlog-GTID      | binlog-POS |
  | ---------------------------------------------- | ---------------- | -------- | ---------------- | ---------- |
  | create database kk                             | 0242c0a8bc33:1   | 307      | 0242c0a8bc33:1   | 307        |
  | use `kk`; create table k1 (id int primary key) | 0242c0a8bc33:1-2 | 478      | 0242c0a8bc33:1-2 | 478        |
  | insert into k1 values (1)                      | 0242c0a8bc33:1-3 | 776      | 0242c0a8bc33:1-3 | 776        |

- 

- 正是这样。

-  

- 也就是说，binlog记录了实例的变化情况。那么如果将这个神奇的binlog在别处重放(replay)，是不是就可以克隆出完全一样的实例了？

- 没错，这就是复制可行的根源！

-  

- **Let'sGo ！今天我们就从对binlog入手，使用position方式搭建一下主从复制。**

-  

- ------

- 3.创建一个新实例

- 既然要做复制架构，那就至少需要两个实例。不过经过了《MySQL探索之旅之一：安装篇》的探索，这便是小菜一碟。

- 如果你已经忘了如何创建新实例，那就回去重温一下上一次的探索吧。

- 简短截说，在相同服务器上再创建一个实例：

- - 
  - 
  - 
  - 
  - 

- ```
  [root@testsrv~]# mkdir -p /data/mysql/mysql3316/{data,logs,tmp}[root@testsrv~]# cp /data/mysql/mysql3306/my3306.cnf /data/mysql/mysql3316/my3316.cnf[root@testsrv~]# chown mysql:mysql -R /data/mysql/mysql3316/[root@testsrv~]# vi /data/mysql/mysql3316/my3316.cnf将3306相关字样替换为3316，保存退出
  ```

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  [mysqld]user                                =mysqlbasedir                            =/opt/mysql-5.7.30-linux-glibc2.12-x86_64/datadir                            =/data/mysql/mysql3316/data/server_id                           =1003316port                                =3316bind-address                      =127.0.0.1character_set_server                =utf8mb4explicit_defaults_for_timestamp     =onlog_timestamps                      =systemlower_case_table_names              =1default_time_zone                    ='+08:00'socket                             =/data/mysql/mysql3316/tmp/mysql.socksecure_file_priv                    =/data/mysql/mysql3316/tmp/
  binlog_format                       =rowlog_bin                            =/data/mysql/mysql3316/logs/mysql-binbinlog_rows_query_log_events        =onlog_slave_updates                   =on
  log_error                   =/data/mysql/mysql3316/logs/error.loggeneral_log                         =offgeneral_log_file                   =/data/mysql/mysql3316/logs/general.log
  slow_query_log                      =onslow_query_log_file                =/data/mysql/mysql3316/logs/slow_query.loglog_queries_not_using_indexes       =onlong_query_time                     =1.000000
  gtid_mode                           =onenforce_gtid_consistency            =on
  ```

- ​       

- - 初始化实例、查看初始密码、启动实例、修改初始密码

    略。如果突然不会做了，快去看上一篇《MySQL探索之旅之一：安装篇》。

- ``

- ​      

- ------

- 4.复制(Replication)简介

- 现在，我们的服务器上有两个MySQL实例已经被初始化，并且正在运行。

- 接下来我们先认识一点简短的概念，然后用它们去配置主从复制。

-    

- - 一些简短的概念

- - master：主从复制里的“主”节点，复制架构中的数据来源。
  - slave：主从复制里的“从”节点，主节点的数据复制到的目标节点。
  - binlog：在主从复制里主要指主节点产生的binlog。
  - relay-log：主节点binlog发送到从节点后，称为relay-log，或relay-binlog。
  - position：binlog文件中事务的位置，同一文件中position具有唯一性。
  - GTID：Global transaction identifiers，全局事务标识符，暂不展开。可以理解为事务的一种标记方式，同样记录在binlog中，但是一个事务GTID在实例中是唯一的，跨越了binlog file的范围，因此在一定程度上比position友好很多。
  - io_thread：从节点上负责接收主节点binlog的线程。
  - sql_thread：从节点上负责将relay-log重放的线程。
  - dump_thread：当从节点的io_thread启动后，主节点便会为此分配一个dump_thread线程，负责读取主节点上的binlog信息并发送给从节点。

- ​    

- - 一个吐槽

- 随着黑命贵black_lives_matter的风潮，MySQL在未来也要更名master和slave了。

- 愿世界和平。

- 

- 

- - Replication相关命令

- 

- 配置复制

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  slave上执行 change master to master_host='',\              master_port=3306,\              master_user='',\              master_password='',\              master_auto_position=,\              master_log_file='',\              master_log_pos=;其中， master_host，master的地址 master_port，master的数据库端口 master_user，master实例上具有replication slave权限的用户名 master_password，master实例上具有replication slave权限的用户的密码 master_auto_position，是否启用自动定位GTID master_log_file，使用position方式时指定要开始复制的binlog filename master_log_pos，使用position方式时指定要开始复制的binlog position，需配合master_log_file参数一起使用
  ```

- 

- 查看slave状态

- - 

- ```
  slave上执行 show slave status \G
  ```

- ​      

- 清空复制配置

- 

- - 

- ```
  slave上执行 reset slave all;   
  ```

-  

- 

- - 一句话说下主从复制的逻辑流程

- slave节点使用master节点的用户账号，去与master建立起连接，然后获取master节点的binlog到本地relay-log，再重放relay-log。

- 

- - 简单描述一下主从复制的逻辑流程

- 1. 1. slave节点使用master节点的用户配置复制(change master)。
     2. 当slave节点启动io_thread时，尝试与master建立起连接，master验证通过后分配dump_thread，完成主从连接的建立。
     3. 当master有binlog变更时，会通知dump_thread线程。dump_thread接到通知后便读取binlog并发送给slave。
     4. slave上的io_thread负责将接受到的binlog写入到slave节点上的relay-log中。
     5. slave上的sql_thread负责重放（执行）relay-log中的日志。

- 

- - 说下GTID和position复制的区别

- 早期没有GTID时，由于position是binlog文件范围内的位置值，MySQL复制需要指定从哪一个binlog的哪一个position位置处开始复制，MySQL只能根据指定的文件及位置开始读取binlog。当出现复制出错时，需要分析binlog以更改binlog文件和position的定义，以便恢复复制进行，人工介入内容较多。

- 5.6版本以后引入GTID，GTID是全局值，因此事务的GTID具备了唯一性，也因此且跨越了binlog filename的束缚。在进行MySQL复制配置时，只需声明master_auto_position=1，或指定特定GTID值，MySQL便会自行对比主从状态，通过GTID扫描找到复制起始点。人工介入内容较少，更加便捷。

- 

- 虽然position方式十分的原始，但是却可以通过position方式了解复制机制的细节，**因此在这里先对position方式进行探索**。

-    

- - 一个建议

- 从主从复制的逻辑流程来看，只需要master配置参数、创建复制用户、开启binlog便可以和slave搭建起主从复制结构，但实际应用中存在主从切换的场景（switchover/failover），也因此二者角色存在互换的可能，所以我们应该在每一个节点上都进行相应的配置，以应对主从切换的需求。

- 关于主从切换，如果有需要，会在未来的探索之旅中进行展开。

- ​       

-  

- ------

- 5.使用position方式搭建全新的异步复制架构

- 开始搭建。

- - 目前的环境信息

- |           | Node1     | Node2     |
  | --------- | --------- | --------- |
  | 角色      | master    | slave     |
  | 地址      | 127.0.0.1 | 127.0.0.1 |
  | 端口      | 3306      | 3316      |
  | server_id | 1003306   | 1003316   |

- 

- - MySQL参数配置

- 相关参数，主从库都要在mycnf中进行配置。

- 如果你是按照我们探索之旅初始化的环境，那么它们已经做好了配置了。

- | 参数          | 设定值                                                       |
  | ------------- | ------------------------------------------------------------ |
  | server_id     | 各实例间不可重复，用来区分实例。建议以xxxxx端口号的方式设定，便于识别管理。如1003306，1003316。 |
  | binlog_format | row                                                          |

- 

- - 分别在主从节点配置，执行下面查询以确认配置正确      

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  查看server-idmysql> show global variables like "%server_id%";+----------------+-----------+| Variable_name  | Value     |+----------------+-----------+| server_id      | 1003306   || server_id_bits | 32        |+----------------+-----------+2 rows in set (0.00 sec)
  查看binlog格式mysql> show global variables like "%binlog_format%";+---------------+-------+| Variable_name | Value |+---------------+-------+| binlog_format | ROW   |+---------------+-------+1 row in set (0.00 sec)
  ```

- 

- - master创建复制账号并授权

- - 
  - 
  - 
  - 
  - 

- ```
  mysql-master> create user 'rep'@'%' identified by 'rep';Query OK, 0 rows affected (0.03 sec)
  mysql-master> grant replication slave on *.* to 'rep'@'%';Query OK, 0 rows affected (0.12 sec)
  ```

- ​       

- - 查看当前master状态

- - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-master> show master status;+------------------+----------+--------------+------------------+------------------------------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                        |+------------------+----------+--------------+------------------+------------------------------------------+| mysql-bin.000001 |     1219 |              |                  | 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-5 |+------------------+----------+--------------+------------------+------------------------------------------+1 row in set (0.00 sec)
  ```

- ​       

-    

- - slave重置binlog

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> reset master;Query OK, 0 rows affected (0.15 sec)
  mysql-slave> show master status;+------------------+----------+--------------+------------------+-------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |+------------------+----------+--------------+------------------+-------------------+| mysql-bin.000001 |      154 |              |                  |                   |+------------------+----------+--------------+------------------+-------------------+1 row in set (0.00 sec)
  ```

- ​       

- ​       

- - slave配置replication

- 

- - 
  - 

- ```
  mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=0;Query OK, 0 rows affected, 2 warnings (0.26 sec)
  ```

-  

- - 查看slave状态

- 先注意其中两行：Slave_IO_Running和Slave_SQL_Running。配置后还未启动复制，因此二者运行状态都为NO。

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> show slave status\G*************************** 1. row ***************************              Slave_IO_State:                 Master_Host: 127.0.0.1                 Master_User: rep                 Master_Port: 3306               Connect_Retry: 60             Master_Log_File: mysql-bin.000001         Read_Master_Log_Pos: 4              Relay_Log_File: ms51-relay-bin.000001               Relay_Log_Pos: 4       Relay_Master_Log_File: mysql-bin.000001            Slave_IO_Running: No           Slave_SQL_Running: No             ……             ……            Master_Server_Id: 1003306                 Master_UUID:            Master_Info_File: /data/mysql/mysql3316/data/master.info                   SQL_Delay: 0         SQL_Remaining_Delay: NULL     Slave_SQL_Running_State:          Master_Retry_Count: 86400             ……               Auto_Position: 0             ……1 row in set (0.00 sec)
  ```

- ​      

- - slave启动复制

- 启动复制前首先查看一下slave的数据库清单

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> show databases;+--------------------+| Database           |+--------------------+| information_schema || mysql              || performance_schema || sys                |+--------------------+4 rows in set (0.00 sec)
  ```

- 

- - 启动方式一：直接启动。

- 这种方式会自动启动io_thread和sql_thread。

- - 
  - 

- ```
  mysql-slave> start slave;Query OK, 0 rows affected (0.01 sec)
  ```

- ​          

- - 启动方式二：手动启动io_thread和sql_thread，可以进行更多的控制。

- 这一部分将在下面章节<尝试玩转复制>中进一步展开。

- - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread;Query OK, 0 rows affected (0.01 sec)
  ```

- ​          

- - 启动复制后查看一下slave的数据库清单

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> show databases;+--------------------+| Database           |+--------------------+| information_schema || kk                 || mysql              || performance_schema || sys                |+--------------------+5 rows in set (0.00 sec)
  ```

- ​       

- 可以看到slave已经复制到了master创建数据库kk的动作。

- 

- - 再次查看slave status，

- 可见信息多了起来，Slave_IO_Running和Slave_SQL_Running运行状态已经是Yes。

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> show slave status\G*************************** 1. row ***************************               Slave_IO_State: Waiting for master to send event                  Master_Host: 127.0.0.1                  Master_User: rep                  Master_Port: 3306                Connect_Retry: 60              Master_Log_File: mysql-bin.000001          Read_Master_Log_Pos: 1219               Relay_Log_File: ms51-relay-bin.000002                Relay_Log_Pos: 1432        Relay_Master_Log_File: mysql-bin.000001             Slave_IO_Running: Yes            Slave_SQL_Running: Yes              ……          Exec_Master_Log_Pos: 1219              Relay_Log_Space: 1638              ……             Master_Server_Id: 1003306                  Master_UUID: 85406fb9-c571-11ea-81ff-0242c0a8bc33             Master_Info_File: /data/mysql/mysql3316/data/master.info                    SQL_Delay: 0          SQL_Remaining_Delay: NULL      Slave_SQL_Running_State: Slave has read all relay log; waiting for more updates           Master_Retry_Count: 86400              ……           Retrieved_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-5            Executed_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-5                Auto_Position: 0              ……1 row in set (0.00 sec)
  ```

- ​       

- - 在master操作数据库，就可以在slave上查看到变更已经被复制到slave上

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-master> use kkDatabase changedmysql-master> create table omg (id int auto_increment primary key , dtl varchar(20));Query OK, 0 rows affected (0.03 sec)
  mysql-master> insert into omg(dtl) values ('aaa');Query OK, 1 row affected (0.01 sec)
  mysql-master> insert into omg(dtl) values ('aaa');Query OK, 1 row affected (0.01 sec)
  mysql-master> insert into omg(dtl) values ('aaa');Query OK, 1 row affected (0.01 sec)
  
  mysql-slave> select * from kk.omg;+----+------+| id | dtl |+----+------+| 1 | aaa || 2 | aaa || 3 | aaa |+----+------+3 rows in set (0.00 sec)
  ```

-  

- - slave停止slave， master在停止复制之后进行多次数据库操作，观察slave状态。

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> show slave status \G*************************** 1. row ***************************               Slave_IO_State:                  Master_Host: 127.0.0.1                  Master_User: rep                  Master_Port: 3306                Connect_Retry: 60              Master_Log_File: mysql-bin.000001          Read_Master_Log_Pos: 2372               Relay_Log_File: ms51-relay-bin.000002                Relay_Log_Pos: 2585        Relay_Master_Log_File: mysql-bin.000001             Slave_IO_Running: No            Slave_SQL_Running: No              ……          Exec_Master_Log_Pos: 2372              Relay_Log_Space: 2791              Until_Condition: None              ……             Master_Server_Id: 1003306                  Master_UUID: 85406fb9-c571-11ea-81ff-0242c0a8bc33             Master_Info_File: /data/mysql/mysql3316/data/master.info                    SQL_Delay: 0              ……           Retrieved_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-9            Executed_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-9                Auto_Position: 0         Replicate_Rewrite_DB:                 Channel_Name:           Master_TLS_Version:1 row in set (0.00 sec)
  
  mysql-master> insert into omg(dtl) values ('b');Query OK, 1 row affected (0.01 sec)
  mysql-master> insert into omg(dtl) values ('b');Query OK, 1 row affected (0.01 sec)
  mysql-master> insert into omg(dtl) values ('b');Query OK, 1 row affected (0.01 sec)
  mysql-master> insert into omg(dtl) values ('b');Query OK, 1 row affected (0.01 sec)
  mysql-master> show master status;+------------------+----------+--------------+------------------+-------------------------------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                         |+------------------+----------+--------------+------------------+-------------------------------------------+| mysql-bin.000001 |     3620 |              |                  | 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-13 |+------------------+----------+--------------+------------------+-------------------------------------------+1 row in set (0.00 sec)
  #此时slave上肯定没有跟进更新啦！mysql-slave> select * from kk.omg;+----+------+| id | dtl |+----+------+| 1 | aaa || 2 | aaa || 3 | aaa |+----+------+3 rows in set (0.00 sec)
  #接下来我们重新开启复制mysql-slave> start slave;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> show slave status\G*************************** 1. row ***************************               Slave_IO_State: Waiting for master to send event                  Master_Host: 127.0.0.1                  Master_User: rep                  Master_Port: 3306                Connect_Retry: 60              Master_Log_File: mysql-bin.000001          Read_Master_Log_Pos: 3620               Relay_Log_File: ms51-relay-bin.000003                Relay_Log_Pos: 1608        Relay_Master_Log_File: mysql-bin.000001             Slave_IO_Running: Yes            Slave_SQL_Running: Yes              ……          Exec_Master_Log_Pos: 3620              Relay_Log_Space: 4245              Until_Condition: None              ……             Master_Server_Id: 1003306                  Master_UUID: 85406fb9-c571-11ea-81ff-0242c0a8bc33             Master_Info_File: /data/mysql/mysql3316/data/master.info                    SQL_Delay: 0          SQL_Remaining_Delay: NULL      Slave_SQL_Running_State: Slave has read all relay log; waiting for more updates              ……           Retrieved_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-13            Executed_Gtid_Set: 85406fb9-c571-11ea-81ff-0242c0a8bc33:1-13                Auto_Position: 0         Replicate_Rewrite_DB:                 Channel_Name:           Master_TLS_Version:1 row in set (0.00 sec)
  #再次查看，发现slave已经更新了。mysql-slave> select * from kk.omg;+----+------+| id | dtl  |+----+------+|  1 | aaa  ||  2 | aaa  ||  3 | aaa  ||  4 | b    ||  5 | b    ||  6 | b    ||  7 | b    |+----+------+7 rows in set (0.00 sec)
  ```

- 可以看到恢复运行后，复制很快便将期间的数据库变更同步到了slave。       

-  

- ------

- 6.尝试玩转复制：sql_thread until

- 实际上，关于复制我们还可以做更多的控制，例如：控制复制从哪里接收、到哪里结束；控制slave在延迟固定时间段后再复制master的动作；控制复制规则，只复制特定的数据库、表，等等等等。

- 

- 在这一章节，我们先来尝试控制复制从哪里接收、到哪里结束，其他的玩法我们在后续的探索中再展开。

- 

- - 玩转场景设计

- 1. 在master上创建复制用户
  2. 分别在master上和slave上创建数据库ky1，创建表ky1.k1
  3. 分别在master和slave上执行reset master；，这样一来，两个实例在数据库ky1上结构一致，且都无binlog，事务状态也一致。
  4. master先做10个事务，并记录每个事务的position和binlogfile信息，之后master不做任何操作。
  5. 在slave上使用position方式配置主从复制，每次指定从不同的position开始及结束复制，观察slave的数据状态。通过这种方式进一步理解日志位置、事务位置和复制结果。
  6. 每次slave对比结束后，都将slave还原，即：在slave上执行：stop slave; reset slave all; deletefrom ky1.k1; reset master;。
  7. 完成还原后再次进行下一次的实验。

- ​       

-  

- - 命令科普

- 在这里了解一下io_thread和sql_thread。在前面章节<配置复制的二三事>中，已经简单描述了io_thread和sql_thread在复制中的重要功能——前者从change master指定的位置开始接收binlog，后者应用前者写完的relay-log。

- ​       

- 我们可以在mysql> 提示符后输入 help start slave; 来查看到更多关于这两位的帮助信息

- 在这里我们截取一小部分，可以发现一个命令参数 until_option——控制复制的停止位。

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql> help start slaveName: 'START SLAVE'Description:Syntax:START SLAVE [thread_types] [until_option] [connection_options] [channel_option]
  thread_types:    [thread_type [, thread_type] ... ]
  thread_type:    IO_THREAD | SQL_THREAD
  until_option:    UNTIL {   {SQL_BEFORE_GTIDS | SQL_AFTER_GTIDS} = gtid_set          |   MASTER_LOG_FILE = 'log_name', MASTER_LOG_POS = log_pos          |   RELAY_LOG_FILE = 'log_name', RELAY_LOG_POS = log_pos          |   SQL_AFTER_MTS_GAPS  }…
  ```

- ​          

- 适应本章节的玩转场景，整理一下，就是：

- - 

- ```
  mysql> start slave sql_thread until MASTER_LOG_FILE= 'log_name', MASTER_LOG_POS= log_pos;
  ```

- ​          

- - 通过relay-log及pos、通过GTID方式的可以自行探索，并思考：

- 1. relay-log和master-log两个方式存在的意义、适合什么场景？
  2. sql_before_gtids和sql_after_gtids两个方式存在的意义、有什么区别？

-    

- ​       

- - 开始玩转！

- - master上创建复制用户

- ​    略。

- ​       

- - master和slave上创建数据库ky1，创建表ky1.k1          

- - 
  - 

- ```
  create database ky1;create table ky1.k1(no int,dtl varchar(20));
  ```

- 

- - 为保证实验清晰，在master和slave上进行reset master

- - 

- ```
  reset master;
  ```

- - master进行事务并记录binlog、pos

- | `No.`  | `SQL`                                                        | `position`                            |
  | ------ | ------------------------------------------------------------ | ------------------------------------- |
  | `准备` | `mysql-master> create database ky1;``mysql-master> create table ky1.k1(no int,dtl varchar(20));``mysql-master> reset master;` |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 154`  |
  | `1`    | `mysql-master>``insert into ky1.k1 select 1,'a';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 462`  |
  | `2`    | `mysql-master>``insert into ky1.k1 select 2,'b';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 770`  |
  | `3`    | `mysql-master>``insert into ky1.k1 select 3,'c';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 1078` |
  | `4`    | `mysql-master>``insert into ky1.k1 select 4,'d';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 1386` |
  | `5`    | `mysql-master>``insert into ky1.k1 select 5,'e';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 1694` |
  | `6`    | `mysql-master>``insert into ky1.k1 select 6,'f';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 2002` |
  | `7`    | `mysql-master>``insert into ky1.k1 select 7,'g';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 2310` |
  | `8`    | `mysql-master>``insert into ky1.k1 select 8,'h';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 2618` |
  | `9`    | `mysql-master>``insert into ky1.k1 select 9,'i';`            |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 2926` |
  | `10`   | `mysql-master>``insert into ky1.k1 select 10,'j';`           |                                       |
  |        |                                                              | `File mysql-bin.000001 Position 3235` |

-    

- - 在slave上使用position方式配置主从复制，并观察结果。

- 

- 实验一：slave从事务1开始，直到最后，不停止复制。

- 从事务1开始，pos=154

- 

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave; reset slave all; delete from ky1.k1; reset master;mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=154;Query OK, 0 rows affected, 2 warnings (0.26 sec)mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread ;Query OK, 0 rows affected (0.01 sec)这里用不上until，想想为什么？
  mysql-slave> select * from ky1.k1;+------+------+| no   | dtl  |+------+------+|    1 | a    ||    2 | b    ||    3 | c    ||    4 | d    ||    5 | e    ||    6 | f    ||    7 | g    ||    8 | h    ||    9 | i    ||   10 | j    |+------+------+10 rows in set (0.00 sec)结论：slave从开始位置一直复制到最新的状态。
  ```

-    

- 实验二：slave从事务1开始，直到事务5之前。

- 从事务1开始，pos=154

- 事务5之前，pos=1386

- 

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave; reset slave all; delete from ky1.k1; reset master;
  mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=154;Query OK, 0 rows affected, 2 warnings (0.26 sec)
  mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread until master_log_file='mysql-bin.000001',master_log_pos=1386;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> select * from ky1.k1;+------+------+| no   | dtl  |+------+------+|    1 | a    ||    2 | b    ||    3 | c    ||    4 | d    |+------+------+4 rows in set (0.01 sec)结论：从指定位置开始复制，位置之前的内容都没有复制到slave；结束位置后的内容也没有复制到slave。
  ```

- ​           

- ​          

- 实验三：slave从事务1开始，直到事务5完成。

- 从事务1开始，pos=154

- 事务5完成，pos=1694

- 

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave; reset slave all; delete from ky1.k1; reset master;
  mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=154;Query OK, 0 rows affected, 2 warnings (0.26 sec)
  mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread until master_log_file='mysql-bin.000001',master_log_pos=1694;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> select * from ky1.k1;+------+------+| no   | dtl  |+------+------+|    1 | a    ||    2 | b    ||    3 | c    ||    4 | d    ||    5 | e    |+------+------+5 rows in set (0.00 sec)结论：从指定位置开始复制，位置之前的内容都没有复制到slave；结束位置后的内容也没有复制到slave。
  ```

- ​    

- 

- ​              

- 实验四：slave从事务3开始，直到事务5完成。

- 从事务3开始，pos=770

- 事务5完成，pos=1694 

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave; reset slave all; delete from ky1.k1; reset master;
  mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=770;Query OK, 0 rows affected, 2 warnings (0.26 sec)
  mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread until master_log_file='mysql-bin.000001',master_log_pos=1694;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> select * from ky1.k1;+------+------+| no   | dtl  |+------+------+|    3 | c    ||    4 | d    ||    5 | e    |+------+------+3 rows in set (0.00 sec)结论：从指定位置开始复制，位置之前的内容都没有复制到slave；结束位置后的内容也没有复制到slave。
  ```

- ​         

- 实验五：slave从事务5完成后开始，直到事务9完成。

- 从事务5完成开始，pos=1694

- 事务9完成，pos=2926

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  mysql-slave> stop slave; reset slave all; delete from ky1.k1; reset master;
  mysql-slave> change master to master_host='127.0.0.1', master_port=3306,master_user='rep',master_password='rep',master_log_file='mysql-bin.000001',master_log_pos=1694;Query OK, 0 rows affected, 2 warnings (0.26 sec)
  mysql-slave> start slave io_thread;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> start slave sql_thread until master_log_file='mysql-bin.000001',master_log_pos=2926;Query OK, 0 rows affected (0.01 sec)
  mysql-slave> select * from ky1.k1;+------+------+| no   | dtl  |+------+------+|    6 | f    ||    7 | g    ||    8 | h    ||    9 | i    |+------+------+4 rows in set (0.00 sec)结论：从指定位置开始复制，位置之前的内容都没有复制到slave；结束位置后的内容也没有复制到slave。
  ```

- 

- 从五个实验结果，结合master事务对应pos去对比，你都发现了什么？

- 至此，我们应该敢于尝试根据不同的场景需求，对主从复制架构的binlog position进行随心所欲的读取了吧！

-  

- ------

- 7.总结，以及一些思考——可能是由浅入深的跳板

- *原本以为异步复制的内容不会很多，事实狠狠的教会我做人。*

- 

- 首先总结一下本次旅途的干货

- 

- POS方式配置主从复制需要配置的内容：

- 1. server_id主从不可重复
  2. binlog_format=row
  3. 需要一个复制用的账号（具有replication slave权限）

-    

- 配置replication的命令

- 

- - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 
  - 

- ```
  slave上执行 change master to master_host='host_address',master_port=3306,master_user='',master_password='',master_auto_position=;其中，  master_host，master的地址  master_port，master的数据库端口  master_user，master实例上具有replication slave权限的用户名  master_password，master实例上具有replication slave权限的用户的密码  master_auto_position，是否启用自动定位GTID  master_log_file，使用position方式时指定要开始复制的binlog filename  master_log_pos，使用position方式时指定要开始复制的binlog position，需配合master_log_file参数一起使用
  ```

- 

- 复制控制相关命令

- 启动、停止复制

- - 

- ```
  slave上执行  start slave; / stop slave;
  ```

- 启动、停止io_thread

- - 

- ```
  slave上执行  start slave io_thread; /stop slave io_thread;
  ```

- 启动、停止sql_thread

- - 

- ```
  slave上执行  start slave sql_thread; /stop slave sql_thread;
  ```

- 设置复制停止位（起始位在change matser中指定了）

- 

- - 
  - 
  - 

- ```
  start slave sql_thread until MASTER_LOG_FILE= 'log_name', MASTER_LOG_POS= log_pos;
  更多玩法在mysql> 中执行 help start slave; 查看。
  ```

- 查看复制状态

- - 

- ```
  slave上执行  show slave status \G
  ```

- 

- 今天实验里复制搭建的逻辑顺序

- 1. 正确配置主从数据库实例的参数
  2. 新搭建的master清空binlog：reset master; *#想想这一步有什么意义？有必要性吗？*
  3. master创建复制用户并授权
  4. 新搭建的slave清空binlog：reset master; *#想想这一步有什么意义？*
  5. slave使用change master 命令配置复制
  6. slave启动复制

- ​          

- 两个思考，留给你们。

- - 搭建实验里，场景是master与slave都为全新环境，搭建完成后才开始提供数据库服务。如果一个MySQL实例已经使用了很久，数据量很大甚至有可能并未启用binlog，该如何以此为master搭建主从复制？这种情况下新建的slave如何能和master同步起来？
  - 如果master已经使用了很久，尽管数据量很大，但是其中只有一个数据量并不大的数据库十分重要，这种情况下如何搭建主从复制？

- ​       

- 

- ------

- *这一次的探索之旅稍显漫长。
  *

- *其实MySQL replication在逻辑上非常简单易懂，不过越是简单的东西延伸的内容便越会复杂。文字码了很多，单凭阅读去理解MySQL复制的话难免有些理想主义，如果你对MySQL复制还很生疏，那么请多多操作练习，多多开动脑洞给自己“找麻烦”，通过各种各样的“麻烦”去促使自己对MySQL复制有进一步的了解。
  *

- 

- *如果本次探索之旅依然令你对MySQL异步复制、主从复制有诸多疑惑，欢迎留言评论，让我们共同讨论学习。另外，由于章节出乎意料的超长，难免有细节考虑不周，欢迎您来拍砖讨论。
  *

- 

- **下一次旅程不一定准的预告：\**GTID你好哇&\**一致性备份数据库&使用备份创建从库**