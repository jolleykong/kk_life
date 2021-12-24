MySQL 主要参数的说明以及一般建议

[TOC]

## 1.  innodb_flush_log_at_trx_commit

| 允许赋值 | 赋值介绍                                                     | 赋值解析                                                     |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 0        | log buffer将每秒一次地写入log file中，并且log file的flush(刷到磁盘)操作同时进行。该模式下在事务提交的时候，不会主动触发写入磁盘的操作。 | 当设置为0，该模式速度最快，但不太安全，mysqld进程的崩溃可能会导致最多上一秒钟内所有事务数据的丢失。 |
| 1        | 每次事务提交时MySQL都会把log buffer的数据写入log file，并且flush(刷到磁盘)中去，该模式为系统默认。 | 会在事务提交的时候，刷出所有  innodb 事务日志（redo），不会有数据丢失 |
| 2        | 每次事务提交时MySQL都会把log buffer的数据写入log file，但是flush(刷到磁盘)操作并不会同时进行。该模式下，MySQL会每秒执行一次  flush(刷到磁盘)操作。 | 当设置为2，该模式速度较快，commit 的时候会写入 logfile，但不会 flush，和设置0类似。 |

 

innodb_flush_log_at_timeout 这个参数的意思是刷新日志的时间，在mysql5.6版本中可以自定义，默认为1s。innodb_flush_log_at_timeout 的设置只针对 innodb_flush_log_at_trx_commit为0/2 起作用，与其配合适当增加日志刷新频率。与oracle中每隔三秒刷一次日志的概念类似。

## 2.  sync_binlog 

| 允许赋值       | 赋值解析                                                     | 总结                                                         |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 0              | 当事务提交之后，MySQL不做fsync之类的磁盘同步指令刷新binlog_cache中的信息到磁盘，而让Filesystem自行决定什么时候来做同步，或者cache满了之后才同步到磁盘。 | 在MySQL中系统默认的设置是sync_binlog=0，也就是不做任何强制性的磁盘刷新指令，这时候的性能是最好的，但是风险也是最大的。因为一旦系统Crash，在binlog_cache中的所有binlog信息都会被丢失。而当设置为“1”的时候，是最安全但是性能损耗最大的设置。因为当设置为1的时候，即使系统Crash，也最多丢失binlog_cache中未完成的一个事务，对实际数据没有任何实质性影响。     参数为0的时候，不会主动 flush 到磁盘上，当这个值是1的时候，每次事务必定需要刷出到磁盘上侯执行，如果设置为1的时候出现实例崩溃，那么不会有数据丢失，binlog cache 是会话级别的变量，未完成的事务可以认为并非成功的事务 |
| N  （N为数值） | 当每进行n次事务提交之后，MySQL将进行一次fsync之类的磁盘同步指令来将binlog_cache中的数据强制写入磁盘。 |                                                              |

 

有推荐做法与innodb_flush_log_at_trx_commit配合使用提高写入性能：要么 两个参数都设置为1，或者都设置为0，设置为0的情况下，必须有从库作为 ha 保障，不能使用崩溃的数据库作为线上服务，避免数据丢失。

## 3.  innodb_file_per_table、 innodb_data_file_path 、innodb_data_home_dir

​       本组主要是数据文件配置相关的参数。

| 参数                  | 赋值范围                                                     | 参数解释                                                     |
| --------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| innodb_file_per_table | on/off                                                       | 是否开启独立表空间，也就是每个表一个单独的文件存储，推荐开启。 |
| innodb_data_file_path | filename:sizeG:autoextend:NM: max:NGB;filename2:sizeG; | 该参数主要是设置数据文件的名字和大小，在未配置参数“innodb_data_home_dir”的情况下可以添加文件的绝对路径如：  innodb_data_file_path  = /data2/sales2:100M:autoextend:8M:max:2GB |
| innodb_data_home_dir  | /path                                                        | 指定数据文件的统一路径，高版本中已经废弃，建议统一使用 mysql 全局data_dir |

 

## 4.  slow_query_log、long_query_time、slow_query_log_file、log_queries_not_using_indexes

  本组主要是慢查询相关的配置参数，所谓慢查询即mysql是否记录运行超过指定时间的sql。比如配置为一秒，那么所有执行时间超过一秒的参数都会被记录到慢查询文件中，方便后续整理优化等操作。

   

 

| 参数                          | 赋值范围                    | 参数解释                                                     |
| ----------------------------- | --------------------------- | ------------------------------------------------------------ |
| slow_query_log                | 0/1/不跟参数                | 是否开启慢查询记录，slow_query_log=0关闭；slow_query_log=1开启（这个1可以不写） |
| long_query_time               | 数字N（可以是小数，单位秒） | 比如：long_query_time  = 1 是记录超过1秒的SQL执行语句（建议<=0.5） |
| slow_query_log_file           | /path                       | 指定慢查询文件的路径                                         |
| log_queries_not_using_indexes | on/off                      | 是否记录未使用索引的sql，默认记录到慢查询文件中              |
| log_slow_slave_statements     | on/off                      | 打开后可以记录 sql 线程执行的慢查询，默认是不记录的，即使 slow log 打开 |

 

 

## 5.  lower_case_table_names

​    大小写敏感参数 

| 允许赋值 | 赋值解析                                                     | 总结                                                         |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 0        | 使用CREATE TABLE或CREATE DATABASE语句指定的大小写字母在硬盘上保存表名和数据库名。名称比较对大小写敏感。 | 在大小写不敏感的操作系统如windows或Mac OS x上我们不能将该参数设为0，如果在大小写不敏感的文件系统上将--lowercase-table-names强制设为0，并且使用不同的大小写访问MyISAM表名，可能会导致索引破坏。 |
| 1        | 表名在硬盘上以小写保存，名称比较对大小写不敏感。MySQL将所有表名转换为小写在存储和查找表上。该行为也适合数据库名和表的别名。 | 该值为Windows的默认值。                                      |
| 2        | 表名和数据库名在硬盘上使用CREATE  TABLE或CREATE DATABASE语句指定的大小写字母进行保存，但MySQL将它们转换为小写在查找表上。名称比较对大小写不敏感，即按照大小写来保存，按照小写来比较。 | 只在对大小写不敏感的文件系统上适用! innodb表名用小写保存。   |

​    备注：这个设置在5.1和5.5版本，对复制过滤的大小写修正有 bug，https://bugs.mysql.com/bug.php?id=51639，请知晓。

## 6.  general_log、general_log_file

| 参数             | 赋值范围 | 参数解释                                                     |
| ---------------- | -------- | ------------------------------------------------------------ |
| general_log      | ON/OFF   | 是否开启查询日志，查询日志记录数据库中所有的查询操作，开启后文件会很大，所以一般系统无需开启 |
| general_log_file | /path    | 设置查询日志路径                                             |

备注：本特性可作为免费的审计工具。

## 7. query_cache_size、query_cache_type

| 参数             | 赋值范围 | 参数解释                                                     |
| ---------------- | -------- | ------------------------------------------------------------ |
| query_cache_size | NM/NG    | 配置查询缓存大小，查询缓存保存查询返回的完整结果。当查询命中该缓存，会立刻返回结果，跳过了解析，优化和执行阶段。   查询缓存会跟踪查询中涉及的每个表，如果这写表发生变化，那么和这个表相关的所有缓存都将失效。   但是随着服务器功能的强大，查询缓存也可能成为整个服务器的资源竞争单点。 |
| query_cache_type | 0/1      | 是否开启查询缓存                                             |

   备注：一般建议关闭，如果命中 query cache 的 select 语句，不会被加入 com_select 计数，而是会增加 Qcache_hits计数，统计数据库访问量的时候需要注意。

## 8.资源限制相关参数

| 参数                   | 赋值范围 | 参数解释                                                     |
| ---------------------- | -------- | ------------------------------------------------------------ |
| max_connection         | 数值     | 数据库的最大连接数                                           |
| max_connect_errors     | 数值     | 最大错误数,当错误连接数超过设定的值后，将无法正常连接，执行下mysqladmin -uroot flush-hosts 即可 |
| max_user_connections   | 数值     | 每个用户最大链接（这里用户的概念是授权时候的“user”@“host” 组合，而非单纯的 user 名称） |
| innodb_open_files      | 数值     | 限制Innodb能打开的表的数据，默认为300，数据库里的表特别多的情况，可以适当增大为1000。innodb_open_files的大小对InnoDB效率的影响比较小。但是在InnoDBcrash的情况下，innodb_open_files设置过小会影响recovery的效率。所以用InnoDB的时候还是把innodb_open_files放大一些比较合适。 |
| table_open_cache       | 数值     | 主要用于设置table高速缓存的数量。由于每个客户端连接都会至少访问一个表，因此此参数的值与max_connections有关。当某一连接访问一个表时，MySQL会检查当前已缓存表的数量。如果该表已经在缓存中打开，则会直接访问缓存中的表已加快查询速度；如果该表未被缓存，则会将当前的表添加进缓存并进行查询。在执行缓存操作之前，table_cache用于限制缓存表的最大数目：如果当前已经缓存的表未达到table_open_cache、则会将新表添加进来；若已经达到此值，MySQL将根据缓存表的最后查询时间、查询率等规则释放之前的缓存，设置为当前数据库表数量。这个参数是全局设置，与连接数无关。 |
| table_definition_cache | 数值     | 与“table_open_cache”类似，但是前者缓存frm文件，本参数应该是缓存ibd/MYI/MYD文件，默认计算公式为 ：400 + (table_open_cache / 2) |
| open_files_limit       | 数值     | 最大打开文件数，建议设置为表数量的三倍。                     |

 

## 9.binlog相关参数

###  9.1.binlog_format

  二进制文件保存格式

| 允许赋值  | 赋值介绍                                          | 赋值解析                                                     |
| --------- | ------------------------------------------------- | ------------------------------------------------------------ |
| Statement | 每一条会修改数据的sql都会记录在binlog中           | 优点：不需要记录每一行的变化，减少了binlog日志量，节约了IO，提高性能。(相比row能节约多少性能与日志量，这个取决于应用的SQL情况，正常同一条记录修改或者插入row格式所产生的日志量还小于Statement产生的日志量，但是考虑到如果带条件的update操作，以及整表删除，ROW格式会产生大量日志，因此在考虑是否使用ROW格式日志时应该跟据应用的实际情况，其所产生的日志量会增加多少，以及带来的IO性能问题。)  缺点：由于记录的只是执行语句，为了这些语句能在slave上正确运行，因此还必须记录每条语句在执行的时候的一些相关信息，以保证所有语句能在slave得到和在master端执行时候相同 的结果。另外mysql 的复制,像一些特定函数功能，slave可与master上要保持一致会有很多相关问题(如sleep()函数，  last_insert_id()，以及user-defined functions(udf)会出现问题).  使用以下函数的语句也无法被复制：  *  LOAD_FILE()  * UUID()  * USER()  *  FOUND_ROWS()  * SYSDATE() (除非启动时启用了 --sysdate-is-now 选项)  同时在INSERT  ...SELECT 会产生比 RBR 更多的行级锁 |
| Row       | 不记录sql语句上下文相关信息，仅保存哪条记录被修改 | 优点： binlog中可以不记录执行的sql语句的上下文相关的信息，仅需要记录那一条记录被修改成什么了。所以rowlevel的日志内容会非常清楚的记录下每一行数据修改的细节。而且不会出现某些特定情况下的存储过程，或function，以及trigger的调用和触发无法被正确复制的问题  缺点:所有的执行的语句当记录到日志中的时候，都将以每行记录的修改来记录，这样可能会产生大量的日志内容,比如一条update语句，修改多条记录，则binlog中每一条修改都会有记录，这样造成binlog日志量会很大。row 格式，alter 不会产生日志 |
| MiXED     | 是以上两种level的混合使用                         | 一般的语句修改使用statment格式保存binlog，如一些函数，statement无法完成主从复制的操作，则采用row格式保存binlog,MySQL会根据执行的每一条具体的sql语句来区分对待记录的日志形式，也就是在Statement和Row之间选择一种.新版本的MySQL中队row level模式也被做了优化，并不是所有的修改都会以row level来记录，mixed 默认保存的是 statement 格式，只有在存在 uuid，UDF 等的时候，才会存储为 row 格式。此处可以参考文档  [*https://dev.mysql.com/doc/refman/5.7/en/binary-log-mixed.html*   ](https://dev.mysql.com/doc/refman/5.7/en/binary-log-mixed.html)小节。推荐配置类型。 |

​    

###    9.2 binlog_row_image

   5.6.2里新增函数binlog_row_image。是动态参数，使用级别session和global，减少binlog_format为row的模式下（mixed分情况），日志的生成量。

 

| 允许赋值 | 赋值介绍                                                     | 赋值解析                                                     |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| full     | 默认值                                                       | 记录所有的行信息，和5.6之前记录的没有区别                    |
| minimal  | 只记录要修改列的记录                                         | 设置 MySQL Group  Replication 的时候，为了减少带宽消耗，一般使用 minimal |
| noblob   | 如果 blob 或者 text 字段没有被更新，记录除了blog和text之外的所有字段 | 当一个表中含有blob、text类型字段时，会导致binary log日志量暴涨，特别是有一些游戏数据库。update的时候，即使不更新这些字段，before image和afterimage都会被写入到binary log日志，我们为了节省磁盘，内存，网络流量等，设置此参数来达到这些需求 |

 

###    9.3 binlog_rows_query_log_events

| 允许赋值 | 赋值介绍                          | 赋值解析                                                     |
| -------- | --------------------------------- | ------------------------------------------------------------ |
| on/off   | 是否将原始的操作sql记录写入事件中 | 它是一个动态的，全局，会话型的变量，即可以通过SQL模式进行关闭开启。在使用RBR也就是行格式的时候，去解析binlog，需要逆向才能分析出对应的原始SQL是什么，而且，里面对应的是每一条具体行变更的内容。当然，你可以开启general log,但如果我们需要的只是记录对应的行变更，而不需要记录这些select普通的查询，因为general  log 会将线上所有的操作都记录下来，只有写操作会被记录，但是没有 select 操作，并且没有语句来源，相比较 general log，并不适合作为审核 |

 

###    9.4 log_bin_use_v1_row_events

  5.6.6引入，默认是0，如果使用1是使用Version1的格式，mysql5.5可以认出来的形式，如果0是5.6.6后使用的version2格式

## 10.GTID相关

  关于gtid的简单介绍，推荐一篇BLOG:

  http://www.cnblogs.com/zhoujinyi/p/4717951.html

 

| 参数                     | 赋值范围 | 参数解释                                                     |
| ------------------------ | -------- | ------------------------------------------------------------ |
| gtid_mode                | on/off   | 是否开启GTID功能                                             |
| enforce_gtid_consistency | on/off   | 是否允许违反GTID事务一致性。  OFF:允许违反GTID事务一致性。  ON:不允许违反GTID事务一致性。 |

 

推荐 ：

gtid_mode=on

enforce_gtid_consistency=on

两个参数必须同时打开

 

## 11.同步相关参数

| 参数                      | 赋值范围   | 参数解释                                                     |
| ------------------------- | ---------- | ------------------------------------------------------------ |
| log_slave_updates         | 0/1        | 参数表示是否slave将复制事件写进自己的二进制日志。设置为1后，从库会把从主库传来的日志写到自己的 binlog，主要用于多级复制。 |
| master_info_repository    | TABLE/FILE | 记录到表中 master信息的方式：  table是记录到数据库 mysql.slave_master_info表中（推荐）。  FILE 记录到 master.info文件中 |
| relay_log_info_repository | TABLE/FILE | 记录replay相关信息的方式：  table是记录到数据库 mysql.slave_relay_log_info表中（推荐）。  FILE 记录到relay-log.info文件中 |
| relay_log_recovery        | 0/1        | 当slave从库宕机后，假如relay-log损坏了，导致一部分中继日志没有处理，则自动放弃所有未执行的relay-log，并且重新从master上获取日志，这样就保证了relay-log的完整性。默认情况下该功能是关闭的，将relay_log_recovery的值设置为 1时，可在slave从库上开启该功能，建议开启。 |
| skip_slave_start          | 0/1        | 是否阻止在崩溃后自动启动，给你充足的时间进行修复，在主从同步的时候配置（推荐为1，即需要阻止） |
| auto_increment_offset     | 1-65535    | 表示自增长字段从那个数开始。在做数据库的主主同步时需要设置自增长的相关配置。 |
| auto_increment_increment  | 1-65535    | 表示自增长字段每次递增的量，其默认值是1。在做数据库的主主同步时需要设置自增长的相关配置。 |

 

## 12.查看mysql事务隔离级别

### 12.1 查询语句

select @@tx_isolation;

### 12.2 事务隔离级别描述

SQL标准定义了4类隔离级别，包括了一些具体规则，用来限定事务内外的哪些改变是可见的，哪些是不可见的。低级别的隔离级一般支持更高的并发处理，并拥有更低的系统开销。

1）Read Uncommitted（读取未提交内容）

在该隔离级别，所有事务都可以看到其他未提交事务的执行结果。本隔离级别很少用于实际应用，因为它的性能也不比其他级别好多少。读取未提交的数据，也被称之为脏读（Dirty Read）。

2）Read Committed（读取提交内容）

这是大多数数据库系统的默认隔离级别（但不是MySQL默认的）。它满足了隔离的简单定义：一个事务只能看见已经提交事务所做的改变。这种隔离级别 也支持所谓的不可重复读（Nonrepeatable Read），因为同一事务的其他实例在该实例处理其间可能会有新的commit，所以同一select可能返回不同结果。

3）Repeatable Read（可重读）

这是MySQL的默认事务隔离级别，它确保同一事务的多个实例在并发读取数据时，会看到同样的数据行。不过理论上，这会导致另一个棘手的问题：幻读 （Phantom Read）。简单的说，幻读指当用户读取某一范围的数据行时，另一个事务又在该范围内插入了新行，当用户再读取该范围的数据行时，会发现有新的“幻影” 行。InnoDB和Falcon存储引擎通过多版本并发控制（MVCC，Multiversion Concurrency Control）机制解决了该问题。

4）Serializable（可串行化）

这是最高的隔离级别，它通过强制事务排序，使之不可能相互冲突，从而解决幻读问题。简言之，它是在每个读的数据行上加上共享锁。在这个级别，可能导致大量的超时现象和锁竞争。

。

### 12.3修改事务的隔离级别

   在MySQL中默认事务隔离级别是可重复读(Repeatable read).可通过SQL语句查询：

   查看InnoDB系统级别的事务隔离级别：

   mysql> SELECT @@global.tx_isolation;

 

   结果：

   +-----------------------+
   | @@global.tx_isolation |
   +-----------------------+
   | REPEATABLE-READ    |
   +-----------------------+

 

   查看InnoDB会话级别的事务隔离级别：

   mysql> SELECT @@tx_isolation;

 

   结果：

   +-----------------+
   | @@tx_isolation |
   +-----------------+
   | REPEATABLE-READ |
   +-----------------+

 

   修改事务隔离级别：

   mysql> set global transaction isolation level read committed;

   mysql> set session transaction isolation level read committed;

## 13.innodb_autoinc_lock_mode

  innodb_autoinc_lock_mode这个参数控制着在向有auto_increment 列的表插入数据时，相关锁的行为；

 

通过对它的设置可以达到性能与安全(主从的数据一致性)的平衡

 

### 13.1我们先对insert做一下分类

首先insert大致上可以分成三类：

1）simple insert 如insert into t(name) values('test')

2）bulk insert 如load data | insert into ... select .... from ....

3）mixed insert 如insert into t(id,name) values(1,'a'),(null,'b'),(5,'c');

### 13.2 innodb_autoinc_lock_mode 的说明

innodb_auto_lockmode有三个取值：

1）0 这个表示tradition 传统

2）1 这个表示consecutive 连续

3）2 这个表示interleaved 交错

 

#### 13.2.1 tradition(innodb_autoinc_lock_mode=0) 模式:

1）它提供了一个向后兼容的能力

2）在这一模式下，所有的insert语句("insert like")都要在语句开始的时候得到一个表级的auto_inc锁，在语句结束的时候才释放这把锁，注意呀，这里说的是语句级而不是事务级的，一个事务可能包涵有一个或多个语句。

3）它能保证值分配的可预见性，与连续性，可重复性，这个也就保证了insert语句在复制到slave的时候还能生成和master那边一样的值(它保证了基于语句复制的安全)。   

  4）由于在这种模式下auto_inc锁一直要保持到语句的结束，所以这个就影响到了并发的插入。

 

#### 13.2.2 consecutive(innodb_autoinc_lock_mode=1，推荐模式) 模式:

1）这一模式下去simple insert 做了优化，由于simple insert一次性插入值的个数可以立马得到确定，所以mysql可以一次生成几个连续的值，用于这个insert语句；总的来说这个对复制也是安全的(它保证了基于语句复制的安全)

2）这一模式也是mysql的默认模式，这个模式的好处是auto_inc锁不要一直保持到语句的结束，只要语句得到了相应的值后就可以提前释放锁

#### 13.2.3 interleaved(innodb_autoinc_lock_mode=2) 模式

由于这个模式下每一行拿一次锁，也可以理解为已经没有了auto_inc锁，所以这个模式下的性能是最好的；但是它也有一个问题，就是对于同一个语句来说它所得到的auto_incremant值可能不是连续的。

 

### 13.3备注

   如果你的二进制文件格式是row 那么这三个值中的任何一个对于你来说都是复制安全的。

 

由于现在mysql已经推荐把二进制的格式设置成row，所以在binlog_format不是statement和mixd的情况下最好是innodb_autoinc_lock_mode=2 这样可能知道更好的性能。

## 14.log_timestamps

​    在MySQL 5.7.2 新增了log_timestamps 这个参数主要是控制 error log、slow_log、genera log，等等记录日志的显示时间参数，但不会影响 general log 和 slow log 写到表 (mysql.general_log, mysql.slow_log) 中的显示时间。在查询行的时候，可以使用 CONVERT_TZ() 函数，或者设置会话级别的系统变量 time_zone 来转换成所需要的时区，在 5.7.2 之后改参数为默认 UTC 这样会导致日志中记录的时间比中国这边的慢，导致查看日志不方便。修改为 SYSTEM 就能解决问题

  该参数全局有效，可以被设置的值有：UTC 和 SYSTEM，默认使用 UTC，建议使用system。它还支持动态设置，不过建议大家在配置文件中就写上，以免重启之后造成不必要的麻烦。

 

## 15.timezone

修改MySQL的时区

### 15.1 可以通过修改my.cnf

在 [mysqld] 之下加

default-time-zone=timezone（默认值为 system，特定的时间计算会存在系统调用，一般建议修改为实际所在时区）

来修改时区。如：

default-time-zone = '+8:00'

修改完了记得记得重启msyql

注意一定要在 [mysqld] 之下加 ，否则会出现 unknown variable ‘default-time-zone=+8:00'

### 15.2 另外也可以通过命令行在线修改

set time_zone = ‘+8:00';

 

### 15.3 通过select now()来验证时区

  show variables like '%time_zone%'; 

select now(); 

 

## 16.lock_wait_timeout

  锁超时阀值定义,默认是1年.可根据情况适当调小，注意此处是 mysql 全局锁而非 innodb 事务行锁，innodb 对应的是innodb_lock_wait_timeout

 

## 17.innodb_spin_wait_delay

  控制自旋时间的参数。

  自旋(spin)是一种通过不间断地测试来查看一个资源是否变为可用状态的等待操作，用于仅需要等待很短的时间等待所需资源的场景。使用自旋这种“空闲循环(busy-loop)”来完成资源等待的方式要比通过上下文切换使线程转入睡眠状态的方式要高效得多。但如果自旋了一个很短的时间后其依然无法获取资源，则仍然会转入前述第二种资源等待方式。此变量则正是用于定义InnoDB自旋操作的空闲循环转数，默认为6转（默认即可）。作用范围为全局级别，可用于选项文件，属动态变量。

 

## 18.innodb_read_io_threads、 innodb_write_io_threads

读io线程数和写io进程数，建议修改为操作系统可用的 cpu 核数

## 19.innodb_io_capacity

磁盘IO吞吐，具体为缓冲区落地的时候，可以刷脏页的数量，默认200，一般建议设置为文佳系统16k 1：1读写压测时候iops 的80%

 

## 20.innodb_max_dirty_pages_pct

​    这个百分比是，最大脏页的百分数，当系统中脏页所占百分比超过这个值，INNODB就会进行写操作以把页中的已更新数据写入到磁盘文件中。争议比较大，一般来说都是在75-90之间，主要控制BP中的脏数据刷盘的时机，如果太小会频繁刷盘造成IO上升，如果太大会导致MySQL正常关闭的时候需要很长的时间才能normal shutdown，具体需要看实际场景。建议50.

## 21.innodb_force_recovery

  innodb_force_recovery影响整个InnoDB存储引擎的恢复状况。默认为0，表示当需要恢复时执行所有的恢复。

  innodb_force_recovery可以设置为1-6,大的数字包含前面所有数字的影响。当设置参数值大于0后，可以对表进行select,create,drop操作,但insert,update或者delete这类操作是不允许的。

  1）1(SRV_FORCE_IGNORE_CORRUPT):忽略检查到的corrupt页。

  2）2(SRV_FORCE_NO_BACKGROUND):阻止主线程的运行，如主线程需要执行full purge  操作，会导致crash。

  3）3(SRV_FORCE_NO_TRX_UNDO):不执行事务回滚操作。

  4）4(SRV_FORCE_NO_IBUF_MERGE):不执行插入缓冲的合并操作。

  5）5(SRV_FORCE_NO_UNDO_LOG_SCAN):不查看重做日志，InnoDB存储引擎会将未提交的事务视为已提交。

  6）6(SRV_FORCE_NO_LOG_REDO):不执行前滚的操作。

  如果主库崩溃 从库没有这时候 从库比主库的可信度要高

 

## 22.undo tablespaces相关参数

| 参数                                    | 含义                                                         |
| --------------------------------------- | ------------------------------------------------------------ |
| innodb_undo_directory[=/opt/mysql/undo] | Innodb为还原日志创建的独立表空间的相对或绝对路径。通常用于日志被放置在哪些不同的存储设备上。配合参数innodb_undo_logs和innodb_undo_tablespaces，这决定了系统表空间外还原日志的磁盘分布。默认目录为undo 默认在 ibdata 里面。  如果想转移undo文件的位置，只需要修改下该配置，并将undo文件拷贝过去就可以了。 |
| innodb_undo_logs[=128]                  | 定义在所有事务中innodb使用的系统表空间中回滚段的个数。如果观察到同回滚日志有关的互斥争用，可以调整这个参数以优化性能。早期版本的命名为innodb_rollback_segments，该变量可以动态调整，但是物理上的回滚段不会减少，只是会控制用到的回滚段的个数;默认为128个回滚段 |
| innodb_undo_tablespaces[=4]             | 用于设定创建的undo表空间的个数，在mysql_install_db时初始化后，就再也不能被改动了；默认值为0，表示不独立设置undo的tablespace，默认记录到ibdata中；否则，则在undo目录下创建这么多个undo文件，例如假定设置该值为4，那么就会创建命名为undo001~undo004的undo tablespace文件，每个文件的默认大小为10M。会影响 undo文件的数量，在 mysql 8开始，这个参数可以在初始化后调整。 |

   当undo超过innodb_max_undo_log_size时会触发truncate工作purge执行innodb_purge_rseg-truncate_frequency次后也会触发truncate工作建议使用独立undo表空间。

 

## 23.innodb_page_size

  innodb中page的大小设置， 5.6版本中。不可调整。5.6版本后支持 8kb、4kb 但不能调大。5.7以上后支持32KB、64KB。全局选项无法在运行过程中动态修改。大 page 会导致读写压力增加，一般建议在 olap 系统设置大页，从checkpoint的角度来讲，page size越小，性能越好。所以最后选择多大的page size可以根据实际的业务测试而定。

 

## 24.innodb_buffer_pool_instances

  innodb_buffer_pool_instances可以开启多个内存缓冲池，把需要缓冲的数据hash到不同的缓冲池中，这样可以并行的内存读写。配置大小时按照一个instances 管理8到16g内存来配置大小。

 

## 25.快速预热相关参数

   如果一台高负荷的机器重启后，内存中大量的热数据被清空，此时就会重新从磁盘加载到Buffer_Pool缓冲池里，这样当高峰期间，性能就会变得很差，连接数就会很高。

  在MySQL5.6里，一个新特性避免的这种问题的出现。

你只需在my.cnf里，加入如下：

  innodb_buffer_pool_dump_at_shutdown = 1

  解释：在关闭时把热数据dump到本地磁盘。

  innodb_buffer_pool_dump_now = 1

  解释：采用手工方式把热数据dump到本地磁盘。

  innodb_buffer_pool_load_at_startup = 1

  解释：在启动时把热数据加载到内存。

  innodb_buffer_pool_load_now = 1

​    解释：采用手工方式把热数据加载到内存。

在关闭MySQL时，会把内存中的热数据保存在磁盘里ib_buffer_pool文件中，位于数据目录下。

 

## 26.innodb_flush_method

  这个参数控制着innodb数据文件及redo log的打开、刷写模式：

  有三个值：fdatasync，O_DSYNC，O_DIRECT。

  默认是fdatasync，调用fsync()去刷数据文件与redo log的buffer。

  为O_DSYNC时，innodb会使用O_SYNC方式打开和刷写redo log,使用fsync()刷写数据文件。

  为O_DIRECT时，innodb使用O_DIRECT打开数据文件，使用fsync()刷写数据文件跟redo log。

  目前可用值为fsync(默认)，而O_DSYNC,O_DIRECT,O_DIRECT_NO_FSYNC, O_DIRECT_NO_FSYNC适用于不需要fsync 保障数据安全的文件系统

  首先文件的写操作包括三步：open,write,flush。

  上面最常提到的fsync(int fd)函数，该函数作用是flush时将与fd文件描述符所指文件有关的buffer刷写到磁盘，并且flush完元数据信息(比如修改日期、创建日期等)才算flush成功。

  使用O_SYNC方式打开redo文件表示当write日志时，数据都write到磁盘，并且元数据也需要更新，才返回成功。

  O_DIRECT则表示我们的write操作是从MySQL innodb buffer里直接向磁盘上写。

  至此我再总结一下三者写数据方式：

  fdatasync模式：写数据时，write这一步并不需要真正写到磁盘才算完成（可能写入到操作系统buffer中就会返回完成），真正完成是flush操作，buffer交给操作系统去flush,并且文件的元数据信息也都需要更新到磁盘。

  O_DSYNC模式：写日志操作是在write这步完成，而数据文件的写入是在flush这步通过fsync完成。

  O_DIRECT模式：数据文件的写入操作是直接从mysql innodb buffer到磁盘的，并不用通过操作系统的缓冲，而真正的完成也是在flush这步,日志还是要经过OS缓冲。

 

## 27.innodb_old_blocks_pct、innodb_old_blocks_time

  innodb缓存池有2个区域一个是sublist of old blocks存放不经常被访问到的数据，另外一个是sublist of new blocks存放经常被访问到的数据

  innodb_old_blocks_pct参数是控制进入到sublist of old blocks区域的数量，初始化默认是37.

innodb_old_blocks_time参数是在访问到sublist of old blocks里面数据的时候控制数据不立即转移到sublist of new blocks区域，而是在多少微秒之后才会真正进入到new区域，这也是防止new区域里面的数据不会立即被踢出。

 

  所以就有2种情况：

  1)如果在业务中做了大量的全表扫描，那么你就可以将innodb_old_blocks_pct设置减小，增到innodb_old_blocks_time的时间，不让这些无用的查询数据进入old区域，尽量不让缓存再new区域的有用的数据被立即刷掉。（这也是治标的方法，大量全表扫描就要优化sql和表索引结构了）

  2)如果在业务中没有做大量的全表扫描，那么你就可以将innodb_old_blocks_pct增大，减小innodb_old_blocks_time的时间，让有用的查询缓存数据尽量缓存在innodb_buffer_pool_size中，减小磁盘io，提高性能。

 

## 28.innodb_fill_factor

  innodb在创建或重建B树索引时执行批量加载。这种索引构建方法称之为排序索引构建。innodb_fill_factor定义在排序索引构建期间填充的每个B树页面上的空间百分比，剩余空间为未来索引增长保留。空间索引不支持索引构建。设置为100的innodb_fill_factor将留下聚集索引页中1/16的空间，以供将来索引增长。

 

## 29.日志相关参数

### 29.1 innodb_log_file_size

对于写很多尤其是大数据量时非常重要。要注意，大的文件提供更高的性能，但数据库恢复时会用更多的时间。我一般用64M-512M，具体取决于服务器的空间。几个日志成员大小加起来差不多和你的innodb_buffer_pool_size相等。目前这个值的最大限制总和512GB。具体大小还需要看你的事务大小，数据大小为依据。

说明：这个值分配的大小和数据库的写入速度，事务大小，异常重启后 的恢复有很大的关系。

### 29.2 innodb_log_buffer_size

事务在内存中的缓冲，默认值对于多数中等写操作和事务短的运用都是可以的。如果经常做更新或者使用了很多blob数据，应该增大这个值。但太大了也是浪费内存，因为1秒钟总会 flush一次，所以不需要设到超过1秒的需求。8-32M一般应该够了。小的运用可以设更小一点。

### 29.3 innodb_log_fles_in_group

  指定你有几个日值组。一般我们可以用２-３个日值组。默认为两个。

## 30.Innodb_fast_shutdown

  Innodb_fast_shutdown告诉innodb在它关闭的时候该做什么工作。有三个值可以选择：

1）0表示在innodb关闭的时候，需要purge all, merge insert buffer,flush dirty pages。这是最慢的一种关闭方式，但是restart的时候也是最快的。需要注意的是，做 mysql 的跨大版本升级的时候，需要使用 fast shutdown =0的设置。后面将介绍purge all,merge insert buffer,flush dirty pages这三者的含义。

2）1表示在innodb关闭的时候，它不需要purge all，merge insert buffer，只需要flush dirty page。

3）2表示在innodb关闭的时候，它不需要purge all，merge insert buffer，也不进行flush dirty page，只将log buffer里面的日志flush到log files。因此等下进行恢复的时候它是最耗时的，相当于崩溃恢复。

 

## 31.innodb_flush_neighbors

  扫描列表，并找到邻居页面，默认值为 1. 在SSD存储上应设置为0(禁用) ,因为使用顺序IO没有任何性能收益. 在使用RAID的某些硬件上也应该禁用此设置,因为逻辑上连续的块在物理磁盘上并不能保证也是连续的.

 

## 32.innodb_buffer_pool_size

  最大内存块 建议为物理内存的50%-80%。

 

## 33.innodb_change_buffering

  当更新/插入的非聚集索引的数据所对应的页不在内存中时（对非聚集索引的更新操作通常会带来随机IO），会将其放到一个insert buffer中，当随后页面被读到内存中时，会将这些变化的记录merge到页中。当服务器比较空闲时，后台线程也会做merge操作

但insert buffer会占用buffer pool，并且在非聚集索引很少时，并不总是必要的，反而会降低buffer pool做data cache的能力，5.5提供了参数innodb_change_buffering来对其进行控制

根据官方文档的描述，主要包括以下几个值：

  1）all

  The default value: buffer inserts, delete-marking operations, and purges.

  2）none

  Do not buffer any operations.

  3）inserts

  Buffer insert operations.

  4）deletes

  Buffer delete-marking operations.（包括delete和update操作）

  5)changes

  Buffer both inserts and delete-marking.

  6)purges

  Buffer the physical deletion operations that happen in the background

  默认all即可。

 

## 34.innodb_sort_buffer_size

  默认1048576,范围524288 .. 67108864

  指定在创建InnoDB索引期间用于排序数据的排序缓冲区的大小。指定的大小定义了用于内部排序并写入磁盘的内存中填充的数据量。在合并阶段，指定大小的缓冲区对“被读入”并合并。设置越大，“运行”和合并就越少，这从调整的角度来看是非常重要的。

  此索引区域仅在创建索引时用于合并排序，而不用于后续索引维护操作。索引创建完成时缓冲区被释放。

 

## 35.innodb_stats_on_metadata

  每当查询information_schema元[数据库](http://www.2cto.com/database/)里的表时，InnoDB还会随机提取其他[数据库](http://www.2cto.com/database/)每个表索引页的部分数据，从而更新information_schema.STATISTICS表，并返回刚才查询的结果。当你的表很大，且数量很多时，耗费的时间就会很长，很多经常不访问的数据也会进入Innodb_Buffer_Pool缓冲池里，那么就会污染缓冲池，并且ANALYZE TABLE和SHOW TABLE STATUS语句也会造成InnoDB随机提取数据。

  从MySQL5.5.X版本开始，你可以动态关闭innodb_stats_on_metadata(建议关闭)，不过默认是开启的。关闭方式如下：

  set global innodb_stats_on_metadata = OFF;