# 实验：将数据库实例备份并恢复到新实例，重跑备份后产生的binlog

将数据库实例备份并恢复到新实例，重跑备份后产生的binlog。

  1. 恢复备份（xtrabackup）

  2. 启动恢复后的实例，show master status.

  3. 记下gtid信息

  4. 去源库binlog中找刚才gtid在源库中对应的position

     ```
     mysqlbinlog -v --base64-output=decode-rows /data/mysql/mysql3306/logs/mysql-bin.00001|grep '1-23'
     
     #position=194
     ```

  5. 重放binlog到sql文件

     ```
     mysqlbinlog -v --start-position=194 /data/mysql/mysql3306/logs/mysql-bin.00001 >restore.sql
     
     mysqlbinlog -v --start-position=194 /data/mysql/mysql3306/logs/mysql-bin.00002 >>restore.sql
     
     mysqlbinlog -v /data/mysql/mysql3306/logs/mysql-bin.00003 >>restore.sql
     
     ……
     ```

     - 注意：此处不应加--base64-output=decode-rows参数，否则语句会被自动加#注释，无法实际应用给数据库。
     - 如有必要，需要加入--skip-gtid参数。

     - --start-position=194     在第一个文件指定，后面不要指定了，不然文件里194前面的东西好像就丢了（每个文件都有自己的position好像，待确认。）

  6. 应用sql文件到新实例，并检查gtid和数据。

- 如果是mysqldump，那么步骤如下：

  1. 一致性备份 mysqldump -S xxx.sock -u -p --single-transaction master-data=2 -A >full.sql

  2. 源库继续进行操作

  3. 建立并初始化新实例

  4. 查看mysqldump的备份文件， 里面有提示信息：

     ```
     -- GTID state at the beginning of the backup 
     --
     SET @@GLOBAL.GTID_PURGED='27bea3ec-33d5-11ea-a145-000c29f0aa33:1';
     --
     -- Position to start replication or point-in-time recovery from
     --
     -- CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000004', MASTER_LOG_POS=194;
     ```

  5. 根据提示信息重放检查源库bin-log（这步不是必须的，仅仅是为了逻辑性上的一致，并验证）

     ```
     mysqlbinlog -v --start-position=194 --base64-output=decode-rows mysql-bin.000004|less
     # 备份后操作确实是194后的内容
     ```

  6. 根据提示信息重放源库binlog到sql文件

     ```
     mysqlbinlog -v --start-position=194  mysql-bin.000004 >~/3309.sql 
     mysqlbinlog -v --start-position=194  mysql-bin.000005 >>~/3309.sql 
     mysqlbinlog -v  mysql-bin.000006 >>~/3309.sql 
     mysqlbinlog -v  mysql-bin.000007 >>~/3309.sql 
     mysqlbinlog -v  mysql-bin.000008 >>~/3309.sql 
     ```

  7. 检查新实例的gtid及数据。
     有个问题，这样做过后，show master status会出现两个gtid，看来需要后续mysql复制的知识来解答用途和原因了。