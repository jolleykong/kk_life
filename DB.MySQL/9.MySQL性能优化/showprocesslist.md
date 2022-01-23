# show processlist 命令详解

如果有 SUPER 权限，则可以看到全部的线程，否则，只能看到自己发起的线程（这是指，当前对应的 MySQL 帐户运行的线程）。

```
mysql> show processlist;

+—–+————-+——————–+
| Id | User | Host | db | Command | Time| State | Info
+—–+————-+——————–+
|207|root |192.168.0.2:51621 |mytest | Sleep | 5 | | NULL
|208|root |192.168.0.2:51622 |mytest | Sleep | 5 | | NULL
|220|root |192.168.0.2:51676 |mytest |Query | 84 | locked |select name,culture,value,type from book where id=1
```

说明各列的含义和用途，

- id列:一个标识，你要kill 一个语句的时候很有用。

- user列: 显示当前用户，如果不是root，这个命令就只显示你权限范围内的sql语句。

- host列:显示这个语句是从哪个ip 的哪个端口上发出的。可用来追踪出问题语句的用户。

- db列:显示这个进程目前连接的是哪个数据库。

- command列:显示当前连接的执行的命令，一般就是休眠（sleep），查询（query），连接（connect）。

  > 通常代表资源未释放，如果是通过连接池，sleep状态应该恒定在一定数量范围内
  >
  > 实战范例：因前端数据输出时（特别是输出到用户终端）未及时关闭[数据库](http://www.2cto.com/database/)连接，导致因网络连接速度产生大量sleep连接，在网速出现异常时，数据库too many connections挂死。
  >
  > 简单解读，数据查询和执行通常只需要不到0.01秒，而网络输出通常需要1秒左右甚至更长，原本数据连接在0.01秒即可释放，但是因为前端程序未执行close操作，直接输出结果，那么在结果未展现在用户桌面前，该数据库连接一直维持在sleep状态！

- time列:此这个状态持续的时间，单位是秒。

- state列:显示使用当前连接的sql语句的状态，很重要的列，后续会有所有的状态的描述，请注意，state只是语句执行中的某一个状态，一个sql语句，已查询为例，可能需要经过copying to tmp table，Sorting result，Sending data等状态才可以完成。

- info列:显示这个sql语句，因为长度有限，所以长的sql语句就显示不全，但是一个判断问题语句的重要依据。 



这个命令中最关键的就是state列，mysql列出的状态主要有以下几种：

- Checking table 

  正在检查数据表（这是自动的）。

- Closing tables 

  正在将表中修改的数据刷新到磁盘中，同时正在关闭已经用完的表。这是一个很快的操作，如果不是这样的话，就应该确认磁盘空间是否已经满了或者磁盘是否正处于重负中。

- Connect Out 

  复制从服务器正在连接主服务器。

- Copying to tmp table on disk 

  由于临时结果集大于 tmp_table_size，正在将临时表从内存存储转为磁盘存储以此节省内存。

  > 索引及现有结构无法涵盖查询条件，才会建立一个临时表来满足查询要求，产生巨大的恐怖的i/o压力。
  >
  > 很可怕的搜索语句会导致这样的情况，如果是数据分析，或者半夜的周期数据清理任务，偶尔出现，可以允许。频繁出现务必优化之。
  >
  > Copy to tmp table通常与连表查询有关，建议逐渐习惯不使用连表查询。
  >
  > 实战范例：
  >
  > 某社区数据库阻塞，求救，经查，其服务器存在多个数据库应用和网站，其中一个不常用的小网站数据库产生了一个恐怖的copy to tmp table操作，导致整个硬盘i/o和cpu压力超载。Kill掉该操作一切恢复。

- Creating tmp table 

  正在创建临时表以存放部分查询结果。

- deleting from main table 

  服务器正在执行多表删除中的第一部分，刚删除第一个表。

- deleting from reference tables 

  服务器正在执行多表删除中的第二部分，正在删除其他表的记录。

- Flushing tables 

  正在执行 FLUSH TABLES，等待其他线程关闭数据表。

- Killed 

  发送了一个kill请求给某线程，那么这个线程将会检查kill标志位，同时会放弃下一个kill请求。MySQL会在每次的主循环中检查kill标志位，不过有些情况下该线程可能会过一小段才能死掉。如果该线程程被其他线程锁住了，那么kill请求会在锁释放时马上生效。

- Locked 

  被其他查询锁住了。   

  > 有更新操作锁定     
  >
  >  通常使用innodb(支持行锁定)可以很好的减少locked状态的产生，但是切记，更新操作要正确使用索引，即便是低频次更新操作也不能疏忽。如上影响结果集范例所示。   
  >
  > 在myisam的时代，locked是很多高并发应用的噩梦。所以[mysql](http://www.2cto.com/database/MySQL/)官方也开始倾向于推荐innodb。 

- Sending data 

  正在处理 SELECT 查询的记录，同时正在把结果发送给客户端。   

  > Sending data并不是发送数据，别被这个名字所欺骗，这是从物理磁盘获取数据的进程，如果你的影响结果集较多，那么就需要从不同的磁盘碎片去抽取数据，
  >
  > 偶尔出现该状态连接无碍。 
  >
  > 回到上面影响结果集的问题，一般而言，如果sending data连接过多，通常是某查询的影响结果集过大，也就是查询的索引项不够优化。
  >
  > 如果出现大量相似的SQL语句出现在show proesslist列表中，并且都处于sending data状态，优化查询索引，记住用影响结果集的思路去思考。  

- Sorting for group

  正在为 GROUP BY 做排序。

- Sorting for order

  正在为 ORDER BY 做排序。    

​       和Sending data类似，结果集过大，排序条件没有索引化，需要在内存里排序，甚至需要创建临时结构排序    

- Opening tables

  这个过程应该会很快，除非受到其他因素的干扰。例如，在执 ALTER TABLE 或 LOCK TABLE 语句行完以前，数据表无法被其他线程打开。 正尝试打开一个表。

- Removing duplicates

  正在执行一个 SELECT DISTINCT 方式的查询，但是MySQL无法在前一个阶段优化掉那些重复的记录。因此，MySQL需要再次去掉重复的记录，然后再把结果发送给客户端。

- Reopen table

  获得了对一个表的锁，但是必须在表结构修改之后才能获得这个锁。已经释放锁，关闭数据表，正尝试重新打开数据表。

- Repair by sorting

  修复指令正在排序以创建索引。

- Repair with keycache

  修复指令正在利用索引缓存一个一个地创建新索引。它会比 Repair by sorting 慢些。

- Searching rows for update

  正在讲符合条件的记录找出来以备更新。它必须在 UPDATE 要修改相关的记录之前就完成了。

- Sleeping

  正在等待客户端发送新请求.

- System lock

  正在等待取得一个外部的系统锁。如果当前没有运行多个 mysqld 服务器同时请求同一个表，那么可以通过增加 –skip-external-locking参数来禁止外部系统锁。

- Upgrading lock

  INSERT DELAYED 正在尝试取得一个锁表以插入新记录。

- Updating

  正在搜索匹配的记录，并且修改它们。

- User Lock

  正在等待 GET_LOCK()。

- Waiting for tables

  该线程得到通知，数据表结构已经被修改了，需要重新打开数据表以取得新的结构。然后，为了能的重新打开数据表，必须等到所有其他线程关闭这个表。以下几种情况下会产生这个通知：FLUSH TABLES tbl_name, ALTER TABLE, RENAME TABLE, REPAIR TABLE, ANALYZE TABLE, 或 OPTIMIZE TABLE。

- waiting for handler insert

​    INSERT DELAYED         已经处理完了所有待处理的插入操作，正在等待新的请求。   

  

- Waiting for net, reading from net, writing to net

  偶尔出现无妨

  如大量出现，迅速检查数据库到前端的网络连接状态和流量

  案例:因外挂程序，内网数据库大量读取，内网使用的百兆交换迅速爆满，导致大量连接阻塞在waiting for net，数据库连接过多崩溃

 大部分状态对应很快的操作，只要有一个线程保持同一个状态好几秒钟，那么可能是有问题发生了，需要检查一下。还有其它的状态没在上面中列出来，不过它们大部分只是在查看服务器是否有存在错误是才用得着。