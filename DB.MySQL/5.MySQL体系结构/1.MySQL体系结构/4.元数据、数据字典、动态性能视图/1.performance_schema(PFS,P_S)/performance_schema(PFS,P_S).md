# performance_schema

- 简称PFS/P_S，用于记录运行过程中的性能、资源、wait事件等信息，用于观测数据库运行情况。
- PFS采用专门的存储引擎
- 5.7起，PFS默认启用，全局开关默认为启用，检测点可以随需启用。
- 开启后，会持续采集监测，但其开销并不大，一般不会导致过多负载
- 可以动态调整监测点(instruments），使用前也需要启用检测点，不用的话可以随时关闭。启用检测点后，也要启用consumer，才能查询到监测数据。
- sys_schema是在PFS基础上对数据加工，提高人性化可读性。(非x$。 有x$的对象为原始数据。)

 

- IFS/I_S主要用于记录metadata，而PFS用于观测数据库运行情况

 

系统学习传送门：[剪辑：Performance Schema](剪辑：Performance Schema\1.Performance Schema使用简介(一).md)

 

# performance_schema的参数

可以动态加载，也可以写到my.cnf中。

| Name                                                         | Cmd-Line | Option  File | System  Var | Status  Var | Var  Scope | Dynamic |
| ------------------------------------------------------------ | -------- | ------------ | ----------- | ----------- | ---------- | ------- |
| performance_schema                                           | Yes      | Yes          | Yes         |             | Global     | No      |
| Performance_schema_accounts_lost                             |          |              |             | Yes         | Global     | No      |
| performance_schema_accounts_size                             | Yes      | Yes          | Yes         |             | Global     | No      |
| [Performance_schema_cond_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_cond_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [performance-schema-consumer-events-stages-current](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-stages-history](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-stages-history-long](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-statements-current](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-statements-history](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-statements-history-long](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-transactions-current](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-transactions-history](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-transactions-history-long](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-waits-current](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-waits-history](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-events-waits-history-long](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-global-instrumentation](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-statements-digest](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [performance-schema-consumer-thread-instrumentation](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [Performance_schema_digest_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [performance_schema_digests_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_stages_history_long_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_stages_history_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_statements_history_long_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_statements_history_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_transactions_history_long_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_transactions_history_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_waits_history_long_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_events_waits_history_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [Performance_schema_file_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_file_handles_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_file_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_hosts_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [performance_schema_hosts_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance-schema-instrument](http://performance-schema.html) | Yes      | Yes          |             |             |            |         |
| [Performance_schema_locker_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [performance_schema_max_cond_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_cond_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_digest_length](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_file_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_file_handles](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_file_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_memory_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_metadata_locks](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_mutex_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_mutex_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_prepared_statements_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_program_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_rwlock_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_rwlock_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_socket_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_socket_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_stage_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_statement_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_statement_stack](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_table_handles](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_table_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_thread_classes](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_max_thread_instances](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [Performance_schema_memory_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_metadata_lock_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_mutex_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_mutex_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_nested_statement_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_prepared_statements_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_program_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_rwlock_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_rwlock_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_session_connect_attrs_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| performance_schema_session_connect_attrs_size                | Yes      | Yes          | Yes         |             | Global     | No      |
| performance_schema_setup_actors_size                         | Yes      | Yes          | Yes         |             | Global     | No      |
| [performance_schema_setup_objects_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |
| [Performance_schema_socket_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_socket_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_stage_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_statement_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_table_handles_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_table_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_thread_classes_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_thread_instances_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [Performance_schema_users_lost](http://performance-schema.html) |          |              |             | Yes         | Global     | No      |
| [performance_schema_users_size](http://performance-schema.html) | Yes      | Yes          | Yes         |             | Global     | No      |

 

 

 

 

# PFS下的表主要有以下几类

| setup_%               | PFS自身设置相关，可修改，且立即生效 |
| --------------------- | ----------------------------------- |
| events_statements_%   | 事件语句相关                        |
| events_waits_%        | 事件等待相关                        |
| events_stages_%       | 事件阶段记录相关                    |
| events_transactions_% | 事务事件相关                        |
| file_%                | 文件系统层调用相关                  |
| memory_summary_%      | 内存监视相关                        |



- _current表中每个线程只保留一条记录，且一旦线程完成工作，该表中不会再记录该线程的事件信息，
- _history表中记录每个线程已经执行完成的事件信息，但每个线程的只事件信息只记录10条，再多就会被覆盖掉，
- *_history_long表中记录所有线程的事件信息，但总记录数量是10000行，超过会被覆盖掉。
- summary表提供所有事件的汇总信息。该组中的表以不同的方式汇总事件数据（如：按用户，按主机，按线程等等）。
- instance表记录了哪些类型的对象会被检测。这些对象在被server使用时，在该表中将会产生一条事件记录

 

 

传送门：[老叶茶馆] - 2018-04-03 不用MariaDB-Percona也能查看DDL的进度.html



## 启用事件阶段记录功能：

mysql> use performance_schema;

mysql> update setup_instruments set enabled='YES' where name like '%STAGE/INNODB/ALTER%';   ---默认就是YES。

mysql> update setup_consumers set enabled='YES' where name like '%STAGES%';

这就开启完了

接下来做DDL吧，事务越大越好， 哈哈哈。

DDL事务过程中，可以查看进展

mysql> select * from events_stages_current ;

mysql> select event_name,work_completed,work_estimated from events_stages_current ;

 

也可以回溯查看历史的记录

mysql> select * from events_stages_history ;

mysql> select event_name,work_completed,work_estimated from events_stages_history ;


 没啥事儿，玩完就关了

mysql> update setup_consumers set enabled='NO' where name like '%STAGES%';

关了之后，history依然可以查看历史记录（只要实例没重启）

## 启用profiling

什么是profiling？ 传送门：[老叶茶馆] - 2015-08-02 [MySQL FAQ]系列 — PROFILING中要关注哪些信息.html

mysql> UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES' WHERE NAME LIKE '%statement/%';
 mysql> UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES' WHERE NAME LIKE '%stage/%';

Ensure that events_statements_* and events_stages_* consumers are enabled. Some consumers may already be enabled by default.
 mysql> UPDATE performance_schema.setup_consumers SET ENABLED = 'YES' WHERE NAME LIKE '%events_statements_%';
 mysql> UPDATE performance_schema.setup_consumers SET ENABLED = 'YES' WHERE NAME LIKE '%events_stages_%';

 

开始跑SQL吧。然后查询

mysql> select * from events_statements_history_long;

 

**26.19.1 Query Profiling Using Performance Schema**

The following example demonstrates how to use Performance Schema statement events and stage events to retrieve data comparable to profiling information provided by [**SHOW PROFILES**](http://sql-syntax.html) and [**SHOW PROFILE**](http://sql-syntax.html) statements.

The [**setup_actors**](http://performance-schema.html) table can be used to limit the collection of historical events by host, user, or account to reduce runtime overhead and the amount of data collected in history tables. The first step of the example shows how to limit collection of historical events to a specific user.

Performance Schema displays event timer information in picoseconds (trillionths of a second) to normalize timing data to a standard unit. In the following example, **TIMER_WAIT** values are divided by 1000000000000 to show data in units of seconds. Values are also truncated to 6 decimal places to display data in the same format as [**SHOW PROFILES**](http://sql-syntax.html) and [**SHOW PROFILE**](http://sql-syntax.html) statements.

1. Limit the collection of historical events to the user that     will run the query. By default,[**setup_actors**](http://performance-schema.html) is     configured to allow monitoring and historical event collection for all     foreground threads:
             mysql> **SELECT \* FROM     performance_schema.setup_actors;**
             +------+------+------+---------+---------+
             | HOST | USER | ROLE | ENABLED | HISTORY |
             +------+------+------+---------+---------+
             | %  | %  | %       | YES   | YES   |
             +------+------+------+---------+---------+
             
             Update     the default row in the [**setup_actors**](http://performance-schema.html) table to disable historical event     collection and monitoring for all foreground threads, and insert a new row     that enables monitoring and historical event collection for the user that     will run the query:
             mysql> **UPDATE     performance_schema.setup_actors**
                 **SET ENABLED = 'NO', HISTORY = 'NO'**
                 **WHERE HOST = '%' AND USER = '%';**
             
             mysql> **INSERT INTO     performance_schema.setup_actors**
                 **(HOST,USER,ROLE,ENABLED,HISTORY)**
                 **VALUES('localhost','test_user','%','YES','YES');**
             
             Data     in the [**setup_actors**](http://performance-schema.html) table should now appear similar to the     following:
             mysql> **SELECT \* FROM     performance_schema.setup_actors;**
             +-----------+-----------+------+---------+---------+
             | HOST   | USER   | ROLE | ENABLED | HISTORY |
             +-----------+-----------+------+---------+---------+
             | %     | %     | %  | NO   | NO   |
             | localhost | test_user | %       | YES   | YES   |
             +-----------+-----------+------+---------+---------+
2. Ensure that     statement and stage instrumentation is enabled by updating the[**setup_instruments**](http://performance-schema.html) table.     Some instruments may already be enabled by default.
             mysql> **UPDATE performance_schema.setup_instruments**
                 **SET ENABLED = 'YES', TIMED = 'YES'**
                 **WHERE NAME LIKE '%statement/%';**
             
             mysql> **UPDATE     performance_schema.setup_instruments**
                 **SET ENABLED = 'YES', TIMED = 'YES'**
                 **WHERE NAME LIKE '%stage/%';**
3. Ensure     that **events_statements_\*** and **events_stages_\*** consumers     are enabled. Some consumers may already be enabled by default.
             mysql> **UPDATE performance_schema.setup_consumers**
                 **SET ENABLED = 'YES'**
                 **WHERE NAME LIKE '%events_statements_%';**
             
             mysql> **UPDATE     performance_schema.setup_consumers**
                 **SET ENABLED = 'YES'**
                 **WHERE NAME LIKE '%events_stages_%';**
4. Under the user account you     are monitoring, run the statement that you want to profile. For     example:
             mysql> **SELECT \*     FROM employees.employees WHERE emp_no = 10001;**
                 +--------+------------+------------+-----------+--------+------------+
             | emp_no | birth_date | first_name | last_name | gender | hire_date     |
                 +--------+------------+------------+-----------+--------+------------+
             | 10001 | 1953-09-02 |     Georgi   | Facello  | M        | 1986-06-26 |
             +--------+------------+------------+-----------+--------+------------+
5. Identify     the **EVENT_ID** of the     statement by querying the[**events_statements_history_long**](http://performance-schema.html) table.     This step is similar to running [**SHOW PROFILES**](http://sql-syntax.html)to identify     the **Query_ID**. The following     query produces output similar to [**SHOW PROFILES**](http://sql-syntax.html):
             mysql> **SELECT EVENT_ID, TRUNCATE(TIMER_WAIT/1000000000000,6) as     Duration, SQL_TEXT
                 FROM     performance_schema.events_statements_history_long WHERE SQL_TEXT like     '%10001%';**
                 +----------+----------+--------------------------------------------------------+
             | event_id | duration | sql_text                            |
             +----------+----------+--------------------------------------------------------+
             |    31 | 0.028310 | SELECT     * FROM employees.employees WHERE emp_no = 10001 |
             +----------+----------+--------------------------------------------------------+
6. Query the [**events_stages_history_long**](http://performance-schema.html) table to     retrieve the statement's stage events. Stages are linked to statements     using event nesting. Each stage event record has a **NESTING_EVENT_ID** column     that contains the **EVENT_ID** of the     parent statement.
             mysql> **SELECT event_name AS Stage, TRUNCATE(TIMER_WAIT/1000000000000,6)     AS Duration
                 FROM     performance_schema.events_stages_history_long WHERE NESTING_EVENT_ID=31;**
             +--------------------------------+----------+
             | Stage                  | Duration |
             +--------------------------------+----------+
             | stage/sql/starting           | 0.000080 |
             | stage/sql/checking permissions | 0.000005 |
             | stage/sql/Opening tables        | 0.027759 |
             | stage/sql/init             | 0.000052 |
             | stage/sql/System lock          | 0.000009 |
             | stage/sql/optimizing          | 0.000006 |
             | stage/sql/statistics          | 0.000082 |
             | stage/sql/preparing           | 0.000008 |
             | stage/sql/executing           | 0.000000 |
             | stage/sql/Sending data         | 0.000017 |
             | stage/sql/end              | 0.000001 |
             | stage/sql/query end           | 0.000004 |
             | stage/sql/closing tables        | 0.000006 |
             | stage/sql/freeing items         | 0.000272 |
             | stage/sql/cleaning up          | 0.000001 |
             +--------------------------------+----------+

 

## 启用MDL监控

mysql> update setup_instruments set enabled ='YES' where name like '%wait/lock/metadata/sql/mdl%';  ----默认开启

查询

mysql> select * from metadata_locks ;  --查询全局锁

 

## 启用表锁监控

mysql> update setup_instruments set enabled ='YES'， timed='YES' where name like '%wait/io/table/sql/handler%';  -----默认开启

查询

mysql> select * from table_handles;  ---不过没看懂。

 

## 监控TOP SQL

mysql> update setup_instruments set enabled ='YES'， timed='YES' where name like '%statement/sql/select%';  -----默认开启

查询

------我有些懵，没找到对应视图
