#    常见SQL的锁模式


  ![ ](.pics/p11-1601259592065.png)





 #  

| select … from                                                | 一致性非锁定读     如果是serializable级别：Lock_ordinary\|S  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| lock in share mode                                           | Lock_ordinary                                                |
| for update                                                   | Lock_ordinary                                                |
| update/delete                                                | Lock_ordinary                                                |
| update t … where col in (select .. from s ..)                | s表加Lock_ordinary                                           |
| 普通 insert                                                  | Lock_insert_intention\|X     写入请求检测到有重复值时，会加锁Lock_ordinary\|X，可能引发死锁 |
| insert… on duplicate key update                              | Lock_ordinary                                                |
| insert into t select … from s                                | t表加Lock_rec_not_gap         \| X      s表加Lock_ordinary         \| S     隔离级别为RC或启用innodb_locks_unsafe_for_binlog时，s表上采用无锁一致性读，     即：RC不加锁，RR加nextkey-lock |
| create table … select                                        | 同 insert.. select                                           |
| replace                                                      | 无冲突/重复值时，和insert一样:Lock_insert_intention         \| X，     否则Lock_ordinary \| X |
| replace into t select .. from s where                        | s表加Lock_ordinary                                           |
| auto_increment列上写新数据时                                 | 索引末尾加 record   lock                                     |
| 请求自增列计数器时，InnoDB使用一个auto-inc mutex，     但只对请求的那个SQL有影响(lock_mode = 1 时) | --------------------------------                             |
| 有外键约束字段上进行insert/update/delete操作时               | 除了自身的锁，还会在外表约束列上同时加Lock_rec_not_gap       |
|                                                              | nextkey-lock 只发生在RR隔离级别下                            |