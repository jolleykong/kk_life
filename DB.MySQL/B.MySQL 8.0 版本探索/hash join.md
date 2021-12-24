# hash join

MySQL 8.0.18+ 新增特性。

多表JOIN时，即使没有索引，也会提速N倍。

- 最好还是加上合适的索引或使用直方图。

- hash join只适合做极端情况下的保底策略。

- join_buffer不适合初始化就设置很大，因为在并发量高的时候，随着并发的增加，内存占用越来越多，会爆炸。因此不划算。



案例

> - DDL
>
>   ```
>   create table t1(
>   c1 int(11) not null,
>   c2 int(11) default null,
>   c3 int(10) unsigned not null,
>   xx int(11) default null,
>   c4 int(10) unsigned not null,
>   dt timestamp not null,
>   primary key(c1)
>   );
>   /* rows = 10090 */
>   
>   create table t2(
>   c1 int(11) not null,
>   c2 int(10) unsigned not null,
>   c3 varchar(10) not null,
>   c4 float(8,2) not null,
>   primary key(c1)
>   );
>   /* rows = 6804*/
>   ```
>
> > 生成数据
> >
> > ```
> > [16:38:34] root@ms81:mysql_random_data_load # ./mysql_random_data_load kk t1 10090 --user root                            
> > INFO[2020-09-24T16:38:47+08:00] Starting                                     
> > 3s [====================================================================] 100%
> > [16:38:51] root@ms81:mysql_random_data_load # ./mysql_random_data_load kk t2 6804 --user root 
> > INFO[2020-09-24T16:39:04+08:00] Starting                                     
> > 1s [====================================================================] 100%
> > 
> > mysql> select * from t1 limit 3;
> > +-------+------------+------------+------------+------------+---------------------+
> > | c1    | c2         | c3         | xx         | c4         | dt                  |
> > +-------+------------+------------+------------+------------+---------------------+
> > |  9441 | 1794386477 | 1593319997 | 2081573837 | 1832517975 | 2020-04-08 09:01:48 |
> > | 64171 |  591341510 |   15029554 | 1558419520 |  599491354 | 2019-10-21 04:08:52 |
> > | 74871 | 1034994191 | 1431750663 |  990707944 |  563285362 | 2020-08-03 23:03:30 |
> > +-------+------------+------------+------------+------------+---------------------+
> > 3 rows in set (0.00 sec)
> > 
> > mysql> select * from t2 limit 3;
> > +--------+------------+---------+------+
> > | c1     | c2         | c3      | c4   |
> > +--------+------------+---------+------+
> > |   3799 |   63450121 | Marie   | 0.00 |
> > | 232483 | 1388080615 | Eric    | 1.38 |
> > | 547790 | 1761950343 | Lillian | 0.82 |
> > +--------+------------+---------+------+
> > 3 rows in set (0.00 sec)
> > 
> > ```
>
> 
>
> - @@join_buffer_size=256k,@@innodb_buffer_pool_size=2G
>
>   ```
>   mysql> select @@join_buffer_size;
>   +--------------------+
>   | @@join_buffer_size |
>   +--------------------+
>   |             262144 |
>   +--------------------+
>   1 row in set (0.00 sec)
>   
>   mysql> select @@innodb_buffer_pool_size;
>   +---------------------------+
>   | @@innodb_buffer_pool_size |
>   +---------------------------+
>   |             2199073587200 |
>   +---------------------------+
>   1 row in set (0.00 sec)
>   
>   mysql> desc select * from t1 join t2 on t1.c2 = t2.c2;
>   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+----------------------------------------------------+
>   | id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                                              |
>   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+----------------------------------------------------+
>   |  1 | SIMPLE      | t2    | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 7040 |   100.00 | NULL                                               |
>   |  1 | SIMPLE      | t1    | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 9753 |    10.00 | Using where; Using join buffer (Block Nested Loop) |
>   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+----------------------------------------------------+
>   2 rows in set, 1 warning (0.00 sec)
>   
>   mysql> explain format=tree  select * from t1 join t2 on t1.c2 = t2.c2\G
>   *************************** 1. row ***************************
>   EXPLAIN: -> Inner hash join (t1.c2 = t2.c2)  (cost=6866881.02 rows=6866112)  
>       -> Table scan on t1  (cost=0.02 rows=9753)
>       -> Hash
>           -> Table scan on t2  (cost=710.25 rows=7040)
>   
>   1 row in set (0.15 sec)
>   --这个SQL使用hash join因为执行计划里有inner hash join了
>   
>   ```
>
> mysql>  select * from t1 join t2 on t1.c2 = t2.c2;
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   | c1        | c2         | c3        | xx         | c4        | dt                  | c1        | c2         | c3      | c4   |
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   | 583532949 | 1342458479 | 280366509 | 1801160058 | 914091476 | 2020-04-04 13:05:11 | 583532949 | 1342458479 | Richard | 3.32 |
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   1 row in set (0.40 sec)
>
>   mysql> show status like 'handler%read%';
>   +-----------------------+-------+
>   | Variable_name         | Value |
>   +-----------------------+-------+
>   | Handler_read_first    | 5     |
>   | Handler_read_key      | 20    |
>   | Handler_read_last     | 0     |
>   | Handler_read_next     | 8     |
>   | Handler_read_prev     | 0     |
>   | Handler_read_rnd      | 0     |
>   | Handler_read_rnd_next | 16904 |
>   +-----------------------+-------+
>   7 rows in set (0.00 sec)
>
>
>   作为对比，mysql 5.7.30
>   mysql> select * from t1 join t2 on t1.c2 = t2.c2;
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   | c1        | c2         | c3        | xx         | c4        | dt                  | c1        | c2         | c3      | c4   |
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   | 583532949 | 1342458479 | 280366509 | 1801160058 | 914091476 | 2020-04-04 13:05:11 | 583532949 | 1342458479 | Richard | 3.32 |
>   +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
>   1 row in set (5.46 sec)
>
>   mysql> show status like 'handler%read%';
>   +-----------------------+-------+
>   | Variable_name         | Value |
>   +-----------------------+-------+
>   | Handler_read_first    | 2     |
>   | Handler_read_key      | 2     |
>   | Handler_read_last     | 0     |
>   | Handler_read_next     | 0     |
>   | Handler_read_prev     | 0     |
>   | Handler_read_rnd      | 0     |
>   | Handler_read_rnd_next | 16926 |
>   +-----------------------+-------+
>   7 rows in set (0.00 sec)
>
>   ```
>   
>   - 看handler_read是看不出来区别的
>   
>   - 只能看耗时和执行计划来确认是否使用了hash join， 当然profile也可以
>   
>   ```
>
>     mysql> show profiles;
>     +----------+------------+-------------------------------------------+
>     | Query_ID | Duration   | Query                                     |
>     +----------+------------+-------------------------------------------+
>     |        1 | 0.21234700 | select * from t1 join t2 on t1.c2 = t2.c2 |
>     +----------+------------+-------------------------------------------+
>     1 row in set, 1 warning (0.00 sec)
>     
>     mysql> show profile for query 1;
>     +--------------------------------+----------+
>     | Status                         | Duration |
>     +--------------------------------+----------+
>     | starting                       | 0.000115 |
>     | Executing hook on transaction  | 0.015787 |
>     | starting                       | 0.000026 |
>     | checking permissions           | 0.000015 |
>     | checking permissions           | 0.000019 |
>     | Opening tables                 | 0.007131 |
>     | init                           | 0.000026 |
>     | System lock                    | 0.000029 |
>     | optimizing                     | 0.000026 |
>     | statistics                     | 0.000049 |
>     | preparing                      | 0.000236 |
>     | executing                      | 0.188349 |
>     | end                            | 0.000019 |
>     | query end                      | 0.000012 |
>     | waiting for handler commit     | 0.000359 |
>     | closing tables                 | 0.000024 |
>     | freeing items                  | 0.000035 |
>     | logging slow query             | 0.000069 |
>     | cleaning up                    | 0.000025 |
>     +--------------------------------+----------+
>     19 rows in set, 1 warning (0.04 sec)
>     
>     作为对比，mysql 5.7.30
>     mysql> show profiles;
>     +----------+------------+-------------------------------------------+
>     | Query_ID | Duration   | Query                                     |
>     +----------+------------+-------------------------------------------+
>     |        1 | 4.38869950 | select * from t1 join t2 on t1.c2 = t2.c2 |
>     |        2 | 4.37783675 | select * from t1 join t2 on t1.c2 = t2.c2 |
>     +----------+------------+-------------------------------------------+
>     2 rows in set, 1 warning (0.00 sec)
>     
>     mysql> show profile for query 2;
>     +----------------------+----------+
>     | Status               | Duration |
>     +----------------------+----------+
>     | starting             | 0.000147 |
>     | checking permissions | 0.000007 |
>     | checking permissions | 0.000019 |
>     | Opening tables       | 0.000041 |
>     | init                 | 0.000102 |
>     | System lock          | 0.000018 |
>     | optimizing           | 0.000013 |
>     | statistics           | 0.000036 |
>     | preparing            | 0.000070 |
>     | executing            | 0.000007 |
>     | Sending data         | 4.377248 |
>     | end                  | 0.000009 |
>     | query end            | 0.000010 |
>     | closing tables       | 0.000009 |
>     | freeing items        | 0.000018 |
>     | logging slow query   | 0.000046 |
>     | cleaning up          | 0.000037 |
>     +----------------------+----------+
>     17 rows in set, 1 warning (0.00 sec)
>
>
> ​    
> ​    
> ​    ```
>
>
> ​    





- [注意事项](https://dev.mysql.com/doc/refman/8.0/en/hash-joins.html)

  ```
   Memory usage by hash joins can be controlled using the join_buffer_size system variable; 
   a hash join cannot use more memory than this amount. 
   When the memory required for a hash join exceeds the amount available, MySQL handles this 
   by using files on disk. If this happens, you should be aware that the join may not succeed 
   if a hash join cannot fit into memory and it creates more files than set for open_files_limit. 
   
   To avoid such problems, make either of the following changes:
  
      Increase join_buffer_size so that the hash join does not spill over to disk.
  
      Increase open_files_limit. 
  
  join buffer不够用的话会打开多个临时文件，
  为保证效率，可以适当加大join buffer大小，也可以适当加大open_file_limit参数。
  ```

  

- 对比测试

  将join buffer 调小到1k，IBP依然是2G，再看结果

  就可以发现handler_read_rnd_next区别很大了

  ```
  mysql> select @@join_buffer_size;
  +--------------------+
  | @@join_buffer_size |
  +--------------------+
  |               1024 |
  +--------------------+
  1 row in set (0.00 sec)
  
  mysql> show status like 'handler%read%';
  +-----------------------+-------+
  | Variable_name         | Value |
  +-----------------------+-------+
  | Handler_read_first    | 9     |
  | Handler_read_key      | 24    |
  | Handler_read_last     | 0     |
  | Handler_read_next     | 8     |
  | Handler_read_prev     | 0     |
  | Handler_read_rnd      | 0     |
  | Handler_read_rnd_next | 50716 |
  +-----------------------+-------+
  7 rows in set (0.00 sec)
  
  
  对比5.7.30
  
  mysql> select @@join_buffer_size;
  +--------------------+
  | @@join_buffer_size |
  +--------------------+
  |               1024 |
  +--------------------+
  1 row in set (0.00 sec)
  
  mysql> select * from t1 join t2 on t1.c2 = t2.c2;
  +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
  | c1        | c2         | c3        | xx         | c4        | dt                  | c1        | c2         | c3      | c4   |
  +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
  | 583532949 | 1342458479 | 280366509 | 1801160058 | 914091476 | 2020-04-04 13:05:11 | 583532949 | 1342458479 | Richard | 3.32 |
  +-----------+------------+-----------+------------+-----------+---------------------+-----------+------------+---------+------+
  1 row in set (4.85 sec)
  
  mysql> show status like 'handler%read%';
  +-----------------------+---------+
  | Variable_name         | Value   |
  +-----------------------+---------+
  | Handler_read_first    | 142     |
  | Handler_read_key      | 142     |
  | Handler_read_last     | 0       |
  | Handler_read_next     | 0       |
  | Handler_read_prev     | 0       |
  | Handler_read_rnd      | 0       |
  | Handler_read_rnd_next | 1419844 |
  +-----------------------+---------+
  7 rows in set (0.00 sec)
  
  ```

  









## 案例：80w join 30w

- 初始化数据

  ```
  [17:53:51] root@ms81:mysql_random_data_load # ./mysql_random_data_load kk t1 800000 --user root 
  INFO[2020-09-24T17:54:07+08:00] Starting                                     
  4m16s [====================================================================] 100%
  INFO[2020-09-24T17:58:25+08:00] 800000 rows inserted                         
  [17:58:25] root@ms81:mysql_random_data_load # ./mysql_random_data_load kk t2 300000 --user root 
  INFO[2020-09-24T17:58:32+08:00] Starting                                     
    58s [====================================================================] 100%
  ```

  

- 查看视图，当前session消耗的内存情况

  ```
  mysql> select * from performance_schema.memory_summary_global_by_event_name where  event_name like '%hash_join%'\G
  *************************** 1. row ***************************
                    EVENT_NAME: memory/sql/hash_join
                   COUNT_ALLOC: 0
                    COUNT_FREE: 0
     SUM_NUMBER_OF_BYTES_ALLOC: 0
      SUM_NUMBER_OF_BYTES_FREE: 0
                LOW_COUNT_USED: 0
            CURRENT_COUNT_USED: 0
               HIGH_COUNT_USED: 0
      LOW_NUMBER_OF_BYTES_USED: 0
  CURRENT_NUMBER_OF_BYTES_USED: 0
     HIGH_NUMBER_OF_BYTES_USED: 0
  1 row in set (0.02 sec)
  ```

  

- 执行SQL前，记录当前值。执行SQL后，再记录当前值

  ```
  mysql> select * from t1 join t2 on t1.c1 = t2.c1;
  
  mysql> select * from performance_schema.memory_summary_global_by_event_name where  event_name like '%hash_join%'\G
  *************************** 1. row ***************************
                    EVENT_NAME: memory/sql/hash_join
                   COUNT_ALLOC: 1
                    COUNT_FREE: 1
     SUM_NUMBER_OF_BYTES_ALLOC: 16392
      SUM_NUMBER_OF_BYTES_FREE: 16392
                LOW_COUNT_USED: 0
            CURRENT_COUNT_USED: 0
               HIGH_COUNT_USED: 1
      LOW_NUMBER_OF_BYTES_USED: 0
  CURRENT_NUMBER_OF_BYTES_USED: 0
     HIGH_NUMBER_OF_BYTES_USED: 16392
  1 row in set (0.01 sec)
  
  ```

  ```
  mysql> select * from performance_schema.file_summary_by_event_name where event_name like '%hash%'\G
  *************************** 1. row ***************************
                 EVENT_NAME: wait/io/file/sql/hash_join
                 COUNT_STAR: 0
             SUM_TIMER_WAIT: 0
             MIN_TIMER_WAIT: 0
             AVG_TIMER_WAIT: 0
             MAX_TIMER_WAIT: 0
                 COUNT_READ: 0
             SUM_TIMER_READ: 0
             MIN_TIMER_READ: 0
             AVG_TIMER_READ: 0
             MAX_TIMER_READ: 0
   SUM_NUMBER_OF_BYTES_READ: 0
                COUNT_WRITE: 0
            SUM_TIMER_WRITE: 0
            MIN_TIMER_WRITE: 0
            AVG_TIMER_WRITE: 0
            MAX_TIMER_WRITE: 0
  SUM_NUMBER_OF_BYTES_WRITE: 0
                 COUNT_MISC: 0
             SUM_TIMER_MISC: 0
             MIN_TIMER_MISC: 0
             AVG_TIMER_MISC: 0
             MAX_TIMER_MISC: 0
  1 row in set (0.02 sec)
  
  ```

  

- 对比后可得知该SQL执行所需的join buffer的大小

  ```
  16392-0=16392 = 16k
  ```

  

- 之后可使用限定buffer方式执行SQL

  ```
  
  ```

  