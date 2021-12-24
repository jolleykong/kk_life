## **| 简介**

跳跃范围扫描是MySQL在8.0.13版本新增加的用于提高性能的新特性，跳跃范围扫描可以使以前部分无法使用到联合索引的SQL利用联合索引进行查询，并且可以更高效的利用联合索引，这对于使用MySQL联合索引进行查询的应用意义重大。

 

## **| 环境信息**

- MySQL版本：8.0.15
- 操作系统版本：redhat-7.4

 

## **| 跳跃范围扫描**

通过一个示例来解释跳跃范围扫描：

```sql
CREATE TABLE t1 (f1 INT NOT NULL, f2 INT NOT NULL, PRIMARY KEY(f1, f2));

INSERT INTO t1 VALUES(1,1), (1,2), (1,3), (1,4), (1,5),(2,1), (2,2), (2,3), (2,4), (2,5);

INSERT INTO t1 SELECT f1, f2 + 5 FROM t1;

INSERT INTO t1 SELECT f1, f2 + 10 FROM t1;

INSERT INTO t1 SELECT f1, f2 + 20 FROM t1;

INSERT INTO t1 SELECT f1, f2 + 40 FROM t1;

ANALYZE TABLE t1;

EXPLAIN SELECT f1, f2 FROM t1 WHERE f2 > 40\G

*************************** 1. row ***************************
       id: 1
  select_type: SIMPLE
    table: t1
   partitions: NULL
     type: range
possible_keys: PRIMARY
      key: PRIMARY
  key_len: 8
      ref: NULL
     rows: 53
 filtered: 100.00
    Extra: Using where; Using index for skip scan
1 row in set, 1 warning (0.00 sec)
 
mysql> select version();
+-----------+
| version() |
+-----------+
| 8.0.15 |
+-----------+
1 row in set (0.00 sec)
```

在这个示例中，SELECT f1,f2 FROM t1 WHERE f2>40在8.0.13版本之前是通过索引全扫描的方式来获取最终的结果集，因为SELECT查询的字段全部都是索引的组成部分。MySQL通过索引全扫描获取所有的行记录，然后通过f2 > 40这个条件过滤，最终筛选出结果集返回给客户端。 

众所周知，索引范围扫描的效率肯定是要高于索引全扫描的，在这个示例中，虽然查询条件是f2 > 40，属于范围查询，但是WHERE条件中不包含f1字段的的条件，所以无法使用索引范围扫描的方式过滤数据。在MySQL-8.0.13版本增加的跳跃范围扫描特性，就是针对类似的场景的优化，跳跃范围扫描在这个示例中实际是针对每一个f1字段的值，进行了范围扫描，即进行了多次范围扫描。 
 针对这个示例，具体的跳跃范围扫描过程如下：

1. 获取联合索引中第一个字段f1的第一个值：f1 = 1
2. 将获取到的值和WHERE条件中的f2的条件组合：f1 = 1 AND f2 > 40
3. 执行这个范围扫描查询
4. 获取联合索引中第一个字段f1的第二个值：f1 = 2
5. 将获取到的值和WHERE条件中的f2的条件组合：f1 = 2 AND f2 > 40
6. 执行这个范围扫描查询
7. 将两次范围扫描查询的结果合并返回给客户端

跳跃范围扫描实际就是将一些全扫描的场景拆分成多个范围扫描，利用范围扫描的效率高于全扫描的效率，最终实现提高SQL效率。 

在这个示例中，比较有跳跃范围扫描特性的SQL执行计划以及没有跳跃范围扫描特性的SQL执行计划：

```sql
# 有跳跃范围扫描特性
mysql> EXPLAIN SELECT f1, f2 FROM t1 WHERE f2 > 40\G
*************************** 1. row ***************************
       id: 1
  select_type: SIMPLE
    table: t1
   partitions: NULL
     type: range
possible_keys: PRIMARY
      key: PRIMARY
  key_len: 8
      ref: NULL
     rows: 53
 filtered: 100.00
    Extra: Using where; Using index for skip scan
1 row in set, 1 warning (0.00 sec)
 
# 没有跳跃范围扫描特性
mysql> EXPLAIN SELECT f1, f2 FROM t1 WHERE f2 > 40\G 
 *************************** 1. row ***************************
       id: 1
  select_type: SIMPLE
    table: t1
   partitions: NULL
     type: index
possible_keys: NULL
      key: PRIMARY
  key_len: 8
      ref: NULL
     rows: 160
 filtered: 33.33
    Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)
```

通过执行计划可以看到,有跳跃范围扫描特性的查询扫描的行数更少且过滤性更高。

 

## **| 使用限制以及场景**

下面来说说跳跃范围扫描使用一些限制以及场景：

- 表上至少存在一个联合索引([A_1,A_2...A_k],B_1,B_2...B_m,C,[,D_1,...,D_n])，其中A部分以及D部分可以为空，但是B和C部分不能为空。A_1,A_2..等代表字段值
- 只针对单表查询
- 查询中不包含GROUP BY或者DISTINCT
- SELECT查询的字段全部被包含在索引组成部分，即符合覆盖索引规范
- 前缀A_1,A_2...A_k部分必须是可以被相等的常量
- 字段C上必须是一个范围条件，大于或大于等于，小于或小于等于
- 允许在D字段上有过滤条件，但是必须和C上的范围条件一起使用

跳跃范围扫描默认是开启的，有两种方式可以关闭跳跃范围扫描特性：

- 通过修改optimizer_switcher变量值，默认MySQL是将optimizer_switcher中的skip_scan设置为on的，可以通过将skip_scan设置为off关闭跳跃范围扫描
- 通过Hint的方式关闭跳跃范围扫描特性：SELECT/*+ NO_SKIP_SCAN(t1 PRIMARY) */ f1, f2 FROM t1 WHERE f2 > 40;

对于使用了跳跃范围扫描特性的SQL，使用EXPLAIN查看其执行计划，可以看到：

- 在执行计划输出的Extra一栏中有：Using index for skip scan
- 在执行计划输出的possible_keys一栏中会显示可以使用到的索引

 

## **| 总结**

跳跃范围扫描是对使用MySQL联合索引查询的SQL意义重大，能在使SQL查询效率更高，但是并不是使用到跳跃范围扫描就能代表SQL执行效率更高。在MySQL一些开发规范中，一般要求建立联合索引时将重复值少的字段放在联合索引前面，将重复值多的字段放在联合索引后面，方便SQL在使用联合索引时通过前面的字段快速过滤结果。但是在跳跃范围扫描特性中，是遍历前面字段的值，与后续字段的范围查询条件组合，进行范围扫描查询，那对于重复值少的字段会被拆分成多个范围扫描查询，在实际使用过程中并不一定会比索引全扫描效率更高。

所以个人觉得跳跃范围扫描适用于联合索引中前导列distinct值较少，后续字段选择过滤性又比较好的场景，能更好的发挥跳跃范围扫描的作用。

 

### **| 作者简介**

**沈 刚·沃趣科技数据库技术专家**