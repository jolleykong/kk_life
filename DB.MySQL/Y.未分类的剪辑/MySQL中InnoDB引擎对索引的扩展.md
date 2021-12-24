##                                                              MySQL中InnoDB引擎对索引的扩展                

​                                                                原创                                                                                                                                                                巩飞                                                                                                                                                                                          [                         数据和云                      ](javascript:void(0);)                                                              *3月23日*                

​                                    

**摘要：**InnoDB引擎对索引的扩展，自动追加主键值及其对执行计划的影响。

**
**

MySQL中，使用InnoDB引擎的每个表，创建的普通索引（即非主键索引），都会同时保存主键的值。

比如语句

```
CREATE TABLE t1 (
  i1 INT NOT NULL DEFAULT 0,
  i2 INT NOT NULL DEFAULT 0,
  d DATE DEFAULT NULL,
  PRIMARY KEY (i1, i2),
  INDEX k_d (d)
) ENGINE = InnoDB;
```

创建了t1表，其主键为(i1, i2)，同时创建了基于d列的索引k_d，但其实在底层，InnoDB引擎将索引k_d扩展成（d，i1，i2）。

InnoDB引擎这么做，是用空间换性能，优化器在判断是否使用索引及使用哪个索引时会有更多列参考，这样可能生成更高效的执行计划，获得更好的性能。

优化器在ref、range和index_merge类型的访问，Loose Index Scan访问，连接和排序优化， MIN()/MAX()优化时使都会使用扩展列。

我们来看个例子：

```
root@database-one 15:15:  [gftest]> CREATE TABLE t1 (
    ->   i1 INT NOT NULL DEFAULT 0,
    ->   i2 INT NOT NULL DEFAULT 0,
    ->   d DATE DEFAULT NULL,
    ->   PRIMARY KEY (i1, i2),
    ->   INDEX k_d (d)
    -> ) ENGINE = InnoDB;
Query OK, 0 rows affected (0.06 sec)

root@database-one 15:15:  [gftest]> INSERT INTO t1 VALUES
    -> (1, 1, '1998-01-01'), (1, 2, '1999-01-01'),
    -> (1, 3, '2000-01-01'), (1, 4, '2001-01-01'),
    -> (1, 5, '2002-01-01'), (2, 1, '1998-01-01'),
    -> (2, 2, '1999-01-01'), (2, 3, '2000-01-01'),
    -> (2, 4, '2001-01-01'), (2, 5, '2002-01-01'),
    -> (3, 1, '1998-01-01'), (3, 2, '1999-01-01'),
    -> (3, 3, '2000-01-01'), (3, 4, '2001-01-01'),
    -> (3, 5, '2002-01-01'), (4, 1, '1998-01-01'),
    -> (4, 2, '1999-01-01'), (4, 3, '2000-01-01'),
    -> (4, 4, '2001-01-01'), (4, 5, '2002-01-01'),
    -> (5, 1, '1998-01-01'), (5, 2, '1999-01-01'),
    -> (5, 3, '2000-01-01'), (5, 4, '2001-01-01'),
    -> (5, 5, '2002-01-01');
Query OK, 25 rows affected (0.01 sec)
Records: 25  Duplicates: 0  Warnings: 0

root@database-one 15:21:  [gftest]> show index from t1;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| t1    |          0 | PRIMARY  |            1 | i1          | A         |           5 |     NULL | NULL   |      | BTREE      |         |               |
| t1    |          0 | PRIMARY  |            2 | i2          | A         |          25 |     NULL | NULL   |      | BTREE      |         |               |
| t1    |          1 | k_d      |            1 | d           | A         |           5 |     NULL | NULL   | YES  | BTREE      |         |               |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
3 rows in set (0.01 sec)
```

在普通索引中追加扩展主键是InnoDB在底层做的，show index等语句不显示追加列，但我们可以通过其它方式来验证。看这个SQL

> SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = ‘2000-01-01’

如果InnoDB没有扩展索引，索引k_d为（d），生成的执行计划应该类似这样，使用k_d索引找到d为’2000-01-01’的5行数据，再回表过滤出i1为3的，最后计算count。或者使用主键索引找到i1为3的5行数据，再回表过滤出d为’2000-01-01’的，最后计算count。下面仅示意走k_d索引的情况：

```
mysql> EXPLAIN SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = '2000-01-01'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t1
         type: ref
possible_keys: PRIMARY,k_d
          key: k_d
      key_len: 4
          ref: const
         rows: 5
        Extra: Using where; Using index
```

如果InnoDB扩展了索引，索引k_d为（d，i1，i2），这时，优化器可以使用最左边的索引前缀（d，i1），生成的执行计划应该类似这样，使用k_d索引找到d为’2000-01-01’及i1为3的1行数据，然后计算count

```
mysql> EXPLAIN SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = '2000-01-01'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t1
         type: ref
possible_keys: PRIMARY,k_d
          key: k_d
      key_len: 8
          ref: const,const
         rows: 1
        Extra: Using index
```

并且d列是DATE类型占4个字节，i1是INT类型占4个字节，所以查询中使用的键值长度就是8个字节（key_len: 8）。

我们看看实际生成的执行计划

```
root@database-one 15:35:  [gftest]> EXPLAIN SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = '2000-01-01'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t1
   partitions: NULL
         type: ref
possible_keys: PRIMARY,k_d
          key: k_d
      key_len: 8
          ref: const,const
         rows: 1
     filtered: 100.00
        Extra: Using index
1 row in set, 1 warning (0.01 sec)
```

果然跟我们的判断一致，注意执行计划中的细节：

- key_len从4字节变为8字节，表明键查找使用列d和i1，而不仅仅是d。
- ref从const更改为const，const，表明查找使用两个键值，而不是一个。
- rows从5减少到1，表明检索更少的行。
- Extra从Using where; Using index改为Using index，表示只用索引读取，不必回表。



InnoDB引擎底层扩展普通索引的情况，也可以通过跟MyISAM引擎对比来进行旁证：

```
root@database-one 16:07:  [gftest]> CREATE TABLE t1MyISAM (
    ->   i1 INT NOT NULL DEFAULT 0,
    ->   i2 INT NOT NULL DEFAULT 0,
    ->   d DATE DEFAULT NULL,
    ->   PRIMARY KEY (i1, i2),
    ->   INDEX k_d (d)
    -> ) ENGINE = MyISAM;
Query OK, 0 rows affected (0.01 sec)

root@database-one 16:07:  [gftest]> INSERT INTO t1myisam VALUES
    -> (1, 1, '1998-01-01'), (1, 2, '1999-01-01'),
    -> (1, 3, '2000-01-01'), (1, 4, '2001-01-01'),
    -> (1, 5, '2002-01-01'), (2, 1, '1998-01-01'),
    -> (2, 2, '1999-01-01'), (2, 3, '2000-01-01'),
    -> (2, 4, '2001-01-01'), (2, 5, '2002-01-01'),
    -> (3, 1, '1998-01-01'), (3, 2, '1999-01-01'),
    -> (3, 3, '2000-01-01'), (3, 4, '2001-01-01'),
    -> (3, 5, '2002-01-01'), (4, 1, '1998-01-01'),
    -> (4, 2, '1999-01-01'), (4, 3, '2000-01-01'),
    -> (4, 4, '2001-01-01'), (4, 5, '2002-01-01'),
    -> (5, 1, '1998-01-01'), (5, 2, '1999-01-01'),
    -> (5, 3, '2000-01-01'), (5, 4, '2001-01-01'),
    -> (5, 5, '2002-01-01');
Query OK, 25 rows affected (0.02 sec)
Records: 25  Duplicates: 0  Warnings: 0

root@database-one 16:07:  [gftest]> EXPLAIN SELECT COUNT(*) FROM t1myisam WHERE i1 = 3 AND d = '2000-01-01'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t1myisam
   partitions: NULL
         type: ref
possible_keys: PRIMARY,k_d
          key: PRIMARY
      key_len: 4
          ref: const
         rows: 4
     filtered: 16.00
        Extra: Using where
1 row in set, 1 warning (0.01 sec)
```

可以看到，同样的结构同样的数据，因为MyISAM引擎不会在底层自动扩展普通索引，所以执行计划还是通过主键索引进行处理。

按照官方手册的说明，也可以用SHOW STATUS命令来验证

```
root@database-one 16:12:  [gftest]> FLUSH TABLE t1;
Query OK, 0 rows affected (0.00 sec)

root@database-one 16:12:  [gftest]> FLUSH STATUS;
Query OK, 0 rows affected (0.14 sec)

root@database-one 16:12:  [gftest]> SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = '2000-01-01';
+----------+
| COUNT(*) |
+----------+
|        1 |
+----------+
1 row in set (0.03 sec)

root@database-one 16:12:  [gftest]> SHOW STATUS LIKE 'handler_read%';
+-----------------------+-------+
| Variable_name         | Value |
+-----------------------+-------+
| Handler_read_first    | 0     |
| Handler_read_key      | 1     |
| Handler_read_last     | 0     |
| Handler_read_next     | 1     |
| Handler_read_prev     | 0     |
| Handler_read_rnd      | 0     |
| Handler_read_rnd_next | 0     |
+-----------------------+-------+
7 rows in set (0.01 sec)

root@database-one 16:13:  [gftest]> FLUSH TABLE t1myisam;
Query OK, 0 rows affected (0.01 sec)

root@database-one 16:13:  [gftest]> FLUSH STATUS;
Query OK, 0 rows affected (0.00 sec)

root@database-one 16:13:  [gftest]> SELECT COUNT(*) FROM t1myisam WHERE i1 = 3 AND d = '2000-01-01';
+----------+
| COUNT(*) |
+----------+
|        1 |
+----------+
1 row in set (0.01 sec)

root@database-one 16:13:  [gftest]> SHOW STATUS LIKE 'handler_read%';
+-----------------------+-------+
| Variable_name         | Value |
+-----------------------+-------+
| Handler_read_first    | 0     |
| Handler_read_key      | 1     |
| Handler_read_last     | 0     |
| Handler_read_next     | 5     |
| Handler_read_prev     | 0     |
| Handler_read_rnd      | 0     |
| Handler_read_rnd_next | 0     |
+-----------------------+-------+
7 rows in set (0.00 sec)
```

Handler_read_next表示在进行索引扫描时,按照索引从数据文件里取数据的次数。使用MyISAM引擎的t1myisam表，Handler_read_next值为5，使用InnoDB引擎的t1表，Handler_read_next值减小到1，就是因为InnoDB引擎对索引进行了主键扩展，读取的次数少，效率更好。

默认情况下，优化器分析InnoDB表的索引时会考虑扩展列，但如果因为特殊原因让优化器不考虑扩展列，可以使用SET optimizer_switch = 'use_index_extensions=off’设置。

```
root@database-one 16:26:  [gftest]> SET optimizer_switch = 'use_index_extensions=off';
Query OK, 0 rows affected (0.01 sec)

root@database-one 16:26:  [gftest]> EXPLAIN SELECT COUNT(*) FROM t1 WHERE i1 = 3 AND d = '2000-01-01'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t1
   partitions: NULL
         type: ref
possible_keys: PRIMARY,k_d
          key: PRIMARY
      key_len: 4
          ref: const
         rows: 5
     filtered: 20.00
        Extra: Using where
1 row in set, 1 warning (0.02 sec)
```


墨天轮原文链接：https://www.modb.pro/db/22927