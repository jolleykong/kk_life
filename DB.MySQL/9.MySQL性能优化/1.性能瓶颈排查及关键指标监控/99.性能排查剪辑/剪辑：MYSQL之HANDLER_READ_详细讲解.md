[TOC]

# MYSQL之HANDLER_READ_详细讲解

 

## 简介:Handler_read_*

在对MySQL的Query进行调优时候，我们可以有效的使用EXPLAIN [EXTENDED ],SHOW　PROFILE内置工具，但是通过这两个工具，得到的是比较粗糙的信息，我们无法得知MySQL到底是如何操作底层的数据。其实可以通过MySQL Status中的Handler_read计数器获知这些详情。下面是基础操作知识：

- 获取Handler_read_*系类状态值命令：

  ```
  show session status like ‘Handler_read%';
  ```

- 重置Handler_read系列状态值命令

  ```
  flush status;
  ```


通过命令`show session status like ‘Handler_read%';`，我们获取到Handler_read_*的状态有下面这些,下面会对这些进行一一解释以及测试：

- Handler_read_first
- Handler_read_last
- Handler_read_next
- Handler_read_prev
- Handler_read_rnd
- Handler_read_rnd_next
- Handler_read_key



测试数据结构：

```
mysql> show  create table test_handler_read \G  
*************************** 1. row ***************************      
Table:  test_handler_read  
Create Table: CREATE TABLE `test_handler_read` 
(`id` int(11) NOT NULL AUTO_INCREMENT,   
`key1` int(11) NOT NULL,   
`key2` int(11) NOT NULL,   
`key3` int(11) NOT NULL,   
`key4` int(11) DEFAULT NULL,   
PRIMARY KEY (`id`),   
KEY `idx` (`key1`),   
KEY `idx_key_2_3` (`key2`,`key3`),   
KEY `idx_key4_id` (`key4`,`id`)  
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8  
1 row in set (0.00 sec)     

mysql> INSERT INTO `test_handler_read` VALUES  (1,1,2,3,4),(2,2,4,6,8),(3,3,6,9,12),(4,4,8,12,16),
 (5,5,10,15,20),(6,6,12,18,24),(7,7,14,21,44), (8,8,16,24,44),(9,9,18,27,44),(10,10,20,30,44),(11,11,22,33,44);        
 
mysql> show  create table test_handler_read_info_v1 \G  
*************************** 1. row ***************************      
Table:  test_handler_read_info_v1  
Create Table: CREATE TABLE `test_handler_read_info_v1` 
(`rid` int(11) NOT NULL,   
`info1` int(11) NOT NULL,   
`info2` int(11) NOT NULL,   
`info3` int(11) NOT NULL,   
PRIMARY  KEY (`rid`),   
KEY `idx_info_1` (`info1`)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8  
1 row in set (0.00 sec)     

mysql> INSERT INTO `test_handler_read_info_v1` VALUES  (1,3,3,3),(2,5,5,5),(3,7,7,7),(4,9,9,9),(5,11,11,11),
 (6,13,14,15),(7,23,24,25),(8,21,22,23),(9,19,20,21),(10,17,18,19),(11,15,16,17);  
```



  

## 解释:Handler_read_*

- Handler_read_key

  通过index获取数据的次数

  > The number of requests to read a row based on a key. If this value is high, it is a good indication that your tables are properly indexed for your queries.

  

- Handler_read_first

  读取索引第一个条目的次数

  > The number of times the first entry in an index was read. If this value is high, it suggests that the server is doing a lot of full index scans; for example, SELECT col1 FROM foo, assuming that col1 is indexed.

  

- Handler_read_last

  读取索引最后一个条目的次数

  > The number of requests to read the last key in an index. With ORDER BY, the server will issue a first-key request followed by several next-key requests, whereas with ORDER BY DESC, the server will issue a last-key request followed by several previous-key requests. This variable was added in MySQL 5.6.1.

  

- Handler_read_next

  通过索引读取下一条数据的次数

  > The number of requests to read the next row in key order. This value is incremented if you are querying an index column with a range constraint or if you are doing an index scan.

  

- Handler_read_prev

  通过索引读取上一条数据的次数

  > The number of requests to read the previous row in key order. This read method is mainly used to optimize ORDER BY … DESC.

  

- Handler_read_rnd

  从固定位置读取数据的次数

  > The number of requests to read a row based on a fixed position. This value is high if you are doing a lot of queries that require sorting of the result. You probably have a lot of queries that require MySQL to scan entire tables or you have joins that do not use keys properly.

  

- Handler_read_rnd_next

  从数据节点读取读取下一条数据的次数

  > The number of requests to read the next row in the data file. This value is high if you are doing a lot of table scans. Generally this suggests that your tables are not properly indexed or that your queries are not written to take advantage of the indexes you have.

  



## 测试:Handler_read_*

### 单表测试

- 全表扫描

  ```
  mysql> select * from  test_handler_read limit 10;     
  mysql> desc select * from  test_handler_read limit 10;  
  +----+-------------+-------------------+------+---------------+------+---------+------+------+-------+  
  | id | select_type | table             | type | possible_keys | key  | key_len | ref  | rows | Extra |  +----+-------------+-------------------+------+---------------+------+---------+------+------+-------+  
  | 1  | SIMPLE      | test_handler_read | ALL  | NULL          | NULL | NULL    | NULL |  11  | NULL  |  +----+-------------+-------------------+------+---------------+------+---------+------+------+-------+  
  1 row in set (0.00 sec)        
  
  mysql> show  status where Value >0 and Variable_name like 'Handler_read%';  
  +-----------------------+-------+  
  | Variable_name         | Value |  
  +-----------------------+-------+  
  | Handler_read_first    |  1   |  
  | Handler_read_key      |  1   |  
  | Handler_read_rnd_next |  10  |  
  +-----------------------+-------+  
  3 rows in set (0.00 sec)
  ```

  - Handler_read_first + 1 : 从键的第一个位置开始读取
  - Handler_read_key + 1 : 根据第一个位置的KEY读1行，其他9行是根据叶节点的链表依次读取
  - Handler_read_rnd_next +10 : 从主键的叶节点(行数据)中顺序读取10行



- 索引扫描

  ```
  mysql> select  info1 from test_handler_read_info_v1 order by info1 asc limit 10;     
  
  mysql> desc  select info1 from test_handler_read_info_v1 order by info1 asc limit 10;  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+ 
  | id | select_type | table                     | type  | possible_keys | key        | key_len | ref  | rows | Extra       |  
  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+
  | 1  | SIMPLE      | test_handler_read_info_v1 | index | NULL          | idx_info_1 | 4       | NULL |  10  | Using index |  
  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+  
  1 row in set (0.00 sec)   
  
  mysql> show  status where Value >0 and Variable_name like 'Handler_read%';  
  +--------------------+-------+  
  | Variable_name      | Value |  
  +--------------------+-------+  
  | Handler_read_first | 1     |  
  | Handler_read_key   | 1     |  
  | Handler_read_next  | 9     |  
  +--------------------+-------+  
  3 rows in set (0.00 sec)
  ```

  - Handler_read_first + 1 : 从键的第一个位置开始读取
  - Handler_read_key + 1 : 根据第一个位置的KEY读1行
  - Handler_read_next + 9 : 按键顺序依次读取之后的9行

  ```
  mysql> select  info1 from test_handler_read_info_v1 order by info1 desc limit 10;     
  
  mysql> desc  select info1 from test_handler_read_info_v1 order by info1 desc limit 10;  
  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+  
  | id | select_type | table                     | type  | possible_keys | key        | key_len | ref  | rows | Extra       |  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+  
  | 1  | SIMPLE      | test_handler_read_info_v1 | index | NULL          | idx_info_1 | 4       | NULL |  10  | Using index |  +----+-------------+---------------------------+-------+---------------+------------+---------+------+------+-------------+  
  1 row in set (0.00 sec)     
  
  mysql> show  status where Value >0 and Variable_name like 'Handler_read%';  
  +-------------------+-------+  
  | Variable_name     | Value |  
  +-------------------+-------+  
  | Handler_read_key  | 1     |  
  | Handler_read_last | 1     |  
  | Handler_read_prev | 9     |  
  +-------------------+-------+  
  3 rows in set (0.00 sec)
  ```

  - Handler_read_key + 1 : 根据第一个位置的KEY读1行
  - Handler_read_last + 1 : 从键的最后一个位置开始读取
  - Handler_read_prev + 9 : 按键顺序依次读取之前的9行

### 多表测试

- 表数据介绍

  test_handler_read表当key4=44有 5行数据

  test_handler_read_info_v1中rid是主键

- where + drived table sort

  - sort: asc

    ```
    mysql> select * from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by a.id asc limit 5;
     
    mysql> desc select * from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by a.id asc limit 5;
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+
    | id | select_type | table | type   | possible_keys | key         | key_len | ref         | rows | Extra       |
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+
    |  1 | SIMPLE      | a     | ref    | idx_key4_id   | idx_key4_id | 5       | const       |    5 | Using where |
    |  1 | SIMPLE      | b     | eq_ref | PRIMARY       | PRIMARY     | 4       | testdb.a.id |    1 | NULL        |
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+
    2 rows in set (0.00 sec)
     
    mysql> show status  where Value >0 and Variable_name like 'Handler_read%';
    +-------------------+-------+
    | Variable_name     | Value |
    +-------------------+-------+
    | Handler_read_key  | 6     |
    | Handler_read_next | 4     |
    +-------------------+-------+
    2 rows in set (0.00 sec)
    ```

    - Handler_read_key + 6 : a 根据idx_key4_id（key4=44）读1次，b 根据 PRIMARY KEY读5次
    - Handler_read_prev + 4 :a 按键顺序依次向后读取4个id

  

  - sort: desc

    ```
    mysql> select *  from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by a.id desc limit 5;       
    
    mysql> desc select * from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by a.id desc limit 5;   
    
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+   
    | id | select_type | table | type   | possible_keys | key         | key_len | ref         | rows | Extra       |   +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+   
    |  1 | SIMPLE      | a     | ref    | idx_key4_id   | idx_key4_id | 5       | const       |    5 | Using where |   
    |  1 | SIMPLE      | b     | eq_ref | PRIMARY       | PRIMARY     | 4       | testdb.a.id |    1 | NULL        |   +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-------------+   
    2 rows in set (0.00 sec)       
    
    mysql> show status  where Value >0 and Variable_name like 'Handler_read%';   
    +-------------------+-------+   
    | Variable_name     | Value |   
    +-------------------+-------+   
    | Handler_read_key  | 6     |   
    | Handler_read_prev | 4     |   
    +-------------------+-------+   
    2 rows in set (0.00 sec)  
    ```

    - Handler_read_key + 6 : a根据idx_key4_id（key4=44）读1次，b根据PRIMARY KEY读5次
    - Handler_read_prev + 4: a按键倒序依次向前读取4个id

    

- where+ second table sort

  - sort: asc

    ```
    mysql> select * from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by b.rid asc limit 5;
     
    mysql> desc select * from test_handler_read a left join test_handler_read_info_v1 b on (a.id = b.rid) where a.key4=44 order by b.rid asc limit 5;
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+---------------------------------+
    | id | select_type | table | type   | possible_keys | key         | key_len | ref         | rows | Extra                           |
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+---------------------------------+
    |  1 | SIMPLE      | a     | ref    | idx_key4_id   | idx_key4_id | 5       | const       |    5 | Using temporary; Using filesort |
    |  1 | SIMPLE      | b     | eq_ref | PRIMARY       | PRIMARY     | 4       | testdb.a.id |    1 | NULL                            |
    +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+---------------------------------+
    2 rows in set (0.00 sec)
     
    mysql> show status  where Value >0 and Variable_name like 'Handler_read%';
    +-----------------------+-------+
    | Variable_name         | Value |
    +-----------------------+-------+
    | Handler_read_key      | 6     |
    | Handler_read_next     | 5     |
    | Handler_read_rnd      | 5     |
    | Handler_read_rnd_next | 6     |
    +-----------------------+-------+
    4 rows in set (0.00 sec)
    ```

    - Handler_read_key + 6 : a 根据idx_key4_id（key4=44）读1次，b 根据PRIMARY KEY读5次

    - Handler_read_next + 5 : a 按键顺序依次读取4个id. 额外的1次是？(没有查出相关文档)

    - Handler_read_rnd + 5 : filesort后每行位置都是固定的,limit 5取5行

    - Handler_read_rnd_next + 6: filesort全表遍历读取temporary表中的5行，进行排序; 额外的1是EOF标志位;

    - Using temporary; Using filesort 原因: 无法使用a表的索引

      

    1. 先查询表a key4=44 的5行与b进行join,将结果保存在temporary表
       - Handler_read_key + 6, Handler_read_next + 5

    2. 然后对临时表排序;
       - Handler_read_rnd_next + 6
    3. 取前10个。
       - Handler_read_rnd + 5

    

- where条件放在join中

  ```
  mysql>  select a.id, a.key4 ,b.* from test_handler_read a force index (idx_key4_id) 
  		left join test_handler_read_info_v1 b on (a.id = b.rid) and a.key4=44 order by a.id  
  		limit 5;
  
  mysql> desc  select a.id, a.key4 ,b.* from test_handler_read a force index (idx_key4_id) 
  		left join test_handler_read_info_v1 b on (a.id = b.rid) and a.key4=44 order by a.id  
  		limit 5;   
  +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-----------------------------+   
  | id | select_type | table | type   | possible_keys | key         | key_len | ref         | rows | Extra                       | 
  +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-----------------------------+   
  |  1 | SIMPLE      | a     | index  | NULL          | idx_key4_id | 9       | NULL        |   11 | Using index; Using filesort |   
  |  1 | SIMPLE      | b     | eq_ref | PRIMARY       | PRIMARY     | 4       | testdb.a.id |    1 | Using where                 |   
  +----+-------------+-------+--------+---------------+-------------+---------+-------------+------+-----------------------------+   
  2 rows in set (0.00 sec)       
  
  mysql> show status  where Value >0 and Variable_name like 'Handler_read%';   
  +-----------------------+-------+   
  | Variable_name         | Value |   
  +-----------------------+-------+   
  | Handler_read_first    | 1     |   
  | Handler_read_key      | 6     |   
  | Handler_read_rnd_next | 12    |   
  +-----------------------+-------+   
  3 rows in set (0.00 sec)  
  ```

  - Handler_read_first + 1 : 从表a中idx_key4_id索引开始位置进行读取
  - Handler_read_key + 6 : a 根据idx_key4_id(key4=44)读1次，b 根据PRIMARY KEY读5次
  - Handler_read_rnd_next + 12 : filesort全表遍历读取表a中idx_key4_id索引的11行，进行排序; 额外的1是EOF标志位;
  - 没有 Using temporary 是因为先对a的索引idx_key4_id进行排序，然后再join, Using filesort 原因:无法使用a表的索引

  1. 先对a表排序，取5个id
     - Handler_read_first + 1, Handler_read_key + 1, Handler_read_rnd_next + 12
  2. 然后根据a.id=b.rid与表b进行join
     - Handler_read_key + 5

  

### 剖析实例

 ```
mysql>select courseguid,starttime from W_ListenRec_1_8 ignore index (idx_listenrec_courseguid) where userid = 5627758 
and courseguid in ('s154717','s149496','s148373','s145703','s148741','s156269',
's158955','s152551','s151599','s158902','s153671','s152798','s151181','s155451',
's151756','s151402','s153248','s153966','s153557','s155208','s155585','s157355',
's156112','s151285','s157049','s153517','s159406','s158813','s151427','s154241',
's154526','s156264','s156322','s149377','s146878','s159755','s153898','s155122',
's152520','s158579','s152861','s156550','s159462','s152663','s157787','s157234',
's153156','s155318','s153168','s154418','s154136','s157160','s155635','s156219',
's151667','s157779','s155611','s159115','s151519','s152790','s157161','s156305',
's154779','s152635','s153482','s157332','s154576','s153692','s159822','s156165',
's151320','s152385','s156997','s158651','s152030','s152829','s153647','s158938',
's155173','s158989','s156008','s156536','s155743','s153928','s155144','s159268',
's156374','s154407','s153381','s151477','s159902','s152161','s159970','s151718',
's151500','s154102','s151692','s153132','s158606','s153077','s157963','s157945',
's152854','s159267','s153136','s152969','s152155','s154899','s141114','s148767',
's158609','s156586','s154909','s152148','s156201','s156673','s158730','s158930',
's152907','s145297','s149059','s158820','s159016') 
group by courseguid order by id desc;
39 rows in set (0.02 sec)
 
+----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+----------------------------------------------+
| id | select_type | table           | type | possible_keys        | key                  | key_len | ref   | rows | Extra                                        |
+----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+----------------------------------------------+
|  1 | SIMPLE      | W_ListenRec_1_8 | ref  | idx_listenrec_userid | idx_listenrec_userid | 4       | const | 2028 | Using where; Using temporary; Using filesort |
+----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+----------------------------------------------+
1 row in set (0.00 sec)
 
mysql> show status where Variable_name like 'Handler_read%' and Value >0;
+-----------------------+-------+
| Variable_name         | Value |
+-----------------------+-------+
| Handler_read_key      | 1     |
| Handler_read_next     | 2029  |
| Handler_read_rnd      | 39    |
| Handler_read_rnd_next | 41    |
+-----------------------+-------+
4 rows in set (0.00 sec)
 ```

- Handler_read_key + 1：从表W_ListenRec_1_8中使用idx_listenrec_userid索引读取

- Handler_read_next + 2029：表W_ListenRec_1_8按照索引顺序读取2028， 额外的1是EOF标志位

- Handler_read_rnd + 39：filesort后每行位置都是固定的，获取全部的39行数据

- Handler_read_rnd_next + 41：filesort全表遍历读取temporary表中的39行，1为EOF标识为，例外的1？？自己测试了一下，sql最后加上limit 39，Handler_read_rnd_next=39， 加上limit 40。39，Handler_read_rnd_next=41，多出来的1目前没出查到来源



那么印证一下子猜测的结果：

- setp 1:

  ```
  mysql>select courseguid,starttime from W_ListenRec_1_8 ignore index (idx_listenrec_courseguid) where userid = 5627758       
  mysql> desc select courseguid,starttime from W_ListenRec_1_8 ignore index (idx_listenrec_courseguid) where userid = 5627758;   
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+-------+   
  | id | select_type | table           | type | possible_keys        | key                  | key_len | ref   | rows | Extra |   
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+-------+   
  |  1 | SIMPLE      | W_ListenRec_1_8 | ref  | idx_listenrec_userid | idx_listenrec_userid | 4       | const | 2028 |       |   
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+-------+   
  1 row in set (0.01 sec)       
  
  mysql> show status where Variable_name like 'Handler_read%' and Value >0;   
  
  +-------------------+-------+   
  | Variable_name     | Value |   
  +-------------------+-------+   
  | Handler_read_key  | 1     |   
  | Handler_read_next | 2029  |   
  +-------------------+-------+   
  2 rows in set (0.00 sec)  
  ```

  从上面这个拆解sql看出来，首先这个sql使用了idx_listenrec_userid读取数据一条数据Handler_read_key + 1，然后按照索引顺序向后再读取了2028条记录，最后读到了EOF,Handler_read_next +2028+1

- step 2:

  ```
  mysql> select courseguid,starttime from W_ListenRec_1_8 ignore index (idx_listenrec_courseguid) where userid = 5627758 
  and courseguid in ('s154717','s149496','s148373','s145703','s148741','s156269',
  's158955','s152551','s151599','s158902','s153671','s152798','s151181','s155451',
  's151756','s151402','s153248','s153966','s153557','s155208','s155585','s157355',
  's156112','s151285','s157049','s153517','s159406','s158813','s151427','s154241',
  's154526','s156264','s156322','s149377','s146878','s159755','s153898','s155122',
  's152520','s158579','s152861','s156550','s159462','s152663','s157787','s157234',
  's153156','s155318','s153168','s154418','s154136','s157160','s155635','s156219',
  's151667','s157779','s155611','s159115','s151519','s152790','s157161','s156305',
  's154779','s152635','s153482','s157332','s154576','s153692','s159822','s156165',
  's151320','s152385','s156997','s158651','s152030','s152829','s153647','s158938',
  's155173','s158989','s156008','s156536','s155743','s153928','s155144','s159268',
  's156374','s154407','s153381','s151477','s159902','s152161','s159970','s151718',
  's151500','s154102','s151692','s153132','s158606','s153077','s157963','s157945',
  's152854','s159267','s153136','s152969','s152155','s154899','s141114','s148767',
  's158609','s156586','s154909','s152148','s156201','s156673','s158730','s158930',
  's152907','s145297','s149059','s158820','s159016') 
  group by courseguid order by null;
   
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+------------------------------+
  | id | select_type | table           | type | possible_keys        | key                  | key_len | ref   | rows | Extra                        |
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+------------------------------+
  |  1 | SIMPLE      | W_ListenRec_1_8 | ref  | idx_listenrec_userid | idx_listenrec_userid | 4       | const | 2028 | Using where; Using temporary |
  +----+-------------+-----------------+------+----------------------+----------------------+---------+-------+------+------------------------------+
  1 row in set (0.00 sec)
   
  mysql> show status where Variable_name like 'Handler_read%' and Value >0;
  +-----------------------+-------+
  | Variable_name         | Value |
  +-----------------------+-------+
  | Handler_read_key      | 1     |
  | Handler_read_next     | 2029  |
  | Handler_read_rnd_next | 41    |
  +-----------------------+-------+
  3 rows in set (0.00 sec)
  ```

  从step 2的拆解看的出来，经过group by的操作后，直接临时表中的结果读取出来



- step 3：见拆解前的sql

  最后的步骤是将临时表中的数据进行排序，然后按照顺序取出来。



## Tunning

应该怎么修改这个sql才能让他性能有比较大的提升呢？从explain和Handler_read_*的结果来看，我们使用了临时表，使用了临时排序，并且我们在where条件的使用过程中，没有将无用的数据全部过滤下去

step1：缩减无效数据的读取

step2：避免临时表的使用

step3：避免filesort

我们可用通过建立符合索引idx_listenrec_userid_courseid来实现避免无效数据的读取，同时也避免了因为group by courseguid造成的使用Using temporary。

分析一下这个sql，order by id desc的目的主要是为了获取最大的相同courseid下最大的starttime（显然这个语句达不到效果，O(∩_∩)O~），我们可以通过使用max(starttime) as starttime 来实现。如果我们真心相对听课时间有一个由近及远的排序，那么我建议放到程序里面去解决。

调整的步骤如下：

- 调整索引：

  alter table W_ListenRec_1_8 drop index idx_listenrec_userid;

  alter table W_ListenRec_1_8 add index idx_listenrec_userid_courseid(userid,courseguid);

- 修改sql：

  ```
  mysql> select courseguid,max(starttime) starttime 
  from W_ListenRec_1_8 ignore index (idx_listenrec_courseguid) where userid = 5627758   
  and courseguid in (
  's154717','s149496','s148373','s145703','s148741','s156269','s158955','s152551','s151599','s158902','s153671','s152798','s151181','s155451',
  's151756','s151402','s153248','s153966','s153557','s155208','s155585','s157355','s156112','s151285','s157049','s153517','s159406','s158813',
  's151427','s154241','s154526','s156264','s156322','s149377','s146878','s159755','s153898','s155122','s152520','s158579','s152861','s156550',
  's159462','s152663','s157787','s157234','s153156','s155318','s153168','s154418','s154136','s157160','s155635','s156219','s151667','s157779',
  's155611','s159115','s151519','s152790','s157161','s156305','s154779','s152635','s153482','s157332','s154576','s153692','s159822','s156165',  
  's151320','s152385','s156997','s158651','s152030','s152829','s153647','s158938','s155173','s158989','s156008','s156536','s155743','s153928',
  's155144','s159268','s156374','s154407','s153381','s151477','s159902','s152161','s159970','s151718','s151500','s154102','s151692','s153132',
  's158606','s153077','s157963','s157945','s152854','s159267','s153136','s152969','s152155','s154899','s141114','s148767','s158609','s156586',
  's154909','s152148','s156201','s156673','s158730','s158930','s152907','s145297','s149059','s158820','s159016')
  group by courseguid ;
  
  +----+-------------+-----------------+-------+-------------------------------+-------------------------------+---------+------+------+-------------+   
  | id | select_type | table           | type  | possible_keys                 | key                           | key_len | ref  | rows | Extra       |   
  +----+-------------+-----------------+-------+-------------------------------+-------------------------------+---------+------+------+-------------+   
  |  1 | SIMPLE      | W_ListenRec_1_8 | range | idx_listenrec_userid_courseid | idx_listenrec_userid_courseid | 102     | NULL | 1144 | Using where |   
  +----+-------------+-----------------+-------+-------------------------------+-------------------------------+---------+------+------+-------------+   
  1 row in set (0.01 sec)       
  
  mysql> show status where Variable_name like 'Handler_read%' and Value >0;
  
  +-------------------+-------+   
  | Variable_name     | Value |   
  +-------------------+-------+   
  | Handler_read_key  | 123   |   
  | Handler_read_next | 1061  |   
  +-------------------+-------+   
  2 rows in set (0.01 sec)  
  ```

  

- 有需要的话再程序中根据starttime进行降序处理





PS：

- 本文针对MySQL5.6版本，MySQL5.5可能略有不同，但原理没有变化，依然可以作为参考

- 本文测试均以engine=innodb进行测试，以其他存储引擎测试时会有些许变化.for example:engine =innodb是索引组织表，而engine=myisam时候是堆表

参考链接：

1）http://dev.mysql.com/doc/refman/5.6/en/server-status-variables.html

 

来自 <https://blog.csdn.net/slqgenius/article/details/71847898> 