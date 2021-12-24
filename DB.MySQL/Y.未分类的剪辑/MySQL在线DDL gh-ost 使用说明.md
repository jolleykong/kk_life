## 背景：

   作为一个DBA，大表的DDL的变更大部分都是使用Percona的[pt-online-schema-change](https://www.percona.com/doc/percona-toolkit/3.0/pt-online-schema-change.html)，本文说明下另一种工具[gh-ost](https://github.com/github/gh-ost)的使用：不依赖于触发器,是因为他是通过模拟从库,在row binlog中获取增量变更,再异步应用到ghost表的。在使用gh-ost之前，可以先看[GitHub 开源的 MySQL 在线更改 Schema 工具【转】](https://www.cnblogs.com/zhoujinyi/p/9187502.html)文章或则官网了解其特性和原理。本文只对使用进行说明。

## 说明：

1）下载安装：https://github.com/github/gh-ost/tags

2）[参数说明](https://github.com/wing324/helloworld_zh/blob/master/MySQL/gh-ost/GitHub开源MySQL Online DDL工具gh-ost参数解析.md)：gh-ost --help



3）使用说明：条件是操作的MySQL上需要的binlog模式是ROW。如果在一个从上测试也必须是ROW模式，还要开启log_slave_updates。根据上面的参数说明按照需求进行调整。

   环境：主库：192.168.163.131；从库：192.168.163.130

[DDL过程](https://yq.aliyun.com/articles/62928)：



```
① 检查有没有外键和触发器。
② 检查表的主键信息。
③ 检查是否主库或从库，是否开启log_slave_updates，以及binlog信息  
④ 检查gho和del结尾的临时表是否存在
⑤ 创建ghc结尾的表，存数据迁移的信息，以及binlog信息等    
---以上校验阶段
⑥ 初始化stream的连接,添加binlog的监听
---以下迁移阶段
⑥ 创建gho结尾的临时表，执行DDL在gho结尾的临时表上
⑦ 开启事务，按照主键id把源表数据写入到gho结尾的表上，再提交，以及binlog apply。
---以下cut-over阶段
⑧ lock源表，rename 表：rename 源表 to 源_del表，gho表 to 源表。
⑨ 清理ghc表。
```



**1. 单实例上DDL**： 单个实例相当于主库，需要开启--allow-on-master参数和ROW模式。

```
gh-ost --user="root" --password="root" --host=192.168.163.131  --database="test" --table="t1"  --alter="ADD COLUMN cc2 varchar(10),add column cc3 int not null default 0 comment 'test' " --allow-on-master  --execute
```

**2. 主从上DDL**：

有2个选择，一是按照1直接在主上执行同步到从上，另一个连接到从库，在主库做迁移（只要保证从库的binlog为ROW即可，主库不需要保证）：

```
gh-ost --user="root" --password="root" --host=192.168.163.130  --database="test" --table="t" --initially-drop-old-table --alter="ADD COLUMN y1 varchar(10),add column y2 int not null default 0 comment 'test' "  --execute
```

此时的操作大致是：

- 行数据在主库上读写
- 读取从库的二进制日志，将变更应用到主库
- 在从库收集表格式，字段&索引，行数等信息
- 在从库上读取内部的变更事件（如心跳事件）
- 在主库切换表

在执行DDL中，从库会执行一次stop/start slave，要是确定从的binlog是ROW的话可以添加参数：--assume-rbr。如果从库的binlog不是ROW，可以用参数--switch-to-rbr来转换成ROW，此时需要注意的是执行完毕之后，binlog模式不会被转换成原来的值。--assume-rbr和--switch-to-rbr参数不能一起使用。

**3. 在从上进行DDL测试**：

```
gh-ost --user="root" --password="root" --host=192.168.163.130  --database="test" --table="t"  --alter="ADD COLUMN abc1 varchar(10),add column abc2 int not null default 0 comment 'test' " --test-on-replica  --switch-to-rbr --execute
```

参数--test-on-replica：在从库上测试gh-ost，包括在从库上数据迁移(migration)，数据迁移完成后stop slave，原表和ghost表立刻交换而后立刻交换回来。继续保持stop slave，使你可以对比两张表。如果不想stop  slave，则可以再添加参数：--test-on-replica-skip-replica-stop

上面三种是gh-ost操作模式，上面的操作中，到最后不会清理临时表，需要手动清理，再下次执行之前果然临时表还存在，则会执行失败，可以通过参数进行删除:



```
--initially-drop-ghost-table:gh-ost操作之前，检查并删除已经存在的ghost表。该参数不建议使用，请手动处理原来存在的ghost表。默认不启用该参数，gh-ost直接退出操作。

--initially-drop-old-table:gh-ost操作之前，检查并删除已经存在的旧表。该参数不建议使用，请手动处理原来存在的ghost表。默认不启用该参数，gh-ost直接退出操作。

--initially-drop-socket-file:gh-ost强制删除已经存在的socket文件。该参数不建议使用，可能会删除一个正在运行的gh-ost程序，导致DDL失败。

--ok-to-drop-table:gh-ost操作结束后，删除旧表，默认状态是不删除旧表，会存在_tablename_del表。
```



还有其他的一些参数，比如：--exact-rowcount、--max-lag-millis、--max-load等等，可以看上面的说明，具体大部分常用的参数命令如下：

```
gh-osc --user= --password= --host= --database= --table= --max-load=Threads_running=30, --chunk-size=1000 --serve-socket-file=/tmp/gh-ost.test.sock --exact-rowcount --allow-on-master/--test-on-replica --initially-drop-ghost-table/--initially-drop-old-table/--initially-drop-socket-file --max-lag-millis= --max-load='Threads_running=100,Threads_connected=500' --ok-to-drop-table
```

**4）额外说明：终止、暂停、限速**

```
gh-ost --user="root" --password="root" --host=192.168.163.131  --database="test" --table="t1"  --alter="ADD COLUMN o2 varchar(10),add column o1 int not null default 0 comment 'test' " --exact-rowcount --serve-socket-file=/tmp/gh-ost.t1.sock --panic-flag-file=/tmp/gh-ost.panic.t1.flag  --postpone-cut-over-flag-file=/tmp/ghost.postpone.t1.flag --allow-on-master  --execute
```

① **标示文件终止运行**：--panic-flag-file

创建文件终止运行，例子中创建**/tmp/gh-ost.panic.t1.flag**文件，终止正在运行的gh-ost，临时文件清理需要手动进行。

② **表示文件禁止cut-over进行**，即禁止表名切换，数据复制正常进行。--postpone-cut-over-flag-file

创建文件延迟cut-over进行，即推迟切换操作。例子中创建**/tmp/ghost.postpone.t1.flag**文件，gh-ost 会完成行复制，但并不会切换表，它会持续的将原表的数据更新操作同步到临时表中。

③ 使用socket监听请求，操作者可以在命令运行后更改相应的参数。--serve-socket-file，--serve-tcp-port（默认关闭）

创建socket文件进行监听，通过接口进行参数调整，当执行操作的过程中发现负载、延迟上升了，不得不终止操作，重新配置参数，如 chunk-size，然后重新执行操作命令，可以通过scoket接口进行**动态调整**。如：

**暂停操作：**

```
#暂停
echo throttle | socat - /tmp/gh-ost.test.t1.sock
#恢复
echo no-throttle | socat - /tmp/gh-ost.test.t1.sock
```

**修改限速参数：**

```
echo chunk-size=100 | socat - /tmp/gh-ost.t1.sock

echo max-lag-millis=200 | socat - /tmp/gh-ost.t1.sock

echo max-load=Thread_running=3 | socat - /tmp/gh-ost.t1.sock
```

 **4）和[pt-online-schema-change](https://www.cnblogs.com/zhoujinyi/p/3491059.html)对比测试**

 \1. 表没有写入并且参数为默认的情况下，二者DDL操作时间差不多，毕竟都是copy row操作。

 \2. 表有大量写入(sysbench)的情况下，因为pt-osc是多线程处理的，很快就能执行完成，而gh-ost是模拟“从”单线程应用的，极端的情况下，DDL操作非常困难的执行完毕。

 **结论：**虽然gh-ost不需要触发器，对于主库的压力和性能影响也小很多，但是针对高并发的场景进行DDL效率还是比pt-osc低，所以还是需要在业务低峰的时候处理。相关的测试可以看[gh-ost和pt-osc性能对比](https://blog.csdn.net/poxiaonie/article/details/75331916)。

 5**）封装脚本：**

环境：M：192.168.163.131（ROW），S：192.168.163.130/132

封装脚本：gh-ost.py

![img](ContractedBlock.gif) View Code

运行：

![img](ContractedBlock.gif) View Code

## 总结：

gh-ost 放弃了触发器，使用 binlog 来同步。gh-ost 作为一个伪装的备库，可以从主库/备库上拉取 binlog，过滤之后重新应用到主库上去，相当于主库上的增量操作通过 binlog 又应用回主库本身，不过是应用在幽灵表上。

![img](163084-20180615233341989-1215951790.png)

**gh-ost 首先连接到主库上，根据 alter 语句创建幽灵表，然后作为一个”备库“连接到其中一个真正的备库上，一边在主库上拷贝已有的数据到幽灵表，一边从备库上拉取增量数据的 binlog，然后不断的把 binlog 应用回主库。**图中 cut-over 是最后一步，锁住主库的源表，等待 binlog 应用完毕，然后替换 gh-ost 表为源表。gh-ost  在执行中，会在原本的 binlog event 里面增加以下 hint  和心跳包，用来控制整个流程的进度，检测状态等。这种架构带来诸多好处，例如：

- **整个流程异步执行**，对于源表的增量数据操作没有额外的开销，高峰期变更业务对性能影响小。
- **降低写压力**，触发器操作都在一个事务内，gh-ost 应用 binlog 是另外一个连接在做。
- **可停止**，binlog 有位点记录，如果变更过程发现主库性能受影响，可以立刻停止拉binlog，停止应用 binlog，稳定之后继续应用。
- 可测试，gh-ost 提供了测试功能，可以连接到一个备库上直接做 Online DDL，在备库上观察变更结果是否正确，再对主库操作，心里更有底。

注意： sync error的错误：https://github.com/github/gh-ost/issues/597

## 参考文档：

https://github.com/github/gh-ost

[GitHub 开源的 MySQL 在线更改 Schema 工具](https://segmentfault.com/a/1190000006158503)

[Online DDL 工具 gh-ost 支持阿里云 RDS](http://mysql.taobao.org/monthly/2018/05/02/)

[gh-ost：不一样的在线表结构变更](https://yq.aliyun.com/articles/62928)

[GitHub开源MySQL Online DDL工具gh-ost参数解析](https://github.com/wing324/helloworld_zh/blob/master/MySQL/gh-ost/GitHub开源MySQL Online DDL工具gh-ost参数解析.md) 