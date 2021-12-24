# [mysqldump关于--set-gtid-purged=OFF的使用](https://www.cnblogs.com/--smile/p/11464687.html)

数据库的模式中我开启了gtid：

mysql> show variables like '%gtid%';

+----------------------------------+-----------+

| Variable_name                    | Value     |

+----------------------------------+-----------+

| binlog_gtid_simple_recovery      | ON        |

| enforce_gtid_consistency         | ON        |

| gtid_executed_compression_period | 1000      |

| gtid_mode                        | ON        |

| gtid_next                        | AUTOMATIC |

| gtid_owned                       |           |

| gtid_purged                      |           |

| session_track_gtids              | OFF       |

+----------------------------------+-----------+

我现在数据库中有一world的库，并且在库中有一个country表，现在进行备份时会提示如下警告：

[root@smiletest data]# mysqldump -uroot -p -R -e --triggers  --master-data=2 --single-transaction  world country >/tmp/countryno.sql

Enter password: 

Warning: A partial dump from a server that has GTIDs will by default include the GTIDs of all transactions, even those that changed suppressed parts of the database. If you don't want to restore GTIDs, pass --set-gtid-purged=OFF. To make a complete dump, pass --all-databases --triggers --routines --events.

我们来对比下加了 --set-gtid-purged=OFF和不加的区别

countryno.sql是没有加--set-gtid-purged=OFF

[root@smiletest data]# mysqldump -uroot -p -R -e --triggers  --master-data=2 --single-transaction  world country >/tmp/countryno.sql

countryyes.sql是加--set-gtid-purged=OFF

[root@smiletest data]# mysqldump -uroot -p -R -e --triggers  --master-data=2 --single-transaction   --set-gtid-purged=OFF world country >/tmp/countryyes.sql

Enter password: 

没有加--set-gtid-purged=OFF的里面会多几条语句

SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;

SET @@SESSION.SQL_LOG_BIN= 0;

-- GTID state at the beginning of the backup 

SET @@GLOBAL.GTID_PURGED='e024c334-8b64-11e9-80dc-fa163e4bfc29:1-761734';

现在我们进行导入刚没有加--set-gtid-purged=OFF备份的/tmp/countryno.sql语句

mysql> show master status;

+------------------+----------+--------------+------------------+-----------------------------------------------+

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                             |

+------------------+----------+--------------+------------------+-----------------------------------------------+

| mysql-bin.000013 |    85019 |              |                  | e024c334-8b64-11e9-80dc-fa163e4bfc29:1-761735 |

+------------------+----------+--------------+------------------+-----------------------------------------------+

1 row in set (0.00 sec)

mysql> source /tmp/countryno.sql

Query OK, 0 rows affected (0.00 sec)

mysql> show master status;

+------------------+----------+--------------+------------------+-----------------------------------------------+

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                             |

+------------------+----------+--------------+------------------+-----------------------------------------------+

| mysql-bin.000013 |    85019 |              |                  | e024c334-8b64-11e9-80dc-fa163e4bfc29:1-761735 |

+------------------+----------+--------------+------------------+-----------------------------------------------+

1 row in set (0.00 sec)

结论发现，gtid事务和 Position都没有增加

现在我们进行导入刚加--set-gtid-purged=OFF备份的/tmp/countryyes.sql语句

mysql> drop table country;

Query OK, 0 rows affected (0.01 sec)

mysql> show master status;

+------------------+----------+--------------+------------------+-----------------------------------------------+

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                             |

+------------------+----------+--------------+------------------+-----------------------------------------------+

| mysql-bin.000013 |   112669 |              |                  | e024c334-8b64-11e9-80dc-fa163e4bfc29:1-761742 |

+------------------+----------+--------------+------------------+-----------------------------------------------+

1 row in set (0.00 sec)

mysql> source /tmp/countryyes.sql

Query OK, 0 rows affected (0.00 sec)

mysql> show master status;

+------------------+----------+--------------+------------------+-----------------------------------------------+

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                             |

+------------------+----------+--------------+------------------+-----------------------------------------------+

| mysql-bin.000013 |   139929 |              |                  | e024c334-8b64-11e9-80dc-fa163e4bfc29:1-761747 |

+------------------+----------+--------------+------------------+-----------------------------------------------+

1 row in set (0.00 sec)

mysql> 

结论发现，gtid事务和 Position都增加了

结论

加了--set-gtid-purged=OFF时，在会记录binlog日志，如果不加，不记录binlog日志，所以在我们做主从用了gtid时，用mysqldump备份时就要加--set-gtid-purged=OFF，否则你在主上导入恢复了数据，主没有了binlog日志，同步则不会被同步。