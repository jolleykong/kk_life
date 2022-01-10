# 探索：小IBP大事务导致1206错误的原因

> 事件回顾：在MySQL5.7下为了验证独立表空间时，在大事务未提交时，会导致ibdata扩大（因为undo）。在实验过程中：
>
> ibp size = 100M 
>
> ```
> set autocommit=0;
> Create Table: CREATE TABLE `k1` (
>   `id` int(11) NOT NULL AUTO_INCREMENT,
>   `name` varchar(10) NOT NULL DEFAULT 'a',
>   PRIMARY KEY (`id`)
> ) ENGINE=InnoDB AUTO_INCREMENT=68418523 DEFAULT CHARSET=utf8mb4
> 
> mysql> insert into k1(name) select name from k1;
> Query OK, 0 rows affected (0.00 sec)
> Records: 0  Duplicates: 0  Warnings: 0
> 
> mysql> insert into k1(name) select name from k1;
> Query OK, 0 rows affected (0.00 sec)
> Records: 0  Duplicates: 0  Warnings: 0
> 
> mysql> insert into k1(name) select 'aaaaa';
> Query OK, 1 row affected (0.01 sec)
> Records: 1  Duplicates: 0  Warnings: 0
> 
> mysql> insert into k1(name) select name from k1;
> Query OK, 1 row affected (0.00 sec)
> Records: 1  Duplicates: 0  Warnings: 0
> 
> mysql> insert into k1(name) select name from k1;
> Query OK, 2 rows affected (0.00 sec)
> Records: 2  Duplicates: 0  Warnings: 0
> ...
> mysql> insert into k1(name) select name from k1;
> Query OK, 8388608 rows affected (2 min 11.94 sec)
> Records: 8388608  Duplicates: 0  Warnings: 0
> 
> mysql> insert into k1(name) select name from k1;
> Query OK, 16777216 rows affected (4 min 34.97 sec)
> Records: 16777216  Duplicates: 0  Warnings: 0
> 
> mysql> select count(*) from k1;
> +----------+
> | count(*) |
> +----------+
> | 33554432 |
> +----------+
> 1 row in set (17.91 sec)
> 
> mysql> insert into k1(name) select name from k1;
> ERROR 1206 (HY000): The total number of locks exceeds the lock table size
> 
> mysql> select count(*) from k1;
> +----------+
> | count(*) |
> +----------+
> |        0 |
> +----------+
> 1 row in set (0.00 sec)
> 
> ```
>
> 期间检查error log ，有如下信息
>
> ```
> 2021-01-08T18:01:14.539166+08:00 2 [Warning] InnoDB: Over 67 percent of the buffer pool is occupied by lock heaps or the adaptive hash index! Check that your transactions do not set too many row locks. Your buffer pool size is 100 MB. Maybe you should make the buffer pool bigger?. Starting the InnoDB Monitor to print diagnostics, including lock heap and hash index sizes.
> 
> =====================================
> 2021-01-08 18:01:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
> =====================================
> Per second averages calculated from the last 33 seconds
> ...
> ...
> ```
>
> 并自动打印engine status monitor信息。
>
> 通过检查对比引擎状态，可以发现在最大事务量的那次动作会引发roll back。
>
> 为什么呢？



日志中出现rolling back 的第一条记录

```
=====================================
2021-01-08 18:10:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1344 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3627
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6982
OS WAIT ARRAY INFO: signal count 9471
RW-shared spins 0, rounds 16929, OS waits 4002
RW-excl spins 0, rounds 21128, OS waits 566
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16929.00 RW-shared, 21128.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1115 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 651459 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 33121259
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
40.55 hash searches/s, 42565.02 non-hash searches/s
---
LOG
---
Log sequence number 4670882003
Log flushed up to   4670232301
Pages flushed up to 4661657778
Last checkpoint at  4661657778
0 pending log flushes, 0 pending chkp writes
3354 log i/o's done, 0.90 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1058
Database pages     541
Old database pages 179
Modified db pages  404
Pending reads      1
Pending writes: LRU 53, flush list 3, single page 0
Pages made young 8632, not young 164333929
0.00 youngs/s, 0.00 non-youngs/s
Pages read 465700, created 364036, written 462309
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 598 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 541, unzip_LRU len: 0
I/O sum[13314]:cur[153], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
89814.36 inserts/s, 0.00 updates/s, 0.00 deletes/s, 89814.36 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================

```

Total large memory allocated 107380736

ROLLING BACK 651459 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 33121259

记录中出现回滚时的两个指标

ibp max size = 107380736/1024/1024=102.4M

1st rollback heap size = 78635216/1024/1024=74M

lru = free buffer + database pages = 1599 * 16 / 1024 = 24.9844 M

heap size + lru 小于100M

 

传说free list + lru list < buffer pool / 4 则会使得事务终止，未经论证。。





 第一条回滚动作前的最后一条innodb engin status状态节选。

考虑到出现回滚动作和记录日志之间会有时间差，也就是上面的记录并不一定是内存被占用到极致时的状态。

```
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1095 sec fetching rows
mysql tables in use 2, locked 2
652025 lock struct(s), heap size 77603024, 79787445 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1662
Old database pages 594
Modified db pages  1315
Pending reads      17
Pending writes: LRU 0, flush list 129, single page 0
Pages made young 8622, not young 160682750
0.00 youngs/s, 0.00 non-youngs/s
Pages read 461056, created 361261, written 457387
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 978 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1662, unzip_LRU len: 0
I/O sum[13200]:cur[245], unzip sum[0]:cur[0]

```

heap size 77603024 /1024/1024=74M

1662*1024*16 = 27230208, 27230208/1024/1024 = 25.96M 

heap size + lru + ahi 约等于 ibp

74+25.96 =100M 

事务的heap size和lru加一起几乎吃满了IBP，因此事务失败，回滚。



参考资料

https://www.jianshu.com/p/fed9a601d768

https://www.jianshu.com/p/f8d0b051d2f8



日志全文

```
2021-01-08T17:53:04.440149+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4005ms. The settings might not be optimal. (flushed=195 and evicted=866, during the time.)
2021-01-08T17:53:45.161732+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4711ms. The settings might not be optimal. (flushed=312 and evicted=806, during the time.)
2021-01-08T17:53:58.949666+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4842ms. The settings might not be optimal. (flushed=306 and evicted=880, during the time.)
2021-01-08T17:55:23.952733+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4307ms. The settings might not be optimal. (flushed=273 and evicted=872, during the time.)
2021-01-08T17:55:31.998683+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4175ms. The settings might not be optimal. (flushed=272 and evicted=736, during the time.)
2021-01-08T17:55:52.846257+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4651ms. The settings might not be optimal. (flushed=301 and evicted=851, during the time.)
2021-01-08T17:56:04.826256+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4039ms. The settings might not be optimal. (flushed=288 and evicted=714, during the time.)
2021-01-08T17:56:19.998827+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 5239ms. The settings might not be optimal. (flushed=283 and evicted=780, during the time.)
2021-01-08T17:58:50.347998+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4171ms. The settings might not be optimal. (flushed=180 and evicted=827, during the time.)
2021-01-08T17:59:11.510274+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4154ms. The settings might not be optimal. (flushed=206 and evicted=803, during the time.)
2021-01-08T17:59:40.765303+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4278ms. The settings might not be optimal. (flushed=200 and evicted=800, during the time.)
2021-01-08T17:59:53.188362+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4155ms. The settings might not be optimal. (flushed=197 and evicted=754, during the time.)
2021-01-08T18:00:09.189674+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4954ms. The settings might not be optimal. (flushed=186 and evicted=878, during the time.)
2021-01-08T18:00:21.504547+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4388ms. The settings might not be optimal. (flushed=178 and evicted=833, during the time.)
2021-01-08T18:00:48.290594+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4018ms. The settings might not be optimal. (flushed=163 and evicted=776, during the time.)
2021-01-08T18:00:59.879880+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4275ms. The settings might not be optimal. (flushed=161 and evicted=847, during the time.)
2021-01-08T18:01:14.539166+08:00 2 [Warning] InnoDB: Over 67 percent of the buffer pool is occupied by lock heaps or the adaptive hash index! Check that your transactions do not set too many row locks. Your buffer pool size is 100 MB. Maybe you should make the buffer pool bigger?. Starting the InnoDB Monitor to print diagnostics, including lock heap and hash index sizes.

=====================================
2021-01-08 18:01:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 33 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1311 srv_active, 0 srv_shutdown, 1781 srv_idle
srv_master_thread log flush and writes: 3091
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5627
OS WAIT ARRAY INFO: signal count 8035
RW-shared spins 0, rounds 13808, OS waits 2686
RW-excl spins 0, rounds 20704, OS waits 557
RW-sx spins 965, rounds 28468, OS waits 941
Spin rounds per wait: 13808.00 RW-shared, 20704.00 RW-excl, 29.50 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1462
Purge done for trx's n:o < 1462 undo n:o < 0 state: running but idle
History list length 22
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 575 sec
mysql tables in use 2, locked 2
595502 lock struct(s), heap size 70230224, 65216100 row lock(s), undo log entries 31602484
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root Sending data
insert into k1(name) select name from k1
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [32, 0, 0, 49] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 1; buffer pool: 1
352539 OS file reads, 429159 OS file writes, 17793 OS fsyncs
137.09 reads/s, 16384 avg bytes/read, 268.96 writes/s, 15.70 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
87406.26 hash searches/s, 831.61 non-hash searches/s
---
LOG
---
Log sequence number 4550171455
Log flushed up to   4542276068
Pages flushed up to 4511752137
Last checkpoint at  4466052350
1 pending log flushes, 0 pending chkp writes
3279 log i/o's done, 1.41 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       25
Database pages     2087
Old database pages 768
Modified db pages  1836
Pending reads      0
Pending writes: LRU 82, flush list 0, single page 1
Pages made young 8284, not young 134079240
0.00 youngs/s, 0.00 non-youngs/s
Pages read 352506, created 320143, written 415627
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 2087, unzip_LRU len: 0
I/O sum[12968]:cur[124], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: flushing log
Number of rows inserted 156127063, updated 0, deleted 0, read 156127069
87908.15 inserts/s, 0.00 updates/s, 0.00 deletes/s, 87908.03 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================




2021-01-08T18:01:21.975344+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4150ms. The settings might not be optimal. (flushed=159 and evicted=860, during the time.)
2021-01-08T18:01:35.242799+08:00 0 [Note] InnoDB: page_cleaner: 1000ms intended loop took 4879ms. The settings might not be optimal. (flushed=161 and evicted=904, during the time.)

=====================================
2021-01-08 18:01:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1328 srv_active, 0 srv_shutdown, 1781 srv_idle
srv_master_thread log flush and writes: 3109
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5652
OS WAIT ARRAY INFO: signal count 8129
RW-shared spins 0, rounds 13924, OS waits 2690
RW-excl spins 0, rounds 20981, OS waits 562
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 13924.00 RW-shared, 20981.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 595 sec inserting
mysql tables in use 2, locked 2
622418 lock struct(s), heap size 73294032, 66816187 row lock(s), undo log entries 33199581
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root Sending data
insert into k1(name) select name from k1
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 27, 52] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 1
355037 OS file reads, 433997 OS file writes, 18103 OS fsyncs
124.89 reads/s, 16384 avg bytes/read, 241.89 writes/s, 15.50 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
79393.63 hash searches/s, 757.01 non-hash searches/s
---
LOG
---
Log sequence number 4641354731
Log flushed up to   4637779187
Pages flushed up to 4606718854
Last checkpoint at  4579343106
0 pending log flushes, 0 pending chkp writes
3314 log i/o's done, 1.75 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       11
Database pages     1914
Old database pages 686
Modified db pages  1689
Pending reads      0
Pending writes: LRU 81, flush list 0, single page 1
Pages made young 8285, not young 134081806
0.00 youngs/s, 0.00 non-youngs/s
Pages read 355004, created 324609, written 420269
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1914, unzip_LRU len: 0
I/O sum[12492]:cur[123], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 157724160, updated 0, deleted 0, read 157724167
79850.86 inserts/s, 0.00 updates/s, 0.00 deletes/s, 79850.91 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:01:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1794 srv_idle
srv_master_thread log flush and writes: 3127
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5661
OS WAIT ARRAY INFO: signal count 8151
RW-shared spins 0, rounds 13960, OS waits 2698
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 13960.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 615 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
355616 OS file reads, 436693 OS file writes, 18242 OS fsyncs
28.95 reads/s, 16384 avg bytes/read, 134.79 writes/s, 6.95 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
17640.47 hash searches/s, 167.64 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 1.10 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1024
Database pages     859
Old database pages 297
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8287, not young 134084957
0.00 youngs/s, 0.00 non-youngs/s
Pages read 355583, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 2 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 859, unzip_LRU len: 0
I/O sum[10153]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 158079017
17741.66 inserts/s, 0.00 updates/s, 0.00 deletes/s, 17741.61 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:02:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1814 srv_idle
srv_master_thread log flush and writes: 3147
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5661
OS WAIT ARRAY INFO: signal count 8151
RW-shared spins 0, rounds 13960, OS waits 2698
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 13960.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 635 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
355616 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1024
Database pages     859
Old database pages 297
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8287, not young 134084957
0.00 youngs/s, 0.00 non-youngs/s
Pages read 355583, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 859, unzip_LRU len: 0
I/O sum[5091]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 158079017
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:02:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1834 srv_idle
srv_master_thread log flush and writes: 3167
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5661
OS WAIT ARRAY INFO: signal count 8151
RW-shared spins 0, rounds 13960, OS waits 2698
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 13960.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 655 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
355616 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1024
Database pages     859
Old database pages 297
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8287, not young 134084957
0.00 youngs/s, 0.00 non-youngs/s
Pages read 355583, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 859, unzip_LRU len: 0
I/O sum[435]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 158079017
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:02:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1854 srv_idle
srv_master_thread log flush and writes: 3187
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 5661
OS WAIT ARRAY INFO: signal count 8151
RW-shared spins 0, rounds 13960, OS waits 2698
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 13960.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 675 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 153 localhost root
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
355616 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1024
Database pages     859
Old database pages 297
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8287, not young 134084957
0.00 youngs/s, 0.00 non-youngs/s
Pages read 355583, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 859, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
0 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 158079017
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:03:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1874 srv_idle
srv_master_thread log flush and writes: 3207
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6095
OS WAIT ARRAY INFO: signal count 8585
RW-shared spins 0, rounds 14937, OS waits 3132
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 14937.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 695 sec
mysql tables in use 1, locked 0
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root Sending data
select count(*) from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
386283 OS file reads, 436693 OS file writes, 18242 OS fsyncs
1533.27 reads/s, 16384 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 714
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 135925862
0.00 youngs/s, 0.00 non-youngs/s
Pages read 386250, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 984 / 1000, young-making rate 0 / 1000 not 981 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[584]:cur[32], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 174417234
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 816871.21 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:03:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1894 srv_idle
srv_master_thread log flush and writes: 3227
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 715 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
1592.92 reads/s, 16384 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 984 / 1000, young-making rate 0 / 1000 not 980 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[1135]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 860765.41 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:03:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1914 srv_idle
srv_master_thread log flush and writes: 3247
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 735 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[1135]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:04:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1934 srv_idle
srv_master_thread log flush and writes: 3267
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 755 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:04:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1954 srv_idle
srv_master_thread log flush and writes: 3287
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 775 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:04:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1974 srv_idle
srv_master_thread log flush and writes: 3307
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 795 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:05:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 1994 srv_idle
srv_master_thread log flush and writes: 3327
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 815 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:05:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 2014 srv_idle
srv_master_thread log flush and writes: 3347
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 835 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:05:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 2034 srv_idle
srv_master_thread log flush and writes: 3367
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 1381, ACTIVE 855 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418143 OS file reads, 436693 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1
Database pages     1882
Old database pages 713
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864349
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418110, created 325600, written 422954
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1882, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:06:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1333 srv_active, 0 srv_shutdown, 2054 srv_idle
srv_master_thread log flush and writes: 3387
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 875 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418145 OS file reads, 436696 OS file writes, 18242 OS fsyncs
0.10 reads/s, 16384 avg bytes/read, 0.15 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1025
Database pages     858
Old database pages 296
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864519
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418112, created 325600, written 422957
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 991 / 1000, young-making rate 0 / 1000 not 809 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 858, unzip_LRU len: 0
I/O sum[0]:cur[5], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:06:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1334 srv_active, 0 srv_shutdown, 2073 srv_idle
srv_master_thread log flush and writes: 3407
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 895 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418145 OS file reads, 436696 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1025
Database pages     858
Old database pages 296
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864519
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418112, created 325600, written 422957
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 858, unzip_LRU len: 0
I/O sum[5]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:06:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1334 srv_active, 0 srv_shutdown, 2093 srv_idle
srv_master_thread log flush and writes: 3427
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 915 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418145 OS file reads, 436696 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1025
Database pages     858
Old database pages 296
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864519
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418112, created 325600, written 422957
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 858, unzip_LRU len: 0
I/O sum[5]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:07:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1334 srv_active, 0 srv_shutdown, 2113 srv_idle
srv_master_thread log flush and writes: 3447
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 935 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418145 OS file reads, 436696 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1025
Database pages     858
Old database pages 296
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864519
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418112, created 325600, written 422957
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 858, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:07:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1334 srv_active, 0 srv_shutdown, 2133 srv_idle
srv_master_thread log flush and writes: 3467
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6538
OS WAIT ARRAY INFO: signal count 9030
RW-shared spins 0, rounds 15988, OS waits 3575
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 15988.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 955 sec
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 154 localhost root
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
418145 OS file reads, 436696 OS file writes, 18242 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1025
Database pages     858
Old database pages 296
Modified db pages  0
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8288, not young 137864519
0.00 youngs/s, 0.00 non-youngs/s
Pages read 418112, created 325600, written 422957
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
No buffer pool page gets since the last printout
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 858, unzip_LRU len: 0
I/O sum[0]:cur[0], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 158079011, updated 0, deleted 0, read 191633449
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:07:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2152 srv_idle
srv_master_thread log flush and writes: 3487
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6588
OS WAIT ARRAY INFO: signal count 9080
RW-shared spins 0, rounds 16088, OS waits 3625
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16088.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 975 sec fetching rows
mysql tables in use 2, locked 2
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 9, 0] , aio writes: [32, 0, 54, 36] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
422922 OS file reads, 439540 OS file writes, 18242 OS fsyncs
238.84 reads/s, 16384 avg bytes/read, 142.19 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 675
Modified db pages  1443
Pending reads      9
Pending writes: LRU 0, flush list 123, single page 0
Pages made young 8618, not young 140243771
0.00 youngs/s, 0.00 non-youngs/s
Pages read 422880, created 329751, written 425679
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 867 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[3051]:cur[242], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 160765148, updated 0, deleted 0, read 194319585
134300.23 inserts/s, 0.00 updates/s, 0.00 deletes/s, 134300.23 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:08:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2172 srv_idle
srv_master_thread log flush and writes: 3507
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6634
OS WAIT ARRAY INFO: signal count 9126
RW-shared spins 0, rounds 16183, OS waits 3671
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16183.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 995 sec fetching rows
mysql tables in use 2, locked 2
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [4, 57, 38, 23] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
429386 OS file reads, 444846 OS file writes, 18242 OS fsyncs
323.18 reads/s, 16384 avg bytes/read, 265.29 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 675
Modified db pages  1496
Pending reads      0
Pending writes: LRU 0, flush list 122, single page 0
Pages made young 8618, not young 143712432
0.00 youngs/s, 0.00 non-youngs/s
Pages read 429353, created 335099, written 430985
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 980 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[8451]:cur[250], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 164227312, updated 0, deleted 0, read 197781749
173099.40 inserts/s, 0.00 updates/s, 0.00 deletes/s, 173099.35 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:08:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2192 srv_idle
srv_master_thread log flush and writes: 3527
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6683
OS WAIT ARRAY INFO: signal count 9175
RW-shared spins 0, rounds 16286, OS waits 3720
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16286.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1015 sec fetching rows
mysql tables in use 2, locked 2
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [1, 0, 0, 0] , aio writes: [36, 58, 0, 35] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
435787 OS file reads, 450147 OS file writes, 18242 OS fsyncs
320.03 reads/s, 16384 avg bytes/read, 265.04 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 675
Modified db pages  1467
Pending reads      1
Pending writes: LRU 0, flush list 129, single page 0
Pages made young 8619, not young 147122594
0.00 youngs/s, 0.00 non-youngs/s
Pages read 435753, created 340356, written 436280
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 980 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[13480]:cur[229], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 167630402, updated 0, deleted 0, read 201184840
170145.59 inserts/s, 0.00 updates/s, 0.00 deletes/s, 170145.59 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:08:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2212 srv_idle
srv_master_thread log flush and writes: 3547
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6736
OS WAIT ARRAY INFO: signal count 9228
RW-shared spins 0, rounds 16396, OS waits 3773
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16396.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1035 sec fetching rows
mysql tables in use 2, locked 2
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [35, 42, 0, 51] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
442380 OS file reads, 455588 OS file writes, 18242 OS fsyncs
329.63 reads/s, 16384 avg bytes/read, 272.04 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 675
Modified db pages  1490
Pending reads      0
Pending writes: LRU 0, flush list 128, single page 0
Pages made young 8619, not young 150658979
0.00 youngs/s, 0.00 non-youngs/s
Pages read 442347, created 345808, written 441721
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 978 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[13667]:cur[250], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 171160194, updated 0, deleted 0, read 204714626
176480.93 inserts/s, 0.00 updates/s, 0.00 deletes/s, 176480.88 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:09:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2232 srv_idle
srv_master_thread log flush and writes: 3567
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6796
OS WAIT ARRAY INFO: signal count 9288
RW-shared spins 0, rounds 16520, OS waits 3833
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16520.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1055 sec fetching rows
mysql tables in use 2, locked 2
628399 lock struct(s), heap size 73982160, 67171703 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 16] , aio writes: [37, 36, 7, 40] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
448848 OS file reads, 460906 OS file writes, 18242 OS fsyncs
323.38 reads/s, 16384 avg bytes/read, 265.89 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1883
Old database pages 675
Modified db pages  1497
Pending reads      16
Pending writes: LRU 0, flush list 120, single page 0
Pages made young 8621, not young 154110126
0.00 youngs/s, 0.00 non-youngs/s
Pages read 448799, created 351128, written 447047
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 978 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1883, unzip_LRU len: 0
I/O sum[13650]:cur[252], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 174604182, updated 0, deleted 0, read 208158619
172190.44 inserts/s, 0.00 updates/s, 0.00 deletes/s, 172190.39 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:09:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2252 srv_idle
srv_master_thread log flush and writes: 3587
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6841
OS WAIT ARRAY INFO: signal count 9333
RW-shared spins 0, rounds 16614, OS waits 3878
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16614.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1075 sec fetching rows
mysql tables in use 2, locked 2
639663 lock struct(s), heap size 75702480, 73185847 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [55, 0, 23, 36] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
454929 OS file reads, 466070 OS file writes, 18242 OS fsyncs
304.03 reads/s, 16384 avg bytes/read, 258.19 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1778
Old database pages 636
Modified db pages  1375
Pending reads      0
Pending writes: LRU 0, flush list 114, single page 0
Pages made young 8622, not young 157375901
0.00 youngs/s, 0.00 non-youngs/s
Pages read 454896, created 356163, written 452217
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 978 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1778, unzip_LRU len: 0
I/O sum[13449]:cur[236], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 177863444, updated 0, deleted 0, read 211417882
162954.75 inserts/s, 0.00 updates/s, 0.00 deletes/s, 162954.70 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:09:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1335 srv_active, 0 srv_shutdown, 2272 srv_idle
srv_master_thread log flush and writes: 3607
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6892
OS WAIT ARRAY INFO: signal count 9384
RW-shared spins 0, rounds 16720, OS waits 3929
RW-excl spins 0, rounds 21038, OS waits 563
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16720.00 RW-shared, 21038.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1095 sec fetching rows
mysql tables in use 2, locked 2
652025 lock struct(s), heap size 77603024, 79787445 row lock(s), undo log entries 33554432
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 17, 0] , aio writes: [48, 51, 30, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
461106 OS file reads, 471255 OS file writes, 18242 OS fsyncs
308.83 reads/s, 16384 avg bytes/read, 259.24 writes/s, 0.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
0.00 hash searches/s, 0.00 non-hash searches/s
---
LOG
---
Log sequence number 4661614102
Log flushed up to   4661614102
Pages flushed up to 4661614102
Last checkpoint at  4661614093
0 pending log flushes, 0 pending chkp writes
3336 log i/o's done, 0.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       0
Database pages     1662
Old database pages 594
Modified db pages  1315
Pending reads      17
Pending writes: LRU 0, flush list 129, single page 0
Pages made young 8622, not young 160682750
0.00 youngs/s, 0.00 non-youngs/s
Pages read 461056, created 361261, written 457387
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 999 / 1000, young-making rate 0 / 1000 not 978 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 1662, unzip_LRU len: 0
I/O sum[13200]:cur[245], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 181164098, updated 0, deleted 0, read 214718536
165024.20 inserts/s, 0.00 updates/s, 0.00 deletes/s, 165024.20 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:10:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1344 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3627
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 6982
OS WAIT ARRAY INFO: signal count 9471
RW-shared spins 0, rounds 16929, OS waits 4002
RW-excl spins 0, rounds 21128, OS waits 566
RW-sx spins 974, rounds 28738, OS waits 950
Spin rounds per wait: 16929.00 RW-shared, 21128.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1115 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 651459 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 33121259
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466

-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
40.55 hash searches/s, 42565.02 non-hash searches/s
---
LOG
---
Log sequence number 4670882003
Log flushed up to   4670232301
Pages flushed up to 4661657778
Last checkpoint at  4661657778
0 pending log flushes, 0 pending chkp writes
3354 log i/o's done, 0.90 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1058
Database pages     541
Old database pages 179
Modified db pages  404
Pending reads      1
Pending writes: LRU 53, flush list 3, single page 0
Pages made young 8632, not young 164333929
0.00 youngs/s, 0.00 non-youngs/s
Pages read 465700, created 364036, written 462309
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 598 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 541, unzip_LRU len: 0
I/O sum[13314]:cur[153], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
89814.36 inserts/s, 0.00 updates/s, 0.00 deletes/s, 89814.36 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:10:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1362 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3645
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7067
OS WAIT ARRAY INFO: signal count 9553
RW-shared spins 0, rounds 17125, OS waits 4038
RW-excl spins 0, rounds 21368, OS waits 574
RW-sx spins 978, rounds 28858, OS waits 954
Spin rounds per wait: 17125.00 RW-shared, 21368.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1135 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 631704 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 31949465
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [11, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
469032 OS file reads, 479329 OS file writes, 18446 OS fsyncs
1 pending preads, 0 pending pwrites
164.89 reads/s, 16384 avg bytes/read, 159.29 writes/s, 7.50 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
109.79 hash searches/s, 115088.70 non-hash searches/s
---
LOG
---
Log sequence number 4695954697
Log flushed up to   4695665030
Pages flushed up to 4681917001
Last checkpoint at  4670342868
0 pending log flushes, 0 pending chkp writes
3393 log i/o's done, 1.95 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1008
Database pages     591
Old database pages 198
Modified db pages  567
Pending reads      1
Pending writes: LRU 13, flush list 0, single page 0
Pages made young 8634, not young 168872601
0.00 youngs/s, 0.00 non-youngs/s
Pages read 468998, created 364036, written 465436
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 393 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 591, unzip_LRU len: 0
I/O sum[12254]:cur[146], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:10:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1381 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3664
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7156
OS WAIT ARRAY INFO: signal count 9644
RW-shared spins 0, rounds 17318, OS waits 4066
RW-excl spins 0, rounds 21698, OS waits 585
RW-sx spins 986, rounds 29098, OS waits 962
Spin rounds per wait: 17318.00 RW-shared, 21698.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1155 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 612606 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 30815874
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
472223 OS file reads, 482722 OS file writes, 18644 OS fsyncs
159.54 reads/s, 16384 avg bytes/read, 169.64 writes/s, 9.90 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
106.09 hash searches/s, 111333.13 non-hash searches/s
---
LOG
---
Log sequence number 4720208553
Log flushed up to   4719841392
Pages flushed up to 4705111084
Last checkpoint at  4696484633
0 pending log flushes, 0 pending chkp writes
3448 log i/o's done, 2.75 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1070
Database pages     529
Old database pages 179
Modified db pages  488
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8635, not young 173136510
0.00 youngs/s, 0.00 non-youngs/s
Pages read 472190, created 364036, written 468707
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 382 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 529, unzip_LRU len: 0
I/O sum[11393]:cur[47], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:11:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1399 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3682
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7217
OS WAIT ARRAY INFO: signal count 9706
RW-shared spins 0, rounds 17371, OS waits 4072
RW-excl spins 0, rounds 21878, OS waits 591
RW-sx spins 990, rounds 29218, OS waits 966
Spin rounds per wait: 17371.00 RW-shared, 21878.00 RW-excl, 29.51 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1175 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 594282 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 29729023
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 1
475275 OS file reads, 485845 OS file writes, 18821 OS fsyncs
152.59 reads/s, 16384 avg bytes/read, 156.14 writes/s, 8.85 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
101.79 hash searches/s, 106757.61 non-hash searches/s
---
LOG
---
Log sequence number 4743464023
Log flushed up to   4743317873
Pages flushed up to 4726328171
Last checkpoint at  4724111472
0 pending log flushes, 0 pending chkp writes
3490 log i/o's done, 2.10 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1023
Database pages     576
Old database pages 193
Modified db pages  530
Pending reads      0
Pending writes: LRU 11, flush list 0, single page 0
Pages made young 8636, not young 177253911
0.00 youngs/s, 0.00 non-youngs/s
Pages read 475242, created 364036, written 471715
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 384 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 576, unzip_LRU len: 0
I/O sum[10428]:cur[138], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:11:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1418 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3701
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7305
OS WAIT ARRAY INFO: signal count 9794
RW-shared spins 0, rounds 17542, OS waits 4104
RW-excl spins 0, rounds 22178, OS waits 601
RW-sx spins 997, rounds 29428, OS waits 973
Spin rounds per wait: 17542.00 RW-shared, 22178.00 RW-excl, 29.52 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1195 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 575607 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 28620875
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 17, 38, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
478429 OS file reads, 489032 OS file writes, 19006 OS fsyncs
1 pending preads, 0 pending pwrites
157.69 reads/s, 16384 avg bytes/read, 159.34 writes/s, 9.25 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
103.74 hash searches/s, 108847.51 non-hash searches/s
---
LOG
---
Log sequence number 4767173359
Log flushed up to   4766684974
Pages flushed up to 4758343096
Last checkpoint at  4747585865
0 pending log flushes, 0 pending chkp writes
3543 log i/o's done, 2.65 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       895
Database pages     704
Old database pages 239
Modified db pages  641
Pending reads      1
Pending writes: LRU 57, flush list 0, single page 0
Pages made young 8643, not young 181114496
0.00 youngs/s, 0.00 non-youngs/s
Pages read 478395, created 364036, written 474722
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 353 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 704, unzip_LRU len: 0
I/O sum[10241]:cur[153], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:11:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 2 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1436 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3719
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7390
OS WAIT ARRAY INFO: signal count 9881
RW-shared spins 0, rounds 17709, OS waits 4131
RW-excl spins 0, rounds 22508, OS waits 612
RW-sx spins 1001, rounds 29548, OS waits 977
Spin rounds per wait: 17709.00 RW-shared, 22508.00 RW-excl, 29.52 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1215 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 555330 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 27417527
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 8, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
481800 OS file reads, 492636 OS file writes, 19193 OS fsyncs
192.40 reads/s, 16384 avg bytes/read, 204.40 writes/s, 10.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
130.43 hash searches/s, 137199.90 non-hash searches/s
---
LOG
---
Log sequence number 4792920293
Log flushed up to   4792059276
Pages flushed up to 4783182674
Last checkpoint at  4775199936
0 pending log flushes, 0 pending chkp writes
3591 log i/o's done, 1.00 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1021
Database pages     578
Old database pages 233
Modified db pages  505
Pending reads      0
Pending writes: LRU 0, flush list 8, single page 0
Pages made young 8647, not young 185564867
0.00 youngs/s, 0.00 non-youngs/s
Pages read 481767, created 364036, written 478247
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 355 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 578, unzip_LRU len: 0
I/O sum[10905]:cur[48], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:12:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1455 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3738
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7480
OS WAIT ARRAY INFO: signal count 9976
RW-shared spins 0, rounds 17960, OS waits 4173
RW-excl spins 0, rounds 22778, OS waits 621
RW-sx spins 1003, rounds 29608, OS waits 979
Spin rounds per wait: 17960.00 RW-shared, 22778.00 RW-excl, 29.52 RW-sx
FAIL TO OBTAIN LOCK MUTEX, SKIP LOCK INFO PRINTING
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
484881 OS file reads, 495675 OS file writes, 19356 OS fsyncs
0 pending preads, 1 pending pwrites
154.04 reads/s, 16384 avg bytes/read, 151.94 writes/s, 8.15 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
103.24 hash searches/s, 108259.04 non-hash searches/s
---
LOG
---
Log sequence number 4816509299
Log flushed up to   4816247987
Pages flushed up to 4804444402
Last checkpoint at  4801336590
0 pending log flushes, 0 pending chkp writes
3630 log i/o's done, 1.95 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       904
Database pages     695
Old database pages 236
Modified db pages  662
Pending reads      0
Pending writes: LRU 121, flush list 0, single page 0
Pages made young 8651, not young 189391898
0.00 youngs/s, 0.00 non-youngs/s
Pages read 484848, created 364036, written 481187
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 352 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 695, unzip_LRU len: 0
I/O sum[10582]:cur[273], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:12:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1473 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3756
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7576
OS WAIT ARRAY INFO: signal count 10075
RW-shared spins 0, rounds 18146, OS waits 4215
RW-excl spins 0, rounds 23138, OS waits 633
RW-sx spins 1010, rounds 29818, OS waits 986
Spin rounds per wait: 18146.00 RW-shared, 23138.00 RW-excl, 29.52 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1255 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 517620 lock struct(s), heap size 78635216, 83380199 row lock(s), undo log entries 25180427
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [40, 38, 1, 7] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
488068 OS file reads, 498908 OS file writes, 19536 OS fsyncs
1 pending preads, 0 pending pwrites
159.34 reads/s, 16384 avg bytes/read, 161.64 writes/s, 9.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
106.24 hash searches/s, 111456.18 non-hash searches/s
---
LOG
---
Log sequence number 4840786039
Log flushed up to   4838344894
Pages flushed up to 4823068176
Last checkpoint at  4822828343
0 pending log flushes, 0 pending chkp writes
3679 log i/o's done, 2.45 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       749
Database pages     850
Old database pages 314
Modified db pages  830
Pending reads      1
Pending writes: LRU 88, flush list 0, single page 0
Pages made young 8652, not young 193291481
0.00 youngs/s, 0.00 non-youngs/s
Pages read 488034, created 364036, written 484214
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 349 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 850, unzip_LRU len: 0
I/O sum[10224]:cur[166], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:12:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1492 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3775
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7668
OS WAIT ARRAY INFO: signal count 10167
RW-shared spins 0, rounds 18379, OS waits 4253
RW-excl spins 0, rounds 23468, OS waits 644
RW-sx spins 1015, rounds 29968, OS waits 991
Spin rounds per wait: 18379.00 RW-shared, 23468.00 RW-excl, 29.53 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1275 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 493902 lock struct(s), heap size 78880976, 83380199 row lock(s), undo log entries 23974478
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 8, 0, 0] , aio writes: [0, 0, 0, 11] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
491537 OS file reads, 502610 OS file writes, 19723 OS fsyncs
173.44 reads/s, 16384 avg bytes/read, 185.09 writes/s, 9.35 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
112.89 hash searches/s, 118450.68 non-hash searches/s
---
LOG
---
Log sequence number 4867652949
Log flushed up to   4867495344
Pages flushed up to 4849995755
Last checkpoint at  4849995755
0 pending log flushes, 0 pending chkp writes
3730 log i/o's done, 2.55 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       943
Database pages     641
Old database pages 252
Modified db pages  577
Pending reads      8
Pending writes: LRU 11, flush list 2, single page 0
Pages made young 8655, not young 198106269
0.00 youngs/s, 0.00 non-youngs/s
Pages read 491496, created 364036, written 487862
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 405 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 641, unzip_LRU len: 0
I/O sum[10684]:cur[150], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:13:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1510 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3793
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7767
OS WAIT ARRAY INFO: signal count 10267
RW-shared spins 0, rounds 18658, OS waits 4292
RW-excl spins 0, rounds 23828, OS waits 656
RW-sx spins 1022, rounds 30178, OS waits 998
Spin rounds per wait: 18658.00 RW-shared, 23828.00 RW-excl, 29.53 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1295 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 470692 lock struct(s), heap size 79208656, 83380199 row lock(s), undo log entries 22847699
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [12, 0, 0, 7] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
494651 OS file reads, 505961 OS file writes, 19900 OS fsyncs
1 pending preads, 0 pending pwrites
155.69 reads/s, 16384 avg bytes/read, 167.54 writes/s, 8.85 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
105.49 hash searches/s, 110681.12 non-hash searches/s
---
LOG
---
Log sequence number 4893015308
Log flushed up to   4892223841
Pages flushed up to 4882064281
Last checkpoint at  4876427321
0 pending log flushes, 0 pending chkp writes
3774 log i/o's done, 2.20 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1011
Database pages     553
Old database pages 224
Modified db pages  526
Pending reads      1
Pending writes: LRU 0, flush list 19, single page 0
Pages made young 8671, not young 201745165
0.00 youngs/s, 0.00 non-youngs/s
Pages read 494617, created 364036, written 491086
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 328 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 553, unzip_LRU len: 0
I/O sum[11036]:cur[64], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:13:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1529 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3812
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 7894
--Thread 140530867619584 has waited at mtr0mtr.ic line 161 for 0  seconds the semaphore:
X-lock on RW-latch at 0x7fcff4be0768 created in file buf0buf.cc line 1468
a writer (thread id 140530781476608) has reserved it in mode  SX
number of readers 0, waiters flag 1, lock_word: 10000000
Last time read locked in file row0row.cc line 999
Last time write locked in file /export/home/pb2/build/sb_0-38465026-1584987238.22/mysql-5.7.30/storage/innobase/buf/buf0flu.cc line 1217
OS WAIT ARRAY INFO: signal count 10395
RW-shared spins 0, rounds 18948, OS waits 4364
RW-excl spins 0, rounds 24140, OS waits 666
RW-sx spins 1032, rounds 30449, OS waits 1007
Spin rounds per wait: 18948.00 RW-shared, 24140.00 RW-excl, 29.50 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1315 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 448956 lock struct(s), heap size 79519952, 83380199 row lock(s), undo log entries 21792403
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [4, 2, 4, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
497625 OS file reads, 509163 OS file writes, 20087 OS fsyncs
148.69 reads/s, 16384 avg bytes/read, 160.09 writes/s, 9.35 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
98.80 hash searches/s, 103637.07 non-hash searches/s
---
LOG
---
Log sequence number 4916768729
Log flushed up to   4916768729
Pages flushed up to 4910238983
Last checkpoint at  4900868595
0 pending log flushes, 0 pending chkp writes
3825 log i/o's done, 2.55 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1108
Database pages     437
Old database pages 0
Modified db pages  416
Pending reads      0
Pending writes: LRU 0, flush list 12, single page 0
Pages made young 8698, not young 204595299
0.00 youngs/s, 0.00 non-youngs/s
Pages read 497592, created 364036, written 494175
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 274 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 437, unzip_LRU len: 0
I/O sum[10638]:cur[134], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:13:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1547 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3830
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8005
OS WAIT ARRAY INFO: signal count 10508
RW-shared spins 0, rounds 19157, OS waits 4405
RW-excl spins 0, rounds 24440, OS waits 676
RW-sx spins 1055, rounds 31139, OS waits 1030
Spin rounds per wait: 19157.00 RW-shared, 24440.00 RW-excl, 29.52 RW-sx
FAIL TO OBTAIN LOCK MUTEX, SKIP LOCK INFO PRINTING
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
500688 OS file reads, 512218 OS file writes, 20293 OS fsyncs
0 pending preads, 1 pending pwrites
153.14 reads/s, 16384 avg bytes/read, 152.74 writes/s, 10.30 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
101.04 hash searches/s, 106007.55 non-hash searches/s
---
LOG
---
Log sequence number 4941060916
Log flushed up to   4940419322
Pages flushed up to 4934182683
Last checkpoint at  4929680171
0 pending log flushes, 0 pending chkp writes
3881 log i/o's done, 2.80 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       954
Database pages     573
Old database pages 199
Modified db pages  536
Pending reads      0
Pending writes: LRU 121, flush list 0, single page 0
Pages made young 8744, not young 206878407
0.00 youngs/s, 0.00 non-youngs/s
Pages read 500655, created 364036, written 497108
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 214 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 573, unzip_LRU len: 0
I/O sum[10222]:cur[153], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:14:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1566 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3849
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8154
OS WAIT ARRAY INFO: signal count 10658
RW-shared spins 0, rounds 19507, OS waits 4491
RW-excl spins 0, rounds 24950, OS waits 693
RW-sx spins 1071, rounds 31595, OS waits 1045
Spin rounds per wait: 19507.00 RW-shared, 24950.00 RW-excl, 29.50 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1355 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 405935 lock struct(s), heap size 80109776, 83380199 row lock(s), undo log entries 19704271
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 5, 14] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
503555 OS file reads, 515336 OS file writes, 20489 OS fsyncs
143.34 reads/s, 16384 avg bytes/read, 155.89 writes/s, 9.80 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
94.50 hash searches/s, 99108.64 non-hash searches/s
---
LOG
---
Log sequence number 4963773463
Log flushed up to   4963658314
Pages flushed up to 4955717372
Last checkpoint at  4945816723
0 pending log flushes, 0 pending chkp writes
3935 log i/o's done, 2.70 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1074
Database pages     435
Old database pages 0
Modified db pages  420
Pending reads      0
Pending writes: LRU 0, flush list 19, single page 0
Pages made young 8774, not young 209231485
0.00 youngs/s, 0.00 non-youngs/s
Pages read 503522, created 364036, written 500083
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 236 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 435, unzip_LRU len: 0
I/O sum[10148]:cur[42], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:14:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1585 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3868
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8359
OS WAIT ARRAY INFO: signal count 10865
RW-shared spins 0, rounds 20080, OS waits 4631
RW-excl spins 0, rounds 25430, OS waits 709
RW-sx spins 1088, rounds 32054, OS waits 1060
Spin rounds per wait: 20080.00 RW-shared, 25430.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1375 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 385112 lock struct(s), heap size 80404688, 83380199 row lock(s), undo log entries 18693473
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [17, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
506528 OS file reads, 518346 OS file writes, 20678 OS fsyncs
148.64 reads/s, 16384 avg bytes/read, 150.49 writes/s, 9.45 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
94.65 hash searches/s, 99266.14 non-hash searches/s
---
LOG
---
Log sequence number 4986524903
Log flushed up to   4986457238
Pages flushed up to 4980122678
Last checkpoint at  4978620140
0 pending log flushes, 0 pending chkp writes
3988 log i/o's done, 2.65 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1083
Database pages     408
Old database pages 0
Modified db pages  397
Pending reads      0
Pending writes: LRU 0, flush list 17, single page 0
Pages made young 8812, not young 211488674
0.00 youngs/s, 0.00 non-youngs/s
Pages read 506495, created 364036, written 502974
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 226 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 408, unzip_LRU len: 0
I/O sum[9670]:cur[42], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:14:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1603 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3886
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8550
OS WAIT ARRAY INFO: signal count 11057
RW-shared spins 0, rounds 20767, OS waits 4766
RW-excl spins 0, rounds 25790, OS waits 721
RW-sx spins 1098, rounds 32354, OS waits 1070
Spin rounds per wait: 20767.00 RW-shared, 25790.00 RW-excl, 29.47 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1395 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 363816 lock struct(s), heap size 80699600, 83380199 row lock(s), undo log entries 17659218
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
509530 OS file reads, 521322 OS file writes, 20857 OS fsyncs
150.09 reads/s, 16384 avg bytes/read, 148.79 writes/s, 8.95 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
96.80 hash searches/s, 101609.07 non-hash searches/s
---
LOG
---
Log sequence number 5009803329
Log flushed up to   5009030751
Pages flushed up to 5004474785
Last checkpoint at  5002841226
0 pending log flushes, 0 pending chkp writes
4034 log i/o's done, 2.30 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       981
Database pages     492
Old database pages 0
Modified db pages  441
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 8850, not young 213391591
0.00 youngs/s, 0.00 non-youngs/s
Pages read 509497, created 364036, written 505856
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 186 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 492, unzip_LRU len: 0
I/O sum[9736]:cur[50], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:15:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1622 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3905
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8625
OS WAIT ARRAY INFO: signal count 11133
RW-shared spins 0, rounds 21041, OS waits 4783
RW-excl spins 0, rounds 26001, OS waits 729
RW-sx spins 1114, rounds 32834, OS waits 1086
Spin rounds per wait: 21041.00 RW-shared, 26001.00 RW-excl, 29.47 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1415 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 341605 lock struct(s), heap size 81010896, 83380199 row lock(s), undo log entries 16581479
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [10, 56, 26, 5] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
512630 OS file reads, 524574 OS file writes, 21029 OS fsyncs
1 pending preads, 0 pending pwrites
154.99 reads/s, 16384 avg bytes/read, 162.59 writes/s, 8.60 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
100.94 hash searches/s, 105837.11 non-hash searches/s
---
LOG
---
Log sequence number 5034057916
Log flushed up to   5033714859
Pages flushed up to 5029438043
Last checkpoint at  5029195108
0 pending log flushes, 0 pending chkp writes
4079 log i/o's done, 2.25 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       963
Database pages     491
Old database pages 0
Modified db pages  446
Pending reads      1
Pending writes: LRU 99, flush list 0, single page 0
Pages made young 8925, not young 214358987
0.00 youngs/s, 0.00 non-youngs/s
Pages read 512596, created 364036, written 508899
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 91 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 491, unzip_LRU len: 0
I/O sum[9985]:cur[136], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:15:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1640 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3923
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8732
OS WAIT ARRAY INFO: signal count 11240
RW-shared spins 0, rounds 21305, OS waits 4821
RW-excl spins 0, rounds 26393, OS waits 742
RW-sx spins 1145, rounds 33755, OS waits 1116
Spin rounds per wait: 21305.00 RW-shared, 26393.00 RW-excl, 29.48 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1435 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 321024 lock struct(s), heap size 81289424, 83380199 row lock(s), undo log entries 15582339
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 40] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
515438 OS file reads, 527558 OS file writes, 21219 OS fsyncs
140.39 reads/s, 16384 avg bytes/read, 149.19 writes/s, 9.50 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
93.60 hash searches/s, 98138.59 non-hash searches/s
---
LOG
---
Log sequence number 5056549253
Log flushed up to   5055912185
Pages flushed up to 5052561295
Last checkpoint at  5044251003
0 pending log flushes, 0 pending chkp writes
4129 log i/o's done, 2.50 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1021
Database pages     416
Old database pages 0
Modified db pages  371
Pending reads      0
Pending writes: LRU 40, flush list 2, single page 0
Pages made young 8977, not young 215253613
0.00 youngs/s, 0.00 non-youngs/s
Pages read 515405, created 364036, written 511821
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 90 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 416, unzip_LRU len: 0
I/O sum[10024]:cur[101], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:15:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1659 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3942
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 8879
OS WAIT ARRAY INFO: signal count 11388
RW-shared spins 0, rounds 21685, OS waits 4904
RW-excl spins 0, rounds 26753, OS waits 754
RW-sx spins 1176, rounds 34661, OS waits 1146
Spin rounds per wait: 21685.00 RW-shared, 26753.00 RW-excl, 29.47 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1455 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 303512 lock struct(s), heap size 81535184, 83380199 row lock(s), undo log entries 14731939
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
517915 OS file reads, 529912 OS file writes, 21412 OS fsyncs
0 pending preads, 1 pending pwrites
123.84 reads/s, 16384 avg bytes/read, 117.69 writes/s, 9.65 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
79.60 hash searches/s, 83515.72 non-hash searches/s
---
LOG
---
Log sequence number 5075692439
Log flushed up to   5075568191
Pages flushed up to 5070641264
Last checkpoint at  5067157701
0 pending log flushes, 0 pending chkp writes
4186 log i/o's done, 2.85 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       847
Database pages     575
Old database pages 196
Modified db pages  539
Pending reads      0
Pending writes: LRU 121, flush list 0, single page 0
Pages made young 8995, not young 215676471
0.00 youngs/s, 0.00 non-youngs/s
Pages read 517882, created 364036, written 514097
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 50 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 575, unzip_LRU len: 0
I/O sum[9213]:cur[171], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:16:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1677 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3960
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9063
OS WAIT ARRAY INFO: signal count 11573
RW-shared spins 0, rounds 22299, OS waits 5033
RW-excl spins 0, rounds 27323, OS waits 773
RW-sx spins 1193, rounds 35147, OS waits 1162
Spin rounds per wait: 22299.00 RW-shared, 27323.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1475 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 282447 lock struct(s), heap size 81830096, 83380199 row lock(s), undo log entries 13709237
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [9, 37, 45, 17] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
520871 OS file reads, 533090 OS file writes, 21593 OS fsyncs
147.79 reads/s, 16384 avg bytes/read, 158.89 writes/s, 9.05 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
95.75 hash searches/s, 100468.43 non-hash searches/s
---
LOG
---
Log sequence number 5098714747
Log flushed up to   5097302174
Pages flushed up to 5094623673
Last checkpoint at  5088805202
0 pending log flushes, 0 pending chkp writes
4237 log i/o's done, 2.55 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       876
Database pages     528
Old database pages 205
Modified db pages  487
Pending reads      0
Pending writes: LRU 109, flush list 0, single page 0
Pages made young 9030, not young 217551683
0.00 youngs/s, 0.00 non-youngs/s
Pages read 520838, created 364036, written 517052
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 186 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 528, unzip_LRU len: 0
I/O sum[8916]:cur[153], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:16:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1696 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3979
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9154
OS WAIT ARRAY INFO: signal count 11666
RW-shared spins 0, rounds 22554, OS waits 5064
RW-excl spins 0, rounds 27743, OS waits 787
RW-sx spins 1219, rounds 35927, OS waits 1188
Spin rounds per wait: 22554.00 RW-shared, 27743.00 RW-excl, 29.47 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1495 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 261899 lock struct(s), heap size 82108624, 83380199 row lock(s), undo log entries 12712061
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
523710 OS file reads, 536096 OS file writes, 21777 OS fsyncs
141.94 reads/s, 16384 avg bytes/read, 150.29 writes/s, 9.20 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
93.40 hash searches/s, 97933.75 non-hash searches/s
---
LOG
---
Log sequence number 5121163737
Log flushed up to   5120338574
Pages flushed up to 5118302480
Last checkpoint at  5114341400
0 pending log flushes, 0 pending chkp writes
4290 log i/o's done, 2.65 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       926
Database pages     461
Old database pages 0
Modified db pages  347
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 9072, not young 217972624
0.00 youngs/s, 0.00 non-youngs/s
Pages read 523677, created 364036, written 520047
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 42 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 461, unzip_LRU len: 0
I/O sum[9441]:cur[33], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:16:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1714 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 3997
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9287
OS WAIT ARRAY INFO: signal count 11806
RW-shared spins 0, rounds 22892, OS waits 5135
RW-excl spins 0, rounds 28163, OS waits 801
RW-sx spins 1243, rounds 36619, OS waits 1211
Spin rounds per wait: 22892.00 RW-shared, 28163.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1515 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 239349 lock struct(s), heap size 82436304, 83380199 row lock(s), undo log entries 11616969
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 2, 7] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
526811 OS file reads, 539301 OS file writes, 21947 OS fsyncs
155.04 reads/s, 16384 avg bytes/read, 160.24 writes/s, 8.50 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
102.49 hash searches/s, 107555.02 non-hash searches/s
---
LOG
---
Log sequence number 5145814609
Log flushed up to   5145340165
Pages flushed up to 5141470044
Last checkpoint at  5136497683
0 pending log flushes, 0 pending chkp writes
4340 log i/o's done, 2.50 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       979
Database pages     388
Old database pages 0
Modified db pages  387
Pending reads      0
Pending writes: LRU 11, flush list 0, single page 0
Pages made young 9126, not young 218720040
0.00 youngs/s, 0.00 non-youngs/s
Pages read 526778, created 364036, written 523127
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 69 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 388, unzip_LRU len: 0
I/O sum[9972]:cur[20], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:17:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1733 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4016
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9413
--Thread 140530867619584 has waited at fut0fut.ic line 65 for 0  seconds the semaphore:
SX-lock on RW-latch at 0x7fcff4dc6280 created in file buf0buf.cc line 1468
a writer (thread id 140530781476608) has reserved it in mode  SX
number of readers 0, waiters flag 1, lock_word: 10000000
Last time read locked in file trx0undo.ic line 198
Last time write locked in file /export/home/pb2/build/sb_0-38465026-1584987238.22/mysql-5.7.30/storage/innobase/buf/buf0flu.cc line 1179
OS WAIT ARRAY INFO: signal count 11937
RW-shared spins 0, rounds 23194, OS waits 5196
RW-excl spins 0, rounds 28755, OS waits 820
RW-sx spins 1262, rounds 37161, OS waits 1229
Spin rounds per wait: 23194.00 RW-shared, 28755.00 RW-excl, 29.45 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1535 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 219934 lock struct(s), heap size 82698448, 83380199 row lock(s), undo log entries 10674724
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [13, 101, 0, 1] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
529534 OS file reads, 542267 OS file writes, 22118 OS fsyncs
136.14 reads/s, 16384 avg bytes/read, 148.29 writes/s, 8.55 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
88.25 hash searches/s, 92555.47 non-hash searches/s
---
LOG
---
Log sequence number 5167026467
Log flushed up to   5167017387
Pages flushed up to 5163829388
Last checkpoint at  5162282771
0 pending log flushes, 0 pending chkp writes
4387 log i/o's done, 2.35 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       946
Database pages     405
Old database pages 0
Modified db pages  349
Pending reads      0
Pending writes: LRU 117, flush list 0, single page 0
Pages made young 9151, not young 218805985
0.00 youngs/s, 0.00 non-youngs/s
Pages read 529501, created 364036, written 525876
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 9 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 405, unzip_LRU len: 0
I/O sum[9593]:cur[141], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:17:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1752 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4035
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9531
OS WAIT ARRAY INFO: signal count 12057
RW-shared spins 0, rounds 23459, OS waits 5248
RW-excl spins 0, rounds 29115, OS waits 832
RW-sx spins 1294, rounds 38106, OS waits 1260
Spin rounds per wait: 23459.00 RW-shared, 29115.00 RW-excl, 29.45 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1555 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 200156 lock struct(s), heap size 82976976, 83380199 row lock(s), undo log entries 9714701
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 3] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 1; buffer pool: 0
532276 OS file reads, 545160 OS file writes, 22311 OS fsyncs
1 pending preads, 0 pending pwrites
137.09 reads/s, 16384 avg bytes/read, 144.64 writes/s, 9.65 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
89.90 hash searches/s, 94282.24 non-hash searches/s
---
LOG
---
Log sequence number 5188638504
Log flushed up to   5188617452
Pages flushed up to 5186584660
Last checkpoint at  5185780274
1 pending log flushes, 0 pending chkp writes
4443 log i/o's done, 2.80 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1022
Database pages     312
Old database pages 0
Modified db pages  221
Pending reads      1
Pending writes: LRU 2, flush list 3, single page 0
Pages made young 9177, not young 219217735
0.00 youngs/s, 0.00 non-youngs/s
Pages read 532242, created 364036, written 528757
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 43 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 312, unzip_LRU len: 0
I/O sum[9782]:cur[47], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:17:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1771 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4054
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9608
OS WAIT ARRAY INFO: signal count 12133
RW-shared spins 0, rounds 23573, OS waits 5260
RW-excl spins 0, rounds 29565, OS waits 847
RW-sx spins 1320, rounds 38886, OS waits 1286
Spin rounds per wait: 23573.00 RW-shared, 29565.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1575 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 182633 lock struct(s), heap size 83222736, 83380199 row lock(s), undo log entries 8864019
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 17, 6] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
534737 OS file reads, 547694 OS file writes, 22477 OS fsyncs
123.04 reads/s, 16384 avg bytes/read, 126.69 writes/s, 8.30 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
79.65 hash searches/s, 83562.32 non-hash searches/s
---
LOG
---
Log sequence number 5207789660
Log flushed up to   5207720906
Pages flushed up to 5205238534
Last checkpoint at  5199810247
0 pending log flushes, 0 pending chkp writes
4490 log i/o's done, 2.35 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       987
Database pages     332
Old database pages 0
Modified db pages  276
Pending reads      0
Pending writes: LRU 25, flush list 0, single page 0
Pages made young 9183, not young 219217871
0.00 youngs/s, 0.00 non-youngs/s
Pages read 534704, created 364036, written 531167
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 332, unzip_LRU len: 0
I/O sum[9003]:cur[16], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:18:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1789 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4072
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9692
OS WAIT ARRAY INFO: signal count 12219
RW-shared spins 0, rounds 23702, OS waits 5267
RW-excl spins 0, rounds 30135, OS waits 866
RW-sx spins 1348, rounds 39702, OS waits 1313
Spin rounds per wait: 23702.00 RW-shared, 30135.00 RW-excl, 29.45 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1595 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 164712 lock struct(s), heap size 83468496, 83380199 row lock(s), undo log entries 7994246
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
537188 OS file reads, 550358 OS file writes, 22678 OS fsyncs
122.54 reads/s, 16384 avg bytes/read, 133.19 writes/s, 10.05 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
81.45 hash searches/s, 85449.03 non-hash searches/s
---
LOG
---
Log sequence number 5227369964
Log flushed up to   5227097415
Pages flushed up to 5225462527
Last checkpoint at  5220761920
0 pending log flushes, 0 pending chkp writes
4552 log i/o's done, 3.10 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       957
Database pages     347
Old database pages 0
Modified db pages  250
Pending reads      0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 9193, not young 219297007
0.00 youngs/s, 0.00 non-youngs/s
Pages read 537155, created 364036, written 533730
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 9 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 347, unzip_LRU len: 0
I/O sum[8398]:cur[31], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:18:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1808 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4091
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9770
OS WAIT ARRAY INFO: signal count 12301
RW-shared spins 0, rounds 23825, OS waits 5276
RW-excl spins 0, rounds 30615, OS waits 882
RW-sx spins 1374, rounds 40482, OS waits 1339
Spin rounds per wait: 23825.00 RW-shared, 30615.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1615 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 145803 lock struct(s), heap size 83730640, 83380199 row lock(s), undo log entries 7075990
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 1, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
539807 OS file reads, 553019 OS file writes, 22843 OS fsyncs
130.94 reads/s, 16384 avg bytes/read, 133.04 writes/s, 8.25 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
85.95 hash searches/s, 90159.14 non-hash searches/s
---
LOG
---
Log sequence number 5248039992
Log flushed up to   5247872933
Pages flushed up to 5245128864
Last checkpoint at  5239527226
0 pending log flushes, 0 pending chkp writes
4604 log i/o's done, 2.60 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       898
Database pages     390
Old database pages 0
Modified db pages  355
Pending reads      0
Pending writes: LRU 3, flush list 0, single page 0
Pages made young 9203, not young 219422883
0.00 youngs/s, 0.00 non-youngs/s
Pages read 539774, created 364036, written 536280
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 13 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 390, unzip_LRU len: 0
I/O sum[8562]:cur[34], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:18:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1826 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4109
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9843
OS WAIT ARRAY INFO: signal count 12377
RW-shared spins 0, rounds 23881, OS waits 5283
RW-excl spins 0, rounds 31215, OS waits 902
RW-sx spins 1399, rounds 41203, OS waits 1362
Spin rounds per wait: 23881.00 RW-shared, 31215.00 RW-excl, 29.45 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1635 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 129974 lock struct(s), heap size 83960016, 83380199 row lock(s), undo log entries 6307389
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 7] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
541981 OS file reads, 555587 OS file writes, 23021 OS fsyncs
108.69 reads/s, 16384 avg bytes/read, 128.39 writes/s, 8.90 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
72.00 hash searches/s, 75512.52 non-hash searches/s
---
LOG
---
Log sequence number 5265343792
Log flushed up to   5265085480
Pages flushed up to 5264026294
Last checkpoint at  5260049430
0 pending log flushes, 0 pending chkp writes
4650 log i/o's done, 2.30 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       1098
Database pages     176
Old database pages 0
Modified db pages  146
Pending reads      0
Pending writes: LRU 0, flush list 7, single page 0
Pages made young 9203, not young 219422883
0.00 youngs/s, 0.00 non-youngs/s
Pages read 541948, created 364036, written 538734
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 176, unzip_LRU len: 0
I/O sum[8387]:cur[53], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:19:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1845 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4128
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 9932
OS WAIT ARRAY INFO: signal count 12466
RW-shared spins 0, rounds 23967, OS waits 5292
RW-excl spins 0, rounds 31846, OS waits 924
RW-sx spins 1422, rounds 41893, OS waits 1385
Spin rounds per wait: 23967.00 RW-shared, 31846.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1655 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 112506 lock struct(s), heap size 84189392, 83380199 row lock(s), undo log entries 5459596
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [3, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
544421 OS file reads, 558043 OS file writes, 23207 OS fsyncs
121.99 reads/s, 16384 avg bytes/read, 122.79 writes/s, 9.30 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
79.35 hash searches/s, 83277.04 non-hash searches/s
---
LOG
---
Log sequence number 5284427369
Log flushed up to   5283609003
Pages flushed up to 5282321478
Last checkpoint at  5279607260
0 pending log flushes, 0 pending chkp writes
4701 log i/o's done, 2.55 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       925
Database pages     335
Old database pages 0
Modified db pages  270
Pending reads      0
Pending writes: LRU 0, flush list 3, single page 0
Pages made young 9203, not young 219422883
0.00 youngs/s, 0.00 non-youngs/s
Pages read 544388, created 364036, written 541081
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 335, unzip_LRU len: 0
I/O sum[8151]:cur[67], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:19:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1864 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4147
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 10002
OS WAIT ARRAY INFO: signal count 12536
RW-shared spins 0, rounds 24149, OS waits 5301
RW-excl spins 0, rounds 32158, OS waits 934
RW-sx spins 1452, rounds 42766, OS waits 1414
Spin rounds per wait: 24149.00 RW-shared, 32158.00 RW-excl, 29.45 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1675 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 91111 lock struct(s), heap size 84500688, 83380199 row lock(s), undo log entries 4420850
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [16, 0, 18, 13] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
547414 OS file reads, 561023 OS file writes, 23371 OS fsyncs
149.64 reads/s, 16384 avg bytes/read, 148.99 writes/s, 8.20 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
97.25 hash searches/s, 102010.20 non-hash searches/s
---
LOG
---
Log sequence number 5307810995
Log flushed up to   5307638525
Pages flushed up to 5304044985
Last checkpoint at  5302518336
0 pending log flushes, 0 pending chkp writes
4751 log i/o's done, 2.50 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       763
Database pages     478
Old database pages 0
Modified db pages  423
Pending reads      0
Pending writes: LRU 49, flush list 0, single page 0
Pages made young 9223, not young 219703594
0.00 youngs/s, 0.00 non-youngs/s
Pages read 547381, created 364036, written 543906
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 27 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 478, unzip_LRU len: 0
I/O sum[8593]:cur[158], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:19:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1882 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4165
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 10126
--Thread 140530867619584 has waited at fsp0fsp.cc line 625 for 0  seconds the semaphore:
SX-lock on RW-latch at 0x7fcff4c545c0 created in file buf0buf.cc line 1468
a writer (thread id 140530781476608) has reserved it in mode  SX
number of readers 0, waiters flag 1, lock_word: 10000000
Last time read locked in file trx0undo.ic line 198
Last time write locked in file /export/home/pb2/build/sb_0-38465026-1584987238.22/mysql-5.7.30/storage/innobase/buf/buf0flu.cc line 1206
OS WAIT ARRAY INFO: signal count 12663
RW-shared spins 0, rounds 24573, OS waits 5368
RW-excl spins 0, rounds 32548, OS waits 947
RW-sx spins 1475, rounds 43456, OS waits 1437
Spin rounds per wait: 24573.00 RW-shared, 32548.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1695 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 68131 lock struct(s), heap size 84811984, 83380199 row lock(s), undo log entries 3305763
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 12] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
550551 OS file reads, 564392 OS file writes, 23552 OS fsyncs
156.84 reads/s, 16384 avg bytes/read, 168.44 writes/s, 9.05 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
104.39 hash searches/s, 109526.92 non-hash searches/s
---
LOG
---
Log sequence number 5332912604
Log flushed up to   5332905651
Pages flushed up to 5327250869
Last checkpoint at  5327250869
0 pending log flushes, 0 pending chkp writes
4807 log i/o's done, 2.80 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       903
Database pages     319
Old database pages 0
Modified db pages  318
Pending reads      0
Pending writes: LRU 12, flush list 2, single page 0
Pages made young 9262, not young 220843530
0.00 youngs/s, 0.00 non-youngs/s
Pages read 550518, created 364036, written 547187
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 103 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 319, unzip_LRU len: 0
I/O sum[9960]:cur[2], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:20:16 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1901 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4184
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 10237
OS WAIT ARRAY INFO: signal count 12776
RW-shared spins 0, rounds 24788, OS waits 5414
RW-excl spins 0, rounds 32938, OS waits 960
RW-sx spins 1507, rounds 44398, OS waits 1468
Spin rounds per wait: 24788.00 RW-shared, 32938.00 RW-excl, 29.46 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1715 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 52643 lock struct(s), heap size 85024976, 83380199 row lock(s), undo log entries 2553617
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 7, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
552717 OS file reads, 566824 OS file writes, 23732 OS fsyncs
1 pending preads, 0 pending pwrites
108.29 reads/s, 16384 avg bytes/read, 121.59 writes/s, 9.00 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
70.45 hash searches/s, 73858.01 non-hash searches/s
---
LOG
---
Log sequence number 5349845348
Log flushed up to   5349820995
Pages flushed up to 5348305359
Last checkpoint at  5341973100
0 pending log flushes, 0 pending chkp writes
4861 log i/o's done, 2.70 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       972
Database pages     237
Old database pages 0
Modified db pages  189
Pending reads      1
Pending writes: LRU 0, flush list 7, single page 0
Pages made young 9262, not young 220843530
0.00 youngs/s, 0.00 non-youngs/s
Pages read 552683, created 364036, written 549508
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 237, unzip_LRU len: 0
I/O sum[9616]:cur[31], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:20:36 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1919 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4202
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 10314
OS WAIT ARRAY INFO: signal count 12853
RW-shared spins 0, rounds 24879, OS waits 5423
RW-excl spins 0, rounds 33418, OS waits 976
RW-sx spins 1530, rounds 45088, OS waits 1491
Spin rounds per wait: 24879.00 RW-shared, 33418.00 RW-excl, 29.47 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1735 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 34953 lock struct(s), heap size 85270736, 83380199 row lock(s), undo log entries 1694841
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 6, 1, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
555135 OS file reads, 569370 OS file writes, 23919 OS fsyncs
120.89 reads/s, 16384 avg bytes/read, 127.29 writes/s, 9.35 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
80.40 hash searches/s, 84377.38 non-hash searches/s
---
LOG
---
Log sequence number 5369175979
Log flushed up to   5368423871
Pages flushed up to 5367370937
Last checkpoint at  5361710326
0 pending log flushes, 0 pending chkp writes
4918 log i/o's done, 2.85 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       892
Database pages     302
Old database pages 0
Modified db pages  229
Pending reads      0
Pending writes: LRU 0, flush list 7, single page 0
Pages made young 9271, not young 220852934
0.00 youngs/s, 0.00 non-youngs/s
Pages read 555102, created 364036, written 551935
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 1 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 302, unzip_LRU len: 0
I/O sum[8579]:cur[59], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================





=====================================
2021-01-08 18:20:56 0x7fcfddacc700 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 20 seconds
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1938 srv_active, 0 srv_shutdown, 2283 srv_idle
srv_master_thread log flush and writes: 4221
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 10398
OS WAIT ARRAY INFO: signal count 12937
RW-shared spins 0, rounds 25043, OS waits 5436
RW-excl spins 0, rounds 33808, OS waits 989
RW-sx spins 1561, rounds 45948, OS waits 1519
Spin rounds per wait: 25043.00 RW-shared, 33808.00 RW-excl, 29.43 RW-sx
------------
TRANSACTIONS
------------
Trx id counter 1466
Purge done for trx's n:o < 1466 undo n:o < 0 state: running but idle
History list length 24
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 422006226438880, not started
0 lock struct(s), heap size 1136, 0 row lock(s)
---TRANSACTION 1381, ACTIVE 1755 sec fetching rows
mysql tables in use 2, locked 2
ROLLING BACK 14932 lock struct(s), heap size 85549264, 83380199 row lock(s), undo log entries 722838
MySQL thread id 2, OS thread handle 140530867619584, query id 226 localhost root Sending data
insert into k1(name) select name from k1
Trx read view will not see trx with id >= 1466, sees < 1466
--------
FILE I/O
--------
I/O thread 0 state: waiting for completed aio requests (insert buffer thread)
I/O thread 1 state: waiting for completed aio requests (log thread)
I/O thread 2 state: waiting for completed aio requests (read thread)
I/O thread 3 state: waiting for completed aio requests (read thread)
I/O thread 4 state: waiting for completed aio requests (read thread)
I/O thread 5 state: waiting for completed aio requests (read thread)
I/O thread 6 state: waiting for completed aio requests (write thread)
I/O thread 7 state: waiting for completed aio requests (write thread)
I/O thread 8 state: waiting for completed aio requests (write thread)
I/O thread 9 state: waiting for completed aio requests (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 16, 18] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
557888 OS file reads, 572349 OS file writes, 24101 OS fsyncs
1 pending preads, 0 pending pwrites
137.64 reads/s, 16384 avg bytes/read, 148.94 writes/s, 9.10 fsyncs/s
-------------------------------------
INSERT BUFFER AND ADAPTIVE HASH INDEX
-------------------------------------
Ibuf: size 1, free list len 0, seg size 2, 0 merges
merged operations:
 insert 0, delete mark 0, delete 0
discarded operations:
 insert 0, delete mark 0, delete 0
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 1 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
Hash table size 26041, node heap has 0 buffer(s)
91.00 hash searches/s, 95457.93 non-hash searches/s
---
LOG
---
Log sequence number 5391052002
Log flushed up to   5390948346
Pages flushed up to 5389244638
Last checkpoint at  5376397174
0 pending log flushes, 0 pending chkp writes
4972 log i/o's done, 2.70 log i/o's/second
----------------------
BUFFER POOL AND MEMORY
----------------------
Total large memory allocated 107380736
Dictionary memory allocated 149778
Buffer pool size   6400
Free buffers       983
Database pages     194
Old database pages 0
Modified db pages  151
Pending reads      1
Pending writes: LRU 36, flush list 0, single page 0
Pages made young 9271, not young 220852934
0.00 youngs/s, 0.00 non-youngs/s
Pages read 557854, created 364036, written 554770
0.00 reads/s, 0.00 creates/s, 0.00 writes/s
Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 194, unzip_LRU len: 0
I/O sum[8412]:cur[124], unzip sum[0]:cur[0]
--------------
ROW OPERATIONS
--------------
0 queries inside InnoDB, 0 queries in queue
1 read views open inside InnoDB
Process ID=1274, Main thread ID=140530745652992, state: sleeping
Number of rows inserted 182960475, updated 0, deleted 0, read 216514913
0.00 inserts/s, 0.00 updates/s, 0.00 deletes/s, 0.00 reads/s
----------------------------
END OF INNODB MONITOR OUTPUT
============================

```

