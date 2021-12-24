已剪辑自: https://blog.csdn.net/woqutechteam/article/details/80265473
|  RC与RR隔离级别下MySQL不同的加锁解锁方式
	• MySQL5.7.21
	• 数据准备
root@localhost : pxs 05:26:27> show create table dots\G
*************************** 1. row ***************************
  Table: dots
Create Table: CREATE TABLE `dots` (
`id` int(11) NOT NULL,
`color` varchar(20) COLLATE utf8_bin NOT NULL,
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
1 row in set (0.00 sec)
root@localhost : pxs 05:27:34> select * from dots;
+----+-------+
| id | color |
+----+-------+
|  1 | black |
|  2 | white |
|  3 | black |
|  4 | white |
+----+-------+
4 rows in set (0.00 sec)
root@localhost : pxs 01:57:02> show variables like 'innodb_locks_unsafe_for_binlog';
+--------------------------------+-------+
| Variable_name                  | Value |
+--------------------------------+-------+
| innodb_locks_unsafe_for_binlog | OFF  |
+--------------------------------+-------+
1 row in set (0.00 sec)



root@localhost : pxs 05:27:35> show variables like '%iso%';
+-----------------------+----------------+
| Variable_name        | Value          |
+-----------------------+----------------+
| transaction_isolation | READ-COMMITTED |
| tx_isolation          | READ-COMMITTED |
+-----------------------+----------------+
2 rows in set (0.01 sec)



	• 同时开启两个会话，按下图的流程开始操作。



root@localhost : pxs 05:24:41> show variables like '%iso%';
+-----------------------+-----------------+
| Variable_name        | Value          |
+-----------------------+-----------------+
| transaction_isolation | REPEATABLE-READ |
| tx_isolation          | REPEATABLE-READ |
+-----------------------+-----------------+
2 rows in set (0.01 sec)



	• 同时开启两个会话，按下图的流程开始操作。



3.半一致读semi-consistent read
	• RC隔离级别
	• RR隔离级别，且innodb_locks_unsafe_for_binlog=true
3.2 innodb_locks_unsafe_for_binlog
	• innodb_locks_unsafe_for_binlog默认为off。 

	• 如果设置为1，会禁用gap锁，但对于外键冲突检测（foreign-key constraint checking）或者重复键检测（duplicate-key checking）还是会用到gap锁。  
	• 启用innodb_locks_unsafe_for_binlog产生的影响等同于将隔离级别设置为RC，不同之处是：
1）innodb_locks_unsafe_for_binlog是全局参数，影响所有session；但隔离级别可以是全局也可以是会话级别。
2）innodb_locks_unsafe_for_binlog只能在数据库启动的时候设置；但隔离级别可以随时更改。   
基于上述原因，RC相比于innodb_locks_unsafe_for_binlog会更好更灵活。 
启用innodb_locks_unsafe_for_binlog还有以下作用：
	• 对于update或者delete语句，InnoDB只会持有匹配条件的记录的锁。在MySQL Server过滤where条件，发现不满足后，会把不满足条件的记录释放锁。这可以大幅降低死锁发生的概率。 

	• 简单来说，semi-consistent read是read committed与consistent read两者的结合。一个update语句，如果读到一行已经加锁的记录，此时InnoDB返回记录最近提交的版本，由MySQL上层判断此版本是否满足update的where条件。若满足(需要更新)，则MySQL会重新发起一次读操作，此时会读取行的最新版本(并加锁)。
来看下面这个例子：
CREATE TABLE t (a INT NOT NULL, b INT) ENGINE = InnoDB; 
INSERT INTO t VALUES (1,2),(2,3),(3,2),(4,3),(5,2); 
COMMIT;



这个例子中，表上没有索引，所以对于记录锁会用到隐藏主键。
假设某个client开启了一个update：
SET autocommit = 0; 
UPDATE t SET b = 5 WHERE b = 3;



假设另一个client紧接着也开启一个update：
SET autocommit = 0; 
UPDATE t SET b = 4 WHERE b = 2;



每当InnoDB发起update，会先对每一行记录加上排它锁，然后再决定记录是否满足条件。如果不匹配，则innodb_locks_unsafe_for_binlog开启，InnoDB就会把记录上的锁释放掉。否则，InnoDB会一直持有锁直到事务结束。具体如下：
如果innodb_locks_unsafe_for_binlog没有开启，第一个update会一直持有x锁
x-lock(1,2); retain x-lock 
x-lock(2,3); update(2,3) to (2,5); retain x-lock 
x-lock(3,2); retain x-lock 
x-lock(4,3); update(4,3) to (4,5); retain x-lock 
x-lock(5,2); retain x-lock



第二个update会阻塞住直到第一个update提交或者回滚
x-lock(1,2); block and wait for first UPDATE to commit or roll back



如果innodb_locks_unsafe_for_binlog开启，第一个update先持有x锁，然后会释放不匹配的记录上面的x锁
x-lock(1,2); unlock(1,2) 
x-lock(2,3); update(2,3) to (2,5); retain x-lock 
x-lock(3,2); unlock(3,2) 
x-lock(4,3); update(4,3) to (4,5); retain x-lock 
x-lock(5,2); unlock(5,2)



对于第二个update，InnoDB会开启半一致读，此时InnoDB返回记录最近提交的版本，由MySQL上层判断此版本是否满足update的where条件。
x-lock(1,2); update(1,2) to (1,4); retain x-lock 
x-lock(2,3); unlock(2,3) 
x-lock(3,2); update(3,2) to (3,4); retain x-lock 
x-lock(4,3); unlock(4,3) 
x-lock(5,2); update(5,2) to (5,4); retain x-lock



session 1执行：
update dots set color = 'black' where color = 'white'; 



由于color列无索引，因此只能走聚簇索引，进行全部扫描。加锁如下： 

注：如果一个条件无法通过索引快速过滤，那么存储引擎层面就会将所有记录加锁后返回，然后由MySQL Server层进行过滤。因此也就把所有的记录，都锁上了。
但在实际中，MySQL做了优化，如同前面作用1所提到的。在MySQL Server过滤条件，发现不满足后，会调用unlock_row方法，把不满足条件的记录放锁 (违背了2PL的约束)。这样做，保证了最后只会持有满足条件记录上的锁，但是每条记录的加锁操作还是不能省略的。 
实际加锁如下： 



session 2执行：
update dots set color = 'white' where color = 'black'; 


session 2尝试加锁的时候，发现行上已经存在锁，InnoDB会开启semi-consistent read，返回最新的committed版本(1,black),(2，white),(3,black),(4,white)。MySQL会重新发起一次读操作，此时会读取行的最新版本(并加锁)。如同前面作用2所提到的。 

加锁如下： 

MySQL优化后实际加锁如下： 



session 1执行：
update dots set color = 'black' where color = 'white'; 



由于color列无索引，因此只能走聚簇索引，进行全部扫描。加锁如下： 


session 2执行：
update dots set color = 'white' where color = 'black';

更新被阻塞。 
等session 1提交commit之后，session 2update才会成功。



引申：RR隔离级别，且开启innodb_locks_unsafe_for_binlog=ON
root@localhost : (none) 04:57:46> show  variables like '%iso%';
+-----------------------+-----------------+
| Variable_name        | Value          |
+-----------------------+-----------------+
| transaction_isolation | REPEATABLE-READ |
| tx_isolation          | REPEATABLE-READ |
+-----------------------+-----------------+
2 rows in set (0.01 sec)
root@localhost : (none) 04:55:25> show variables like 'innodb_locks_unsafe_for_binlog';
+--------------------------------+-------+
| Variable_name                  | Value |
+--------------------------------+-------+
| innodb_locks_unsafe_for_binlog | ON    |
+--------------------------------+-------+
1 row in set (0.00 sec)
root@localhost : pxs 05:00:54> select * from dots;
+----+-------+
| id | color |
+----+-------+
|  1 | black |
|  2 | white |
|  3 | black |
|  4 | white |
+----+-------+
4 rows in set (0.00 sec)






注：过程现象满足RR隔离级别，也符合设置innodb_locks_unsafe_for_binlog=ON的情况。因为前面所讲的启用innodb_locks_unsafe_for_binlog会产生作用1与作用2，所以整个加锁与解锁情况与RC隔离级别类似。


《数据库事务处理的艺术：事务管理与并发控制》 
https://dev.mysql.com/doc/refman/5.5/en/innodb-parameters.html#sysvar_innodb_locks_unsafe_for_binlog 
http://hedengcheng.com/?p=771 
http://hedengcheng.com/?p=220


韩杰  沃趣科技MySQL数据库工程师
熟悉mysql体系架构、主从复制，熟悉问题定位与解决。