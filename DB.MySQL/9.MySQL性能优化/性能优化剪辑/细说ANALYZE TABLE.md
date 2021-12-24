## 细说ANALYZE TABLE
叶师傅   老叶茶馆  *2017-07-07*                

## 导读

> 本文详细介绍了ANALYZE TABLE的作用及更深入的原理，执行代价估算公式等

###  

### ANALYZE TABLE 作用

- ANALYZE TABLE 会统计索引分布信息，并将结果持久化存储；
- 对于 MyISAM 表，相当于执行了一次 myisamchk –analyze；
- 支持 InnoDB、NDB、MyISAM 等存储引擎，但不支持 **视图**（view）；
- ANALYZE TABLE也可以用在表分区上；
- 对InnoDB、MyISAM表执行 ANALYZE TABLE 时，会加上**读锁**（read lock）；
- 执行 ANALYZE TABLE 会记录binlog。（这是合理的，因为索引分析这个操作，在MASTER端执行完后，SLAVE端也是需要的）

###  

### 索引分布分析都干了啥

若自从上次索引分析后没有数据更新的话，执行 ANALYZE TABLE 并不会再分析一次。
optimizer 会根据索引分析结果来判断表 JOIN 的驱动顺序，以及选用哪个索引。

###  

### 关于 innodb_stats_persistent 选项

我们可以通过设定该选项，决定索引分析结果**是否要持久化存储到磁盘中**。

不持久化存储的话，可能需要频繁更新统计信息，并由此引发执行计划反复变化。

这个设置在每个表创建（或后期 ALTER 修改）时都可以自行指定 **STATS_PERSISTENT** 选项，也可以设置全局选项 **innodb_stats_persistent**（这个选项设置为 1 时，则表统计信息将持久化存储）。



### 关于 innodb_stats_persistent_sample_pages 选项

该选项决定了每次统计索引及其他信息时要采集多少个data page，默认值是 20。

增加这个值，可以提高统计信息的精确度，同样也能提高执行计划的准确性，不过也相应增加了在InnoDB表上分析的I/O开销。

**备注**

- 增加 innodb_stats_persistent_sample_pages 的值可能导致 ANALYZE TABLE 的耗时增加。可以参考下方公式估算执行 ANALYZE TABLE 的代价。
- 只有在 innodb_stats_persistent 选项启用后，innodb_stats_persistent_sample_pages  也才能跟着生效，否则的话，只有选项 innodb_stats_transient_sample_pages 才能生效。
- 选项 innodb_stats_transient_sample_pages 设定的是 **动态** 统计信息采集的data page数量，默认值是 8。

选项 innodb_stats_persistent_sample_pages 是全局作用的，但如果某个表想单独定义采集的page数目，可以在DDL时自行设定：

```
CREATE TABLE ... STATS_SAMPLE_PAGES = 30;
```

或

```
ALTER TABLE ... STATS_SAMPLE_PAGES = 30;
```

###  

### ANALYZE TABLE 代价估算

关于执行ANALYZE TABLE 的代价计算公式：
影响代价因素：

- innodb_stats_persistent_sample_pages定义值大小；
- 表中索引数多少；
- 表中分区数多少。

代价粗略估算公式：innodb_stats_persistent_sample_pages * 索引数 * 分区数。

而更严谨的计算公式见下：

```
O(n_sample
  * (n_cols_in_uniq_i
     + n_cols_in_non_uniq_i
     + n_cols_in_pk * (1 + n_non_uniq_i))
  * n_part)
```

各项指标解释：

- n_sample，采集的data page数量；
- n_cols_in_uniq_i，所有唯一索引（不含主键索引）中的列总数；
- n_cols_in_non_uniq_i，所有普通索引中的列总数；
- n_cols_in_pk，主键索引中的列总数（若未显式定义主键，则相当于只有一列的ROWID）；
- n_non_uniq_i，非唯一索引数量；
- n_part，表分区数量。

以下表为例：

```
CREATE TABLE t (
  a INT,
  b INT,
  c INT,
  d INT,
  e INT,
  f INT,
  g INT,
  h INT,
  PRIMARY KEY (a, b),
  UNIQUE KEY i1uniq (c, d),
  KEY i2nonuniq (e, f),
  KEY i3nonuniq (g, h)
);
```

我们执行下面的SQL来查询这个表的索引信息：

```
  SELECT index_name, stat_name, stat_description
  FROM mysql.innodb_index_stats
  WHERE
  database_name='test' AND
  table_name='t' AND
  stat_name like 'n_diff_pfx%';

  +------------+--------------+------------------+
  | index_name | stat_name    | stat_description |
  +------------+--------------+------------------+
  | PRIMARY    | n_diff_pfx01 | a                |
  | PRIMARY    | n_diff_pfx02 | a,b              |
  | i1uniq     | n_diff_pfx01 | c                |
  | i1uniq     | n_diff_pfx02 | c,d              |
  | i2nonuniq  | n_diff_pfx01 | e                |
  | i2nonuniq  | n_diff_pfx02 | e,f              |
  | i2nonuniq  | n_diff_pfx03 | e,f,a            |
  | i2nonuniq  | n_diff_pfx04 | e,f,a,b          |
  | i3nonuniq  | n_diff_pfx01 | g                |
  | i3nonuniq  | n_diff_pfx02 | g,h              |
  | i3nonuniq  | n_diff_pfx03 | g,h,a            |
  | i3nonuniq  | n_diff_pfx04 | g,h,a,b          |
  +------------+--------------+------------------+
```

上面这个结果看起来有点奇怪是不是，其实没错，先科普几点知识：

- 所有的普通索引，实际物理存储时，都要包含主键列的，也就是所谓的 index extensions 特性；
- 统计索引信息时，是根据最左原则，要统计各种组合的。比如(a,b) 索引，要统计(a), (a,b), (a,b,pk) 三种信息，而不是只统计(a,b)这个信息；
- 不过，在 mysql.innodb_index_stats 中存储统计信息时，是不统计唯一索引后面存储主键列信息的，非唯一普通索引后存储主键列信息则会被统计进去；

因此，上面 mysql.innodb_index_stats 中存储的统计结果是正确的。

我们再回来看下索引统计的代价公式，像下面这样计算：

```
- n_sample，采集的data page数量，值为 20（默认值）；

- n_cols_in_uniq_i，所有唯一索引（不含主键索引）中的列总数，值为 2；

- n_cols_in_non_uniq_i，所有普通索引中的列总数，值为 4；

- n_cols_in_pk，主键索引中的列总数（若未显式定义主键，则相当于只有一列的ROWID），值为 2；

- n_non_uniq_i，非唯一索引数量，值为 2；

- n_part，表分区数量，值为 1（没有表分区，值为1，而不是0）。
```

那么最终需要扫描的data page数结果就是：

```
20 * (2 + 4 + 2 * (1 + 2)) * 1 = 240
```

实际需要读取的字节数则是：

```
240 * 16384 = 3932160 （即 3.84M）
```

当然了，要读取的data page，有可能已经在buffer pool中了，因此并不全是物理读。

从中，我们也可以看到，这个代价和表的数据量并无直接关系。
不过，当表数量越大时，聚集索引的 B+ 树也越大，搜索代价肯定也越大。

**参考**

- https://dev.mysql.com/doc/refman/5.7/en/analyze-table.html
- https://dev.mysql.com/doc/refman/5.7/en/innodb-analyze-table-complexity.html
- https://dev.mysql.com/doc/refman/5.7/en/index-extensions.html