已剪辑自: http://blog.sina.com.cn/s/blog_4673e6030102xmie.html

最近查阅了阿里的金融版本rds for mysql的介绍文档，思考了下如果使用raft协议保证主备数据一致性又哪些功能点需要考虑。
 
 使用raft主要目的应该包括：
 \1. 节点选主
 
 一个raft强复制的主备集群，同一时间只能有一个主存在。
 考虑到raft协议term的存在，mysql内核和raft融合的时候需要额外记录term的信息。
 按照raft协议选主的原则，比较的是[term,index]，term大的胜出，term相同的话，选取index大的。
 使用mysql主备复制，gtid具有天然的递增熟悉，在一个term内（主节点确定）gtid肯定是连续递增的，应该可以考虑直接使用gtid的值作为index。当然这样做的前提是不存在多主复制，只是1主多从的架构，金融raft3节点集群就满足这个要求。
 
 \2. binlog复制
 
 在raft协议里应该是日志复制，应用到mysql上，就是对应的binlog的复制。
 raft协议要求半数节点同意才提交一个日志，所以基于mysql的半同步复制，我们可以要求至少一半的slave响应半同步的ack，这个功能在mysql5.7版本中已经有了，并且主节点必须等待投票结果，所以半同步绝对不可以退化为异步，半同步的超时时间必须是无穷大。
 考虑到 raft主节点必须周期性地向follower节点发送心跳的，可以直接服用mysql主备复制的heartbeat.
 
 日志复制过程可以存在事务回滚的需求：
 a. follower包含了新主没有的binlog gtid，新主向该follower发送的appendentriesRPC的实现需要在覆盖本地binlog日志之前，将改被覆盖的binlog gtid事务整个反转回滚。
 b. raft要求主节点只能提交当前term的日志，在raft论文给的极端的场景中，新主可能没有集群多数节点包含的gtid，这时候要把集群多数节点的该gtid回滚，但3节点集群应该不存在这个问题。
 
 回滚需要依赖binlog反转工具，例如flashback。如果碰到无法反转场景例如 ddl，就需要通过快照进行重置了（重做该节点）。
 
 \3. 快照
 
 raft和mysql内核的融合应该需要在mysql内部去记录raft的日志，即term+gtid+binlog，这个日志可以是一个内部系统表中记录term+gtid，binlog依然存储在磁盘上。
 binlog的过期将与节点的热备相结合。
 每次节点做一次全量/增量后，该全量/增量可以视为一次raft的快照，然后就可以purge binlog文件并清理系统表中镜像版本之前的term+gtid记录。
 当新的slave节点作为follower加入集群发现无法找到要同步的binlog时，直接从raft镜像(备份)中还原。
 
 
 \4. 需要有个前端的router，确保请求只被转发到当前term的主节点
 这个应该可以通过zookeeper或直接读取raft集群的拓扑。
 
 
 \5. 其他
 由于raft选主切换的前提是follower拥有所有日志，在这个场景中，slave节点被选为主的前提是必须应用完所有的relay log。所以复制性能也是关键，所有业务表理论上必须有主键。阿里的alisql会内部自动为无主键表添加隐式主键。
 
 转载请注明转自高孝鑫的博客！
 
 