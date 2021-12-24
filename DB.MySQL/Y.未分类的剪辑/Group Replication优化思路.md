已剪辑自: https://www.jianshu.com/p/b34bea493546

Group Replication 是一种新的复制模式，它彻底颠覆了传统的复制模式，虽然还是异步复制（或者可称其为同步复制，异步应用），但能够实现强最终一致性，并且完全实现了无人干预式高可用，必将成为未来的主流。本文不详细介绍Group Replication的实现原理，网上有许多资料，这里主要对如何优化Group Replication集群进行分析探讨。

首先我们分析下影响GR性能的主要因素。

#### *影响GR性能主要因素：*

1. 网络带宽
              在写节点上产生的事务，在最终被commit前，需要发送到复制组中做冲突校验，这需要消耗网络带宽，并给事务的延迟至少增加一个RTT(Round Trip Time,TCP数据包旅行一个回路的时间)。
2. 校验吞吐量
              事务会被按照相同的顺序发送到各节点做冲突校验，校验通过后会被远端节点写入relay-log，这个写入是由一个单线程负责。当校验的速率很高，磁盘吞吐量（relay-log写入）将会成为瓶颈。
3. 读节点applier线程应用效率
              读节点的applier线程的应用不及时会触发writer节点flow-control，对于多主模式架构，applier线程的低效可能会造成校验失败率升高。

GR性能瓶颈主要存在上面三个方面，有些是需要提升物理硬件，有些则是参数调整。我们来分析下针对每一个方面的优化措施。

#### *网络因素：*

1. 使用高带宽低延迟网络，使所有节点都处于同一网关
2. 减少带宽消耗，如采取启用压缩,尽量缩小binlog等措施

group_replication_compression_threshold=1000000 # default in mysql8.0.11
 binlog_row_image=MINIMAL

group_replication_compression_threshold 当复制组间通信的event超过这一阈值时，启用LZ4压缩，以减小通信量。

binlog_row_image默认是full,即将某行数据的改变前(before)和改变后(after)的数据都写入binlog.实际上只有update才会产生改变前和改变后两个数据镜像，而对于insert只会有改变后的数据镜像，delete只会有改变前的数据镜像。如果每个表都有primary key(表定义在主从架构中完全相同，group replication要求表必须有主键),完全可以在binlog中的before镜像中记入主键值（它已经能唯一标识数据改变的行了），而在after镜像中只记录所改变的字段的值，而不是所有的字段的值。这样binlog就大大缩小，网络间通信量也就大大减少了。只是在从节点应用这样的binlog event时，效率会有点低。

1. 通过频繁等待，减少group replication线程睡眠次数

SET GLOBAL group_replication_poll_spin_loops= 10000; # default 0

这样可使GCT(Group Comunitcatoin Thread)积极地在消息队列处等待，一旦队列中有新消息可以更快地响应。同时也降低了操作系统对其上下文切换频率。

#### *校验速率：*

1. 可以使用single-primary模式，因为正常情况下，这种模式是不需要校验的（有一种情况除外，就是新master正在应用从之前的primary复制来的binlog，这种情况下是需要校验的），但这种模式下，一旦primary宕机，需要选举一个新的master,多了一个选举的过程。
2. 将relay-log，tmpdir 置于高性能硬盘, 校验通过后非local_transaction要写入relay log，对于大事务writeset的抽取可能会需要写入磁盘临时文件，如果relay log/临时文件读写性能很差，将会大大增加事务的延时。在这两个地方可能产生物理IO瓶颈。
3. 对于多主架构减少校验的复杂度 

group_replication_gtid_assignment_block_size=1000000 # default

事务在节点执行完成，commit前发送到GR做校验。校验成功后，GR会给此事务分配一个GTID（如果该事务没有GTID）。GR会给每个节点预留一个范围的GTID，（GTID是由server_uuid+数字组成，gr中GTID中的UUID部分都是一样的，数字部分则为各节点分配一个范围段，用完了再分配一个新的范围段）。这个范围段的大小就是有group_replication_gtid_assignment_block_size变量控制，默认是1000000。这个数字范围如果很大的话，gtid_executed就不能及时合并,许多GTID interval 会使校验算法变得复杂。

#### *Applier应用线程*

1. 启用MTS多线程应用

set global slave_parallel_type=LOGICAL_CLOCK;
 set global slave_parallel_workers=8/16/32/+;
 set global slave_preserve_commit_order=ON;
 

1. 启用基于写集依赖的多线程应用，使并发效率更高

\# for mysql8
 binlog_transaction_dependency_tracking=WRITESET

Applier线程的高效应用对提升集群性能非常重要。因为Applier 线程应用不及时可能会触发writer节点启用flow control,直接影响性能。除此之外，它对校验也会有重要的影响。因为Applier 的及时应用可以使transaction_commit_on_all_memebers及时跟进，stable set 更加接近最新的事务。这会使校验集合（Certification_info）中的无用的快照版本被及时垃圾回收，从而降低了校验的复杂度，提高了整体性能的吞吐量。这是一个很重要的优化策略！

#### *总结*

根据group replication的实现原理，其瓶颈主要产生于三点：

1. 复制组间通信（高带宽网络）
2. 事务在各节点的校验
3. Applier应用效率

优化的思路也是主要集中在这三个方向。每次调整参数都应压测对比效果，确保理论符合实际。盲目根据理论调优而不压测对比是不可取的。一套优化方案，都是经过反复调参反复压测而得出的最终结果。

参考资料：
 *之前读过一篇文章，写的很好，现在找不到了，很抱歉！*