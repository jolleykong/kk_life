
# mysqldump --master-data=2 --single-transaction

- mysqldump导出数据主要有两种控制：
1. 一种是导出的全过程都加锁 lock-all-tables, 
2. 另一种则是不加。

前者会在导出开始时执行 FLUSH TABLES WITH READ LOCK; 也就是加全局读锁，会阻塞其它写操作，以保证导出是一致性的；因此只有在导出测试数据时或导出时没有业务连接操作时可不加 lock-all-tables .

至于说一致性导出的另一种方式 single-transaction, 则是有适用范围的，见下边。

 

- single-transaction 选项和 lock-all-tables 选项是二选一的

前者是在导出开始时设置事务隔离状态并使用一致性快照开始事务,而后马上unlock tables，然后执行导出,导出过程不影响其它事务或业务连接，但只支持类似innodb多版本特性的引擎，因为必须保证即使导出期间其它操作(事务点t2)改变了数据，而导出时仍能取出导出开始的事务点t1时的数据。而lock-all-tables则一开始就 FLUSH TABLES WITH READ LOCK; 加全局读锁，直到dump完毕。

# 关于一致性快照，简单地说，就是通过回滚段能记录不同的事务点的各版本数据

- --single-transaction 的流程如下：
    ```
    SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ

    START TRANSACTION /*!40100 WITH CONSISTENT SNAPSHOT */

    SHOW MASTER STATUS        -- 这一步就是取出 binlog index and position

    UNLOCK TABLES

    ...dump...
    ```


- master_data 选项开启时默认会打开lock-all-tables，因此同时实现了两个功能，一个是加锁，一个是取得log信息。

- master_data取1和取2的区别，只是后者把 change master ... 命令注释起来了，没多大实际区别；

 

- 当master_data和 single_transaction 同时使用时，先加全局读锁，然后设置事务一致性和使用一致性快照开始事务，然后马上就取消锁，然后执行导出。过程如下
    ```
    FLUSH TABLES WITH READ LOCK

    SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ

    START TRANSACTION /*!40100 WITH CONSISTENT SNAPSHOT */

    SHOW MASTER STATUS        -- 这一步就是取出 binlog index and position

    UNLOCK TABLES

    ...dump...
    ```


# 总结，了解了这些选项作用后，使用起来就明确了.

如果需要binlog信息则使用 master_data; 

如果不想阻塞同时表是innodb引擎可使用 single_transaction 取得一致性快照(取出的数据是导出开始时刻事务点的状态)

如果表不支持多版本特性，则只能使用 lock-all-tables 阻塞方式来保证一致性的导出数据。

当然，如果能保证导出期间没有任何写操作，可不加或关闭 lock-all-tables

 

来自 <https://blog.csdn.net/linuxheik/article/details/71480882> 



>```
>--master-data[=*`value`*]
>```
>
>Use this option to dump a master replication server to **<u>produce a dump file that can be used to set up another server as a slave of the master.</u>** It causes the dump output to include a [`CHANGE MASTER TO`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/sql-syntax.html#change-master-to) statement that indicates the binary log coordinates (file name and position) of the dumped server. These are the master server coordinates from which the slave should start replicating after you load the dump file into the slave.
>
>If the option value is 2, the [`CHANGE MASTER TO`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/sql-syntax.html#change-master-to) statement is written as an SQL comment, and thus is informative only; it has no effect when the dump file is reloaded. If the option value is 1, the statement is not written as a comment and takes effect when the dump file is reloaded. If no option value is specified, the default value is 1.
>
>This option requires the [`RELOAD`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/security.html#priv_reload) privilege and the binary log must be enabled.
>
>The `--master-data` option automatically turns off [`--lock-tables`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/programs.html#option_mysqldump_lock-tables). It also turns on [`--lock-all-tables`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/programs.html#option_mysqldump_lock-all-tables), unless[`--single-transaction`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/programs.html#option_mysqldump_single-transaction) also is specified, in which case, a global read lock is acquired only for a short time at the beginning of the dump (see the description for [`--single-transaction`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/programs.html#option_mysqldump_single-transaction)). In all cases, any action on logs happens at the exact moment of the dump.
>
>It is also possible to set up a slave by dumping an existing slave of the master, using the [`--dump-slave`](dfile:///Users/kk/Library/Application Support/Dash/Versioned DocSets/MySQL - DHDocsetDownloader/5-7/MySQL.docset/Contents/Resources/Documents/programs.html#option_mysqldump_dump-slave) option, which overrides `--master-data` and causes it to be ignored if both options are used.
>
>