冷备 热备

物理 逻辑

 

 

在线基于逻辑备份

mysqldump & mydumper

mysqlpump

可用来跨平台迁移

逻辑备份不备份索引数据，所以占用会比物理备份小很多

在线物理备份

xtrabackup

还有官方的MySQL enterprise hotbackup

clone pugin(8.0.17) 未来可能实现集中的远程备份，由一台机器发起，多台执行备份动作。

增量备份

mysql binary log

 

 

 

mysqldump

mysqlpump

mydumper

filesystem backup

xtrabackup

锁定实例进行备份

binlog 备份

 

逻辑备份，讲所有数据库、表结构、数据和存储过程鞥对象导出到一组可以再次执行的sql语句中，以重新创建数据库状态

物理备份，包含文件系统上的所有文件

 

对于时间点回复，备份应该能够提供开始做备份之前的二进制文件的位置，这被称为连续的备份

可以使用slave备份，备份到一个别的位置。

 

使用mysqldump

 

- 完整备份所有数据库

mysqldump --all-databases > alldump.sql

8.0版本之前，存储过程和时间存储在mysql.proc和mysql.event表中。

8.0版本开始，对象的定义存储在数据字典表中，但是默认的情况下这些表不会被备份。要将存储过程和时间包含在完整数据库备份中，要附加上参数 --routines --events

mysqldump --all-databases --routines --events > alldump.sql

 

可以查看一下备份文件的内容。

 

 

- 时间点恢复

要获得时间点恢复，应该指定--single-transaction和--master-data

--single-transaction选项在执行备份之前，通过将事务隔离级别更改为RR，并执行start transaction来提供一致性备份。 选项仅适用于InnoDB之类的事务表，因为它在start transaction 执行时能保存数据库的一致性状态而不阻塞任何应用程序

 

--master-data选项将服务器的二进制日志的位置输出到dump文件。

如果值为2，将打印为注释。 它也使用FTWRL语句来获取二进制日志的快照

mysqldump --all-database --routines --events --single-transaction --master-data=2 >alldump.sql

 

- 保存主库二进制日志位置

备份使用在slave上进行。要获取悲愤诗master的binlog pos，可以使用--dump-slave选项，如果正在从master进行binlog备份，那么使用这个选项，否则使用--master-data

输出将包含change master 语句

 

指定数据库和表

指定数据库

mysqldump --databases db1 > db1.sql

指定表

mysqldump --databases db1 --tables tb1 > db1_tb1.sql

 

忽略表

--ignore-table = db.tb ， 如果要忽略多个表，需要多次使用该参数

mysqldump --database db1 --ignore-table db1.tb2 > db1_tithout_tb2.sql

 

过滤特定条件

mysqldump --database db1 --tables tb1 --where="id>100" > db1_tb1_id_after100.sql

mysqldump --database db1 --tables tb1 --where="id>100 limit 5" > db1_tb1_id_after100_top5.sql

 

将远程DB备份到本地

就不用ssh到目标服务器了，但是需要有连接和备份的权限

mysqldump --all-database --routines --events --triggers --hostname $REMOTE_HOST >remote_host_all_backup.sql

 

 

用于重建另一个具有不同schema的服务器的备份（什么鸟语）

仅备份不包含数据的schema

使用--no-data备份结构

mysqldump --all-databases --routines --events --triggers --no-data > no_data.sql

 

仅备份不包含schema的数据

使用--complete-insert，将在insert中指定完全列名，这样便于后续修改

mysqldump --all-databases --no-create-db --no-create-info --complete-insert > data.sql

 

 

用于与其他服务器合并数据的备份

可以通过备份来替换旧数据，或在发生冲突时，保留旧数据

用新数据替换

使用--replace选项后，将使用replace into语句替代insert 语句，以将新数据合并。

使用--skip-add-drop-table选项，不在dump文件写入drop table语句。

如果要替换数据的对象的表和表结构相同，则还可以使用--no-create-info选项，不在dump文件写入create table语句

mysqldump --databases db1 --skip-add-drop-table --no-create-info --replace > to_dev.sql

 

忽略数据，保留现有数据并插入新数据

在写入dump文件时可以使用insert ingnore 语句替代replace。

--insert-ignore

 

 

 

使用mysqlpump

mysqlpump也是mysql自带的工具，相比mysqldump，有一些不同

mysqlpump支持并行处理，可以通过指定线程数量来加速备份过程，线程数量根据cpu数量进行设定。

使用8线程进行备份

mysqlpump --default-parallelism=8 >full_backup_with_8thread.sql

针对不同的数据库定不同的线程

mysqlpump --parallel-schemas=4:db1 --default-prarllelism=2 > full_backup.sql

对db1使用4线程，其他使用2线程。

mysqldump --parallel-schemas=3:dba,db2 --parallel-schemas=2:db3,db4 --default-parallelism=4 > full_backup.sql

对db1，db2使用3线程，db3，db4使用2线程，其他使用4线程。

 

使用正则表达式来过滤数据库对象

对包含prod结尾的数据库进行备份

mysqlpump --include-databases=%prod --result-file=db_prod.sql

排除掉所有数据库中名为test的表

mysqlpump --exclude-tables=test --result-file=db_excluding_test.sql

每个包含和排除选项的值都可以是逗号分隔的列表，并且允许对象名称使用下列通配符：

%匹配多个字符

_匹配单个字符

除了数据库和表，还可以包含或排除触发器、过程、事件和用户

--include-routines , --include-events, --include-triggers,--exclude-routines 等等

 

备份用户

使用mysqldump工具时，若想备份用户，需要备份mysql.user表。

在mysqlpump中，可以将用户备份为sql（看得晕，回头试验一下）

mysqlpump --exclude-database=% --users > user.sql

也可排除一些用户

mysqlpump --exclude-database=% --exclude-users=root --users > users.sql

 

压缩备份

支持zlib或lz4方式压缩

解压时需要具有相应解压工具

mysqlpump --compress-output=lz4 >dump.lz4

mysqlpump --compress-output=zlib > dump.zlib

解压缩

lz4_decompress dump.lz4 dump.sql

zlib_decompress dump.zlib dump.sql

 

mysqlpump输出的dump文件中，将辅助索引从create table语句中缩略了，这提交了load的速度，后续使用alter table 在insert结尾添加这些索引。

 

mydumper