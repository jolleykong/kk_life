# 环境信息

单机多实例搭建。

| IP              | mysql_port | mysqlx_port |
| --------------- | ---------- | ----------- |
| 192.168.188.201 | 3306       | 13306       |
|                 | 3307       | 13307       |
|                 | 3308       | 13308       |
|                 | 3309       | 13309       |

 

# 搭建环境

先搭建3306

由于MGR group name只接受UUID格式，所以可以先从bash中运行**uuidgen**来生成一个。

[root@mysqlvm1-1 mysql3306]# uuidgen

6e84d643-a0be-4e66-826e-96465d3d6397

 

常规配置文件中加入以下内容，以开启MGR：single-master

\#其它注意参数

log-bin=$mysql-bin_path

server_id=$n

gtid_mode=ON

enforce_gtid_consistency=ON

master_info_repository=TABLE

relay_log_info_repository=TABLE

binlog_checksum=NONE

log_slave_update=ON

binlog_format=ROW

 

\#MGR

transaction_write_set_extraction=XXHASH64

loose-group_replication_group_name="6e84d643-a0be-4e66-826e-96465d3d6397" #must be use UUID format ，同一个GR里的group_name一致。

loose-group_replication_start_on_boot=off

loose-group_replication_local_address="192.168.188.201:13306"

loose-group_replication_group_seeds="192.168.188.201:13306,192.168.188.201:13307,192.168.188.201:13308,192.168.188.201:13309"

loose-group_replication_bootstrap_group=off

 

\#MGR multi master

\#loose-group_replication_single_primary_mode=off

\#loose-group_replication_enforce_update_everywhere_checks=on

 

并且，要注意以下两个参数：

server_id 必须唯一，不能重复

binlog_checksum=none

 

初始化实例

[root@mysqlvm1-1 ~]# ./mysql_onekey_3.1.sh /opt/mysql-5.7.26-linux-glibc2.12-x86_64/ 3306

或

[root@mysqlvm1-1 ~]# mysqld --defaults-file=/data/mysq/mysql3306/my3306.cnf --initialize-insecure

 

# 配置3306的MGR

```
[root@mysqlvm1-1 ~]# mysql -S /data/mysql/mysql3306/tmp/mysql.sock 
mysql> set global super_read_only=0;
 
mysql> set global read_only=0;
 
mysql> set sql_log_bin=0;
 
mysql> create user 'rep'@'%' identified by 'rep';
 
mysql> grant replication slave on *.* to 'rep'@'%';
 
mysql> set sql_log_bin=1;
 
mysql> show master status;
+------------------+----------+--------------+------------------+-------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000003 |   150 |       |         |          |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
 
mysql> change master to master_user='rep',master_password='rep' for channel 'group_replication_recovery';
Query OK, 0 rows affected, 2 warnings (0.01 sec)
 
mysql> install plugin group_replication soname 'group_replication.so';
Query OK, 0 rows affected (0.00 sec)
 
mysql> show plugins ;
| group_replication     | ACTIVE  | GROUP REPLICATION | group_replication.so | GPL   |
 
mysql> set global group_replication_bootstrap_group=on;
Query OK, 0 rows affected (0.00 sec)
 
mysql> start group_replication;
Query OK, 0 rows affected (2.02 sec)
###启动后，就可以set global group_replication_bootstrap_group=off;了。这样的好处是：如果节点1挂掉，那么选举时间会提升。
```

 

第一个节点要执行set global group_replication_bootstrap_group=on再进行，否则start group_replication：

```
mysql> start group_replication;
ERROR 3092 (HY000): The server is not configured properly to be an active member of the group. Please see more details on error log.
 
查看节点加入情况
mysql> select * from performance_schema.replication_group_members;
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME       | MEMBER_ID              | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | b20aa95c-69fb-11ea-9f37-000c2950e14e | mysqlvm1-1 |    3306 | ONLINE    |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
1 row in set (0.00 sec)
 
```

查看single-primary角色

```
mysql> select * from performance_schema.global_status where variable_name='group_replication_primary_member';
+----------------------------------+--------------------------------------+
| VARIABLE_NAME          | VARIABLE_VALUE            |
+----------------------------------+--------------------------------------+
| group_replication_primary_member | b20aa95c-69fb-11ea-9f37-000c2950e14e |
+----------------------------------+--------------------------------------+
1 row in set (0.03 sec)
 
```

# 搭建并配置3307\3308\3309

```
[root@mysqlvm1-1 mysql]# mkdir mysql3307/{logs,data,tmp} -p
[root@mysqlvm1-1 mysql]# cp mysql3306/my3306.cnf mysql3307/my3307.cnf
[root@mysqlvm1-1 mysql]# chown mysql:mysql -R mysql3307
[root@mysqlvm1-1 mysql]# sed -i 's/3306/3307/g' mysql3307/my3307.cnf 
[root@mysqlvm1-1 mysql]# vi !$
 
#MGR
transaction_write_set_extraction=XXHASH64
loose-group_replication_group_name="6e84d643-a0be-4e66-826e-96465d3d6397" #must be use UUID format 
loose-group_replication_start_on_boot=off
loose-group_replication_local_address="192.168.188.201:13307"
loose-group_replication_group_seeds="192.168.188.201:13306,192.168.188.201:13307,192.168.188.201:13308,192.168.188.201:13309"
loose-group_replication_bootstrap_group=off
 
#MGR multi master
#loose-group_replication_single_primary_mode=off
#loose-group_replication_enforce_update_everywhere_checks=on
 
[root@mysqlvm1-1 mysql]# mysqld --defaults-file=/data/mysql/mysql3307/my3307.cnf --initialize-insecure
[root@mysqlvm1-1 mysql]# mysqld --defaults-file=/data/mysql/mysql3307/my3307.cnf &
[root@mysqlvm1-1 mysql]# mysql -S /data/mysql/mysql3307/tmp/mysql.sock
 
mysql> set global super_read_only=0;
Query OK, 0 rows affected (0.00 sec)
 
mysql> set global read_only=0;
Query OK, 0 rows affected (0.00 sec)
 
mysql> set sql_log_bin=0;
Query OK, 0 rows affected (0.00 sec)
 
mysql> create user 'rep'@'%' identified by 'rep';
Query OK, 0 rows affected (0.00 sec)
 
mysql> grant replication slave on *.* to 'rep'@'%';
Query OK, 0 rows affected (0.00 sec)
 
mysql> set sql_log_bin=1;
Query OK, 0 rows affected (0.00 sec)
 
mysql> change master to master_user='rep',master_password='rep' for channel 'group_replication_recovery';
Query OK, 0 rows affected, 2 warnings (0.00 sec)
 
mysql> install plugin group_replication soname 'group_replication.so';
Query OK, 0 rows affected (0.01 sec)
 
mysql> start group_replication;
Query OK, 0 rows affected (3.07 sec)
 
mysql> set global group_replication_bootstrap_group=on;       其实就是这步不做，其他都一样。
Query OK, 0 rows affected (0.00 sec) 
 
配置3308、3309同理，略了。
 
 
查看节点加入情况
mysql> select * from performance_schema.replication_group_members;
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME       | MEMBER_ID              | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 19cb564a-6a01-11ea-9965-000c2950e14e | mysqlvm1-1 |    3307 | ONLINE    |
| group_replication_applier | 41c082c3-6a02-11ea-a88f-000c2950e14e | mysqlvm1-1 |    3308 | ONLINE    |
| group_replication_applier | 499988d9-6a02-11ea-aa0a-000c2950e14e | mysqlvm1-1 |    3309 | ONLINE    |
| group_replication_applier | b20aa95c-69fb-11ea-9f37-000c2950e14e | mysqlvm1-1 |    3306 | ONLINE    |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
4 rows in set (0.06 sec)
 
```

查看single-primary角色

```
mysql> select * from performance_schema.global_status where variable_name='group_replication_primary_member';
+----------------------------------+--------------------------------------+
| VARIABLE_NAME          | VARIABLE_VALUE            |
+----------------------------------+--------------------------------------+
| group_replication_primary_member | b20aa95c-69fb-11ea-9f37-000c2950e14e |
+----------------------------------+--------------------------------------+
1 row in set (0.03 sec)
```

 

MGR搭建完成。

 

\----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 此时做个实验：

1. 在primary(3306)上建库建表

```
mysql> create database kk;
Query OK, 1 row affected (0.16 sec)
 
mysql> use kk
Database changed
 
mysql> create table kktb(id int primary key,name varchar(100));
Query OK, 0 rows affected (0.23 sec)
 
mysql> insert into kktb(id,name) values (1,'aa');
Query OK, 1 row affected (0.74 sec)
 
mysql> insert into kktb(id,name) values (2,'b');
Query OK, 1 row affected (0.06 sec)
 
mysql> select * from kk.kktb;
+----+------+
| id | name |
+----+------+
| 1 | aa  |
| 2 | b  |
+----+------+
2 rows in set (0.01 sec)
```

 

1. 在slave上查询

```
mysql> select * from kk.kktb;
+----+------+
| id | name |
+----+------+
| 1 | aa  |
| 2 | b  |
+----+------+
2 rows in set (0.00 sec)
 
mysql> select @@port,@@server_id;
+--------+-------------+
| @@port | @@server_id |
+--------+-------------+
|  3307 |  10243307 |
+--------+-------------+
1 row in set (0.01 sec)
```

 

1. 在所有节点进行一次insert，看看会发生什么

```
3306mysql> insert into kk.kktb(id,name) values (@@port,@@server_id);
Query OK, 1 row affected (0.02 sec)
 
3307、3308、3309mysql> insert into kk.kktb(id,name) values (@@port,@@server_id);
ERROR 1290 (HY000): The MySQL server is running with the --super-read-only option so it cannot execute this statement
 
mysql> select * from kk.kktb;
+------+----------+
| id  | name   |
+------+----------+
|  1 | aa    |
|  2 | b    |
| 3306 | 10243306 |
+------+----------+
3 rows in set (0.00 sec)
 
```

**结论：****single primary****模式下，在****MGR****启动后，非****primary****角色会自动****read_only&& super_read_only**

```
 
mysql> select @@port,@@server_id,@@read_only,@@super_read_only;
+--------+-------------+-------------+-------------------+
| @@port | @@server_id | @@read_only | @@super_read_only |
+--------+-------------+-------------+-------------------+
|  3306 |  10243306 |      0 |         0 |
+--------+-------------+-------------+-------------------+
1 row in set (0.00 sec)
 
mysql> select @@port,@@server_id,@@read_only,@@super_read_only;
+--------+-------------+-------------+-------------------+
| @@port | @@server_id | @@read_only | @@super_read_only |
+--------+-------------+-------------+-------------------+
|  3307 |  10243307 |      1 |         1 |
+--------+-------------+-------------+-------------------+
1 row in set (0.00 sec)
 
mysql> select @@port,@@server_id,@@read_only,@@super_read_only;
+--------+-------------+-------------+-------------------+
| @@port | @@server_id | @@read_only | @@super_read_only |
+--------+-------------+-------------+-------------------+
|  3308 |  10243308 |      1 |         1 |
+--------+-------------+-------------+-------------------+
1 row in set (0.00 sec)
 
mysql> select @@port,@@server_id,@@read_only,@@super_read_only;
+--------+-------------+-------------+-------------------+
| @@port | @@server_id | @@read_only | @@super_read_only |
+--------+-------------+-------------+-------------------+
|  3309 |  10243309 |      1 |         1 |
+--------+-------------+-------------+-------------------+
1 row in set (0.00 sec)
 
```

 

如果强制更改为可写呢？

——经过实验，目前发现后果会这样：

slave将read_only=1，slave创建db、table等操作，也会复制到其他节点，但查询主节点时，结果依然是原主节点，集群状态查询还是ONLIINE。

当该slave和master同时对一个表做DML的时候，其中一个会报错，此时再查看MGR状态，集群便ERROR了。

 

```
mysql> select * from performance_schema.replication_group_members;select * from performance_schema.global_status where variable_name='group_replication_primary_member';
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME       | MEMBER_ID              | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 19cb564a-6a01-11ea-9965-000c2950e14e | mysqlvm1-1 |    3307 | ONLINE    |
| group_replication_applier | 41c082c3-6a02-11ea-a88f-000c2950e14e | mysqlvm1-1 |    3308 | ONLINE    |
| group_replication_applier | 499988d9-6a02-11ea-aa0a-000c2950e14e | mysqlvm1-1 |    3309 | ONLINE    |
| group_replication_applier | b20aa95c-69fb-11ea-9f37-000c2950e14e | mysqlvm1-1 |    3306 | ONLINE    |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
4 rows in set (0.02 sec)
 
+----------------------------------+--------------------------------------+
| VARIABLE_NAME          | VARIABLE_VALUE            |
+----------------------------------+--------------------------------------+
| group_replication_primary_member | b20aa95c-69fb-11ea-9f37-000c2950e14e |
+----------------------------------+--------------------------------------+
1 row in set (0.02 sec)
 
mysql> insert into tt values(9,'a');
ERROR 1062 (23000): Duplicate entry '9' for key 'PRIMARY'
mysql> select * from performance_schema.replication_group_members;select * from performance_schema.global_status where variable_name='group_replication_primary_member';
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME       | MEMBER_ID              | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | b20aa95c-69fb-11ea-9f37-000c2950e14e | mysqlvm1-1 |    3306 | ERROR    |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
1 row in set (0.02 sec)
 
+----------------------------------+----------------+
| VARIABLE_NAME          | VARIABLE_VALUE |
+----------------------------------+----------------+
| group_replication_primary_member | UNDEFINED   |
+----------------------------------+----------------+
1 row in set (0.05 sec)
 
```

此时3306的err log：

2020-03-20T01:39:44.117125+08:00 17 [ERROR] Slave SQL for channel 'group_replication_applier': Worker 1 failed executing transaction '6e84d643-a0be-4e66-826e-96465d3d6397:1000011'; Could not execute Write_rows event on table kk.tt; Duplicate entry '9' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY, Error_code: 1062

2020-03-20T01:39:44.129420+08:00 16 [Warning] Slave SQL for channel 'group_replication_applier': ... The slave coordinator and worker threads are stopped, possibly leaving data in inconsistent state. A restart should restore consistency automatically, although using non-transactional storage for data or info tables or DDL queries could lead to problems. In such cases you have to examine your data (see documentation for details). Error_code: 1756

2020-03-20T01:39:44.129467+08:00 16 [Note] Error reading relay log event for channel 'group_replication_applier': slave SQL thread was killed

2020-03-20T01:39:44.129554+08:00 16 [ERROR] Plugin group_replication reported: 'The applier thread execution was aborted. Unable to process more transactions, this member will now leave the group.'

2020-03-20T01:39:44.129732+08:00 13 [ERROR] Plugin group_replication reported: 'Fatal error during execution on the Applier process of Group Replication. The server will now leave the group.'

2020-03-20T01:39:44.129785+08:00 13 [ERROR] Plugin group_replication reported: 'The server was automatically set into read only mode after an error was detected.'

2020-03-20T01:39:44.142619+08:00 16 [Note] Slave SQL thread for channel 'group_replication_applier' exiting, replication stopped in log 'FIRST' at position 222

2020-03-20T01:39:44.149003+08:00 13 [Note] Plugin group_replication reported: 'Going to wait for view modification'

2020-03-20T01:39:47.358636+08:00 0 [Note] Plugin group_replication reported: 'Group membership changed: This member has left the group.'

2020-03-20T01:39:47.359467+08:00 13 [Note] Plugin group_replication reported: 'The group replication applier thread was killed'

```
 
```