- 所以主从复制环境里，DDL切记要诸多留意。
  > - 从库复制的一个坑
  >  MySQL 5.7.17，在主库上不使用 `use db1;`，直接在db2库上执行` truncate table db1.tb1;`，从库上会不生效。

这个case一直存在，原因为DDL在复制场景下都是以statement方式实现的。

问题复现方式：

从库

```
mysql> change replication filter replicate_do_db=(kk); #只复制kk库的变更
Query OK, 0 rows affected (0.00 sec)
```

主库

```
mysql> use kk; #主库use kk后，在kk库建表
mysql> show tables;
+--------------+
| Tables_in_kk |
+--------------+
| new     |
| uu      |
| xx      |
| yy      |
+--------------+
4 rows in set (0.00 sec)
 
mysql> create table tb01(id int);
Query OK, 0 rows affected (0.02 sec)
 
```

从库

```
mysql> show tables;  #从库确认操作被重放
+--------------+
| Tables_in_kk |
+--------------+
| new     |
| tb01     |
| uu      |
| xx      |
| yy      |
+--------------+
5 rows in set (0.00 sec)
 
mysql> create table tb02(id int); #主库use kk后，在kk库建表
Query OK, 0 rows affected (0.01 sec)
 
```

从库

```
mysql> show tables;  #从库确认操作被重放
+--------------+
| Tables_in_kk |
+--------------+
| new     |
| tb01     |
| tb02     |
| uu      |
| xx      |
| yy      |
+--------------+
6 rows in set (0.00 sec)
 
主库
mysql> use db2020  #主库use db2020后，在kk库建表
Database changed
mysql> create table kk.tb03(id int);
Query OK, 0 rows affected (0.03 sec)
```

 

从库

```
mysql> show tables;  #从库未重放
+--------------+
| Tables_in_kk |
+--------------+
| new     |
| tb01     |
| tb02     |
| uu      |
| xx      |
| yy      |
+--------------+
6 rows in set (0.00 sec)
 
mysql> show master status; #从库查看
+------------------+----------+-------------------------------------------+
| File       | Position | Executed_Gtid_Set             |
+------------------+----------+-------------------------------------------+
| mysql-bin.000001 |  14876 | af98b3b7-393c-11ea-bd78-000c29f0aa33:1-64 |
+------------------+----------+-------------------------------------------+
1 row in set (0.00 sec)
 
mysql> show slave status \G #从库查看
*************************** 1. row ***************************
       Master_Log_File: mysql-bin.000004
     Read_Master_Log_Pos: 6488
        Relay_Log_File: mysqlvm1-1-relay-bin.000004
 
[root@mysqlvm1-1 data]# mysqlbinlog --base64-output=decode-rows mysqlvm1-1-relay-bin.000004 |less  #从库查看relaylog，看到事务binlog传输正常
 
SET @@SESSION.GTID_NEXT= 'af98b3b7-393c-11ea-bd78-000c29f0aa33:64'/*!*/;
# at 6276
#200120 18:40:14 server id 941673308 end_log_pos 6488 CRC32 0xd60b1a6e     Query  thread_id=21  exec_time=0   error_code=0
use `db2020`/*!*/;
SET TIMESTAMP=1579516814/*!*/;
create table kk.tb03(id int)
/*!*/;
SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/;
DELIMITER ;
# End of log file
 
[root@mysqlvm1-1 logs]# mysqlbinlog --base64-output=decode-rows mysql-bin.000001 |less #从库查看binlog，看到事务64被忽略（因为filter规则）
 
SET @@SESSION.GTID_NEXT= 'af98b3b7-393c-11ea-bd78-000c29f0aa33:62'/*!*/;
# at 14407
#200120 18:39:40 server id 941673308 end_log_pos 14502 CRC32 0x5668188a    Query  thread_id=21  exec_time=0   error_code=0
SET TIMESTAMP=1579516780/*!*/;
create table tb01(id int)
/*!*/;
# at 14502
#200120 18:39:58 server id 941673308 end_log_pos 14567 CRC32 0x6093a4c6    GTID  last_committed=52    sequence_number=53   rbr_only=no
SET @@SESSION.GTID_NEXT= 'af98b3b7-393c-11ea-bd78-000c29f0aa33:63'/*!*/;
# at 14567
#200120 18:39:58 server id 941673308 end_log_pos 14662 CRC32 0x95917a53    Query  thread_id=21  exec_time=0   error_code=0
SET TIMESTAMP=1579516798/*!*/;
create table tb02(id int)
/*!*/;
# at 14662
#200120 18:40:14 server id 941673308 end_log_pos 14727 CRC32 0x06781961    GTID  last_committed=53    sequence_number=54   rbr_only=no
SET @@SESSION.GTID_NEXT= 'af98b3b7-393c-11ea-bd78-000c29f0aa33:64'/*!*/;
# at 14727
#200120 18:40:14 server id 941673308 end_log_pos 14801 CRC32 0xf7fb29d8    Query  thread_id=21  exec_time=0   error_code=0
SET TIMESTAMP=1579516814/*!*/;
BEGIN
/*!*/;
# at 14801
#200120 18:40:14 server id 941673308 end_log_pos 14876 CRC32 0x8478c466    Query  thread_id=21  exec_time=0   error_code=0
SET TIMESTAMP=1579516814/*!*/;
COMMIT
/*!*/;
SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/;
DELIMITER ;
# End of log file
```