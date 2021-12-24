# [innodb_max_dirty_pages_pct与检查点的关系        ](https://www.cnblogs.com/zengkefu/p/5678122.html)             

 

http://ourmysql.com/archives/310

数据库运行一段时间后，经常导致服务器大量的swap,我怀疑是innodb中的脏数据太多了，因为没有free  space了，mysql通知OS，把一些脏页交换出去，以上只是猜测。有一个现象是每次关数据库时都要关很久,并且在关数据库时，发现有大量的swap in。如果是数据库进程异常关闭，打开数据库又会花很长的时间来作恢复。我想提高一下mysql检查点发生的频率。看了[Adaptive checkpointing](http://www.mysqlperformanceblog.com/2008/11/13/adaptive-checkpointing/),发现mysql检查点事件受两个因素的制约：一个是amount,另外一个是age.amount主要由innodb_max_dirty_pages_pct参数控制;至于age,主要是由日志文件大小有关。因为修改日志文件大小，要重启数据库，所以没有做这个尝试；于是尝试修改innodb_max_dirty_pages_pct参数。

查看当前innodb_max_dirty_pages_pct参数的值：

mysql> show variables like ‘%pct%’;
+—————————-+——-+
| Variable_name       | Value |
+—————————-+——-+
| innodb_max_dirty_pages_pct | 90  |
+—————————-+——-+
1 row in set (0.00 sec)

查看当前的检查点位置（对于如何获取此信息，花了比较多的时间,才找到此方法）

show innodb status\G;

LOG
—
Log sequence number 16 881655880
Log flushed up to  16 881649862
Last checkpoint at 16 546135914 

我们可以看到检查点与log sequence number,Log flushed up to都有相当大的差距。

———————-
BUFFER POOL AND MEMORY
———————-
Total memory allocated 19338953832; in additional pool allocated 13600768
Buffer pool size  1048576
Free buffers    17666
Database pages   1009478
Modified db pages 204553  

修改的页占到整个数据库buffer  pool页将近20%,大小为204553*16k/1024=3.196G,有这么多的脏数据没有写到数据文件。如果此时关闭数据库，必然要花很长的时间。如果数据库服务器因为掉电或者mysqld进程异常中断，那么打开，恢复的时间也会很长。

在咨询mysql界的朋友后，大家对innodb_max_dirty_pages_pct基本上也是采用默认值，不过，觉得这个方向是对的，就开始一步步调此参数。因为脏页占整个pool的20%,所以直接将此参数从90调到20.反复执行命令show innodb  status\G;发现检查点仍然增长缓慢。过了一会儿，发现系统并无任何异常之处，继续调低此参数到15,此时间发现脏页Modified db  pages减少下来，检查点增长稍微快一点。最终综合考虑缓存大小，把此参数设为5.

mysql> set global innodb_max_dirty_pages_pct=5;
Query OK, 0 rows affected (0.00 sec)

—
LOG
—
Log sequence number 16 1160564756
Log flushed up to  16 1160560077
Last checkpoint at 16 1037968260  –检查点追上来了

———————-
BUFFER POOL AND MEMORY
———————-
Total memory allocated 19338952464; in additional pool allocated 15022080
Buffer pool size  1048576
Free buffers    5291
Database pages   1021765
Modified db pages 61626     –这个值从204553快速下降

情况如自己预计的那样，脏页迅速减少，检查点追上来了。使用mysql的朋友，对于mysql服务器的交换，一直都采用直接关闭swap的做法。不知道使用此方法，即提高检查点发生的频率，减少脏页数量，能否解决我们常见的mysql交换问题呢？让我们试目以待吧。过一段时间，再把结果发上来。