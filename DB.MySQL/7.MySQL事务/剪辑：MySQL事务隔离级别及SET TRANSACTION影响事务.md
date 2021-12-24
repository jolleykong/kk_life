##                                                              3分钟搞懂MySQL事务隔离级别及SET TRANSACTION影响事务                

原创 巩飞   数据和云  4月17日

​                                    

**导读：**MySQL支持SQL:1992标准中的所有事务隔离级别，使用SET TRANSACTION来设置不同的事务隔离级别或访问模式，我们一起实战下它的效果。



我们都知道，MySQL的内置引擎中只有InnoDB、NDB支持事务，而又以InnoDB引擎对于事务的支持最全面也使用最广泛，所以本文的讨论都是基于InnoDB引擎，实验中用的表都是基于InnoDB的表。

| Feature      | MyISAM | Memory | InnoDB | Archive | NDB  |
| ------------ | ------ | ------ | ------ | ------- | ---- |
| Transactions | No     | No     | Yes    | No      | Yes  |



MySQL中可以使用SET TRANSACTION来影响事务特性，此语句可以指定一个或多个由逗号分隔的特征值列表，每个特征值设置事务隔离级别或访问模式。此语句在MySQL 5.7中的完整语法

```
SET [GLOBAL | SESSION] TRANSACTION    transaction_characteristic [, transaction_characteristic] ...
transaction_characteristic: {    ISOLATION LEVEL level  | access_mode}
level: {     REPEATABLE READ   | READ COMMITTED   | READ UNCOMMITTED   | SERIALIZABLE}
access_mode: {     READ WRITE   | READ ONLY}
```

``

语法很简单清晰，这里有几个关键概念需要理解清楚。



- **Transaction Isolation Levels（事务隔离级别）**


事务隔离是数据库的基础能力，ACID中的I指的就是事务隔离，通俗点讲就是多个用户并发访问数据库时，数据库为每一个用户开启的事务，不能被其他事务的操作数据所干扰，多个并发事务之间要相互隔离。

那么到底如何做才算是相互隔离呢？SQL:1992标准规定了四种事务隔离级别：READ UNCOMMITTED、READ COMMITTED、REPEATABLE READ和SERIALIZABLE。

InnoDB对四种隔离级别都支持，默认级别是REPEATABLE READ。



```
root@database-one 07:43:  [(none)]> select @@tx_isolation;+-----------------+| @@tx_isolation  |+-----------------+| REPEATABLE-READ |+-----------------+1 row in set (0.00 sec)
```

``

新建会话进行验证，会话的默认隔离级别确实REPEATABLE-READ。

InnoDB是靠不同的锁策略实现每个事务隔离级别，隔离级别越高付出的锁成本也就会越高。我们通过例子来看看不同级别的区别。



```
root@database-one 08:38:  [gftest]> create table testtx(name varchar(10),money decimal(10,2)) engine=innodb;Query OK, 0 rows affected (0.12 sec)
root@database-one 08:42:  [gftest]> insert into testtx values('A',6000),('B',8000),('C',9000);Query OK, 3 rows affected (0.00 sec)Records: 3  Duplicates: 0  Warnings: 0
root@database-one 08:43:  [gftest]> select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


上面创建了表testtx，并插入了3条数据，表示A有6000元，B有8000元，C有9000元。

> REPEATABLE READ，同一事务内的consistent reads读取由第一次读取建立的快照。这意味着，如果在同一事务中发出多个普通（非锁定）SELECT语句，则这些SELECT语句查到的数据保持一致。



创建会话1，关闭MySQL默认的事务自动提交模式（相关知识可以参考MySQL中的事务控制语句，地址：https://www.modb.pro/db/23348）。

```
root@database-one 08:58:  [(none)]> prompt \u@database-one \R:\m:\s [\d] session1>PROMPT set to '\u@database-one \R:\m:\s [\d] session1>'root@database-one 08:58:41 [(none)] session1>use gftest;Database changedroot@database-one 08:58:55 [gftest] session1>SET autocommit=0;Query OK, 0 rows affected (0.00 sec)
root@database-one 08:59:21 [gftest] session1>show variables like 'autocommit';+---------------+-------+| Variable_name | Value |+---------------+-------+| autocommit    | OFF   |+---------------+-------+1 row in set (0.02 sec)
root@database-one 08:59:36 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```



创建会话2，关闭MySQL默认的事务自动提交模式（相关知识可以参考MySQL中的事务控制语句，地址：https://www.modb.pro/db/23348）。

```
root@database-one 09:01:  [(none)]> prompt \u@database-one \R:\m:\s [\d] session2>PROMPT set to '\u@database-one \R:\m:\s [\d] session2>'root@database-one 09:02:13 [(none)] session2>use gftest;Database changedroot@database-one 09:02:24 [gftest] session2>SET autocommit=0;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:02:30 [gftest] session2>show variables like 'autocommit';+---------------+-------+| Variable_name | Value |+---------------+-------+| autocommit    | OFF   |+---------------+-------+1 row in set (0.00 sec)
root@database-one 09:02:37 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```



创建会话3，关闭MySQL默认的事务自动提交模式（相关知识可以参考MySQL中的事务控制语句，地址：https://www.modb.pro/db/23348）。


```
root@database-one 09:03:  [(none)]> prompt \u@database-one \R:\m:\s [\d] session3>PROMPT set to '\u@database-one \R:\m:\s [\d] session3>'root@database-one 09:03:44 [(none)] session3>use gftest;Database changedroot@database-one 09:03:47 [gftest] session3>SET autocommit=0;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:03:56 [gftest] session3>show variables like 'autocommit';+---------------+-------+| Variable_name | Value |+---------------+-------+| autocommit    | OFF   |+---------------+-------+1 row in set (0.01 sec)
root@database-one 09:04:04 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```



A给B转100元。在session1中模拟。


```
root@database-one 09:06:03 [gftest] session1>update testtx set money=money-100 where name='A';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 09:07:34 [gftest] session1>update testtx set money=money+100 where name='B';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 09:07:58 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


session1看到了金额进行了变化，但还未进行提交。

此时，分别去session2、session3进行查询。

```
root@database-one 09:02:45 [gftest] session2>root@database-one 09:12:23 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:04:10 [gftest] session3>root@database-one 09:14:12 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2、session3均未看到金额变化。

A对转账进行确认，即提交。


```
root@database-one 09:09:28 [gftest] session1>commit;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:18:03 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


此时，再分别去session2、session3进行查询。



```
root@database-one 09:12:28 [gftest] session2>root@database-one 09:18:15 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:14:22 [gftest] session3>root@database-one 09:18:24 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2、session3还未看到金额变化。因为他们还在自己的事务中（由自己session第一个select * from testtx即隐式开启了事务），根据REPEATABLE READ事务隔离的原则确实不应该看到。

当session2、session3结束当前事务后，再去查询就能看到变化了。



```
root@database-one 09:18:20 [gftest] session2>root@database-one 09:26:58 [gftest] session2>commit;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:27:05 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:18:26 [gftest] session3>root@database-one 09:27:17 [gftest] session3>rollback;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:27:24 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

> READ COMMITTED，即使在同一事务中，每个consistent read操作都设置并读取自己的新快照。



我们将数据还原，并调整三个会话的事务隔离级别均为READ UNCOMMITTED。



```
root@database-one 09:38:42 [gftest] session1>update testtx set money=6000 where name='A';Query OK, 0 rows affected (0.00 sec)Rows matched: 1  Changed: 0  Warnings: 0
root@database-one 09:39:20 [gftest] session1>update testtx set money=8000 where name='B';Query OK, 1 row affected (0.01 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 09:39:44 [gftest] session1>commit;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:39:49 [gftest] session1>SET SESSION TRANSACTION ISOLATION LEVEL read committed;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:40:33 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:41:31 [gftest] session2>SET SESSION TRANSACTION ISOLATION LEVEL read committed;Query OK, 0 rows affected (0.00 sec)
root@database-one 09:41:44 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:42:16 [gftest] session3>SET SESSION TRANSACTION ISOLATION LEVEL read committed;Query OK, 0 rows affected (0.01 sec)
root@database-one 09:42:24 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

A给B转100元。在session1中模拟。


```
root@database-one 09:40:42 [gftest] session1>update testtx set money=money-100 where name='A';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 09:44:10 [gftest] session1>update testtx set money=money+100 where name='B';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 09:44:20 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


session1看到了金额进行了变化，但还未进行提交。

此时，分别去session2、session3进行查询。



```
root@database-one 09:42:28 [gftest] session3>root@database-one 09:47:15 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:42:28 [gftest] session3>root@database-one 09:47:15 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2、session3均未看到金额变化。

A对转账进行确认，即提交。


```
root@database-one 09:50:37 [gftest] session1>commit;Query OK, 0 rows affected (0.03 sec)
root@database-one 09:50:43 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```



此时，再分别去session2、session3视角进行查询。


```
root@database-one 09:48:02 [gftest] session2>root@database-one 09:52:18 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 09:48:18 [gftest] session3>root@database-one 09:53:11 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2、session3均看到金额变化。因为他们虽然还在自己的事务中（由自己session第一个select * from testtx即隐式开启了事务），根据READ COMMITTED事务隔离的原则应该看到。

> READ UNCOMMITTED，SELECT语句是以非锁定方式执行的，但可能会使用数据的早期版本，这样的读取是不一致的，因此也被称为脏读。



我们将数据还原，并调整三个会话的事务隔离级别均为READ COMMITTED。


```
root@database-one 10:02:49 [gftest] session1>update testtx set money=6000 where name='A';Query OK, 1 row affected (0.01 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 10:03:10 [gftest] session1>update testtx set money=8000 where name='B';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 10:03:20 [gftest] session1>commit;Query OK, 0 rows affected (0.00 sec)
root@database-one 10:03:30 [gftest] session1>SET SESSION TRANSACTION ISOLATION LEVEL read uncommitted;Query OK, 0 rows affected (0.00 sec)
root@database-one 10:03:49 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 10:02:52 [gftest] session2>SET SESSION TRANSACTION ISOLATION LEVEL read uncommitted;Query OK, 0 rows affected (0.00 sec)
root@database-one 10:04:58 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 10:05:35 [gftest] session3>SET SESSION TRANSACTION ISOLATION LEVEL read uncommitted;Query OK, 0 rows affected (0.00 sec)
root@database-one 10:05:37 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

A给B转100元。在session1中模拟。


```
root@database-one 10:06:43 [gftest] session1>update testtx set money=money-100 where name='A';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 10:06:47 [gftest] session1>update testtx set money=money+100 where name='B';Query OK, 1 row affected (0.00 sec)Rows matched: 1  Changed: 1  Warnings: 0
root@database-one 10:06:57 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


session1看到了金额进行了变化，但还未进行提交。

此时，分别去session2、session3进行查询。


```
root@database-one 10:05:07 [gftest] session2>root@database-one 10:08:34 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 10:06:02 [gftest] session3>root@database-one 10:08:42 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2看到金额变化，session3未看到金额变化。因为他们虽然还在自己的事务中（由自己session第一个select *  from testtx即隐式开启了事务），根据READ  UNCOMMITTED事务隔离的原则，session3没有看到金额变化是因为使用了数据的早期版本。这里需要特别注意，有时可能是session2会看到金额变化、有时可能是session3会看到金额变化、有时可能是session2和session3都会看到金额变化、有时可能是session2和session3都不会看到金额变化，这个是由MySQL根据数据的版本情况即时确定的。

A对转账进行确认，即提交。


```
root@database-one 10:35:52 [gftest] session1>commit;Query OK, 0 rows affected (0.01 sec)
root@database-one 10:36:01 [gftest] session1>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
```


此时，再分别去session2、session3视角进行查询。


```
root@database-one 10:09:24 [gftest] session2>root@database-one 11:09:45 [gftest] session2>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 11:08:29 [gftest] session3>root@database-one 11:11:54 [gftest] session3>select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 5900.00 || B    | 8100.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)

```

session2、session3均看到金额变化。



SERIALIZABLE，这个级别类似于REPEATABLE  READ，但更严格。在非自动提交模式下，InnoDB隐式地将所有SELECT语句转换为SELECT … LOCK IN SHARE  MODE。在自动提交模式下，SELECT在自己的事务里，以事务的原则运行。



因为效果和REPEATABLE READ类似，我这里就不再演示了，有兴趣的同学可以自己验证。SERIALIZABLE执行的规则比REPEATABLE READ更为严格，主要用于特殊情况，如XA事务、解决并发和死锁问题等场景。



- **Transaction Access Mode（事务访问模式）**


事务的访问模式很容易理解，就是指在事务中如何对表中的数据进行使用，分为READ WRITE和READ ONLY，默认是READ WRITE。

还是testtx这张表，我们开启一个READ ONLY事务，对其中的数据进行修改，看看会发生什么。


```
root@database-one 11:56:  [gftest]> select @@tx_isolation,@@autocommit;+-----------------+--------------+| @@tx_isolation  | @@autocommit |+-----------------+--------------+| REPEATABLE-READ |            1 |+-----------------+--------------+1 row in set (0.00 sec)
root@database-one 11:57:  [gftest]> SET SESSION TRANSACTION read only;Query OK, 0 rows affected (0.00 sec)
root@database-one 11:57:  [gftest]> start transaction;Query OK, 0 rows affected (0.00 sec)
root@database-one 11:59:  [gftest]> select * from testtx;+------+---------+| name | money   |+------+---------+| A    | 6000.00 || B    | 8000.00 || C    | 9000.00 |+------+---------+3 rows in set (0.00 sec)
root@database-one 11:59:  [gftest]> update testtx set money=0 where name='A';ERROR 1792 (25006): Cannot execute statement in a READ ONLY transaction.
```


可以看到，READ ONLY模式的事务修改数据时会报错。

- **Transaction Characteristic Scope（事务属性的作用范围）**


细心的同学可能已经注意到，在SET TRANSACTION时有可选关键字GLOBAL和SESSION，它们决定了事务属性的作用范围。

- 使用GLOBAL时，该语句影响所有后续会话，现有会话不受影响。
- 使用SESSION时，该语句影响当前会话中的所有后续事务。
- 不使用GLOBAL或SESSION时，该语句仅影响会话中执行的下一个事务。



墨天轮原文链接：https://www.modb.pro/db/23447（复制到浏览器中打开或者点击“阅读原文”）



推荐阅读：[144页！分享珍藏已久的数据库技术年刊](http://mp.weixin.qq.com/s?__biz=MjM5MDAxOTk2MQ==&mid=2650283781&idx=1&sn=dbad144136abc2f90df72675f30d4b5b&chksm=be47871389300e05026659e899e323119e375b95dd3b71a89a4ddd1b02c506b20bd1b7d7dd70&scene=21#wechat_redirect)