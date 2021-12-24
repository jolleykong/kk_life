[mysql备份与还原](https://www.cnblogs.com/Cherie/p/3309456.html)

**一、备份常用操作基本命令**

1、备份命令mysqldump格式

  格式：mysqldump -h主机名 -P端口 -u用户名 -p密码 –database 数据库名 > 文件名.sql 

2、备份MySQL数据库为带删除表的格式

备份MySQL数据库为带删除表的格式，能够让该备份覆盖已有数据库而不需要手动删除原有数据库。

mysqldump --add-drop-table -uusername -ppassword -database databasename > backupfile.sql

3、直接将MySQL数据库压缩备份

mysqldump -hhostname -uusername -ppassword -database databasename | gzip > backupfile.sql.gz

4、备份MySQL数据库某个(些)表

mysqldump -hhostname -uusername -ppassword databasename specific_table1 specific_table2 > backupfile.sql

5、同时备份多个MySQL数据库

mysqldump -hhostname -uusername -ppassword –databases databasename1 databasename2 databasename3 > multibackupfile.sql仅仅备6、仅备份份数据库结构

mysqldump –no-data –databases databasename1 databasename2 databasename3 > structurebackupfile.sql

7、备份服务器上所有数据库

mysqldump –all-databases > allbackupfile.sql

8、还原MySQL数据库的命令

mysql -hhostname -uusername -ppassword databasename < backupfile.sql

9、还原压缩的MySQL数据库

gunzip < backupfile.sql.gz | mysql -uusername -ppassword databasename

10、将数据库转移到新服务器

mysqldump -uusername -ppassword databasename | mysql –host=*.*.*.* -C databasename

11、--master-data 和--single-transaction

  在mysqldump中使用--master-data=2，会记录binlog文件和position的信息 。--single-transaction会将隔离级别设置成repeatable-commited

12、导入数据库

常用source命令，用use进入到某个数据库，mysql>source d:\test.sql，后面的参数为脚本文件。

13、查看binlog日志

查看binlog日志可用用命令 mysqlbinlog binlog日志名称|more

 

14、general_log

General_log记录数据库的任何操作，查看general_log 的状态和位置可以用命令show variables like "general_log%" ,开启general_log可以用命令set global general_log=on

**二、增量备份**

小量的数据库可以每天进行完整备份，因为这也用不了多少时间，但当数据库很大时，就不太可能每天进行一次完整备份了，这时候就可以使用增量备份。增量备份的原理就是使用了[mysql](http://www.centos.bz/category/mysql/)的binlog志。

 

1、首先做一次完整备份：

mysqldump -h10.6.208.183 -utest2 -p123 -P3310 --single-transaction --master-data=2 test>test.sql这时候就会得到一个全备文件test.sql

在sql文件中我们会看到：

-- CHANGE MASTER TO MASTER_LOG_FILE='bin-log.000002', MASTER_LOG_POS=107;是指备份后所有的更改将会保存到bin-log.000002二进制文件中。

2、在test库的t_student表中增加两条记录，然后执行flush logs命令。这时将会产生一个新的二进制日志文件bin-log.000003，bin-log.000002则保存了全备过后的所有更改，既增加记录的操作也保存在了bin-log.00002中。

3、再在test库中的a表中增加两条记录，然后误删除t_student表和a表。a中增加记录的操作和删除表a和t_student的操作都记录在bin-log.000003中。

 

**三、恢复**

1、首先导入全备数据

mysql -h10.6.208.183 -utest2 -p123 -P3310 < test.sql，也可以直接在mysql命令行下面用source导入

2、恢复bin-log.000002

  mysqlbinlog bin-log.000002 |mysql -h10.6.208.183 -utest2 -p123 -P3310 

3、恢复部分 bin-log.000003

  在general_log中找到误删除的时间点，然后更加对应的时间点到bin-log.000003中找到相应的position点，需要恢复到误删除的前面一个position点。

可以用如下参数来控制binlog的区间

--start-position 开始点 --stop-position 结束点

--start-date 开始时间 --stop-date 结束时间

找到恢复点后，既可以开始恢复。

 mysqlbinlog mysql-bin.000003 --stop-position=208 |mysql -h10.6.208.183 -utest2 -p123 -P3310 

 

 

 

来自 <https://www.cnblogs.com/Cherie/p/3309456.html> 