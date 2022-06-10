前言
在使用redis的过程中，不免会产生过期的key，而这些key过期后并不会实时地马上被删除，当这些key数量累积越来越多，就会占用很多内存，因此在redis底层同时使用了三种策略来删除这些key。

第一种策略：被动删除
当读/写一个key时，redis首先会检查这个key是否存在，如果存在且已过期，则直接删除这个key并返回nil给客户端。

第二种策略：定期删除
redis中有一系列的定期任务（serverCron），这些任务每隔一段时间就会运行一次，其中就包含清理过期key的任务，运行频率由配置文件中的hz参数来控制，取值范围1~500，默认是10，代表每秒运行10次。清理过程如下：

遍历所有的db
从db中设置了过期时间的key的集合中随机检查20个key
删除检查中发现的所有过期key
如果检查结果中25%以上的key已过期，则继续重复执行步骤2-3，否则继续遍历下一个db
调大hz将会提高redis定期任务的执行频率，如果你的redis中包含很多过期key的话，可以考虑将这个值调大，但要注意同时也会增加CPU的压力，redis作者建议这个值不要超过100。

第三种策略：强制删除
如果redis使用的内存已经达到maxmemory配置的值时，会触发强制清理策略，清理策略由配置文件的maxmemory-policy参数来控制，有以下这些清理策略：

volatile-lru：使用LRU算法对设置了过期时间的key进行清理（默认值）
allkeys-lru：使用LRU算法对所有key进行清理
volatile-lfu：使用LFU算法对设置了过期时间的key进行清理（redis 4.0版本开始支持）
allkeys-lfu：使用LFU算法对所有key进行清理（redis 4.0版本开始支持）
volatile-random：对所有设置了过期时间的key进行随机清理
allkeys-random：从所有key进行随机清理
volatile-ttl：清理生存时间最小的一部分key
noeviction：不做任何清理，拒绝执行所有的写操作
为了节省内存和性能上的考虑，上述的清理策略都不需要遍历所有数据，而是采用随机采样的方法，每次随机取出特定数量（由maxmemory-samples配置项控制，默认是5个）的key，然后在这些key中执行LRU算法、RANDOM算法、或者是找出TTL时间最小的一个key，然后进行删除。

注：这个清理过程是阻塞的，直到清理出足够的内存空间才会停止。

> - LRU： 最近最少使用淘汰
> - LFU：最少使用频率最低淘汰
> - random：随机
> - TTL：将要过期的淘汰



关于big key的清理
在删除元素数量很多的集合（set/hash/list/sortedSet）时，无论是使用DEL命令删除还是redis为了释放内存空间而进行的删除，在删除这些big key的时候，会导致redis主线程阻塞。为了解决这个问题，在redis 4.0版本中，提供了lazy free（懒惰删除）的特性。

使用lazy free删除big key时，和一个O(1)指令的耗时一样，亚毫秒级返回，然后把真正删除key的耗时动作交由bio后台子线程执行。

UNLINK命令
UNLINK命令是与DEL一样删除key功能的lazy free实现。唯一不同的是，UNLINK在删除集合类型的键时，如果集合键的元素个数大于64个，会把真正的内存释放操作，交给单独的后台线程来操作，使用示例：

127.0.0.1:6379> UNLINK mylist
(integer) 1
1
2
FLUSHALL/FLUSHDB命令
FLUSHALL/FLUSHDB命令也有lazy free的实现，在命令后加上ASYNC关键字就可以，使用示例：

127.0.0.1:6379> FLUSHALL ASYNC
1
lazy free相关配置项
与lazy free相关的配置项有以下这些，默认值都是no，即关闭。

lazyfree-lazy-eviction
针对redis内存使用达到maxmemory，并设置有淘汰策略时，在淘汰键时是否采用lazy free机制。

注：如果此场景开启lazy free，可能会使淘汰键的内存释放不及时，导致redis不能迅速将内存使用下降到maxmemory以下。

lazyfree-lazy-expire
针对设置有过期时间的key，达到过期后，被redis清理删除时是否采用lazy free机制，此场景建议开启。

lazyfree-lazy-server-del
针对有些命令在处理已存在的键时，会带有一个隐式的DEL键的操作。如RENAME命令，当目标键已存在，redis会先删除目标键，如果这些目标键是一个big key，那就会出现阻塞的性能问题。 此参数设置就是解决这类问题，建议开启。

slave-lazy-flush
针对slave进行全量数据同步，slave在加载master的RDB文件前，会运行FLUSHALL来清理自己的数据场景。
参数设置决定是否采用lazy free flush机制。如果内存变动不大，建议可开启。可减少全量同步耗时，从而减少主库因输出缓冲区爆涨引起的内存使用增长。



