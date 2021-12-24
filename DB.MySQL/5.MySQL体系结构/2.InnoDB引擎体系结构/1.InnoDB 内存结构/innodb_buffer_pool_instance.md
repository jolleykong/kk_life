# innodb_buffer_pool_instance

 

将 buffer pool 分成几个区，每个区用独立的锁保护，这样就减少了访问 buffer pool 时需要上锁的粒度，以提高性能。

 

```
mysql> show global variables like "%innodb_buffer_pool_instances%";
+------------------------------+-------+
| Variable_name        | Value |
+------------------------------+-------+
| innodb_buffer_pool_instances | 1   |
+------------------------------+-------+
1 row in set (0.01 sec)
```

 

 

5.6以后引入的特性。5.6以前整个buffer pool是统一管理的，不管多少个并发，都是由全局mutex进行全局保护，因此并发性能会受到一些影响。

 

如果一大块内存分配给buffer pool ，还是有些大

可以使buffer pool拆分成小块，如 64G/8 = 8G ， 管理起来会好很多

8.0以前，虽然已经支持多个Innodb instance，但是还是由统一的全局mutex进行保护，因此瓶颈依旧。

 

 该特性源自于percona，percona从5.5 5.6左右便支持独立mutex，官方版本8.0才支持。

每一个buffer pool instance都有自己的mutex来保护自己。