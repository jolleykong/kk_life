已剪辑自: https://www.jianshu.com/p/62e95a131028

## 1. 简介

Orchestrator是一款开源的MySQL复制拓扑管理工具，采用go语言编写，支持MySQL主从复制拓扑关系的调整、支持MySQL主库故障自动切换、手动主从切换等功能。

Orchestrator后台依赖于MySQL或者SQLite存储元数据，能够提供Web界面展示MySQL集群的拓扑关系及实例状态，通过Web界面可更改MySQL实例的部分配置信息，同时也提供命令行和api接口，以便更加灵活的自动化运维管理。

相比于MHA，Orchestrator更加偏重于复制拓扑关系的管理，能够实现MySQL任一复制拓扑关系的调整，并在此基础上，实现MySQL高可用，另外Orchestrator自身可以部署多个节点，通过raft分布式一致性协议，保证自身的高可用。

## 2. 源码编译

源码地址：[https://github.com/github/orchestrator.git
 ](https://github.com/github/orchestrator.git) 目前最新版：v3.0.11
 编译（需要联网）：

git clone [https://github.com/github/orchestrator.git
 ](https://github.com/github/orchestrator.git) cd orchestrator
 script/build

编译完成后生成可执行文件： ./bin/orchestrator

## 3. 环境搭建

### 3.1 配置文件

在源码的orchestrator/conf目录中有3个配置文件模板，可参考使用。

- orchestrator-sample.conf.json
- orchestrator-sample-sqlite.conf.json
- orchestrator-simple.conf.json

这里列出一个简化的参数配置orchestrator.conf.json

{
   "Debug": true,
   "ListenAddress": ":3000",            #http开放端口
 
   "MySQLTopologyUser": "admin",          #mysql管理账号，所有被管理的MySQL集群都需要有该账号
   "MySQLTopologyPassword": "123456",       #mysql管理账号密码
 
   "MySQLOrchestratorHost": "127.0.0.1",      #后台mysql数据库地址，orchestrator依赖MySQL或者SQLite存储管理数据
   "MySQLOrchestratorPort": 3306,          #后台mysql数据库端口 
   "MySQLOrchestratorDatabase": "orchestrator",   #后台mysql数据库名
   "MySQLOrchestratorUser": "root",         #后台mysql数据库账号
   "MySQLOrchestratorPassword": "123456"      #后台mysql数据库密码
 
   "BackendDB": "sqlite",
   "SQLite3DataFile": "/root/orchestrator/orchestrator.sqlite3",
 
   "RecoverMasterClusterFilters": ["*"],
   "RecoverIntermediateMasterClusterFilters": ["*"],
 }

MySQLTopologyUser 这个配置项为被管理的MySQL集群的admin账号，该账号需要有super,process,reload,select,replicatiopn slave,replicatiopn client 权限。

### 3.2 后台数据库

orchestrator后台依赖MySQL或者SQLite存储管理数据，以MySQL为例，搭建Orchestrator环境，需要先搭建一个MySQL后台数据库，MySQL具体搭建过程不再详细介绍，搭建完，将MySQL账号密码等信息写入配置文件，如下：
 "MySQLOrchestratorHost": "127.0.0.1",
 "MySQLOrchestratorPort": 3306,
 "MySQLOrchestratorDatabase": "orchestrator",
 "MySQLOrchestratorUser": "root",
 "MySQLOrchestratorPassword": "123456",

如果觉得安装MySQL太麻烦，只想快速体验一下Orchestrator，建议使用SQLite，只需在配置文件中写入如下配置：
 "BackendDB": "sqlite",
 "SQLite3DataFile": "/root/orchestrator/orchestrator.sqlite3",

## 4. 执行命令

orchestrator 通过 -c 来执行具体的命令，通过 orchestrator help 查看所有命令的帮助文档， orchestrator help relocate 查看具体命令relocate的帮助文档。
 orchestrator 提供的命令很多，这里提一些比较重要和常用的命令，没有提到的可自行去文档或者源码中查看。
 比如执行一个命令：
 ./orchestrator --config=./orchestrator.conf.json -c discover -i mysql_host_name

### 4.1 MySQL实例管理命令

discover
 forget
 begin-maintenance
 end-maintenance
 in-maintenance
 begin-downtime
 end-downtime

**discover
 用于发现实例以及该实例的主、从库信息，将获取到的信息写入后台数据库database_instance等相关表
 orchestrator --config=./orchestrator.conf.json -c discover -i host_name**

**forget
 移除实例信息，即从database_instance表中删除相关记录
 orchestrator --config=./orchestrator.conf.json -c forget -i host_name**

**begin-maintenance
 标记一个实例进入维护模式，在database_instance_maintenance表中插入记录
 orchestrator -c begin-maintenance -i instance.to.lock.com --duration=3h --reason="load testing; do not disturb"**

**end-maintenance
 标记一个实例退出维护模式，即更新 database_instance_maintenance 表中相关记录
 orchestrator -c end-maintenance -i locked.instance.com**

**in-maintenance
 查询实例是否处于维护模式，从表database_instance_maintenance中查询
 orchestrator -c in-maintenance -i locked.instance.com**

**begin-downtime
 标记一个实例进入下线模式，在database_instance_downtime表中插入记录
 orchestrator -c begin-downtime -i instance.to.downtime.com --duration=3h --reason="dba handling; do not do recovery"**

**end-downtime
 标记一个实例退出下线模式，在database_instance_downtime表中删除记录
 orchestrator -c end-downtime -i downtimed.instance.com**

### 4.2 MySQL实例信息查询命令

find
 search
 clusters
 clusters-alias
 all-clusters-masters
 topology
 topology-tabulated
 all-instances
 which-instance
 which-cluster
 which-cluster-domain
 which-heuristic-domain-instance
 which-cluster-master
 which-cluster-instances
 which-cluster-osc-replicas
 which-cluster-gh-ost-replicas
 which-master
 which-downtimed-instances
 which-replicas
 which-lost-in-recovery
 instance-status
 get-cluster-heuristic-lag

**find
 通过正则表达式搜索实例名
 orchestrator -c find -pattern "backup.\*us-east"**

**search
 通过关键字匹配搜索实例名
 orchestrator -c search -pattern "search string"**

**clusters
 输出所有的MySQL集群名称，通过sql查询database_instance相关表获取
 orchestrator -c clusters**

**clusters-alias
 输出所有MySQL集群名称以及别名
 orchestrator -c clusters-alias**

**all-clusters-masters
 输出所有MySQL集群可写的主库信息
 orchestrator -c all-clusters-masters**

**topology
 输出实例所属集群的拓扑信息
 orchestrator -c topology -i instance.belonging.to.a.topology.com**

**topology-tabulated
 输出实例所属集群的拓扑信息，类似topology命令，输出格式稍有不同
 orchestrator -c topology-tabulated -i instance.belonging.to.a.topology.com**

**all-instances
 输出所有已知的实例
 orchestrator -c all-instances**

**which-instance
 输出实例的完整的信息
 orchestrator -c which-instance -i instance.to.check.com**

**which-cluster
 输出MySQL实例所属的集群名称
 orchestrator -c which-cluster -i instance.to.check.com**

**which-cluster-domain
 输出MySQL实例所属集群的域名
 orchestrator -c which-cluster-domain -i instance.to.check.com**

**which-heuristic-domain-instance
 给定一个集群域名，输出与其关联的可写的实例
 orchestrator -c which-heuristic-domain-instance -alias some_alias**

**which-cluster-master
 输出实例所属集群的主库信息
 orchestrator -c which-cluster-master -i instance.to.check.com**

**which-cluster-instances
 输出实例所属集群的所有实例信息
 orchestrator -c which-cluster-instances -i instance.to.check.com**

**which-master
 列出实例所属集群的主库信息，与which-cluster-master类似
 orchestrator -c which-master -i a.known.replica.com**

**which-downtimed-instances
 列出处于下线状态的实例
 orchestrator -c which-downtimed-instances**

**which-replicas
 输出实例的从库信息
 orchestrator -c which-replicas -i a.known.instance.com**

**which-lost-in-recovery
 输出处于下线状态，在故障恢复过程中丢失的实例
 orchestrator -c which-lost-in-recovery**

**instance-status
 输出实例的状态信息
 orchestrator -c instance-status -i instance.to.investigate.com**

**get-cluster-heuristic-lag
 输出实例所属集群的最大延迟信息
 orchestrator -c get-cluster-heuristic-lag -i instance.that.is.part.of.cluster.com**

### 4.3 故障恢复命令

recover
 recover-lite
 force-master-failover
 force-master-takeover
 graceful-master-takeover
 replication-analysis
 ack-all-recoveries
 ack-cluster-recoveries
 ack-instance-recoveries
 relocate

**recover
 主库故障切换，主库必须关闭，执行才有效果， -i 参数必须是已经关闭的主库， 新主库不需要指定，由orchestrator自己选择。
 orchestrator -c recover -i dead.instance.com --debug**

**recover-lite
 主库故障切换，与recover类似，简化的部分操作，更加轻量化。
 orchestrator -c recover-lite -i dead.instance.com --debug**

**force-master-failover
 不管主库是否正常，强制故障切换，切换后主库不关闭，新主库不需要指定，由orchestrator选择。这个操作比较危险，谨慎使用。
 orchestrator -c force-master-failover**

**force-master-takeover
 不管主库是否正常，强制主从切换，-i指定集群中任一实例，-d 指定新主库， 注意 切换后旧主库不会指向新主库**，需要手动操作。
 orchestrator -c force-master-takeover -i instance.in.relevant.cluster.com -d immediate.child.of.master.com

**graceful-master-takeover
 主从切换，旧主库会指向新主库，但是复制线程是停止的，需要人工手动执行start slave，恢复复制。
 orchestrator -c graceful-master-takeover -i instance.in.relevant.cluster.com -d immediate.child.of.master.com**

**replication-analysis
 根据已有的拓扑关系分析潜在的故障事件，分析结果输出格式不稳定，未来可能改变，建议不要使用该功能。
 orchestrator -c replication-analysis**

**ack-all-recoveries
 ack-cluster-recoveries
 ack-instance-recoveries
 确认已有的故障恢复，防止未来再次发生故障时，会阻塞故障切换
 orchestrator -c ack-all-recoveries --reason="dba has taken taken necessary steps"
 orchestrator -c ack-cluster-recoveries -i instance.in.a.cluster.com --reason="reson message"
 orchestrator -c ack-instance-recoveries -i instance.that.failed.com --reason="reson message"**

**relocate
 调整拓扑结构，-i 指定的实例更改为 -d 指定实例的从库。
 orchestrator -c relocate -i replica.to.relocate.com -d instance.that.becomes.its.master**

## 5. 自动故障切换

Orchestrator能够配置成自动检测主库故障，并完成故障切换。

1. 以http方式启动后台Web服务
              orchestrator     --config=./orchestrator.conf.json --debug http
              成功启动后，可通过浏览器访问Web页面：
              http://192.168.56.110:3000
2. 参数配置

"RecoverMasterClusterFilters": ["*"],
 "RecoverIntermediateMasterClusterFilters": ["*"],
 "FailureDetectionPeriodBlockMinutes": 60,
 "RecoveryPeriodBlockSeconds": 3600

RecoverMasterClusterFilters 和 RecoverIntermediateMasterClusterFilters 必须配置为["*"]，否则自动切换不会触发。
 FailureDetectionPeriodBlockMinutes 和 RecoveryPeriodBlockSeconds 参数默认值为1个小时，也就是如果发生了故障切换，在1个小时之内，该主库再次出现故障，将不会被监测到，也不会触发故障切换。

## 6. Orchestrator 高可用

Orchestrator多节点部署，通过raft一致性协议实现自身高可用。
 例如在如下3台机器部署Orchestrator节点：

- 192.168.56.110
- 192.168.56.111
- 192.168.56.112

在每个节点上修改orchestrator.conf.json配置文件：

"RaftEnabled": true, 
 "RaftDataDir": "/var/lib/orchestrator", 
 "RaftBind": "192.168.56.110", 
 "DefaultRaftPort": 10008, 
 "RaftNodes": [ "192.168.56.110", "192.168.56.111", "192.168.56.112" ],

RaftBind配置为当前节点ip，在每个节点上启动orchestrator服务：
 ./orchestrator --config=./orchestrator.conf.json --debug http

在浏览器中访问：
 [http://192.168.56.110:3000/api/leader-check
 ](http://192.168.56.110:3000/api/leader-check) 返回 "OK"，当前leader为192.168.56.110
 [http://192.168.56.110:3000/api/raft-health
 ](http://192.168.56.110:3000/api/raft-health) 返回 "healthy"

[http://192.168.56.111:3000/api/leader-check
 ](http://192.168.56.111:3000/api/leader-check) 返回 "Not leader"
 [http://192.168.56.111:3000/api/raft-health
 ](http://192.168.56.111:3000/api/raft-health) 返回 "healthy"

关闭192.168.56.110节点上的orchestrator服务，leader自动切换到192.168.56.111或者192.168.56.112，如果192.168.56.110重新启动后，加入集群，它将作为follower。

## 7. 注意事项

1. Orchestrator官方文档部分内容不准确，比如 MySQLTopologyUser 账号的权限应该设置为super,process,reload,select,replicatiopn     slave,replicatiopn client，文档中缺少了select权限，orchestrator切换过程中需要通过读取从库的mysql.slave_master_info表，获取复制账号和密码，如果没有select权限，将导致读取失败，并且不会有任何错误信息报出来。
2. orchestrator 建议使用机器名，而不是ip来管理MySQL实例，比如change master to 中的 master_host 如果指定的是ip，有可能导致主从切换或者故障切换出现问题。

最后附上Web页面图：


 

Orchestrator