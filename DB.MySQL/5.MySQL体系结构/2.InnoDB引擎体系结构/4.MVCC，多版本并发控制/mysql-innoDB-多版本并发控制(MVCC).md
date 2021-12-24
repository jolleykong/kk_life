# 			 [     mysql-innoDB-多版本并发控制(MVCC)        ](https://www.cnblogs.com/happyflyingpig/p/7718678.html) 		

　　InnoDB的MVCC,是通过在每行记录后面保存**三个**隐藏的列来实现的其中的两个列一个保存了行的创建时间，一个保存行的过期时间(或删除时间)。当然存储的并不是实际的时间值，而是系统版本号(system version number)：

　　1、DB_TRX_ID ：6字节的事务ID，每处理一个事务，其值自动+1，上述说的 “创建时间”和 “删除时间” 记录的就是这个DB_TRX_ID值，DB_TRX_ID是最重要的一个，可以通过“show engine innodb status”来查

　　2、DB_ROLL_PTR:大小时7byte，指向写到rollback segment(回滚段)的一条undo log记录(update操作的话，记录update前的row值)

　　3、DB_ROLL_ID:大小是6字节，该值随新行插入单调增加，**当由innodb自动产生聚集索引时，聚集索引包括这个DB_ROW_ID的值，不然的话聚集索引中不包括这个值（我的理解是如果聚集索引不是自动产生的话，就不会有DB_ROLL_ID这个值）。** 这个用于索引当中
　　MVCC只在REPEATABLE READ和READ COMMITTED两个隔离级别下工作。其他两个隔离级别都和MVCC不兼容。下面看一下在REPEATABLE READ隔离级别下，MVCC具体是如何操作的

　　***SELECT\***

- - InnoDB只查找版本早于当前事务版本的数据行(也就是行的系统版本号必须小于等于事务的版本)，这确保当前事务读取的行都是事务之前已经存在的，或者是由当前事务创建或修改过的。
  - 行的删除操作的版本一定是未定义的或者大于当前事务的版本号。确定了当前事务开始之前，行没有被删除

　　只有符合上述两点才能返回查询结果。

　　***INSERT***

　　　　InnoDB为每个新增行记录当前系统版本号作为创建ID

　　***DELETE***

 　　　InnoDB为删除的每一行保存当前系统版本号作为行删除标识

　　***UPDATE***　

　　　　InnoDB为插入一行新记录，保存当前系统版本号作为行版本号，同事保存当前系统版本号到原来的行作为行删除标识

参考：

[1] 《高性能MySQL》(第三版)， Baron Schwartz等 著，宁海元等 译，电子工业出版社 ，2013

[2] 博客，http://www.cnblogs.com/chenpingzhao/p/5065316.html

[3] 博客，https://www.percona.com/blog/2014/12/17/innodbs-multi-versioning-handling-can-be-achilles-heel/

[4] 博客，http://blogread.cn/it/article/5969

[5] 博客，http://blog.csdn.net/chen77716/article/details/6742128

[6] 博客，http://blog.chinaunix.net/link.php?url=http://forge.mysql.com%2Fwiki%2FMySQL_Internals