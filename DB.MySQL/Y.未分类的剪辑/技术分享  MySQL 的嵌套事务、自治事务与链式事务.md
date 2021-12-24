## 技术分享 | MySQL 的嵌套事务、自治事务与链式事务 

以下文章来源于爱可生开源社区 ，作者杨涛涛 

 

[**爱可生开源社区** ](http://)

[爱可生开源社区，提供稳定的MySQL企业级开源工具及服务，每年1024开源一款优良组件，并持续运营维护。](http://)

这篇文章有感于最近支持某客户从 Oracle 迁移到 MySQL 过程中的启示。接下来我们**详细说明 MySQL 中的事务种类。
 分类**1. 普通事务以 begin / start transaction 开始，commit / rollback 结束的事务。或者是带有保存点 savepoint 的事务。

\2. 链式事务

一个事务在提交的时候自动将上下文传给下一个事务，也就是说一个事务的提交和下一个事务的开始是原子性的，下一个事务可以看到上一个事务的处理结果。MySQL 的链式事务靠参数 completion_type 控制，并且回滚和提交的语句后面加上 work 关键词。

\3. 嵌套事务

有多个 begin / commit / rollback 这样的事务块的事务，并且有父子关系。子事务的提交完成后不会真的提交，而是等到父事务提交才真正的提交。

\4. 自治事务

内部事务的提交不随外部事务的影响，一般用作记录内部事务的异常情况。MySQL 不支持自治事务，但是某些场景可以用 MySQL 的插件式引擎来变相实现。接下来，我们每种事务用详细例子来说明。
 实例**1. 普通事务**下表 c1，开始一个事务块，有两个保存点 s1 & s2。我们回滚了 s2 之后的所有操作，并且提交了 s2 之前的所有操作，此时 s1 & s2 已经失效。那记录数刚好两条。

{"db":"ytt"},"port":"3320"}-mysql>truncate c1;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>

{"db":"ytt"},"port":"3320"}-mysql>

{"db":"ytt"},"port":"3320"}-mysql>use ytt

Database changed

{"db":"ytt"},"port":"3320"}-mysql>begin;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (1,20,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>savepoint s1;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (2,30,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>savepoint s2;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (3,40,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>rollback to savepoint s2;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>commit;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>select * from c1;

+----+------+---------------------+

| id | c1  | c2         |

+----+------+---------------------+

| 1 |  20 | 2019-12-02 10:07:02 |

| 2 |  30 | 2019-12-02 10:07:12 |

+----+------+---------------------+

2 rows in set (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>

**2. 链式事务**

设置 completion_type=1，也就是开启了链式事务特征。下面例子，commit work 后的语句是一个隐式事务语句。也就是说语句 rollback 语句执行后，默认的话，sql 2 肯定已经提交了。但是由于继承了上下文，也就是语句 sql 2变为 begin;SQL2;　那此时 sql 2 和 rollback 语句其实是一个事务块儿了。最终结果就是只有两条记录。

{"db":"ytt"},"port":"3320"}-mysql>truncate table c1;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>set completion_type=1;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (4,50,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (5,60,now());

Query OK, 1 row affected (0.00 sec)


 

-- sql 1

{"db":"ytt"},"port":"3320"}-mysql>commit work;

Query OK, 0 rows affected (0.00 sec)


 

-- sql 2

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (6,70,now());

Query OK, 1 row affected (0.00 sec)


 

-- sql 3

{"db":"ytt"},"port":"3320"}-mysql>rollback;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>select * from c1;

+----+------+---------------------+

| id | c1  | c2         |

+----+------+---------------------+

| 4 |  50 | 2019-12-02 10:14:16 |

| 5 |  60 | 2019-12-02 10:14:31 |

+----+------+---------------------+

2 rows in set (0.00 sec)

**3. 嵌套事务**

其实严格意义上来说，MySQL 是不支持嵌套事务的。MySQL 的每个事务块的开始默认的会提交掉之前的事务。比如下面的例子，第二个 begin 语句默认会变为 commit;begin; 那之后的 rollback 其实只回滚了一条记录。最终记录数为 ID=7 这条。

{"db":"ytt"},"port":"3320"}-mysql>truncate table c1;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>begin;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (7,80,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>begin;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>insert into c1 values (8,90,now());

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>rollback;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3320"}-mysql>select * from c1;

+----+------+---------------------+

| id | c1  | c2         |

+----+------+---------------------+

| 7 |  80 | 2019-12-02 10:24:44 |

+----+------+---------------------+

1 row in set (0.00 sec)

**4. 自治事务**

其实 MySQL 本来不支持自治事务，但是基于 MySQL 先天的可插拔架构来说，也可以变相的实现自治事务。比如可以把记录日志的表变为非事务引擎表，比如 MyISAM。

{"db":"(none)"},"port":"3326"}-mysql>use ytt

Database changed

{"db":"ytt"},"port":"3326"}-mysql>create table log(err_msg varchar(200))engine myisam;

Query OK, 0 rows affected (0.01 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>begin;

Query OK, 0 rows affected (0.00 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>insert into t1 values (100);

Query OK, 1 row affected (0.01 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>insert into log values ('这个记录不应该插入进来');

Query OK, 1 row affected (0.00 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>select * from t1;

+------+

| id  |

+------+

| 100 |

+------+

1 row in set (0.00 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>rollback;

Query OK, 0 rows affected, 1 warning (0.00 sec)


 

{"db":"ytt"},"port":"3326"}-mysql>select * from log;

+-----------------------------------+

| err_msg              |

+-----------------------------------+

| 这个记录不应该插入进来      |

+-----------------------------------+

1 row in set (0.00 sec)


 

**总结**

本篇内容主要把 MySQL 的事务类别简单介绍了下，针对了日常使用的几种场景做了简单的 SQL 演示，希望对大家有帮助。


 


 [](http://mp.weixin.qq.com/s?__biz=MzI1OTU2MDA4NQ==&mid=2247490678&idx=1&sn=037bc0b63b936320a9877f3167cfa724&chksm=ea765b8cdd01d29abd26a0072671897653a5b1e400a6fbfd1c5c31f4cc6e8903f18ddc9840ed&mpshare=1&scene=1&srcid=&sharer_sharetime=1580772708745&sharer_shareid=4ccc32335c079a86eae33281fea18c34#rd)