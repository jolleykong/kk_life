## MySQL方向工作的三股清流 

这段时间虽然因为疫情导致原本的一些工作有了延后，但是整体来说，大方向的事情还是基本成为定数。

如果让我来选择今年要做的几件事情，我觉得有三股清流是需要关注的，也就是说不单单从技术层面来考虑，而是综合业务使用场景和整体的演进过程。

第一股清流就是备份恢复，似乎在这些年被淡忘了，淡忘了还好，一旦要记起来的时候基本就来不及了，你会发现所有你能想到的优化的地方都是一篇荒漠，基于云环境确实提供了一些便利和稳定性，但是不代表你不需要做投入去完善和补充。如何能够更高效的完成备份，使用性价比最好的存储模式，稳定可控的恢复效率，应该是我们需要持续不断迭代改进备份恢复方向工作的大目标。在任何优先级面前，备份恢复可能在业务层代表的含义是很单薄的，但是这是数据生死攸关的大事，请先把它放在最基础紧要的工作里面。

第二股清流就是高可用，我们有传统概念中理解的高可用，也有基于分布式环境的高可用方案，高可用代表着我们的后端服务不是死板的，动不得的，而是在保证业务可用的前提下，实现业务和系统的可用性。高可用可做的事情非常多，不同阶段对标的目标也大不相同，如何换句话说，我们可以不用苛求数据库层100%的可用，而结合业务层，基于几秒的闪断来换取业务服务真正的高可用，其实可做的事情很多，改进的空间也一下子大了许多。


 

第三股清流就是数据流转，数据流转是一个较大的体系，数据迁移算是其中的一个子集。如何能够让数据流进来，走出去，实现环境间，异构环境间的数据同步，提供多维度，近实时的数据访问，算是把原来散乱的数据盘活了。数据流转可以打破很多技术层面的壁垒，能够提供鞥更多更加灵活的数据侧解决方案。

当然有的同学说这三个任务是不是太简单了。我们可以在此基础上做一些扩展和补充说明，让这三股清流更加清晰一些。
 

**备份恢复**，毫无疑问我们要先改善已有的备份效率和存储，在备份方式上，实现一次全量，永远增量的目标，而对于增量方案，不局限于已有的增备方案，还需要充分结合binlog方案，实现全量+增量+binlog三者有效结合的快速恢复方案，在基于binlog的数据闪回方向上能够做深做细，使得数据可恢复性更加灵活，比如提供自助的数据恢复服务，在数据采集方面，基于binlog侧的备份可以逐步沉淀成为binlog集市，而基于集市的方案也为后续的数据流转可以打好基础。备份恢复不是呆板的，而是可以提供其他维度的功能，比如我们可以基于快照设计的思想来快速恢复某一个数据库，然后在上面做真实数据量的业务压力测试或者是SQL优化服务。

**高可用**，如果实现了同机房，跨机房的高可用方案，那么后面需要做的事情就是盘活高可用方案的发展空间，比如我们原本认为的高可用就是数据库层老老实实，不要动，在满足高可用目标的前提下，数据库层可以更加主动，比如可以实现更加平滑的在线升级，实现秒级业务闪断的服务快速切换，实现秒级别的服务切换和跨机房高可用方案。在这方面需要颠倒我们固化的高可用认知，而选择更加主动，具有弹性的高可用方案。

**数据流转，**同类型数据间同步和异构数据间同步是我们需要打通的部分，数据的流动性也能够反映出业务侧相应的成熟度，我们可以在流转的采集侧进行数据的实时提取，然后基于binlog服务或者binlog集市实现数据的实时消费，在环境间维护中引入数据生命周期管理，能够实现基于版本化的管理模式，基于业务使用模式，实现缓存，持久化存储，文件存储等多个维度的数据存储方案，能够让数据的接入成本更低，通过数据关联发掘更多的数据价值。
 