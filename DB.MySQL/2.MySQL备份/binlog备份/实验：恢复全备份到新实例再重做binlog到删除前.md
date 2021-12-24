- 3306实例全备份（xtrabackup），而后操作3306数据库，创建数据库、表，插入数据，再删除数据并提交。

- 现在要恢复数据到删除前。

- 使用策略：恢复全备份到新实例，再重做binlog到删除前，数据恢复后确认无误，再恢复到3306库。

  1. 使用全备建立新实例3307：

     ```
     [root@mysqlvm1 logs]# innobackupex --defaults-files=/data/mysql/mysql3307/my3307.cnf --copy-back /data/backup/3306_2/
     200113 23:59:28 completed OK!
     [root@mysqlvm1 data]# pwd
     /data/mysql/mysql3307/data
     [root@mysqlvm1 data]# chown mysql:mysql -R ./*
     [root@mysqlvm1 data]# mysqld --defaults-file=/data/mysql/mysql3307/my3307.cnf &
     [root@mysqlvm1 data]# mysql -S /data/mysql/mysql3307/tmp/mysql.sock -proot
     
     mysql> show databases;
     +--------------------+
     | Database      |
     +--------------------+
     | information_schema |
     | cp         |
     | kk         |
     | mysql       |
     | performance_schema |
     | sys        |
     +--------------------+
     6 rows in set (0.00 sec)
     
     mysql> show master status;
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set             |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | mysql-bin.000001 |   154 |       |         | d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-23 |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     1 row in set (0.00 sec)
     
     mysql> 
     ```

  2. 根据gtid 1-23 去源库搜索binlog对应的文件名及position：

     ```
     [root@mysqlvm1 logs]# mysqlbinlog -v --base64-output=decode-rows mysql-bin.000006 |grep 1-23
     
     [root@mysqlvm1 logs]# mysqlbinlog -v --base64-output=decode-rows mysql-bin.000007 |grep 1-23
     # d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-23
     # d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-23
     # at 194
     ```

  3. 根据源库当前gtid，推算删除前的gtid所在的文件及gtid，确定stop position

     ```
     mysql> show master status;
     
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set             |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | mysql-bin.000010 |   194 |       |         | d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-46 |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     
     [root@mysqlvm1 logs]# mysqlbinlog -v --base64-output=decode-rows mysql-bin.000009|grep 1-45
     # d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-45
     # d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-45
     # at 194
     ```

  通过检索binlog内容，确定1-45之后是delete动作。

  4. 重放binlog到sql文件

     ```
     [root@mysqlvm1 logs]# mysqlbinlog -v --start-position=194 mysql-bin.000007 >~/before.sql   #7号binlog194位置为全备恢复后的位置，也就是start
     
     [root@mysqlvm1 logs]# mysqlbinlog -v mysql-bin.000008 >>~/before.sql                    #8号文件不包含gtid:1-46，所以全binlog都需要重放
     
     [root@mysqlvm1 logs]# mysqlbinlog -v --stop-position=194 mysql-bin.000009 >>~/before.sql  #9号文件中包含gtid:1-46，在该gtid前的位置为194，也就是stop（都是194，很是巧合）
     
     # 10号binlog呢？ 不要了，因为9号到194位置就足够了，后面就多余了（又删了）
     ```

  5. 加载sql文件到3307库

     ```
     #忘记关闭read_only，直接加载后gtid会变，直接用set gtid_purged 会提示一个看不懂的东西。这个如何解决，留给后面的学习内容去解答。
     
     mysql> set global super_read_only=0;
     Query OK, 0 rows affected (0.00 sec)
     
     mysql> set global read_only=0;
     Query OK, 0 rows affected (0.00 sec)
     
     mysql> show master status;
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set             |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | mysql-bin.000001 |   154 |       |         | d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-23 |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     1 row in set (0.00 sec)
     
     mysql> source /root/before.sql
     
     mysql> show master status;
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set             |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     | mysql-bin.000001 |  269943 |       |         | d5c3b189-33d4-11ea-a48c-000c29f0aa33:1-45 |
     +------------------+----------+--------------+------------------+-------------------------------------------+
     1 row in set (0.00 sec)
     
     mysql> show databases;
     +--------------------+
     | Database      |
     +--------------------+
     | information_schema |
     | cp         |
     | cpp        |
     | kk         |
     | mysql       |
     | performance_schema |
     | sys        |
     +--------------------+
     7 rows in set (0.00 sec)
     
     mysql> use cpp;
     Database changed
     
     mysql> show tables;
     +---------------+
     | Tables_in_cpp |
     +---------------+
     | aa      |
     | cpp      |
     +---------------+
     2 rows in set (0.00 sec)
     
     mysql> select count(*) from aa;
     +----------+
     | count(*) |
     +----------+
     |  22016 |
     +----------+
     1 row in set (0.01 sec)
     ```

  6. 对比源库3306，确认数据恢复回来了

     ```
     mysql> select count(*) from aa;
     +----------+
     | count(*) |
     +----------+
     |  12288 |
     +----------+
     1 row in set (0.00 sec)
     ```

  7. 将数据从3307弄回3306~

     ```
     [root@mysqlvm1 mysql3307]# mysqldump -S tmp/mysql.sock -proot cpp aa>~/aa.sql
     
     [root@mysqlvm1 mysql3306]#
     
     mysql> rename table aa to aab;
     Query OK, 0 rows affected (0.02 sec)
     
     mysql> source /root/aa.sql
     
     mysql> select count(*) from aa;
     +----------+
     | count(*) |
     +----------+
     |  22016 |
     +----------+
     1 row in set (0.01 sec)
     ```

  8. 完活。