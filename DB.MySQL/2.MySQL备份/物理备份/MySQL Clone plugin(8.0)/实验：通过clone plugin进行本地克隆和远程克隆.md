# 实验：通过clone plugin进行本地克隆和远程克隆

[TOC]



## 本地克隆

环境信息

| 192.168.188.81 | 3306 | localnode1      | /data/mysql/mysql3306  |
| -------------- | ---- | --------------- | ---------------------- |
|                | 3309 | localnode1clone | /data/mysql/mysql3306c |



- 为克隆实例创建目录
由于mysql clone plugin的限制，不能指定已经存在的目录，否则会报1007错误，因此在这一步不创建data目录。
```
[root@ms81 mysql]# mkdir -p mysql3306c/{logs,tmp}
[root@ms81 mysql]# chown mysql:mysql -R /data/mysql/mysql3306c
[root@ms81 mysql]# ls
mysql3306 mysql3306c mysql3307
[root@ms81 mysql]# cd mysql3306c
[root@ms81 mysql3306c]# ls
logs tmp
```

- 检查被克隆实例的参数，并安装clone plugin
```
mysql> show global variables like '%require%';
+--------------------------+-------+
| Variable_name      | Value |
+--------------------------+-------+
| password_require_current | OFF  |
| require_secure_transport | OFF  |
| sql_require_primary_key | OFF  |
+--------------------------+-------+
3 rows in set (0.00 sec)
 
mysql> show global variables like '%timestamp%';
+---------------------------------+--------+
| Variable_name          | Value |
+---------------------------------+--------+
| explicit_defaults_for_timestamp | ON   |
| log_timestamps         | SYSTEM |
+---------------------------------+--------+
2 rows in set (0.00 sec)
 
mysql> install plugin clone soname 'mysql_clone.so';
Query OK, 0 rows affected (0.01 sec)
 mysql> show plugins;
+---------------------------------+----------+--------------------+----------------+---------+
| clone              | ACTIVE  | CLONE       | mysql_clone.so | GPL   |
+---------------------------------+----------+--------------------+----------------+---------+
45 rows in set (0.01 sec)
 
mysql> show global variables like '%clone%';
+-----------------------------+---------+
| Variable_name        | Value  |
+-----------------------------+---------+
| clone_autotune_concurrency | ON   |
| clone_buffer_size      | 4194304 |
| clone_ddl_timeout      | 300   |
| clone_enable_compression  | OFF   |
| clone_max_concurrency    | 16   |
| clone_max_data_bandwidth  | 0    |
| clone_max_network_bandwidth | 0    |
| clone_ssl_ca        |     |
| clone_ssl_cert       |     |
| clone_ssl_key        |     |
| clone_valid_donor_list   |     |
+-----------------------------+---------+
11 rows in set (0.00 sec)
```

- 先查看一下被克隆库的状态
```
mysql> show master status;
+------------------+----------+--------------+------------------+---------------------------------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set              |
+------------------+----------+--------------+------------------+---------------------------------------------+
| mysql-bin.000007 |   748 |       |         | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------------------+----------+--------------+------------------+---------------------------------------------+
1 row in set (0.00 sec)
 
mysql> select count(*) from kk.k1;
+----------+
| count(*) |
+----------+
|  108100 |
+----------+
1 row in set (0.00 sec)
```

- 在被克隆库上执行，克隆实例到指定目录
/data/mysql/mysql3306c/data绝对不能存在，否则报错
```
mysql> clone local data directory='/data/mysql/mysql3306c/data';
Query OK, 0 rows affected (0.38 sec)
```

- 检查克隆状态
```
mysql> SELECT * FROM performance_schema.clone_status;
+------+------+-----------+-------------------------+-------------------------+----------------+------------------------------+----------+---------------+-------------+-----------------+---------------+
| ID  | PID | STATE   | BEGIN_TIME       | END_TIME        | SOURCE     | DESTINATION
   | ERROR_NO | ERROR_MESSAGE | BINLOG_FILE | BINLOG_POSITION | GTID_EXECUTED |
+------+------+-----------+-------------------------+-------------------------+----------------+------------------------------+----------+---------------+-------------+-----------------+---------------+
|  1 | 9831 | Completed | 2020-05-11 09:40:51.691 | 2020-05-11 09:40:52.063 | LOCAL INSTANCE | /data/mysql/mysql3306c/data/ |    0 |        |       |        0 |        |
+------+------+-----------+-------------------------+-------------------------+----------------+------------------------------+----------+---------------+-------------+-----------------+---------------+
1 row in set (0.00 sec)
```

- 查看克隆目标目录结构
```
[root@ms81 mysql3306c]# tree
.
├── data
│  ├── #clone
│  │  ├── #replace_files
│  │  ├── #status_fix
│  │  ├── #view_progress
│  │  └── #view_status
│  ├── ib_buffer_pool
│  ├── ibdata1
│  ├── ib_logfile0
│  ├── ib_logfile1
│  ├── kk
│  │  └── k1.ibd
│  ├── mysql
│  ├── mysql.ibd
│  ├── sys
│  │  └── sys_config.ibd
│  ├── undo_001
│  └── undo_002
├── logs
└── tmp
```

- 对比被克隆库的目录结构
```
[root@ms81 mysql3306]# tree
.
├── data
│  ├── auto.cnf
│  ├── ca-key.pem
│  ├── ca.pem
│  ├── client-cert.pem
│  ├── client-key.pem
│  ├── #ib_archive
│  │  └── ib_dblwr
│  │    └── dblwr_0
│  ├── ib_buffer_pool
│  ├── ibdata1
│  ├── ib_logfile0
│  ├── ib_logfile1
│  ├── ib_logfile2
│  ├── ibtmp1
│  ├── #innodb_temp
│  │  ├── temp_1.ibt
│  │  ├── temp_2.ibt
│  ├── kk
│  │  └── k1.ibd
│  ├── ms81.pid
│  ├── mysql
│  │  ├── general_log_201.sdi
│  │  ├── general_log.CSM
│  │  ├── general_log.CSV
│  │  ├── slow_log_202.sdi
│  │  ├── slow_log.CSM
│  │  └── slow_log.CSV
│  ├── mysql.ibd
│  ├── performance_schema
│  │  ├── accounts_138.sdi
│  │  ├── variables_by_thr_174.sdi
│  │  └── variables_info_177.sdi
│  ├── private_key.pem
│  ├── public_key.pem
│  ├── server-cert.pem
│  ├── server-key.pem
│  ├── sys
│  │  └── sys_config.ibd
│  ├── undo_001
│  └── undo_002
├── logs
│  ├── error.log
│  ├── general.log
│  ├── mysql-bin.000001
│  ├── mysql-bin.index
│  └── slow_query.log
├── my3306.cnf
└── tmp
  ├── mysql.sock
  └── mysql.sock.lock
```

- 尝试启动克隆库

对比中发现，clone plugin只克隆了data目录。根据cloneplugin特性得知，如果有自定义undo目录，那么该目录结构也不会被克隆，在这种情况下，需要手动创建目录结构并移动自定义undo表空间文件，或直接修改my.cnf文件。

 

- 参照源库my.cnf文件进行调整
```
[root@ms81 mysql3306c]# pwd
/data/mysql/mysql3306c

[root@ms81 mysql3306c]# ls
data logs my3306c.cnf tmp

[root@ms81 mysql3306c]# cp ../mysql3306/my3306.cnf ./my3306c.cnf
[root@ms81 mysql3306c]# sed -i 's/3306/3309/g' my3306c.cnf
[root@ms81 mysql3306c]# sed -i 's#/data/mysql/mysql3309#/data/mysql/mysql3306c#g' my3306c.cnf

[root@ms81 mysql3306c]# mysqld --defaults-file=/data/mysql/mysql3306c/my3306c.cnf &

[root@ms81 mysql3306c]# mysql -S /data/mysql/mysql3306c/tmp/mysql.sock
```

- 检查克隆库状态
```
mysql> show master status;

+------------------+----------+--------------+------------------+---------------------------------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set              |
+------------------+----------+--------------+------------------+---------------------------------------------+
| mysql-bin.000002 |   155 |       |         | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------------------+----------+--------------+------------------+---------------------------------------------+
1 row in set (0.00 sec)

mysql> select count(*) from kk.k1;

+----------+
| count(*) |
+----------+
|  108100 |
+----------+
1 row in set (0.09 sec)
```

## 远程克隆到本地：克隆到当前实例

环境信息

| 192.168.188.81 | 3306 | remote node（被克隆库） | /data/mysql/mysql3306 |
| -------------- | ---- | ----------------------- | --------------------- |
| 192.168.188.82 | 3306 | localnode（克隆库）     | /data/mysql/mysql3306 |

在远程库（被克隆库）上创建克隆user

```
mysql> create user clone@'192.168.188.%' identified by 'clone';
Query OK, 0 rows affected (0.02 sec)
mysql> grant backup_admin on *.* to clone@'192.168.188.%';
Query OK, 0 rows affected (0.02 sec)
```

- 在远程库上安装clone plugin
```
mysql> install plugin clone soname 'mysql_clone.so';
Query OK, 0 rows affected (0.01 sec)
 mysql> show plugins;
+---------------------------------+----------+--------------------+----------------+---------+
| clone              | ACTIVE  | CLONE       | mysql_clone.so | GPL   |
+---------------------------------+----------+--------------------+----------------+---------+
45 rows in set (0.01 sec)
 
mysql> show global variables like '%clone%';
+-----------------------------+---------+
| Variable_name        | Value  |
+-----------------------------+---------+
| clone_autotune_concurrency | ON   |
| clone_buffer_size      | 4194304 |
| clone_ddl_timeout      | 300   |
| clone_enable_compression  | OFF   |
| clone_max_concurrency    | 16   |
| clone_max_data_bandwidth  | 0    |
| clone_max_network_bandwidth | 0    |
| clone_ssl_ca        |     |
| clone_ssl_cert       |     |
| clone_ssl_key        |     |
| clone_valid_donor_list   |     |
+-----------------------------+---------+
11 rows in set (0.00 sec)
```

- 查看远程库状态
```
mysql> show master status;
+------------------+----------+--------------+------------------+---------------------------------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set              |
+------------------+----------+--------------+------------------+---------------------------------------------+
| mysql-bin.000007 |   748 |       |         | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------------------+----------+--------------+------------------+---------------------------------------------+
1 row in set (0.00 sec)
 
mysql> select count(*) from kk.k1;
+----------+
| count(*) |
+----------+
|  108100 |
+----------+
1 row in set (0.00 sec)
```

- 启动本地实例（克隆目标库），设置参数并安装clone plugin
```
mysql> set global super_read_only=0;
Query OK, 0 rows affected (0.00 sec)
 
mysql> install plugin clone soname 'mysql_clone.so';
Query OK, 0 rows affected (0.02 sec)
```
- 查看当前本地实例状态
```
（新库）
mysql> show master status;
+------------------+----------+--------------+------------------+-------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000002 |   155 |       |         |          |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
 
mysql> show global variables like '%clone%';
+-----------------------------+---------+
| Variable_name        | Value  |
+-----------------------------+---------+
| clone_autotune_concurrency | ON   |
| clone_buffer_size      | 4194304 |
| clone_ddl_timeout      | 300   |
| clone_enable_compression  | OFF   |
| clone_max_concurrency    | 16   |
| clone_max_data_bandwidth  | 0    |
| clone_max_network_bandwidth | 0    |
| clone_ssl_ca        |     |
| clone_ssl_cert       |     |
| clone_ssl_key        |     |
| clone_valid_donor_list   |     |
+-----------------------------+---------+
11 rows in set (0.01 sec)
```

- 在本地实例配置clone donor
```
mysql> set global clone_valid_donor_list='192.168.188.81:3306';
Query OK, 0 rows affected (0.00 sec)
```
- 克隆远程实例到本地，覆盖本地实例
由于mysqld启动的，所以不会自动拉起实例。
```
mysql> clone instance from 'clone'@'192.168.188.81':3306 identified by 'clone';
ERROR 3707 (HY000): Restart server failed (mysqld is not managed by supervisor process).
mysql> exit
Bye
```

- 手动拉起实例
```
[root@ms82 ~]# mysqld --defaults-file=/data/mysql/mysql3306/my3306.cnf &
[1] 438
 
[root@ms82 data]# mysql -S /data/mysql/mysql3306/tmp/mysql.sock
```

- 查看本地实例（克隆库）状态
```
mysql> show master status;
+------------------+----------+--------------+------------------+---------------------------------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set              |
+------------------+----------+--------------+------------------+---------------------------------------------+
| mysql-bin.000002 |   155 |       |         | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------------------+----------+--------------+------------------+---------------------------------------------+
1 row in set (0.00 sec)
 
mysql> select count(*) from kk.k1;
+----------+
| count(*) |
+----------+
|  108100 |
+----------+
1 row in set (0.09 sec)
```

- 本地实例查看clone plugin 任务情况
```
mysql> SELECT * FROM performance_schema.clone_status;
+------+------+-----------+-------------------------+-------------------------+---------------------+----------------+----------+---------------+------------------+-----------------+---------------------------------------------+
| ID  | PID | STATE   | BEGIN_TIME       | END_TIME        | SOURCE       | DESTINATION  | ERROR_NO | ERROR_MESSAGE | BINLOG_FILE   | BINLOG_POSITION | GTID_EXECUTED                |
+------+------+-----------+-------------------------+-------------------------+---------------------+----------------+----------+---------------+------------------+-----------------+---------------------------------------------+
|  1 |  0 | Completed | 2020-05-11 10:08:07.050 | 2020-05-11 10:08:42.229 | 192.168.188.81:3306 | LOCAL INSTANCE |    0 |        | mysql-bin.000007 |       748 | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------+------+-----------+-------------------------+-------------------------+---------------------+----------------+----------+---------------+------------------+-----------------+---------------------------------------------+
1 row in set (0.01 sec)
 
```

## 远程克隆到本地：克隆到其它目录

- 环境信息

| 192.168.188.81 | 3306 | remote node（被克隆库）         | /data/mysql/mysql3306 |
| -------------- | ---- | ------------------------------- | --------------------- |
| 192.168.188.82 | 3307 | local target node（克隆目标库） | /data/mysql/mysql3307 |
| 192.168.188.82 | 3306 | localnode（操作库）             | /data/mysql/mysql3306 |

- 被克隆库创建clone用户，授权

略

- 被克隆库安装clone plugin

略

- 查看被克隆库状态

- 操作库配置clone 参数

```
mysql> set global clone_valid_donor_list='192.168.188.81:3306';
Query OK, 0 rows affected (0.00 sec)
```

- 操作库上执行clone，注意目标路径权限，并保证底层目录不存在
```
mysql> clone instance from 'clone'@'192.168.188.81':3306 identified by 'clone' DATA DIRECTORY = '/data/mysql/mysql3307/data';

Query OK, 0 rows affected (0.91 sec)
```

- 查看克隆目标目录
```
[root@ms82 mysql]# ls
mysql3306 mysql3307

[root@ms82 mysql]# tree mysql3307
mysql3307
└── data
  ├── #clone
  │  ├── #replace_files
  │  ├── #status_fix
  │  ├── #view_progress
  │  └── #view_status
  ├── ib_buffer_pool
  ├── ibdata1
  ├── ib_logfile0
  ├── ib_logfile1
  ├── kk
  │  └── k1.ibd
  ├── mysql
  ├── mysql.ibd
  ├── sys
  │  └── sys_config.ibd
  ├── undo_001
  └── undo_002
```

- 参照远程库my.cnf配置克隆库参数文件，拉起实例

- 补充配置目录

```
[root@ms82 mysql3307]# mkdir {logs,tmp}
[root@ms82 mysql3307]# chown mysql:mysql ./*
[root@ms82 mysql3307]# ll
total 12
drwxr-x--- 6 mysql mysql 4096 May 11 10:52 data
drwxr-xr-x 2 mysql mysql 4096 May 11 10:58 logs
drwxr-xr-x 2 mysql mysql 4096 May 11 10:58 tmp
```

- 调整配置文件

略

- 拉起实例

略

- 查看克隆库状态

```
mysql> show master status;
+------------------+----------+--------------+------------------+---------------------------------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set              |
+------------------+----------+--------------+------------------+---------------------------------------------+
| mysql-bin.000001 |   155 |       |         | 9064a50b-91a5-11ea-ac56-0242c0a8bc51:1-9818 |
+------------------+----------+--------------+------------------+---------------------------------------------+
1 row in set (0.00 sec)
 
mysql> select count(*) from kk.k1;
+----------+
| count(*) |
+----------+
|  108100 |
+----------+
1 row in set (0.09 sec)
```