[TOC]

# Sys schema

- sys schema的数据主要源自P_S

- x$开头的对象，这种适合工具采集数据，是原始类数据

- sys_开头的是schema配置表



## 用户、连接、线程类

- 查看每个客户端IP连接消耗的资源情况
- 查看每个用户消耗资源情况
- 查看当前连接情况
- 查看当前正在执行的SQL
- 查看当前的内部线程活动



### 查看每个客户端IP连接消耗的资源情况

```
mysql> select * from sys.memory_by_thread_by_current_bytes where thread_id=42;
+-----------+----------------+--------------------+-------------------+-------------------+-------------------+-----------------+
| thread_id | user           | current_count_used | current_allocated | current_avg_alloc | current_max_alloc | total_allocated |
+-----------+----------------+--------------------+-------------------+-------------------+-------------------+-----------------+
|        42 | root@localhost |                  0 | 0 bytes           | 0 bytes           | 0 bytes           | 0 bytes         |
+-----------+----------------+--------------------+-------------------+-------------------+-------------------+-----------------+
1 row in set (0.08 sec)

```



 ```
mysql> show tables like '%user%';
+-------------------------------------+
| Tables_in_sys (%user%)              |
+-------------------------------------+
| memory_by_user_by_current_bytes     |
| user_summary                        |
| user_summary_by_file_io             |
| user_summary_by_file_io_type        |
| user_summary_by_stages              |
| user_summary_by_statement_latency   |
| user_summary_by_statement_type      |
| waits_by_user_by_latency            |
| x$memory_by_user_by_current_bytes   |
| x$user_summary                      |
| x$user_summary_by_file_io           |
| x$user_summary_by_file_io_type      |
| x$user_summary_by_stages            |
| x$user_summary_by_statement_latency |
| x$user_summary_by_statement_type    |
| x$waits_by_user_by_latency          |
+-------------------------------------+
16 rows in set (0.00 sec)
 ```



- 即使show processlist 显示为空， 也可以通过视图查询到最后一次执行的SQL

  ```
  mysql> select * from performance_schema.threads where thread_id=42\G
  *************************** 1. row ***************************
            THREAD_ID: 42
                 NAME: thread/sql/one_connection
                 TYPE: FOREGROUND
       PROCESSLIST_ID: 17
     PROCESSLIST_USER: root
     PROCESSLIST_HOST: localhost
       PROCESSLIST_DB: sys
  PROCESSLIST_COMMAND: Query
     PROCESSLIST_TIME: 0
    PROCESSLIST_STATE: Sending data
     PROCESSLIST_INFO: select * from performance_schema.threads where thread_id=42
     PARENT_THREAD_ID: NULL
                 ROLE: NULL
         INSTRUMENTED: YES
              HISTORY: YES
      CONNECTION_TYPE: Socket
         THREAD_OS_ID: 9145
  1 row in set (0.00 sec)
  ```

  

## TOP SQL/IO

- 查看TOP IO
- 查看TOP SQL
- 查看IO中TOP Read/Write



 ```
mysql> show tables like '%io%';
+--------------------------------------+
| Tables_in_sys (%io%)                 |
+--------------------------------------+
| host_summary_by_file_io              |
| host_summary_by_file_io_type         |
| io_by_thread_by_latency              |
| io_global_by_file_by_bytes           |
| io_global_by_file_by_latency         |
| io_global_by_wait_by_bytes           |
| io_global_by_wait_by_latency         |
| latest_file_io                       |
| ps_check_lost_instrumentation        |
| session                              |
| session_ssl_status                   |
| user_summary_by_file_io              |
| user_summary_by_file_io_type         |
| version                              |
| x$host_summary_by_file_io            |
| x$host_summary_by_file_io_type       |
| x$io_by_thread_by_latency            |
| x$io_global_by_file_by_bytes         |
| x$io_global_by_file_by_latency       |
| x$io_global_by_wait_by_bytes         |
| x$io_global_by_wait_by_latency       |
| x$latest_file_io                     |
| x$ps_digest_avg_latency_distribution |
| x$ps_schema_table_statistics_io      |
| x$session                            |
| x$user_summary_by_file_io            |
| x$user_summary_by_file_io_type       |
+--------------------------------------+
27 rows in set (0.00 sec)

mysql> show tables like '%stat%';
+-----------------------------------------------+
| Tables_in_sys (%stat%)                        |
+-----------------------------------------------+
| host_summary_by_statement_latency             |
| host_summary_by_statement_type                |
| innodb_buffer_stats_by_schema                 |
| innodb_buffer_stats_by_table                  |
| schema_index_statistics                       |
| schema_table_statistics                       |
| schema_table_statistics_with_buffer           |
| session_ssl_status                            |
| statement_analysis                            |   **
| statements_with_errors_or_warnings            |
| statements_with_full_table_scans              |
| statements_with_runtimes_in_95th_percentile   |
| statements_with_sorting                       |
| statements_with_temp_tables                   |
| user_summary_by_statement_latency             |
| user_summary_by_statement_type                |
| x$host_summary_by_statement_latency           |
| x$host_summary_by_statement_type              |
| x$innodb_buffer_stats_by_schema               |
| x$innodb_buffer_stats_by_table                |
| x$ps_schema_table_statistics_io               |
| x$schema_index_statistics                     |
| x$schema_table_statistics                     |
| x$schema_table_statistics_with_buffer         |
| x$statement_analysis                          |
| x$statements_with_errors_or_warnings          |
| x$statements_with_full_table_scans            |
| x$statements_with_runtimes_in_95th_percentile |
| x$statements_with_sorting                     |
| x$statements_with_temp_tables                 |
| x$user_summary_by_statement_latency           |
| x$user_summary_by_statement_type              |
+-----------------------------------------------+
32 rows in set (0.00 sec)

 ```



## Buffer Pool、内存

- 查看总共分配了多少内存
- 每个database占用多少buffer pool
- 统计InnoDB引擎的InnoDB缓存
- 统计每张表具体在InnoDB中具体的情况
- 查询没给连接分配了多少内存

 



## 字段、索引、锁

- 查看表自增字段最大值和当前值、
- MySQL索引使用情况统计
- MySQL中有哪些冗余索引和无用索引
- 查看InnoDB锁信息
- 查看database级别的锁信息（需要先打开MDL锁监控）

 ```
mysql> show tables like '%schema%wait%';
+-------------------------------+
| Tables_in_sys (%schema%wait%) |
+-------------------------------+
| schema_table_lock_waits       |	**
| x$schema_table_lock_waits     |
+-------------------------------+
2 rows in set (0.00 sec)
 ```





 

### 统计表DML\IO情况

> MySQL 5.7 +  或 Percona

```
mysql> use sys;
Database changed

mysql> show tables like 'schema%';
+-------------------------------------+
| Tables_in_sys (schema%)             |
+-------------------------------------+
| schema_auto_increment_columns       |
| schema_index_statistics             |
| schema_object_overview              |
| schema_redundant_indexes            |
| schema_table_lock_waits             |
| schema_table_statistics             |
| schema_table_statistics_with_buffer |
| schema_tables_with_full_table_scans |
| schema_unused_indexes               |
+-------------------------------------+
9 rows in set (0.00 sec)
```



- table statistics

  > select table_name,
  >     rows_fetched,
  >     rows_inserted,
  >     rows_updated,
  >     rows_deleted,
  >     io_read_requests,
  >     io_read,
  >     io_write_requests,
  >     io_write 
  > from sys.schema_table_statistics 
  > where table_schema=xxx 
  > 	and table_name=xxx;

  ```
  mysql> select table_name,rows_fetched,rows_inserted,rows_updated,rows_deleted,io_read_requests,io_read,io_write_requests,io_write from schema_table_statistics;
  +---------------+--------------+---------------+--------------+--------------+------------------+------------+-------------------+------------+
  | table_name    | rows_fetched | rows_inserted | rows_updated | rows_deleted | io_read_requests | io_read    | io_write_requests | io_write   |
  +---------------+--------------+---------------+--------------+--------------+------------------+------------+-------------------+------------+
  | x1            |     24384755 |       4762635 |            0 |            0 |            22910 | 357.46 MiB |             14900 | 232.44 MiB |
  | x2            |      1530000 |        310000 |            0 |            0 |               14 | 2.72 KiB   |               779 | 11.80 MiB  |
  | x3            |      4718752 |             0 |            0 |            0 |             5536 | 85.99 MiB  |              6759 | 105.24 MiB |
  | b2            |        18855 |          1500 |            0 |            0 |               33 | 2.56 KiB   |               105 | 1.33 MiB   |
  | t2            |            0 |          1245 |            0 |            0 |               21 | 1.92 KiB   |                66 | 644.64 KiB |
  ...
  ...
  ```

  

- index statistics

  > select index_name,
  >     rows_selected,
  >     rows_inserted,
  >     rows_updated,
  >     rows_deleted
  > from sys.schema_index_statistics
  > where table_schema=xxx
  > 	and table_name=xxx;

  ```
  mysql> select index_name, rows_selected, rows_inserted, rows_updated, rows_deleted from schema_index_statistics;
  +-----------------------------+---------------+---------------+--------------+--------------+
  | index_name                  | rows_selected | rows_inserted | rows_updated | rows_deleted |
  +-----------------------------+---------------+---------------+--------------+--------------+
  | seq                         |      14465998 |             0 |            0 |            0 |
  | PRIMARY                     |           600 |             0 |            0 |            0 |
  | via                         |         18855 |             0 |            0 |            0 |
  | char2                       |             6 |             0 |            0 |            0 |
  | PRIMARY                     |             1 |             0 |            0 |            0 |
  ...
  ...
  ```

  

### 统计冗余索引

> select * from sys.schema_redundant_indexes\G

```
mysql> select * from schema_redundant_indexes\G
*************************** 1. row ***************************
              table_schema: kk
                table_name: unidex
      redundant_index_name: a_2
   redundant_index_columns: a,b
redundant_index_non_unique: 1
       dominant_index_name: a
    dominant_index_columns: a,b,c
 dominant_index_non_unique: 1
            subpart_exists: 0
            sql_drop_index: ALTER TABLE `kk`.`unidex` DROP INDEX `a_2`
1 row in set (0.01 sec)
```



### 统计无用索引

> select * from sys.schema_unused_indexes;

```
mysql> select * from schema_unused_indexes;
+---------------+---------------+-----------------------------+
| object_schema | object_name   | index_name                  |
+---------------+---------------+-----------------------------+
| kk            | b1            | n                           |
| kk            | c1            | char1                       |
| kk            | c2            | char1                       |
| kk            | c2            | char2                       |
| kk            | c3            | char2                       |
| kk            | c3            | char1                       |
...
...
```



### 统计全表扫描

> select * from sys.schema_tables_with_full_table_scans limit 5;

```
mysql> select * from schema_tables_with_full_table_scans limit 5;
+---------------+-------------+-------------------+---------+
| object_schema | object_name | rows_full_scanned | latency |
+---------------+-------------+-------------------+---------+
| kk            | x1          |           9918757 | 1.46 m  |
| kk            | x3          |           4718752 | 3.83 s  |
| kk            | x2          |           1530000 | 4.17 s  |
| kk            | city        |               600 | 1.36 ms |
| kk            | merge       |                34 | 2.07 ms |
+---------------+-------------+-------------------+---------+
5 rows in set (0.01 sec)
```



### buffer pool消耗排名

> select * from sys.innodb_buffer_stats_by_table order by pages desc limit 10;

```
mysql> select * from innodb_buffer_stats_by_table order by pages desc limit 10;
+---------------+--------------------+-----------+-----------+-------+--------------+-----------+-------------+
| object_schema | object_name        | allocated | data      | pages | pages_hashed | pages_old | rows_cached |
+---------------+--------------------+-----------+-----------+-------+--------------+-----------+-------------+
| kk            | x3                 | 54.89 MiB | 50.11 MiB |  3513 |         1545 |      1335 |     1814156 |
| InnoDB System | SYS_TABLES         | 6.66 MiB  | 6.04 MiB  |   426 |            0 |       320 |      225871 |
| mysql         | innodb_index_stats | 48.00 KiB | 18.89 KiB |     3 |            1 |         0 |         206 |
| mysql         | innodb_table_stats | 16.00 KiB | 2.22 KiB  |     1 |            0 |         0 |          40 |
+---------------+--------------------+-----------+-----------+-------+--------------+-----------+-------------+
4 rows in set (0.11 sec)

```



### 统计指定表的buffer消耗

> select * from sys.schema_table_statistics_with_buffer where table_schema=xxx and table_name=xxx \G

 ```


mysql> select * from schema_table_statistics_with_buffer where table_schema='kk' and table_name='x3'\G
*************************** 1. row ***************************
              table_schema: kk
                table_name: x3
              rows_fetched: 4718752
             fetch_latency: 3.83 s
             rows_inserted: 0
            insert_latency: 0 ps
              rows_updated: 0
            update_latency: 0 ps
              rows_deleted: 0
            delete_latency: 0 ps
          io_read_requests: 5536
                   io_read: 85.99 MiB
           io_read_latency: 1.21 s
         io_write_requests: 6759
                  io_write: 105.24 MiB
          io_write_latency: 635.04 ms
          io_misc_requests: 263
           io_misc_latency: 3.85 s
   innodb_buffer_allocated: 50.69 MiB
        innodb_buffer_data: 46.27 MiB
        innodb_buffer_free: 4.42 MiB
       innodb_buffer_pages: 3244
innodb_buffer_pages_hashed: 1545
   innodb_buffer_pages_old: 1066
 innodb_buffer_rows_cached: 1675352
1 row in set (0.11 sec)

 ```



### 确认某会话内存消耗

> select b.thd_id,
> 	b.user,
> 	current_count_used,
> 	current_allocated,
> 	current_avg_alloc,
> 	current_max_alloc,
> 	total_allocated,
> 	current_statement
> from sys.memory_by_thread_by_current_bytes a, sys.session b
> where a.thread_id = b.thd_id limit 1\G

```
mysql> select b.thd_id, b.user, current_count_used, current_allocated, current_avg_alloc, current_max_alloc, total_allocated, current_statement from memory_by_thread_by_current_bytes a, session b where a.thread_id = b.thd_id \G
*************************** 1. row ***************************
            thd_id: 42
              user: root@localhost
current_count_used: 0
 current_allocated: 0 bytes
 current_avg_alloc: 0 bytes
 current_max_alloc: 0 bytes
   total_allocated: 0 bytes
 current_statement: select b.thd_id, b.user, curre ... b where a.thread_id = b.thd_id
1 row in set (0.13 sec)
```



### 查看逻辑读写top的表

> select object_schema,
> 	object_name,
> 	count_star as rows_io_total,
> 	count_read as rows_read,
> 	count_write as rows_write,
> 	count_fetch as rows_fetchs,
> 	count_insert as rows_inserts,
> 	count_update as rows_updates,
> 	count_delete as rows_deletes,
> 	concat( round( sum_timer_fetch / 3600000000000000, 2), 'h') as fetch_latency,
> 	concat( round( sum_timer_insert / 3600000000000000, 2), 'h') as insert_latency,
> 	concat( round( sum_timer_update / 3600000000000000, 2), 'h') as update_latency,
> 	concat( round( sum_timer_delete / 3600000000000000, 2), 'h') as delete_latency
> from performance_schema.table_io_waits_summary_by_table
> order by sum_timer_wait desc limit 10;

```
mysql> select object_schema,
er_fetch / 3600000000000000, 2), 'h') as fetch_latency,
concat( round( sum_timer_insert / 3600000000000000, 2), 'h') as insert_latency,
concat( round( sum_timer_update / 3600000000000000, 2), 'h') as update_latency,
concat( round( sum_timer_delete / 360000object_name,
    -> count_star as rows_io_total,
    -> count_read as rows_read,
    -> count_write as rows_write,
    -> count_fetch as rows_fetchs,
    -> count_insert as rows_inserts,
    -> count_update as rows_updates,
    -> count_delete as rows_deletes,
    -> concat( round( sum_timer_fetch / 3600000000000000, 2), 'h') as fetch_latency,
    -> concat( round( sum_timer_insert / 3600000000000000, 2), 'h') as insert_latency,
    -> concat( round( sum_timer_update / 3600000000000000, 2), 'h') as update_latency,
    -> concat( round( sum_timer_delete / 3600000000000000, 2), 'h') as delete_latency
    -> from performance_schema.table_io_waits_summary_by_table
    -> order by sum_timer_wait desc limit 10;
+---------------+-------------+---------------+-----------+------------+-------------+--------------+--------------+--------------+---------------+----------------+----------------+----------------+
| object_schema | object_name | rows_io_total | rows_read | rows_write | rows_fetchs | rows_inserts | rows_updates | rows_deletes | fetch_latency | insert_latency | update_latency | delete_latency |
+---------------+-------------+---------------+-----------+------------+-------------+--------------+--------------+--------------+---------------+----------------+----------------+----------------+
| kk            | x1          |      29147390 |  24384755 |    4762635 |    24384755 |      4762635 |            0 |            0 | 0.01h         | 0.02h          | 0.00h          | 0.00h          |
| kk            | x2          |       1840000 |   1530000 |     310000 |     1530000 |       310000 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | x3          |       4718752 |   4718752 |          0 |     4718752 |            0 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | b2          |         20355 |     18855 |       1500 |       18855 |         1500 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | t2          |          1245 |         0 |       1245 |           0 |         1245 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | t4          |            24 |         0 |         24 |           0 |           24 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| sys           | sys_config  |             1 |         1 |          0 |           1 |            0 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | city        |          1200 |      1200 |          0 |        1200 |            0 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | merge       |            58 |        34 |         24 |          34 |           24 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
| kk            | c1          |            28 |        16 |         12 |          16 |           12 |            0 |            0 | 0.00h         | 0.00h          | 0.00h          | 0.00h          |
+---------------+-------------+---------------+-----------+------------+-------------+--------------+--------------+--------------+---------------+----------------+----------------+----------------+
10 rows in set (0.00 sec)

```



### 查看TOP物理I/O

> select * from io_global_by_file_by_bytes limit 10;

```
mysql> select * from io_global_by_file_by_bytes limit 10;
+---------------------------------------------+------------+------------+-----------+-------------+---------------+-----------+------------+-----------+
| file                                        | count_read | total_read | avg_read  | count_write | total_written | avg_write | total      | write_pct |
+---------------------------------------------+------------+------------+-----------+-------------+---------------+-----------+------------+-----------+
| @@datadir/ibdata1                           |        431 | 8.75 MiB   | 20.79 KiB |       10364 | 642.11 MiB    | 63.44 KiB | 650.86 MiB |     98.66 |
| @@datadir/kk/x1.ibd                         |      22877 | 357.45 MiB | 16.00 KiB |       14873 | 232.44 MiB    | 16.00 KiB | 589.89 MiB |     39.40 |
| @@datadir/ibtmp1                            |       8979 | 140.30 MiB | 16.00 KiB |       13928 | 229.44 MiB    | 16.87 KiB | 369.73 MiB |     62.05 |
| @@datadir/ib_logfile1                       |          0 | 0 bytes    | 0 bytes   |         177 | 200.36 MiB    | 1.13 MiB  | 200.36 MiB |    100.00 |
| @@datadir/ib_logfile0                       |          7 | 68.50 KiB  | 9.79 KiB  |       27769 | 200.00 MiB    | 7.38 KiB  | 200.06 MiB |     99.97 |
| @@datadir/ib_logfile2                       |          0 | 0 bytes    | 0 bytes   |         100 | 193.17 MiB    | 1.93 MiB  | 193.17 MiB |    100.00 |
| @@datadir/kk/x3.ibd                         |       5503 | 85.98 MiB  | 16.00 KiB |        6732 | 105.23 MiB    | 16.01 KiB | 191.22 MiB |     55.03 |
| /data/mysql/mysql3306/logs/mysql-bin.000004 |          0 | 0 bytes    | 0 bytes   |       32428 | 112.04 MiB    | 3.54 KiB  | 112.04 MiB |    100.00 |
| @@datadir/kk/x2.ibd                         |          0 | 0 bytes    | 0 bytes   |         752 | 11.80 MiB     | 16.06 KiB | 11.80 MiB  |    100.00 |
| /data/mysql/mysql3306/logs/mysql-bin.000002 |        489 | 8.40 MiB   | 17.58 KiB |           0 | 0 bytes       | 0 bytes   | 8.40 MiB   |      0.00 |
+---------------------------------------------+------------+------------+-----------+-------------+---------------+-----------+------------+-----------+
10 rows in set (0.02 sec)

```



### 统计MDL锁

> 前提：开启MDL统计
>
> update performance_schema.setup_instruments set enabled ='YES' where name like '%wait/lock/metadata/sql/mdl%';
>
> 
>
> select * from schema_table_lock_waits

```
<s1>:lock table b1 write; -- 其他session不能读写。
<s2>:select * from kk.b1; -- hang.

mysql>  select * from sys.schema_table_lock_waits\G
*************************** 1. row ***************************
               object_schema: kk
                 object_name: b1
           waiting_thread_id: 43
                 waiting_pid: 18
             waiting_account: root@localhost
           waiting_lock_type: SHARED_READ
       waiting_lock_duration: TRANSACTION
               waiting_query: select * from kk.b1
          waiting_query_secs: 2
 waiting_query_rows_affected: 0
 waiting_query_rows_examined: 0
          blocking_thread_id: 42
                blocking_pid: 17
            blocking_account: root@localhost
          blocking_lock_type: SHARED_NO_READ_WRITE
      blocking_lock_duration: TRANSACTION
     sql_kill_blocking_query: KILL QUERY 17
sql_kill_blocking_connection: KILL 17
1 row in set (0.01 sec)

mysql> select * from performance_schema.metadata_locks;
+-------------+--------------------+----------------+-----------------------+----------------------+---------------+-------------+--------+-----------------+----------------+
| OBJECT_TYPE | OBJECT_SCHEMA      | OBJECT_NAME    | OBJECT_INSTANCE_BEGIN | LOCK_TYPE            | LOCK_DURATION | LOCK_STATUS | SOURCE | OWNER_THREAD_ID | OWNER_EVENT_ID |
+-------------+--------------------+----------------+-----------------------+----------------------+---------------+-------------+--------+-----------------+----------------+
| GLOBAL      | NULL               | NULL           |       140231425547664 | INTENTION_EXCLUSIVE  | STATEMENT     | GRANTED     |        |              42 |          38575 |
| SCHEMA      | kk                 | NULL           |       140231421914096 | INTENTION_EXCLUSIVE  | TRANSACTION   | GRANTED     |        |              42 |          38575 |
| TABLE       | kk                 | b1             |       140231422307616 | SHARED_NO_READ_WRITE | TRANSACTION   | GRANTED     |        |              42 |          38575 |
| TABLE       | kk                 | b1             |       140231836327664 | SHARED_READ          | TRANSACTION   | PENDING     |        |              43 |            118 |
| TABLE       | performance_schema | metadata_locks |       140231153532608 | SHARED_READ          | TRANSACTION   | GRANTED     |        |              45 |            142 |
+-------------+--------------------+----------------+-----------------------+----------------------+---------------+-------------+--------+-----------------+----------------+
5 rows in set (0.00 sec)

```

 

 