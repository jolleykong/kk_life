[TOC]

# 提升查询效率

- 提高数据检索效率

- 提高聚合函数效率，sum()、avg()、count()

- 提高排序效率，order by asc/desc

- 有时可以避免回表（覆盖索引）

- 减少多表关联时扫描行数

- 唯一、外键索引还可以作为辅助约束

- 列定义为DEFAULT NULL时，NULL值也会有索引，存放在索引树的最前端部分，因此尽量不要定义允许NULL

  - where is null 时， 会扫描索引b+tree的最左边，所以会有性能影响，但是影响有多大，看数据量。

 

## min() / max() 优化

对一个表频繁更新后，根节点的最小记录值可能还在，但是叶子节点上的数据已经没有了——索引并不保证非叶子节点的数据实时最新。

 ```
mysql> desc select max(id) from b1\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: NULL
   partitions: NULL
         type: NULL
possible_keys: NULL
          key: NULL
      key_len: NULL
          ref: NULL
         rows: NULL
     filtered: NULL
        Extra: Select tables optimized away
1 row in set, 1 warning (0.00 sec)
 ```

 

## group by 优化

```
mysql> alter table b1 add index(n);


mysql> desc select max(id) from b1 group by n\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: b1
   partitions: NULL
         type: range
possible_keys: n
          key: n
      key_len: 51
          ref: NULL
         rows: 2
     filtered: 100.00
        Extra: Using index for group-by
1 row in set, 1 warning (0.00 sec)
```



## 影响insert效率

结论：有辅助索引时，纯数据加载耗时相比无索引时多2%

```
CREATE TABLE `b2` (
  `aid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `via` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4


[17:07:33] root@ms51:~ # mysqlslap -S /data/mysql/mysql3306/tmp/mysql.sock --no-drop --create-schema kk -i 3 concurrency=10 --number-of-queries 500 -q "insert into b2(via) select round(rand()*1024);" 
Benchmark
	Average number of seconds to run all queries: 29.515 seconds
	Minimum number of seconds to run all queries: 28.884 seconds
	Maximum number of seconds to run all queries: 29.946 seconds
	Number of clients running queries: 1
	Average number of queries per client: 500


mysql> alter table b2 add index(via);
Query OK, 0 rows affected (0.57 sec)
Records: 0  Duplicates: 0  Warnings: 0

[17:09:07] root@ms51:~ # mysqlslap -S /data/mysql/mysql3306/tmp/mysql.sock --no-drop --create-schema kk -i 3 concurrency=10 --number-of-queries 500 -q "insert into b2(via) select round(rand()*1024);"
Benchmark
	Average number of seconds to run all queries: 30.230 seconds
	Minimum number of seconds to run all queries: 29.869 seconds
	Maximum number of seconds to run all queries: 30.556 seconds
	Number of clients running queries: 1
	Average number of queries per client: 500

```