## Innodb DML流程（update）

client发起update/delete请求，提交到server层进行权限、语义语法校验后，server层将请求提交给innodb层。

在IBP中请求的数据，如果存在记录，尝试对最新版本加排它锁；如果不存在IBP中，则调用IO读入到IBP中并加锁。IBP中修改数据时，会将当前数据存入undo段，再进行修改，同时将更改动作记录到redo buffer。将数据复制到undo段后，回滚指针会指向数据在undo段中的位置，并将回滚指针记录在数据的最新版本的头部信息中。

>  事务中涉及到主键、唯一索引变更时，会立即修改主键、唯一索引，并将变化追加到索引中，而不是重建整个索引。
>
> 如果不涉及主键、唯一索引，仅涉及到二级索引的变更，由于二级索引往往是不唯一的，DML操作也会影响索引树上的不相邻的二级索引页，因此会用到change buffer来优化磁盘IO效率，如果涉及到的页不在IBP，会直接将页变更缓存写入change buffer，然后记录redo log并落盘redo；当change buffer中的变更会在之后merge到IBP。此时查询变更数据时，会调用IO将数据页读入IBP并将变更操作merge到IBP。只有从change buffer加载或merge到IBP时，才会将索引的变更合并。
>
> change buffer在数据库空闲、buffer free不足、redo将满时，才会刷盘。

提交阶段，cilent发起提交请求，server层向innodb层发起第一阶段提交，此时会将事务XID写入redo并刷新redo到磁盘，此时事务标记为prepare，innodb返回给server层后，server层开始写binlog到file cache，并将binlog落盘。完成binlog落盘后，server层向innodb层发起第二阶段提交，将binlog filename、position信息记录到redo中并根据参数配置，刷新redo到磁盘，引擎层提交后，之前生成的undo信息便被清除。主线程会在后续将脏页刷新到磁盘。

刷新脏页到磁盘时，会先将脏页复制到double write buffer一份，并将dblwb落盘。完成落盘后，才开始将脏页由内存中刷新到磁盘。如果此过程中出现问题，可以直接从double write中读入脏页数据到内存，重新执行落盘。

## IBP

- innodb对任何数据的读写都是基于内存的。

- IBP中最大的三个区域为，database pages, modofied db pages, free buffers.
- IBP不够用时，会先写脏页。
- 脏页占比全部pages大于等于90%、IBP_wait_free指标大于0、IBP_pages_dirty指标占比非常高，都说明IBP不够用。



## double write

- innodb页为16k，磁盘一般是4k。16k的页写入部分数据时发生crash，就丢了数据。

- 刷脏页前将脏页复制到double write buffer，刷新double write后再刷新脏页。如果刷新脏页出了问题，就从double write中恢复。
- double write分为两部分，内存和磁盘。脏页拷贝到内存部分时，会要求这份buffer先刷新到磁盘，**保证double write buffer先于脏页刷新到磁盘**。

- 保证数据写入的可靠性（防止数据页损坏，又无从修复）

## change buffer

- 早期为insert的缓存区域，后来扩充功能也包含update、delete。用来缓存辅助索引页变化。

- 当需要修改的辅助索引页不在内存，会将索引页的变化缓存在change buffer

- 对索引的变更先缓存在change buffer，然后等待主线程merge，将修改的数据合并到IBP，然后刷新到磁盘。或者发生该条数据的读请求时，直接载入到IBP

- 将辅助索引上的DML操作，由随机IO变为顺序IO，提高IO效率

  > 与聚集索引不同，二级索引通常是不唯一的，并且二级索引中的插入以相对随机的顺序发生。 同样，删除和更新可能会影响索引树中不相邻的二级索引页。
  >
  > [MySQL索引的更新策略](..\5.MySQL体系结构\2.InnoDB引擎体系结构\1.InnoDB 内存结构\MySQL索引的更新策略.md)
  >
  > [MySQL写入缓冲区在数据库中的作用( Change Buffer )](..\5.MySQL体系结构\2.InnoDB引擎体系结构\1.InnoDB 内存结构\MySQL写入缓冲区在数据库中的作用( Change Buffer ).md)

- 在MySQL`5.5`之前，叫插入缓冲(`insert buffer`)，只针对insert做了优化；现在对`delete`和`update`也有效，叫做写缓冲(`change buffer`)。
- 它是一种应用在`非唯一普通索引页`(non-unique secondary index  page)不在缓冲池中，对页进行了写操作，并不会立刻将磁盘页加载到缓冲池，而仅仅记录缓冲变更(buffer  changes)，等未来数据被读取时，再将数据合并(merge)恢复到缓冲池中的技术。写缓冲的目的是降低写操作的磁盘IO，提升数据库性能。