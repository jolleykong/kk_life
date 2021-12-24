从MySQL 5.6.5 开始新增了一种基于 GTID 的复制方式。通过 GTID 保证了每个在主库上提交的事务在集群中有一个唯一的ID。这种方式强化了数据库的主备一致性，故障恢复以及容错能力。

GTID (Global Transaction  ID)是全局事务ID,当在主库上提交事务或者被从库应用时，可以定位和追踪每一个事务，对DBA来说意义就很大了，我们可以适当的解放出来，不用手工去可以找偏移量的值了，而是通过CHANGE MASTER TO MASTER_HOST='xxx',  MASTER_AUTO_POSITION=1的即可方便的搭建从库，在故障修复中也可以采用MASTER_AUTO_POSITION=‘X’的方式。

可能大多数人第一次听到GTID的时候会感觉有些突兀，但是从架构设计的角度，GTID是一种很好的分布式ID实践方式，通常来说，分布式ID有两个基本要求：

1）全局唯一性

2）趋势递增

这个ID因为是全局唯一，所以在分布式环境中很容易识别，因为趋势递增，所以ID是具有相应的趋势规律，在必要的时候方便进行顺序提取，行业内适用较多的是基于Twitter的ID生成算法snowflake,所以换一个角度来理解GTID，其实是一种优雅的分布式设计。

1。如何开启GTID

如何开启GTID呢，我们先来说下基础的内容，然后逐步深入，通常来说，需要在my.cnf中配置如下的几个参数：

①log-bin=mysql-bin

②binlog_format=row

③log_slave_updates=1

④gtid_mode=ON

⑤enforce_gtid_consistency=ON

其中参数log_slave_updates在5.7中不是强制选项，其中最重要的原因在于5.7在mysql库下引入了新的表gtid_executed。

在开始介绍GTID之前，我们换一种思路，通常我们都会说一种技术和特性能干什么，我们了解一个事物的时候更需要知道边界，那么GTID有什么限制呢，这些限制有什么解决方案呢，我们来看一下。

2。 GTID的限制和解决方案

如果说GTID在5.6试水，在5.7已经发展完善，但是还是有一些场景是受限的。比如下面的两个。

一个是create table xxx as select 的模式；另外一个是临时表相关的,我们就来简单说说这两个场景。

1）create 语句限制和解法

create table xxx as select的语句，其实会被拆分为两部分，create语句和insert语句，但是如果想一次搞定，MySQL会抛出如下的错误。

mysql> create table test_new as select *from test;

ERROR 1786 (HY000): Statement violates GTID consistency: CREATE TABLE ... SELECT.

这种语句其实目标明确，复制表结构，复制数据，insert的部分好解决，难点就在于create table的部分，如果一个表的列有100个，那么拼出这么一个语句来就是一个工程了。

除了规规矩矩的拼出建表语句之外，还有一个方法是MySQL特有的用法 like。

create table xxx as select 的方式可以拆分成两部分，如下。

create table xxxx like data_mgr;

insert into xxxx select *from data_mgr;

2）临时表的限制和建议

使用GTID复制模式时，不支持create temporary table 和 drop temporary  table。但是在autocommit=1的情况下可以创建临时表，Master端创建临时表不产生GTID信息，所以不会同步到slave，但是在删除临时表的时候会产生GTID会导致，主从中断.

3。 从三个视角看待GTID

前面聊了不少GTID的内容，我们来看看GTID的一个体系内容，如下是我梳理的一个GTID的概览信息，分别从变量视图，表和文件视图，操作视图来看待GTID.

[![搞懂MySQL GTID原理](3e3283c4e9c0496fa6a9a96ca48eec24)](http://p9.pstatp.com/large/pgc-image/3e3283c4e9c0496fa6a9a96ca48eec24)

 

我们分别从每个视图来简单说下：

1）变量视图

我们来用下面的表格来阐述下常见的这几个变量

[![搞懂MySQL GTID原理](5aa635ef076d4220ab2f0577d2e9784c)](http://p1.pstatp.com/large/pgc-image/5aa635ef076d4220ab2f0577d2e9784c)

 

2）表和文件视图

先来说下文件层面的关联，根据MySQL的复制原理，MySQL Server在写binlog的时候，会先写一个特殊的Binlog  Event，类型为GTID_Event，指定下一个事务的GTID，然后再写事务的Binlog，主从同步时GTID_Event和事务的Binlog都会传递到从库，在从库应用Relay Log,从库在执行的时候也是用同样的GTID写binlog.

然后说一下表mysql.gtid_executed,在5.6版本中必须要设置log_slave_updates,因为当slave重启后，无法得知当前slave已经运行到的GTID位置，因为变量gtid_executed是一个内存值，而这个问题在5.7中通过表mysql.gtid_executed把这个值持久化来得以解决，也就意味着log_slave_updates是一个可选项。

此外，引入该解决方案之后又带来了新的问题，那就是在gtid_executed里面的数据会越来越多，如何精简管理呢，MySQL引入了一个新的线程和参数来进行管理。

线程为：thread/sql/compress_gtid_table，可以查询performance_schema.threads来查看。

参数为 gtid_executed_compression_period ，主要用于控制每执行多少个事务，对表gtid_executed进行压缩，默认值为：1000 。

3）操作视图

对于操作，我们列举了较为简单常规的操作方式，为了避免歧义，我对一些命令做了取舍。

这些主要是在搭建主从复制关系时所用，基本都是一次开启，长期生效的方式。

如果是修复主从复制中的异常，如果是在确认错误可以跳过的情况下，可以使用如下的方式:

l stop slave；

l set gtid_next='xxxxxxx:N'; --指定下一个事务执行的版本，即想要跳过的GTID

l begin;

l commit; --注入一个空事物

l set gtid_next='AUTOMATIC' --自动的寻找GTID事务。

l start slave; --开始同步