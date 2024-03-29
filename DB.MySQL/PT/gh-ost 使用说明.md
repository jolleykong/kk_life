# gh-ost原理

本文来自：https://segmentfault.com/a/1190000006158503

原文：[gh-ost: GitHub's online schema migration tool for MySQL](http://githubengineering.com/gh-ost-github-s-online-migration-tool-for-mysql/)

 

MySQL在线更改schema的工具很多，如Percona的[pt-online-schema-change](https://www.percona.com/doc/percona-toolkit/2.2/pt-online-schema-change.html)、 Facebook的 [OSC](https://www.facebook.com/notes/mysql-at-facebook/online-schema-change-for-mysql/430801045932/) 和 [LHM](https://github.com/soundcloud/lhm) 等，但这些都是基于触发器（Trigger）的，今天咱们介绍的 `gh-ost` 号称是不需要触发器（Triggerless）支持的在线更改表结构的工具。

> 本文先介绍一下当前业界已经存在的这些工具的使用场景和原理，然后再详细介绍 `gh-ost` 的工作原理和特性。

今天我们开源了GitHub内部使用的一款 不需要触发器支持的 MySQL 在线更改表结构的工具 [gh-ost](http://github.com/github/gh-ost)

开发 `gh-ost` 是为了应付GitHub在生产环境中面临的持续的、不断变化的在线修改表结构的需求。`gh-ost` 通过提供低影响、可控、可审计和操作友好的解决方案改变了现有的在线迁移表工具的工作模式。

MySQL表迁移及结构更改操作是业界众所周知的问题，2009年以来已经可以通过在线（不停服务）变更的工具来解决。迅速增长，快速迭代的产品往往需要频繁的需改数据库的结构。增加/更改/删除/ 字段和索引等等，这些操作在MySQL中默认都会锁表，影响线上的服务。 向这种数据库结构层面的变更我们每天都会面临多次，当然这种操作不应该影响用户的正常服务。

在开始介绍 `gh-ost` 工具之前，咱们先来看一下当前现有的这些工具的解决方案。

## 在线修改表结构，已存在的场景

如今，在线修改表结构可以通过下面的三种方式来完成：

- 在从库上修改表结构，操作会在其他的从库上生效，将结构变更了的从库设置为主库
- 使用 MySQL InnoDB 存储引擎提供的在线DDL特性
- 使用在线修改表结构的工具。现在最流行的是 [pt-online-schema-change](https://www.percona.com/doc/percona-toolkit/2.2/pt-online-schema-change.html) 和 Facebook 的 [OSC](https://www.facebook.com/notes/mysql-at-facebook/online-schema-change-for-mysql/430801045932/)；当然还有 [LHM](https://github.com/soundcloud/lhm) 和比较原始的 [oak-online-alter-table](http://shlomi-noach.github.io/openarkkit/oak-online-alter-table.html) 工具。

其他的还包括 Galera 集群的Schema滚动更新，以及一些其他的非InnoDB的存储引擎等待，在 GitHub 我们使用通用的 主-从 架构 和 InnoDB 存储引擎。

为什么我们决定开始一个新的解决方案，而不是使用上面的提到的这些呢？现有的每种解决方案都有其局限性，下文会对这些方式的普遍问题简单的说明一下，但会对基于触发器的在线变更工具的问题进行详细说明。

- 基于主从复制的迁移方式需要很多的前置工作，如：大量的主机，较长的传输时间，复杂的管理等等。变更操作需要在一个指定的从库上或者基于sub-tree的主从结构中执行。需要的情况也比较多，如：主机宕机、主机从早先的备份中恢复数据、新主机加入到集群等等，所有这些情况都有可能对我们的操作造成影响。最要命的是可能这些操作一天要进行很多次，如果使用这种方法我们操作人员每天的效率是非常高的（译者注：现如今很少有人用这种方式了吧）

- MySQL针对Innodb存储引擎的在线DDL操作在开始之前都需要一个短时间排它锁(exclusive)来准备环境，所以alter命令发出后，会首先等待该表上的其它操作完成，在alter命令之后的请求会出现等待waiting meta data lock。同样在ddl结束之前，也要等待alter期间所有的事务完成，也会堵塞一小段时间，这对于繁忙的数据库服务来说危险系数是非常高的。另外DDL操作不能中断，如果中途kill掉，会造成长时间的事务回滚，还有可能造成元数据的损坏。它操作起来并不那么的Nice，不能限流和暂停，在大负载的环境中甚至会影响正常的业务。

- 我们用了很多年的 `pt-online-schema-change` 工具。然而随着我们不断增长的业务和流量，我们遇到了很多的问题，我们必须考虑在操作中的哪些 `危险操作` （译者注：pt工具集的文档中经常会有一些危险提示）。某些操作必须避开高峰时段来进行，否则MySQL可能就挂了。所有现存的在线表结构修改的工具都是利用了MySQL的触发器来执行的，这种方式有一些潜藏的问题。

## 基于触发器的在线修改有哪些问题呢？

所有在线表结构修改工具的操作方式都类似：创建与原表结构一致的临时表，该临时表已经是按要求修改后的表结构了，缓慢增量的从原表中复制数据，同时记录原表的更改(所有的 INSERT, DELETE, UPDATE 操作) 并应用到临时表。当工具确认表数据已经同步完成，它会进行替换工作，将临时表更名为原表。

`pt-online-schema-change`, `LHM` 和 `oak-online-alter-table` 这些工具都使用同步的方式，当原表有变更操作时利用一些事务的间隙时间将这些变化同步到临时表。Facebook 的工具使用异步的方式将变更写入到changelog表中，然后重复的将changelog表的变更应用到临时表。所有的这些工具都使用触发器来识别原表的变更操作。

当表中的每一行数据有 INSERT, DELETE, UPDATE 操作时都会调用存储的触发器。一个触发器可能在一个事务空间中包含一系列查询操作。这样就会造成一个原子操作不单会在原表执行，还会调用相应的触发器执行多个操作。

在基于触发器迁移实践中，遇到了如下的问题：

- 触发器是以解释型代码的方式保存的。MySQL 不会预编译这些代码。 会在每次的事务空间中被调用，它们被添加到被操作的表的每个查询行为之前的分析和解释器中。

- 锁表：触发器在原始表查询中共享相同的事务空间，而这些查询在这张表中会有竞争锁，触发器在另外一张表会独占竞争锁。在这种极端情况下，同步方式的锁争夺直接关系到主库的并发写性能。以我们的经验来说，在生产环境中当竞争锁接近或者结束时，数据库可能会由于竞争锁而被阻塞住。触发锁的另一个方面是创建或销毁时所需要的元数据锁。我们曾经遇到过在繁忙的表中当表结构修改完成后，删除触发器可能需要数秒到分钟的时间。

- 不可信：当主库的负载上升时，我们希望降速或者暂停操作，但基于触发器的操作并不能这么做。虽然它可以暂停行复制操作，但却不能暂停出触发器，如果删除触发器可能会造成数据丢失，因此触发器需要在整个操作过程中都要存在。在我们比较繁忙的服务器中就遇到过由于触发器占用CPU资源而将主库拖死的例子。
- 并发迁移：我们或者其他的人可能比较关注多个同时修改表结构（不同的表）的场景。鉴于上述触发器的开销，我们没有兴趣同时对多个表进行在线修改操作，我们也不确定是否有人在生产环境中这样做过。

- 测试：我们修改表结构可能只是为了测试，或者评估其负载开销。基于触发器的表结构修改操作只能通过基于语句复制的方式来进行模拟实验，离真实的主库操作还有一定的距离，不能真实的反映实际情况。

## gh-ost

`gh-ost` GitHub 的在线 Schema 修改工具，下面工作原理图：

![图片描述](.pics/bVz0gO)

`gh-ost` 具有如下特性:

- 无触发器
- 轻量级
- 可暂停
- 可动态控制
- 可审计
- 可测试
- 值得信赖 

## 无触发器

`gh-ost` 没有使用触发器。它通过分析binlog日志的形式来监听表中的数据变更。因此它的工作模式是异步的，只有当原始表的更改被提交后才会将变更同步到临时表（ghost table）

`gh-ost` 要求binlog是RBR格式 ( 基于行的复制)；然而也不是说你就不能在基于SBR（基于语句的复制）日志格式的主库上执行在线变更操作。实际上是可以的。gh-ost 可以将从库的 SBR日志转换为RBR日志，只需要重新配置就可以了。

## 轻量级

由于没有使用触发器，因此在操作的过程中对主库的影响是最小的。当然在操作的过程中也不用担心并发和锁的问题。 变更操作都是以流的形式顺序的写到binlog文件中，gh-ost只是读取他们并应用到gh-ost表中。实际上，gh-ost 通过读取binlog的写事件来进行顺序的行复制操作。因此，主库只会有一个单独连接顺序的将数据写入到临时表（ghost table）。这和ETL操作有很大的不同。

## 可暂停

所有的写操作都是由gh-ost控制的，并且以异步的方式读取binlog，当限速的时候，gh-ost可以暂停向主库写入数据，限速意味着不会在主库进行复制，也不会有行更新。当限速时gh-ost会创建一个内部的跟踪（tracking）表，以最小的系统开销向这个表中写入心跳事件

gh-ost 支持多种方式的限速：

- 负载: 为熟悉 `pt-online-schema-change` 工具的用户提供了类似的功能，可以设置MySQL中的状态阈值，如 Threads_running=30
- 复制延迟: `gh-ost` 内置了心跳机制，可以指定不同的从库，从而对主从的复制延迟时间进行监控，如果达到了设定的延迟阈值程序会自动进入限速模式。
- 查询: 用户可以可以设置一个限流SQL，比如 `SELECT HOUR(NOW()) BETWEEN 8 and 17` 这样就可以动态的设置限流时间。
- 标示文件: 可以通过创建一个标示文件来让程序限速，当删除文件后可以恢复正常操作。
- 用户命令: 可以动态的连接到 `gh-ost` (下文会提到) 通过网络连接的方式实现限速。

## 可动态控制

现在的工具，当执行操作的过程中发现负载上升了，DBA不得不终止操作，重新配置参数，如 chunk-size，然后重新执行操作命令，我们发现这种方式效率非常低。

`gh-ost` 可以通过 unix socket 文件或者TCP端口（可配置）的方式来监听请求，操作者可以在命令运行后更改相应的参数，参考下面的例子：

- `echo throttle | socat - /tmp/gh-ost.sock` 打开限速，同样的，可以使用 `no-throttle` 来关闭限流。
- 改变执行参数: `chunk-size=1500`, `max-lag-millis=2000`, `max-load=Thread_running=30` 这些参数都可以在运行时变更。

## 可审计

同样的，使用上文提到的程序接口可以获取 `gh-ost` 的状态。`gh-ost` 可以报告当前的进度，主要参数的配置以及当前服务器的标示等等。这些信息都可以通过网络接口取到，相对于传统的tail日志的方式要灵活很多。

## 可测试

因为日志文件和主库负载关系不大，因此在从库上执行修改表结构的操作可以更真实的体现出这些操作锁产生的实际影响。(虽然不是十分理想，后续我们会做优化工作)。

`gh-ost` 內建支持测试功能，通过使用 `--test-on-replica` 的参数来指定: 它可以在从库上进行变更操作，在操作结束时`gh-ost` 将会停止复制，交换表，反向交换表，保留2个表并保持同步，停止复制。可以在空闲时候测试和比较两个表的数据情况。

这是我们在GitHub的生产环境中的测试：我们生产环境中有多个从库；部分从库并不是为用户提供服务的，而是用来对所有表运行的连续覆盖迁移测试。我们生产环境中的表，小的可能没有数据，大的会达到数百GB，我们只是做个标记，并不会正在的修改表结构（engine=innodb）。当每一个迁移结束后会停止复制，我们会对原表和临时表的数据进行完整的checksum确保他们的数据一致性。然后我们会恢复复制，再去操作下一张表。我们的生产环境的从库中已经通过 gh-ost 成功的操作了很多表。

## 值得信赖

上文提到说了这么多，都是为了提高大家对 `gh-ost` 的信任程度。毕竟在业界它还是一个新手，类似的工具已经存在了很多年了。

- 在第一次试手之前我们建议用户先在从库上测试，校验数据的一致性。我们已经在从库上成功的进行了数以千计的迁移操作。
- 如果在主库上使用 `gh-ost` 用户可以实时观察主库的负载情况，如果发现负载变化很大，可以通过上文提到的多种形式进行限速，直到负载恢复正常，然后再通过命令微调参数，这样可以动态的控制操作风险。
- 如果迁移操作开始后预完成计时间（ETA）显示要到夜里2点才能完成，结束时候需要切换表，你是不是要留下来盯着？你可以通过标记文件让gh-ost推迟切换操作。gh-ost 会完成行复制，但并不会切换表，它会持续的将原表的数据更新操作同步到临时表中。你第二天来到办公室，删除标记文件或者通过接口 `echo unpostpone` 告诉gh-ost开始切换表。我们不想让我们的软件把使用者绑住，它应该是为我们拜托束缚。
- 说到 ETA, `--exact-rowcount` 参数你可能会喜欢。相对于一条漫长的 `SELECT COUNT(*)` 语句，gh-ost 会预估出迁移操作所需要花费的时间，还会根据当前迁移的工作状况更新预估时间。虽然ETA的时间随时更改，但进度百分比的显示是准确的。

## gh-ost 操作模式

gh-ost 可以同时连接多个服务器，为了获取二进制的数据流，它会作为一个从库，将数据从一个库复制到另外一个。它有各种不同的操作模式，这取决于你的设置，配置，和要运行迁移环境。

![图片描述](.pics/bVz0gP)

### a. 连接到从库，在主库做迁移

这是 gh-ost 默认的工作方式。gh-ost 将会检查从库状态，找到集群结构中的主库并连接，接下来进行迁移操作：

- 行数据在主库上读写
- 读取从库的二进制日志，将变更应用到主库
- 在从库收集表格式，字段&索引，行数等信息
- 在从库上读取内部的变更事件（如心跳事件）
- 在主库切换表

如果你的主库的日志格式是 SBR，工具也可以正常工作。但从库必须启用二级制日志(log_bin, log_slave_updates) 并且设置 `binlog_format=ROW` ( gh-ost 是读取从库的二级制文件)。

如果直接在主库上操作，当然也需要二进制日志格式是RBR。

### b. 连接到主库

如果你没有从库，或者不想使用从库，你可以直接在主库上操作。`gh-ost` 将会直接在主库上进行所有操作。你需要持续关注复制延迟问题。

- 你的主库的二进制日志必须是 RBR 格式。
- 在这个模式中你必须指定 `--allow-on-master` 参数

### c. 在从库迁移/测试

该模式会在从库执行迁移操作。gh-ost 会简单的连接到主库，此后所有的操作都在从库执行，不会对主库进行任何的改动。整个操作过程中，gh-ost 将控制速度保证从库可以及时的进行数据同步

- `--migrate-on-replica` 表示 gh-ost 会直接在从库上进行迁移操作。即使在复制运行阶段也可以进行表的切换操作。
- `--test-on-replica` 表示 迁移操作只是为了测试在切换之前复制会停止，然后会进行切换操作，然后在切换回来，你的原始表最终还是原始表。两个表都会保存下来，复制操作是停止的。你可以对这两个表进行一致性检查等测试操作。

## gh-ost at GitHub

我们已经在所有线上所有的数据库在线操作中使用了gh-ost ，我们每天都需要使用它，根据数据库修改需求，可能每天要运行多次。凭借其审计和控制功能我们已经将它集成到了[ChatOps](https://www.pagerduty.com/blog/what-is-chatops/)流程中。我们的工程师可以清醒的了解到迁移操作的进度，而且可以灵活的控制其行为。

## 开源

gh-ost 在[MIT的许可](https://github.com/github/gh-ost/blob/master/LICENSE)下发布到了[开源社区](https://github.com/github/gh-ost)。

虽然gh-ost在使用中很稳定，我们还在不断的完善和改进。我们将其开源也欢迎社会各界的朋友能够参与和贡献。随后我们会发布 贡献和建议的页面。

我们会积极的维护 gh-ost 项目，同时希望广大的用户可以尝试和测试这个工具，我们做了很大努力使之更值得信赖。

\~~~~~~~~~~~~~~~ 万物之中,希望至美 ~~~~~~~~~~~~~~~

----

# gh-ost使用说明

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

```
#!/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------
# Purpose:     gh-ost
# Created:     2018-06-16
#----------------------------------------------
 
import MySQLdb
import re
import sys
import time
import subprocess
import os
from optparse import OptionParser
 
def calc_time(func):
    def _deco(*args, **kwargs):
        begin_time = time.time()
        func(*args, **kwargs)
        cost_time = time.time() - begin_time
        print 'cost time: %ss' % round(cost_time,2)
    return _deco
 
def get_table_count(conn,dbname,tbname):
    query  = ''' SELECT count(*) FROM %s.%s ''' %(dbname,tbname)
    cursor = conn.cursor()
    cursor.execute(query)
    row_nums = cursor.fetchone()
    cursor.close()
    conn.close()
    return row_nums
 
def online_ddl(conn,ddl_cmd):
    cursor = conn.cursor()
    cursor.execute(ddl_cmd)
    conn.commit()
    cursor.close()
    conn.close() 
 
#@calc_time
def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True)
    return p,p.pid
 
def drop_ghost_table(conn,ghost_name_list):
    try:
        cursor = conn.cursor()
        query  = ''' DROP TABLE IF EXISTS %s; ''' %(ghost_name_list)
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception,e:
        print e
 
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-P", "--Port", help="Port for search", dest="port")
    parser.add_option("-D", "--Dbname", help="the Dbname to use", dest="dbname")
    parser.add_option("-T", "--Table", help="the Table to use", dest="tablename")
 
    (options, args) = parser.parse_args()
 
    if not options.port:
        print 'params port need to apply'
        exit()
 
    if not options.dbname:
        print 'params dbname need to apply'
        exit()
 
    if not options.tablename:
        print 'params tablename need to apply'
        exit()
 
    gh_ost_socket   = '/tmp/gh-ost.%s.%s.sock' %(options.dbname,options.tablename)
    #终止标志
    panic_flag      = '/tmp/gh-ost.panic.%s.%s.flag' %(options.dbname,options.tablename)
    # postpone_flag   =  '/tmp/gh-ost.postpone.%s.%s.flag' %(options.dbname,options.tablename)
    #暂停标志
    throttle_flag   = '/tmp/gh-ost.throttle.%s.%s' %(options.dbname,options.tablename)
#    socket = '/data/%s/tmp/mysql.sock' %(options.port)
    socket = '/var/run/mysqld/mysqld.sock'
 
     
 
    get_conn = MySQLdb.connect(host='192.168.163.131', port=int(options.port), user='root', passwd='root', db=options.dbname, unix_socket=socket,charset='utf8')
    conn     = MySQLdb.connect(host='192.168.163.131', port=int(options.port), user='root', passwd='root', db=options.dbname, unix_socket=socket,charset='utf8')
     
    (table_count,) = get_table_count(get_conn,options.dbname,options.tablename)
    print ("\033[0;32m%s\033[0m" % "表的数量：%s" %table_count)
 
    DDL_CMD    = raw_input('Enter DDL CMD   : ').replace('`','')
 
    gh_command_list = re.split('[ ]+',DDL_CMD)
    if gh_command_list[0].upper() == 'CHANGE' and gh_command_list[1] != gh_command_list[2]:
        print ("\033[0;31m%s\033[0m" % "renamed columns' data will be lost,pt-osc exit...")
        exit()
 
    if table_count <= 10000:
        ddl = ''' ALTER TABLE %s %s ''' %(options.tablename,DDL_CMD)
        print ("\033[0;36m%s\033[0m" %ddl)
        print ("\033[0;32m%s\033[0m" % "online ddl ...")
        online_ddl(conn,ddl)
        print ("\033[0;32m%s\033[0m" % "执行完成 ...")
        exit()
 
    else:
        MAX_LOAD   = raw_input('Enter Max Threads_running【25】 : ')
        if not MAX_LOAD:
            Threads_running = 25
        else:
            try:
                Threads_running = int(MAX_LOAD)
            except ValueError:
                print ("\033[0;31m%s\033[0m" % "输入类型错误,退出...")
                exit()
 
        CHUNK_SIZE = raw_input('Enter Max chunk-size【1000】    : ')
        if not CHUNK_SIZE:
            chunk_size = 1000
        else:
            try:
                chunk_size = int(CHUNK_SIZE)
            except ValueError:
                print ("\033[0;31m%s\033[0m" % "输入类型错误,退出...")
                exit()
 
        print ("\033[0;32m%s\033[0m" % "gh-ost ddl ...")
        #--postpone-cut-over-flag-file=%s
        gh_command = '''/usr/bin/gh-ost --user="root" --password="root" --host=192.168.163.131 --port=%s --database="%s" --table="%s" --allow-on-master  --max-load='Threads_running=%d' --chunk-size=%d --serve-socket-file=%s --panic-flag-file=%s --throttle-additional-flag-file=%s --alter="%s"  --execute ''' %(options.port,options.dbname,options.tablename,Threads_running,chunk_size,gh_ost_socket,panic_flag,throttle_flag,DDL_CMD)
        print ("\033[0;36m%s\033[0m" %gh_command)
 
     
        child,pid = run_cmd(gh_command)
        print ("\033[0;31mgh-ost's PID：%s\033[0m" %pid)
        print ("\033[0;33m创建：【touch %s】文件，暂停DDL ...\033[0m" %throttle_flag)
        try:
            child.wait()
        except:
            child.terminate()
            #clean
            ghost_name_list = '_%s_ghc,_%s_gho'  %(options.tablename,options.tablename)
            drop_ghost_table(conn,ghost_name_list)
            if os.path.exists(gh_ost_socket):
                os.system('rm -r %s' %gh_ost_socket)
                print ("\033[0;32m%s\033[0m" % "清理完成 ...")
                exit()
            print ("\033[0;32m%s\033[0m" % "清理完成 ...")
            exit()
        finally :
            pass
```



运行：

```
root@test2:~# python gh-ost.py -P3306 -Dtest -Tzjy
表的数量：1310720
Enter DDL CMD   : ADD COLUMN q1 varchar(10),ADD COLUMN q2 varchar(10)
Enter Max Threads_running【25】 : 10
Enter Max chunk-size【1000】    : 200
gh-ost ddl ...
/usr/bin/gh-ost --user="root" --password="root" --host=192.168.163.131 --port=3306 --database="test" --table="zjy" --allow-on-master  --max-load='Threads_running=10' --chunk-size=200 --serve-socket-file=/tmp/gh-ost.test.zjy.sock --panic-flag-file=/tmp/gh-ost.panic.test.zjy.flag --throttle-additional-flag-file=/tmp/gh-ost.throttle.test.zjy --alter="ADD COLUMN q1 varchar(10),ADD COLUMN q2 varchar(10)"  --execute
gh-ost's PID：2105
创建：【touch /tmp/gh-ost.throttle.test.zjy】文件，暂停DDL ...
2018/06/17 14:37:37 binlogsyncer.go:79: [info] create BinlogSyncer with config {99999 mysql 192.168.163.131 3306 root   false false <nil>}
2018/06/17 14:37:37 binlogsyncer.go:246: [info] begin to sync binlog from position (mysql-bin.000013, 31197930)
2018/06/17 14:37:37 binlogsyncer.go:139: [info] register slave for master server 192.168.163.131:3306
2018/06/17 14:37:37 binlogsyncer.go:573: [info] rotate to (mysql-bin.000013, 31197930)
# Migrating `test`.`zjy`; Ghost table is `test`.`_zjy_gho`
# Migrating test2:3306; inspecting test2:3306; executing on test2
# Migration started at Sun Jun 17 14:37:37 +0800 2018
# chunk-size: 200; max-lag-millis: 1500ms; dml-batch-size: 10; max-load: Threads_running=10; critical-load: ; nice-ratio: 0.000000
# throttle-additional-flag-file: /tmp/gh-ost.throttle.test.zjy
# panic-flag-file: /tmp/gh-ost.panic.test.zjy.flag
# Serving on unix socket: /tmp/gh-ost.test.zjy.sock
Copy: 0/1305600 0.0%; Applied: 0; Backlog: 0/1000; Time: 0s(total), 0s(copy); streamer: mysql-bin.000013:31199542; State: migrating; ETA: N/A
Copy: 0/1305600 0.0%; Applied: 0; Backlog: 0/1000; Time: 1s(total), 1s(copy); streamer: mysql-bin.000013:31202866; State: migrating; ETA: N/A
Copy: 44400/1305600 3.4%; Applied: 0; Backlog: 0/1000; Time: 2s(total), 2s(copy); streamer: mysql-bin.000013:33352548; State: migrating; ETA: 56s
Copy: 91200/1305600 7.0%; Applied: 0; Backlog: 0/1000; Time: 3s(total), 3s(copy); streamer: mysql-bin.000013:35598132; State: migrating; ETA: 39s
Copy: 135200/1305600 10.4%; Applied: 0; Backlog: 0/1000; Time: 4s(total), 4s(copy); streamer: mysql-bin.000013:37727925; State: migrating; ETA: 34s
Copy: 174000/1305600 13.3%; Applied: 0; Backlog: 0/1000; Time: 5s(total), 5s(copy); streamer: mysql-bin.000013:39588956; State: migrating; ETA: 32s
Copy: 212200/1305600 16.3%; Applied: 0; Backlog: 0/1000; Time: 6s(total), 6s(copy); streamer: mysql-bin.000013:41430090; State: migrating; ETA: 30s
Copy: 254800/1305600 19.5%; Applied: 0; Backlog: 0/1000; Time: 7s(total), 7s(copy); streamer: mysql-bin.000013:43483555; State: migrating; ETA: 28s
Copy: 303600/1305600 23.3%; Applied: 0; Backlog: 0/1000; Time: 8s(total), 8s(copy); streamer: mysql-bin.000013:45834978; State: migrating; ETA: 26s
Copy: 351200/1305600 26.9%; Applied: 0; Backlog: 0/1000; Time: 9s(total), 9s(copy); streamer: mysql-bin.000013:48128675; State: migrating; ETA: 24s
Copy: 401400/1305600 30.7%; Applied: 0; Backlog: 0/1000; Time: 10s(total), 10s(copy); streamer: mysql-bin.000013:50547454; State: migrating; ETA: 22s
Copy: 451200/1305600 34.6%; Applied: 0; Backlog: 0/1000; Time: 11s(total), 11s(copy); streamer: mysql-bin.000013:52946991; State: migrating; ETA: 20s
Copy: 490000/1305600 37.5%; Applied: 0; Backlog: 0/1000; Time: 12s(total), 12s(copy); streamer: mysql-bin.000013:54817320; State: migrating; ETA: 19s
Copy: 529600/1305600 40.6%; Applied: 0; Backlog: 0/1000; Time: 13s(total), 13s(copy); streamer: mysql-bin.000013:56735431; State: migrating; ETA: 19s
Copy: 589200/1305600 45.1%; Applied: 0; Backlog: 0/1000; Time: 14s(total), 14s(copy); streamer: mysql-bin.000013:59606450; State: migrating; ETA: 17s
Copy: 639400/1305600 49.0%; Applied: 0; Backlog: 0/1000; Time: 15s(total), 15s(copy); streamer: mysql-bin.000013:62025561; State: migrating; ETA: 15s
Copy: 695200/1305600 53.2%; Applied: 0; Backlog: 0/1000; Time: 16s(total), 16s(copy); streamer: mysql-bin.000013:64704138; State: migrating; ETA: 14s
Copy: 751200/1305600 57.5%; Applied: 0; Backlog: 0/1000; Time: 17s(total), 17s(copy); streamer: mysql-bin.000013:67401961; State: migrating; ETA: 12s
Copy: 803800/1305600 61.6%; Applied: 0; Backlog: 0/1000; Time: 18s(total), 18s(copy); streamer: mysql-bin.000013:69935884; State: migrating; ETA: 11s
Copy: 856400/1305600 65.6%; Applied: 0; Backlog: 0/1000; Time: 19s(total), 19s(copy); streamer: mysql-bin.000013:72470455; State: migrating; ETA: 9s
Copy: 907400/1305600 69.5%; Applied: 0; Backlog: 0/1000; Time: 20s(total), 20s(copy); streamer: mysql-bin.000013:74927401; State: migrating; ETA: 8s
Copy: 958800/1305600 73.4%; Applied: 0; Backlog: 0/1000; Time: 21s(total), 21s(copy); streamer: mysql-bin.000013:77404243; State: migrating; ETA: 7s
Copy: 999200/1305600 76.5%; Applied: 0; Backlog: 0/1000; Time: 22s(total), 22s(copy); streamer: mysql-bin.000013:79351223; State: migrating; ETA: 6s
Copy: 1009600/1305600 77.3%; Applied: 0; Backlog: 0/1000; Time: 23s(total), 23s(copy); streamer: mysql-bin.000013:79855229; State: migrating; ETA: 6s
Copy: 1059600/1305600 81.2%; Applied: 0; Backlog: 0/1000; Time: 24s(total), 24s(copy); streamer: mysql-bin.000013:82264712; State: migrating; ETA: 5s
Copy: 1107200/1305600 84.8%; Applied: 0; Backlog: 0/1000; Time: 25s(total), 25s(copy); streamer: mysql-bin.000013:84558411; State: migrating; ETA: 4s
Copy: 1147000/1305600 87.9%; Applied: 0; Backlog: 0/1000; Time: 26s(total), 26s(copy); streamer: mysql-bin.000013:86486148; State: migrating; ETA: 3s
Copy: 1198000/1305600 91.8%; Applied: 0; Backlog: 0/1000; Time: 27s(total), 27s(copy); streamer: mysql-bin.000013:88943747; State: migrating; ETA: 2s
Copy: 1245400/1305600 95.4%; Applied: 0; Backlog: 0/1000; Time: 28s(total), 28s(copy); streamer: mysql-bin.000013:91218202; State: migrating; ETA: 1s
Copy: 1286600/1305600 98.5%; Applied: 0; Backlog: 0/1000; Time: 29s(total), 29s(copy); streamer: mysql-bin.000013:93203991; State: migrating; ETA: 0s
Copy: 1310720/1310720 100.0%; Applied: 0; Backlog: 0/1000; Time: 29s(total), 29s(copy); streamer: mysql-bin.000013:94366846; State: migrating; ETA: due
Copy: 1310720/1310720 100.0%; Applied: 0; Backlog: 1/1000; Time: 30s(total), 29s(copy); streamer: mysql-bin.000013:94369042; State: migrating; ETA: due
# Migrating `test`.`zjy`; Ghost table is `test`.`_zjy_gho`
# Migrating test2:3306; inspecting test2:3306; executing on test2
# Migration started at Sun Jun 17 14:37:37 +0800 2018
# chunk-size: 200; max-lag-millis: 1500ms; dml-batch-size: 10; max-load: Threads_running=10; critical-load: ; nice-ratio: 0.000000
# throttle-additional-flag-file: /tmp/gh-ost.throttle.test.zjy
# panic-flag-file: /tmp/gh-ost.panic.test.zjy.flag
# Serving on unix socket: /tmp/gh-ost.test.zjy.sock
Copy: 1310720/1310720 100.0%; Applied: 0; Backlog: 0/1000; Time: 30s(total), 29s(copy); streamer: mysql-bin.000013:94371928; State: migrating; ETA: due
2018/06/17 14:38:08 binlogsyncer.go:107: [info] syncer is closing...
2018/06/17 14:38:08 binlogstreamer.go:47: [error] close sync with err: sync is been closing... （这里的error不影响使用，重复关闭了sync，等作者修复）
2018/06/17 14:38:08 binlogsyncer.go:122: [info] syncer is closed
# Done
```



## 总结：

gh-ost 放弃了触发器，使用 binlog 来同步。gh-ost 作为一个伪装的备库，可以从主库/备库上拉取 binlog，过滤之后重新应用到主库上去，相当于主库上的增量操作通过 binlog 又应用回主库本身，不过是应用在幽灵表上。

![img](.pics/163084-20180615233341989-1215951790.png)

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