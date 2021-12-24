MySQL Group Replication冲突检测机制再剖析

 

《[MySQL MGR事务认证机制优化](https://zhuanlan.zhihu.com/p/41175310)》一文对MySQL Group Replication（MGR）的事务认证/冲突检测机制实现进行了介绍，并分析了其潜在的问题。本文将从certification_info对象，即冲突检测数据库实现作为切入点，来重点分析certification_info里面保存了什么东西，有什么用，如何对其进行管理，最后结合具体业务场景分析冲突检测机制存在的不足并提供可能的优化建议。

certification_info中有什么

/**   Certification database.  */  
 Certification_info certification_info;

从注释看，它是冲突检测数据库。再进一步看下Certification_info的定义

/**
  This class is a core component of the database state machine
  replication protocol. It implements conflict detection based
  on a certification procedure.

Snapshot Isolation is based on assigning logical timestamp to optimistic
  transactions, i.e. the ones which successfully meet certification and
  are good to commit on all members in the group. This timestamp is a
  monotonically increasing counter, and is same across all members in the group.

This timestamp, which in our algorithm is the snapshot version, is further
  used to update the certification info.
  The snapshot version maps the items in a transaction to the GTID_EXECUTED
  that this transaction saw when it was executed, that is, on which version
  the transaction was executed.

If the incoming transaction snapshot version is a subset of a
  previous certified transaction for the same write set, the current
  transaction was executed on top of outdated data, so it will be
  negatively certified. Otherwise, this transaction is marked
  certified and goes into applier.
 */
 typedef std::map<std::string, Gtid_set_ref*> Certification_info;

意思是说，MGR通过一个事务认证过程来实现冲突检测，而Certification_info是MGR复制状态机的核心组件。在MGR中，每个节点上的事务都是乐观执行的，在最终进行提交前，会通过paxos协议发送到MGR中的每个节点，随事务writeset一起发送的数据包还包括事务执行时执行节点的gtid_executed信息，该信息即为事务的快照版本。在进行事务认证时，会对比事务携带的gtid_executed和certification_info里面对应的gtid_set，如果前者是后者的真子集，那么意味着该事务操作的是旧的数据，或者说，该事务执行时，MGR的其他节点已经对事务操作的数据进行了更改，且已经先于该事务被MGR集群所接受。如果未能在certification_info中找到对应的gtid_set或者gtid_set是事务携带的gtid_executed的子集，意味着事务认证通过，可以在执行节点提交，在其他节点回放。

 

certification_info里有什么

从Certification_info定义可看出，他是一个C++的标准map，将一个字符串映射到一个Gtid_set_ref上：

/**
  This class extends Gtid_set to include a reference counter.

It is for Certifier only, so it is single-threaded and no locks
  are needed since Certifier already ensures sequential use.

It is to be used to share by multiple entries in the
  certification info and released when the last reference to it
  needs to be freed.
 */
 class Gtid_set_ref: public Gtid_set
 {
 public:
  Gtid_set_ref(Sid_map *sid_map, int64 parallel_applier_sequence_number)
   :Gtid_set(sid_map), reference_counter(0),
   parallel_applier_sequence_number(parallel_applier_sequence_number)
  {}

Gtid_set_ref是Gtid_set的超集，包括了引用计数reference_counter和parallel_applier_sequence_number。从名字看parallel_applier_sequence_number就不难猜测，其跟事务并行回放相关，进一步来说，就是基于它可以确定事务并行复制二元组（last_commited, sequence_number）中的sequence_number，具体逻辑稍后分析。

 

事务的writeset

简单了解了Gtid_set_ref后，再分析Certification_info中std::string这个字符串的含义，其来源就是事务提交时用于进行冲突检测的writeset，即事务DML操作更改的记录信息。那么如何定义事务DML操作并正确进行冲突检测呢，是不是获取记录的主键信息就可以了。下面结合实验结果进行分析。

先定义tprimary是包含2个列，一个主键的表：

node1-citest>create table tprimary (a int primary key, b int);
 Query OK, 0 rows affected (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

通过查看performance_schema.replication_group_member_stats的COUNT_TRANSACTIONS_ROWS_VALIDATING列可以知道当前certification_info里面有多少条记录。显然，由于建表语句是DDL，并没有writeset，所以显示为0；

接着插入一条新记录：

node1-citest>insert into tprimary values (1,1);
 Query OK, 1 row affected (0.01 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 2
 1 row in set (0.00 sec)

可以看到，COUNT_TRANSACTIONS_ROWS_VALIDATING变为2；

然后分别更新该记录的非索引列和索引列：

node1-citest>update tprimary set b=2 where a=1;
 Query OK, 1 row affected (0.01 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 2
 1 row in set (0.00 sec)

node1-citest>update tprimary set a=2 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 4
 1 row in set (0.00 sec)

可以看到，更新非索引列的时候，COUNT_TRANSACTIONS_ROWS_VALIDATING保持不变，而更新主键列的时候COUNT_TRANSACTIONS_ROWS_VALIDATING增加了一倍变为4；

最后删除该记录：

node1-citest>delete from tprimary where a=2;
 Query OK, 1 row affected (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 4
 1 row in set (0.00 sec)

可能看了上面一轮insert，update和delete，本来有点了解的同学反而迷惑了。不符合预期啊。为什么insert会产生2个writeset，update非索引列writeset没有增加，update主键增加了一倍，insert也没有增加。这怎么解释？为了排除历史操作影响，接下来的操作在update和delete前，都先通过重启等方式确保操作前COUNT_TRANSACTIONS_ROWS_VALIDATING为0。

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>update tprimary set b=2 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 2
 1 row in set (0.00 sec)

可以看到，update非索引列，writeset跟insert一样，也是2。

node1-citest>update tprimary set a=2 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 4
 1 row in set (0.00 sec)

update主键列，writeset会变为4。

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>delete from tprimary where a=2;
 Query OK, 1 row affected (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 2
 1 row in set (0.00 sec)

delete的时候，也是产生了2个writeset。

基于上面，可以做个简单总结，在只有主键的情况下，insert，delete和非主键update产生的writeset数是操作记录数的2倍。如果更新了主键，那么writeset是记录数的4倍，可以认为update主键时，update前后的主键都会产生writeset。从binlog_log_row函数可以得到证明：

int binlog_log_row(TABLE* table,
              const uchar *before_record,
              const uchar *after_record,
              Log_func *log_func)
 {
  bool error= 0;
  THD *const thd= table->in_use;

if (check_table_binlog_row_based(thd, table))
  {
   if (thd->variables.transaction_write_set_extraction != HASH_ALGORITHM_OFF)
   {
    if (before_record && after_record)
    {
     size_t length= table->s->reclength;
     uchar* temp_image=(uchar*) my_malloc(PSI_NOT_INSTRUMENTED,
                       length,
                       MYF(MY_WME));
     if (!temp_image)
     {
      sql_print_error("Out of memory on transaction write set extraction");
      return 1;
     }
     add_pke(table, thd);

memcpy(temp_image, table->record[0],(size_t) table->s->reclength);
     memcpy(table->record[0],table->record[1],(size_t) table->s->reclength);

add_pke(table, thd);

memcpy(table->record[0], temp_image, (size_t) table->s->reclength);

my_free(temp_image);
    }
    else
    {
     add_pke(table, thd);
    }
   }

由于更新非主键列的场景，由于writeset仅提取唯一确定该记录的字段，所以前后记录产生的writeset是一样的，其实等同于一条。

现在唯一说不通的是为什么都翻倍。这个时候就只能看代码了，在add_pke函数中，我们看到这么一句注释：

/*
     To handle both members having hash values with and without collation
     in the same group, we generate and send both versions (with and without
     collation) of the hash in the newer versions. This would mean that a row
     change will generate 2 instead of 1 writeset, and 4 instead of 2, when PK
     are involved. This will mean that a transaction will be certified against
     two writesets instead of just one.

To generate both versions (with and without collation) of the hash, it
     first converts using without collation support algorithm (old algorithm),
     and then using with collation support conversion algorithm, and adds
     generated value to key_list_to_hash vector, for hash generation later.

Since the collation writeset is bigger or equal than the raw one, we do
     generate first the collation and reuse the buffer without the need to
     resize for the raw.
    */

应该说，这个注释解释得很清楚了，对于每条记录，都会产生带校对和不带校对（with and without collation）2个版本的writeset。至于为什么需要2个版本，这是历史原因了，在MGR早期版本，产生writeset哈希值的算法是不管该字段的校对规则的，但后来发现有bug（[86078](https://link.zhihu.com/?target=https%3A//bugs.mysql.com/bug.php%3Fid%3D86078)、[88120](https://link.zhihu.com/?target=https%3A//bugs.mysql.com/bug.php%3Fid%3D88120)），所以就改为带校对规则的哈希产生算法。为了兼容早期版本，于是后续版本就为一条记录都产生前后2个版本。

 

writeset与索引对应关系

再来看看二级索引对writeset的影响。

node1-citest>show create table tuniq;
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 | Table | Create Table                                                                                           |
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 | tuniq | CREATE TABLE `tuniq` (
  `a` int(11) NOT NULL,
  `b` int(11) DEFAULT NULL,
  `c` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`a`),
  UNIQUE KEY `b_u` (`b`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 |
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 1 row in set (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.01 sec)

node1-citest>insert into tuniq values(1,2,'3');
 Query OK, 1 row affected (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 4
 1 row in set (0.00 sec)

上面是唯一索引

node1-citest>show create table tsec;
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 | Table | Create Table                                                                                        |
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 | tsec | CREATE TABLE `tsec` (
  `a` int(11) NOT NULL,
  `b` int(11) DEFAULT NULL,
  `c` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`a`),
  KEY `b_sec` (`b`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 |
 +-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 1 row in set (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>insert into tsec values(1,2,'3');
 Query OK, 1 row affected (0.01 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 2
 1 row in set (0.00 sec)

上面是普通二级索引

显然，唯一索引会产生writeset，而普通的二级索引不会有writeset。通过add_pke函数中的注释也能够进一步确认。

/*
   The next section extracts the primary key equivalent of the rows that are
   changing during the current transaction.

\1. The primary key field is always stored in the key_part[0] so we can simply
    read the value from the table->s->keys.

\2. Along with primary key we also need to extract the unique key values to
    look for the places where we are breaking the unique key constraints.

These keys (primary/unique) are prefixed with their index names.

In MySQL, the name of a PRIMARY KEY is PRIMARY. For other indexes, if
   you do not assign a name, the index is assigned the same name as the
   first indexed column, with an optional suffix (_2, _3, ...) to make it
   unique.

example :
    CREATE TABLE db1.t1 (i INT NOT NULL PRIMARY KEY, j INT UNIQUE KEY, k INT
               UNIQUE KEY);

INSERT INTO db1.t1 VALUES(1, 2, 3);

Here the write set string will have three values and the prepared value before
    hash function is used will be :

i -> PRIMARYdb13t1211 => PRIMARY is the index name (for primary key)

j -> jdb13t1221    => 'j' is the index name (for first unique key)
    k -> kdb13t1231    => 'k' is the index name (for second unique key)

Finally these value are hashed using the murmur hash function to prevent sending more
   for certification algorithm.
  */

该注释除了说明primary和unique索引会产生writeset，还进一步解释了每个writeset包含了哪几部分：索引名称+db名+db名长度+表名+表名长度+构成索引唯一性的每个列的值+值长度，将其进行XXHASH64哈希后，才是最终呈现在certification_info对象std::string上的字符串。

进一步，对于update场景，规律应该是这样的，如果更新了主键列或唯一索引列，那么会产生更新前后2个版本不同的writeset。

node1-citest>select * from tuniq;
 +---+------+------+
 | a | b  | c  |
 +---+------+------+
 | 1 |  2 | 3  |
 +---+------+------+
 1 row in set (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>update tuniq set c=4 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 4

上面为未更新唯一键的场景。主键和唯一索引分别产生2条writeset。

node1-citest>select * from tuniq;
 +---+------+------+
 | a | b  | c  |
 +---+------+------+
 | 1 |  2 | 4  |
 +---+------+------+
 1 row in set (0.01 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>update tuniq set b=3 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 6
 1 row in set (0.00 sec)

上面为更新唯一键的场景。主键产生2条writeset，唯一索引产生4条writeset。

node1-citest>select * from tuniq;
 +---+------+------+
 | a | b  | c  |
 +---+------+------+
 | 1 |  3 | 4  |
 +---+------+------+
 1 row in set (0.00 sec)

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 0
 1 row in set (0.00 sec)

node1-citest>update tuniq set a=2, b=4 where a=1;
 Query OK, 1 row affected (0.00 sec)
 Rows matched: 1 Changed: 1 Warnings: 0

node1-citest>select COUNT_TRANSACTIONS_ROWS_VALIDATING from performance_schema.replication_group_member_stats\G
 *************************** 1. row ***************************
 COUNT_TRANSACTIONS_ROWS_VALIDATING: 8
 1 row in set (0.00 sec)

上面为同时更新了主键和唯一键的场景，分别产生了4条writeset。

除了唯一索引外，如果表中存在外键约束，也需要将该外键值加入到writeset中，确保外键约束未被破坏。在此不再一一举例。

显然，分别基于记录的主键索引、各个唯一索引和外键约束产生各自的writeset是必要的，因为三者的冲突检测都是独立的，主键索引的writeset无法检测出是否违反了唯一索引约束，同样的，主键和唯一索引也无法替代外键约束这样的跨表一致性限制，在此也不一一举例说明。

综上所述，对于事务中每个DML操作，不考虑外键时，产生的writeset个数如下：

insert和delete操作：（x）* 2；

update操作：（x+y）* 2 ；

其中x为唯一索引总数（包括主键），y为被update的唯一索引数（包括主键）。

 

事务认证过程简述

（本文对认证过程仅做简单描述，更详细的过程请参考本文开始时提供的链接）

在上述基础上，事务就能够进行认证了：提取该事务哈希后的writeset，逐一到certification_info对象中取相同哈希值的kv键值对，如果没有取到，说明没有冲突。如果取到，则对比gtid_set来确定事务是提交还是回滚。

for (std::list<const char*>::iterator it= write_set->begin();
     it != write_set->end();
     ++it)
   {
    Gtid_set *certified_write_set_snapshot_version=
      get_certified_write_set_snapshot_version(*it);
      
    /*
     If the previous certified transaction snapshot version is not
     a subset of the incoming transaction snapshot version, the current
     transaction was executed on top of outdated data, so it will be
     negatively certified. Otherwise, this transaction is marked
     certified and goes into applier.
    */
    if (certified_write_set_snapshot_version != NULL &&
      !certified_write_set_snapshot_version->is_subset(snapshot_version))
    {
     goto end;
    }
   }

如果该事务认证通过，那么其携带的writeset会加入到certification_info中。

for(std::list<const char*>::iterator it= write_set->begin();
     it != write_set->end();
     ++it)
   {
    int64 item_previous_sequence_number= -1;

add_item(*it, snapshot_version_value,
        &item_previous_sequence_number);

/*
     Exclude previous sequence number that are smaller than global
     last committed and that are the current sequence number.
     transaction_last_committed is initialized with
     parallel_applier_last_committed_global on the beginning of
     this method.
    */
    if (item_previous_sequence_number > transaction_last_committed &&
      item_previous_sequence_number != parallel_applier_sequence_number)
     transaction_last_committed= item_previous_sequence_number;
   }

 

事务认证与并行回放行为

调用add_item加入writeset后，会返回item_previous_sequence_number，表示DML了该记录的前一个事务其组提交信息中的sequence_number值，由于操作了相同的记录意味着两个事务存在冲突，所以本事务一定要在前一个事务回放后才能进行回放，即需要将本事务的last_commited设置为item_previous_sequence_number。至于本事务的sequence_number，则MGR会维护一个全局的parallel_applier_sequence_number，每个认证通过的事务都赋予该值后，该值增一。也就是说，MGR在完成非本地事务冲突检测/认证的同时，将事务(last_commited，sequence_number)这组用于并行复制的组提交信息也确定了。所以，certification_info并不仅仅用于冲突检测，还是基于writeset的并行复制机制的关键组成部分，在MGR单主模式下也是不可或缺的。

此外，在冲突检测通过后，会为事务分配全局唯一的gtid，MGR各个节点对统一事务分配的gtid都是一样。这也是MGR进行事务冲突检测的基础。具体之前的文章。

 

writeset垃圾清理

既然writeset会不断加入到certification_info中，就应该有配套的writeset清理线程。那么什么时候writeset才能从certification_info清理出去呢，显然，如果某个事务已经在MGR所有节点都执行/回放了。那么其writeset信息肯定没有用了，因为这些writeset对于后续开始执行的事务来说肯定是可见的。所以，在MGR中，每个节点会每隔一段时间广播自己的gtid_executed信息。

// Broadcast gtid_executed and stable_gtid_set
   if (broadcast_counter % broadcast_gtid_executed_period_var == 0)
   {
    applier_module->get_pipeline_stats_member_collector()->set_send_transaction_identifiers();
    broadcast_gtid_executed();
   }

在MySQL社区版中broadcast_gtid_executed_period_var硬编码为60s。每个节点收集到所有节点的gtid_executed信息后，取交集。

/*
      We have three sets:
       member_set:     the one sent from a given member;
       executed_set:    the one that contains the intersection of
                 the computed sets until now;
       intersection_result: the intersection between set and
                 intersection_result.
      So we compute the intersection between set and executed_set, and
      set that value to executed_set to be used on the next intersection.
     */
     if (member_set.intersection(&executed_set, &intersection_result) != RETURN_STATUS_OK)
     {
      log_message(MY_ERROR_LEVEL, "Error processing intersection of stable transactions set"); /* purecov: inspected */
      error= 1; /* purecov: inspected */
     }
     else
     {
      executed_set.clear();
      if (executed_set.add_gtid_set(&intersection_result) != RETURN_STATUS_OK)
      {
       log_message(MY_ERROR_LEVEL, "Error processing stable transactions set"); /* purecov: inspected */
       error= 1; /* purecov: inspected */
      }
     }
    }
   }

delete packet;
  }

if (!error && set_group_stable_transactions_set(&executed_set))

set_group_stable_transactions_set(&executed_set)函数即将交集设置到stable_gtid_set上。如果certification_info的writeset对应的gtid_set是stable_gtid_set的真子集，那么就可以被清理了。

/*
   When a transaction "t" is applied to all group members and for all
   ongoing, i.e., not yet committed or aborted transactions,
   "t" was already committed when they executed (thus "t"
   precedes them), then "t" is stable and can be removed from
   the certification info.
  */
   stable_gtid_set_lock->wrlock();
   while (it != certification_info.end())
   {
    if (it->second->is_subset_not_equals(stable_gtid_set))
    {
     if (it->second->unlink() == 0)
      delete it->second;
     certification_info.erase(it++);
    }
    else
     ++it;
   }
   stable_gtid_set_lock->unlock();

 

垃圾清理引发的问题

显然，将writeset加入certification_info和从其中清理无用的writeset，都需要在锁保护下进行。MGR定义了mysql_mutex_t LOCK_certification_info作为保护certification_info的互斥锁。事务的认证是顺序而频繁的，或者说往certification_info加writeset是快速且频繁的，与业务的事务提交行为一一对应。而后台的certification_info清理线程是每个60s清理一次，但每次都会遍历certification_info中的所有writeset并释放满足条件的writeset内存，属于非频繁但耗时的。如果certification_info中的writeset数目积累过多，那就可能导致后台的清理线程阻塞前台的事务提交时冲突检测。

设想如果业务对一张表以每秒1500 tps进行DML操作，该表有3个唯一索引，那么每秒会产生至少9000条writeset，每分钟就是超过50w条writeset，也就是说，每隔一分钟就需要加LOCK_certification_info锁遍历50w多个writeset。遍历过程中，业务的事务正常提交就阻塞了。会出现类似的性能曲线

图中蓝色曲线为业务tps，黄色曲线为提交延时。非常明显地出现每隔一分钟出现tps下降，同时延时急剧很高的问题。刚开始也怀疑过其他问题，经升级扩容后，问题依旧存在。

 

参数调优和机制优化

通过将清理周期调整为10s后，性能就变得非常平滑，下图前半段是未调整时，后半段是调整后。

下图是另一个场景下不同值的对比情况：

当然，该参数调节功能仅限于我们自己的MySQL分支版本。除了保留清理周期参数外，我们还引入了其他优化：

1、除了调整清理周期，也可以通过优化索引数量来缓解该问题，比如可以将多个索引合并为一个复合索引等，但，一般情况下调整的余地比较小；

2、减少writeset产生个数。一般情况下，同一个MGR集群内，MySQL版本都是统一的，没有必要产生带校对和不带校对2个writeset版本，该优化可以直接减少一半的writeset；

3、在单主模式下，若能保障primary切换上线前relay log已经回放完，那么就不再有节点间的事务冲突问题，那也就不需要基于stale_gtid_set来选择性清理writeset，因此，可以每隔一段时间清空certification_info，这样节省了gtid_set比较的步骤。需要指出的是，这并不会影响certification_info的正常功能，因为每隔一段时间清空writeset是普通的基于writeset并行复制机制下的默认行为，启用该复制机制后，缓存的writeset数目超过binlog_transaction_dependency_history_size即清空。详见[https://dev.mysql.com/doc/mysql-replication-excerpt/5.7/en/replication-options-binary-log.html#sysvar_binlog_transaction_dependency_history_size](https://link.zhihu.com/?target=https%3A//dev.mysql.com/doc/mysql-replication-excerpt/5.7/en/replication-options-binary-log.html%23sysvar_binlog_transaction_dependency_history_size)。

 

总结

本文主要介绍了事务writeset产生机制，MGR如何基于writeset进行冲突检测来确认事务是回滚还是提交，如何基于writeset来确定并行回放行为。最后分析了当前这套机制存在的不足和我们的优化设想。

欢迎感兴趣的同学评论交流指正。

 

本文作者：网易数据库团队

原文链接：[MySQL Group Replication冲突检测机制再剖析](https://zhuanlan.zhihu.com/p/55323854)

发布于 2019-04-04

 

来自 <https://zhuanlan.zhihu.com/p/61336729> 