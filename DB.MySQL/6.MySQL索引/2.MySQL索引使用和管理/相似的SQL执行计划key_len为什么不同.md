## 相似的SQL执行计划key_len为什么不同

## 导读

> 执行计划中看到key_len值发生变化，表示联合索引有时能用到多个列，有时却只能用到部分列，这是为啥子呢？

我的朋友小明同学这几天又遇到一件令人懵*的事，有个SQL执行计划看起来挺诡异的，我看了下，也是有点发懵。

## 基本信息

严格遵循我自己要求的“提问的艺术”，先交代下必要的背景信息。

### 1、表DDL

```
[root@yejr.me]>show create table t_keylen\G
*************************** 1. row ***************************
       Table: t_keylen
Create Table: CREATE TABLE `t_keylen` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `userid` bigint(20) unsigned NOT NULL DEFAULT '0',
  `balance` int(10) unsigned NOT NULL DEFAULT '0',
  `type` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `fullName` json NOT NULL,
  PRIMARY KEY (`id`),
  KEY `i_userid_balance` (`userid`,`balance`)
) ENGINE=InnoDB AUTO_INCREMENT=19;

[root@yejr.me]>select * from t_keylen;
+----+--------+---------+------+-----------------------------------------------------------------+
| id | userid | balance | type | fullName                                                        |
+----+--------+---------+------+-----------------------------------------------------------------+
|  1 |      1 |     121 |    1 | {"lastName": "1", "firstName": "fn", "middleName": "mn"}        |
|  2 |      2 |    1236 |    0 | {}                                                              |
|  3 |      3 |     100 |    0 | {"lastName": "3"}                                               |
|  4 |      4 |       5 |    0 | {"lastName": "4", "firstName": "fn"}                            |
|  6 |      5 |      11 |    0 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
|  7 |      6 |       5 |    0 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
|  9 |      7 |       5 |    0 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
| 10 |      8 |       5 |    0 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
| 11 |     11 |      11 |    0 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
| 13 |     10 |      11 |    1 | {"lastName": "ln", "firstName": "fn", "middleName": "mn"}       |
| 15 |     14 |      47 |    1 | {"lastName": "wqQSi", "firstName": "U1lc", "middleName": "ijK"} |
| 18 |     12 |       2 |    1 | {"lastName": "K196J", "firstName": "4Uf3", "middleName": "Vlt"} |
+----+--------+---------+------+-----------------------------------------------------------------+
12 rows in set (0.00 sec)
```

### 2、索引统计信息（有些输出不影响本案例判断，我给去掉了，建议手机横过来观看）

```
[root@yejr.me]>show index from t_keylen;
+------------+------------------+--------------+-------------+-------------+
| Non_unique | Key_name         | Seq_in_index | Column_name | Cardinality |
+------------+------------------+--------------+-------------+-------------+
|          0 | PRIMARY          |            1 | id          |          12 |
|          1 | i_userid_balance |            1 | userid      |          12 |
|          1 | i_userid_balance |            2 | balance     |          12 |
+------------+------------------+--------------+-------------+-------------+
```

注意到 **i_userid_balance** 是一个联合索引，由两列构成，数据类型分别是 bigint 和 int，如果整个索引都被用上的话，其key_len值为12，如果只用到了userid列，则其key_len值为8。

### 3、查看SQL执行计划

先看第一条SQL的执行计划（建议手机横过来观看）

```
[root@yejr.me]>desc select * from t_keylen where
    userid > 10 and balance > 1\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t_keylen
   partitions: NULL
         type: range
possible_keys: i_userid_balance
          key: i_userid_balance
      key_len: 8
          ref: NULL
         rows: 3
     filtered: 33.33
        Extra: Using index condition
```

在本例中，key_len值为8，说明联合索引只用到了 userid 列，因为条件 **userid > 10** 是范围查询，看起来没毛病。

再看第二条SQL（建议手机横过来观看）

```
[root@yejr.me]>desc select * from t_keylen where
    userid >= 10 and balance > 1\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: t_keylen
   partitions: NULL
         type: range
possible_keys: i_userid_balance
          key: i_userid_balance
      key_len: 12
          ref: NULL
         rows: 4
     filtered: 33.33
        Extra: Using index condition
```

这个结果就有点出乎意料了，不是说联合索引里，如果有一列开始是范围查询的话，那么从它后面的列都用不到索引了，但在本例中，我们看到的是 **key_len=12**，说明两个列还是都用上了，这是为啥呢？

### 4、解惑

请教了下**知数堂《SQL优化》班的松华老师**，终于解惑了。

原来对于数字型的联合索引，最左边的列的是否有等号非常重要，直接决定key_len的大小。本例中是 **>= 和>** 这种 **左列包含等号** 的条件，索引长度就可以计算到第二个列。如果是 **> 和 >** 这种条件，因为最左边的列不包含等号所以只能用到第一个。同理，下面案例是 **<=和=** 那就key_len值算到第二个列，即其值为12。（建议手机横过来观看）

```
[root@yejr.me]>desc select * from t_keylen where
    userid <= 10 and balance = 1\G
*************************** 1. row ***************************
...
         type: range
possible_keys: i_userid_balance
          key: i_userid_balance
      key_len: 12
...
```

好吧，又涨姿势了。