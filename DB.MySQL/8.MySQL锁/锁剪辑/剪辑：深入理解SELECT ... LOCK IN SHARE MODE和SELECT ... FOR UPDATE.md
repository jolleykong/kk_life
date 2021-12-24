# 深入理解SELECT ... LOCK IN SHARE MODE和SELECT ... FOR UPDATE

​                           

# 概念和区别

SELECT ... LOCK IN SHARE  MODE走的是IS锁(意向共享锁)，即在符合条件的rows上都加了共享锁，这样的话，其他session可以读取这些记录，也可以继续添加IS锁，但是无法修改这些记录直到你这个加锁的session执行完成(否则直接锁等待超时)。

 SELECT ... FOR UPDATE  走的是IX锁(意向排它锁)，即在符合条件的rows上都加了排它锁，其他session也就无法在这些记录上添加任何的S锁或X锁。如果不存在一致性非锁定读的话，那么其他session是无法读取和修改这些记录的，但是innodb有非锁定读(快照读并不需要加锁)，for update之后并不会阻塞其他session的快照读取操作，除了select ...lock in share mode和select ... for update这种显示加锁的查询操作。

 通过对比，发现for update的加锁方式无非是比lock in share mode的方式多阻塞了select...lock in share mode的查询方式，并不会阻塞快照读。



# 应用场景

在我看来，SELECT ... LOCK IN SHARE  MODE的应用场景适合于两张表存在关系时的写操作，拿mysql官方文档的例子来说，一个表是child表，一个是parent表，假设child表的某一列child_id映射到parent表的c_child_id列，那么从业务角度讲，此时我直接insert一条child_id=100记录到child表是存在风险的，因为刚insert的时候可能在parent表里删除了这条c_child_id=100的记录，那么业务数据就存在不一致的风险。正确的方法是再插入时执行select * from parent where c_child_id=100 lock in share  mode,锁定了parent表的这条记录，然后执行insert into child(child_id) values (100)就ok了。


 但是如果是同一张表的应用场景，举个例子，电商系统中计算一种商品的剩余数量，在产生订单之前需要确认商品数量>=1,产生订单之后应该将商品数量减1。
 1 select amount from product where product_name='XX';
 2 update product set amount=amount-1 where product_name='XX';


 显然1的做法是是有问题，因为如果1查询出amount为1，但是这时正好其他session也买了该商品并产生了订单，那么amount就变成了0，那么这时第二步再执行就有问题。
 那么采用lock in share mode可行吗，也是不合理的，因为两个session同时锁定该行记录时，这时两个session再update时必然会产生死锁导致事务回滚。以下是操作范例(按时间顺序)


 session1
 mysql> begin;
 Query OK, 0 rows affected (0.00 sec)


 mysql> select * from test_jjj lock in share mode;
 +-----+------------+
 | id  | name    |
 +-----+------------+
 | 234 | asdasdy123 |
 | 123 | jjj     |
 +-----+------------+
 2 rows in set (0.00 sec)


 session2(同样锁定了相同的行)
 mysql> begin;
 Query OK, 0 rows affected (0.00 sec)


 mysql> select * from test_jjj lock in share mode;
 +-----+------------+
 | id  | name    |
 +-----+------------+
 | 234 | asdasdy123 |
 | 123 | jjj     |
 +-----+------------+
 2 rows in set (0.00 sec)


 session1(这时session1再update时就会引起锁等待)
 mysql> update test_jjj set name='jjj1' where name='jjj';


 session2(这时session2同样update就会检测到死锁，回滚session2，注意执行时间不要超过session1的锁等待超时检测时间，即不要超过innodb_lock_wait_timeout设置的值)
 mysql> update test_jjj set name='jjj1' where name='jjj';
 ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction


 session1(此时session1执行完成)
 mysql> update test_jjj set name='jjj1' where name='jjj';
 Query OK, 1 row affected (29.20 sec)
 Rows matched: 1  Changed: 1  Warnings: 0


 通过该案例可知lock in share mode的方式在这个场景中不适用，我们需要使用for  update的方式直接加X锁，从而短暂地阻塞session2的select...for update操作;以下是操作范例


 session1
 mysql> begin;
 Query OK, 0 rows affected (0.00 sec)


 mysql> select * from test_jjj for update;
 +-----+------------+
 | id  | name    |
 +-----+------------+
 | 234 | asdasdy123 |
 | 123 | jjj1    |
 +-----+------------+
 2 rows in set (0.00 sec)


 session2(此时session2处于锁等待状态，得不到结果)
 mysql> begin;
 Query OK, 0 rows affected (0.00 sec)


 mysql> select * from test_jjj for update;


 session1(这时session1 update之后提交，可完成)
 mysql> update test_jjj set name='jjj1' where name='jjj';
 Query OK, 0 rows affected (0.00 sec)
 Rows matched: 0  Changed: 0  Warnings: 0


 mysql> commit;
 Query OK, 0 rows affected (0.00 sec)


 session2(session1提交之后session2刚才的查询结果就出来了，也就可以再次update往下执行了)
 mysql> select * from test_jjj for update;
 +-----+------------+
 | id  | name    |
 +-----+------------+
 | 234 | asdasdy123 |
 | 123 | jjj1    |
 +-----+------------+
 2 rows in set (37.19 sec)
 mysql> select * from test_jjj for update;
 +-----+------------+
 | id  | name    |
 +-----+------------+
 | 234 | asdasdy123 |
 | 123 | jjj1    |
 +-----+------------+
 2 rows in set (37.19 sec)


 mysql> update test_jjj set name='jjj1' where name='jjj';
 Query OK, 0 rows affected (0.00 sec)
 Rows matched: 0  Changed: 0  Warnings: 0


 mysql> commit;

Query OK, 0 rows affected (0.00 sec)

通过对比，lock in share mode适用于两张表存在业务关系时的一致性要求，for  update适用于操作同一张表时的一致性要求。