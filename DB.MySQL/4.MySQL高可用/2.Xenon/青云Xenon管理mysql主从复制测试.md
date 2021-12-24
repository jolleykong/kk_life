**环境：2台VM虚拟机CentOS7  X86_64 位系统**

# 配置环境要求:

**一、2台虚拟机器要关闭iptables 关闭firewalld, 关闭selinux，开启时间同步参数，保证2台虚拟机器的时间是一致的
二、2台虚拟机的sshd服务要开启22端口（Xenon代码中只支持通过22端口来ssh相互之间访问）
三、Xenon服务启动用户要和mysql服务的启动用户必须是相同的用户才行，此实例模拟演示都是采用的系统用户mysql.
四、2台虚拟机系统用户mysql，要允许shell登录，而且2台虚拟机mysql用户之间能互相免秘钥访问
五、2台虚拟机系统上安装的mysql的版本必须是mysql5.7版本以上(含mysql5.7)，而且2台mysql要开启半同步复制参数（Xenon是基于半同步复制的）
六、2台虚拟机系统上都要安装sshpass软件
七、2台虚拟机系统上的Xenon.json配置文件中要调用shell命令来执行相关的命令。由于xenon服务是系统普通用户mysql启动的，所以通过xenon.json文件执行命令行命令时，
需要授权mysql系统用户相关命令的sudo权限，才能够执行系统命令
八、xenon.json配置文件中要配置几个账户权限，来让xenon服务能够自动创建mysql的主从复制关系，以及自动切换mysql复制关系和自动故障恢复等等操作
提示：在xenon.json配置文件中配置mysql复制账户和密码时，xenon服务是能够自动创建复制账户的，并且给的权限是%的权限。并且自动创建复制关系。但是在测试中发现会报错，提示复制账户权限不正确。**

  **于是在此次演示过程中，本人自己直接在2台mysql的实例上创建相同的复制账户。**
  **命令如下**：

```
grant replication slave on *.* to repuser@'172.16.0.%' identified by 'repuser9slave'; flush privileges; ##复制账户和密码 
 grant all on *.* to root@'127.0.0.1' identified by 'rrtestjianwei';flush privileges;  
```

 **##在xenon构建的HA+  mysql集群中，建议读写都在master库上，所以在xenon维护的mysql集群中，slave库是不允许写的.master主库发生故障后，节点slave库要发生切换变成主库，所以原先的只读权限要通过这个账户登录数据库修改权限变为可读写**

```
 grant all on *.* to codeuser@'172.16.0.%' identified by 'rrtestjianwei';flush privileges;   
```

 **##允许代码连接库的账户和密码，以及IP地址，建议此处直接给绑定网卡的服务ip 172.16.0.100作为唯一的代码连接库的地址**

**九、2台虚拟机的IP地址和绑定 /etc/hosts**

```
系统IP地址
10.0.0.130  172.16.0.130
10.0.0.131  172.16.0.131
```

**提示：在2台物理机器上测试的时候，一开始由于2台物理机器插内网线的网口不相同（一个在网口2，一个在网口3），使得配置内网ip地址的网卡也不相同，在2台机器xenon.json配置文件中绑定服务ip的到网卡em1上。
虽然后面的测试，2台机器的上的xenon服务都能成功启动，并且也可以把各自的mysql服务拉起来，在2台机器上/data/xenon/bin/xenoncli cluster add ip:8801 添加对方的节点mysql。
并且服务ip也可以成功的绑定到预先设置的em1上。接着后面的问题出现了：在绑定有服务ip的机器上通过这个服务ip和他自身的内网ip是可以登录数据库的，但是在没有绑定服务ip机器上通过这个服务ip登录对端的mysql服务
居然被拒绝登录mysql服务（登录mysql服务的权限确定给的没问题）
于是让机房把这2台内网线重新到插到相同的网卡上，然后在相同的网卡上配置各自的内网ip地址，同时有在xenon.json配置文件中指定绑定服务ip到插内网线的网卡上。此时以上的问题得以解决**

**绑定 /etc/hosts:**

```
[root@mgr01 ~]# cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
172.16.0.130 mgr01
172.16.0.131 mgr03
[root@mgr03 ~]# cat /etc/hosts
172.16.0.130 mgr01
172.16.0.131 mgr03
```

# 下面介绍具体的配置步骤

**提示：下面的配置步骤要在2台虚拟机器上都要执行的**

**第一、安装二进制版本mysql5.7.24**

```
tar xf  mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz -C /usr/local/
cd /usr/local/
ln -sv mysql-5.7.24-linux-glibc2.12-x86_64 mysql
echo "export PATH=$PATH:/usr/local/mysql/bin" >/etc/profile.d/mysql.sh 
source  /etc/profile
初始化mysql：
mysqld  --defaults-file=/data/mysql/mysql3306/my3306.cnf  --initialize
启动mysql：
mysqld  --defaults-file=/data/mysql/mysql3306/my3306.cnf  &

[root@mgr01 ~]# cat .my.cnf 
[client]
socket = /tmp/mysql.sock
user=root
password=123456
prompt="(\\u@\\'mgr01':\\p)[\\d]>"
```

**登录mysql进行账户授权：**

```
grant replication slave on *.* to repuser@'172.16.0.%' identified by 'repuser9slave'; flush privileges;
grant all on *.* to root@'127.0.0.1' identified by 'rrtestjianwei';flush privileges;
grant all on *.* to codeuser@'172.16.0.%' identified by 'rrtestjianwei';flush privileges;
```

**提示:2台机器上都执行上面的步骤安装mysql.要求/data/mysql/mysql3306/my3306.cnf 配置文件都要开启MySQL的半同步复制的参数**

**下面的参数要写入到/data/mysql/mysql3306/my3306.cnf 配置文件:**

```
plugin-load="semisync_master.so;semisync_slave.so"
rpl_semi_sync_master_enabled=OFF
rpl_semi_sync_slave_enabled=ON
rpl_semi_sync_master_wait_no_slave=ON
rpl_semi_sync_master_timeout=1000000000000000000  ##参数目的就是不让半同步复制转化为异步复制
```

**第二、安装xenon服务**

**介绍：**
Xenon是一个自包含的二进制文件，在操作系统级别不需要其他系统库。 它基于Linux构建。 没有关于MS Windows和OS / X的提示，并且该版本与Windows和OS / X不兼容。 
它是一个独立的应用程序。 配置为与MySQL后端一起运行时，因此需要mysqld。

**Xenon使用GTID半同步并行复制技术，MySQL版本最好是5.7或更高版本**。 有关详细信息，请参见my.cnf
地址：https://github.com/radondb/xenon/blob/master/docs/config/MySQL.md
下面的mysql的半同步复制参数要写入到/data/mysql/mysql3306/my3306.cnf 配置文件

```
plugin-load="semisync_master.so;semisync_slave.so"
rpl_semi_sync_master_enabled=OFF
rpl_semi_sync_slave_enabled=ON
rpl_semi_sync_master_wait_no_slave=ON
rpl_semi_sync_master_timeout=1000000000000000000
```

**由于xenon服务是go语言开发的，所以需要go环境来运行，且要求需要Go版本1.8或更高版本**

**2.1安装go环境**

```
需要Go版本1.8或更高版本（对于ubuntu是“ sudo apt install golang”，对于centOS / redhat是“ yum install golang”）。
采用二进制安装golang ，版本是go1.9.3.linux-amd64.tar.gz
go 二进制包下载地址：
wget  https://storage.googleapis.com/golang/go1.9.3.linux-amd64.tar.gz
tar xf go1.11.linux-amd64.tar.gz  -C /usr/local/

[root@mgr01 ~]# tail -2 /etc/profile
export GOROOT=/usr/local/go
export PATH=$PATH:$GOROOT/bin
[root@mgr01 ~]# go version
go version go1.11 linux/amd64
```

**2.2 安装xenon服务**

```
1下载：
git clone https://github.com/radondb/xenon.git
cd xenon
2.编译构建
make build
 ls bin/
xenon  xenoncli
3.配置config
 cp xenon/conf/xenon-sample.conf.json /etc/xenon/xenon.json

[mysql@mgr01 ~]$ cat /data/xenon/bin/config.path
/etc/xenon/xenon.json
```

  **这里需要注意的是，运行xenon的帐户必须与mysql帐户一致，例如使用ubuntu帐户启动xenon，它需要ubuntu mysql的启动和mysql目录的权限。
这与传统的mysql地方不一样，不需要mysql帐户，运行xenon帐户的同事就是mysql帐户。**

**注意：以下是命令行示例的摘要。 为简单起见，我们假设xenon在您的指定的路径下。 如果不是，replace xenon with /path/to/xenon.
在xenon命令路径中，您需要有一个名为config.path的文件，它是xenon.json文件的绝对路径。 确保使用-c或--config指定xenon_config_file的位置。**

**2.3、2台机器创建系统用户mysql**

**2台机器创建系统用户mysql并且2台机器之间实现mysql用户免秘钥访问，而且mysql系统账户只能是22端口才能访问**

useradd mysql 
passwd mysql
 **授权mysql用户sudo权限可以执行下面的命令：**

```
 [root@mgr01 ~]# tail -1 /etc/sudoers
mysql ALL=(ALL)     NOPASSWD: /usr/sbin/ip
```

**2台虚拟机之间系统用户mysql相互免秘钥操作：**

```
 ssh-keygen -t rsa 
 .ssh/authorized_keys
 chmod 600 .ssh/authorized_keys 
```

**2.4、启动xenon服务：**

**172.16.0.130 机器xenon.json内容如下：（172.16.0.131配置文件要把IP跟换成自己内网卡172.16.0.131地址）**

```
[mysql@mgr01 ~]$ cat /etc/xenon/xenon.json 
{
    "server":
    {
        "endpoint":"172.16.0.130:8801"
    },

    "raft":
    {
        "meta-datadir":"raft.meta",
        "heartbeat-timeout":1000,
        "election-timeout":3000,
        "leader-start-command":"sudo /usr/sbin/ip a a 172.16.0.100/16 dev eth0 && arping -c 3 -A  172.16.0.100  -I eth0",
        "leader-stop-command":"sudo /usr/sbin/ip a d 172.16.0.100/16 dev eth0"
    },

    "mysql":
    {
        "admin":"root",
        "passwd":"rrtestjianwei",
        "host":"127.0.0.1",
        "port":3306,
        "basedir":"/usr/local/mysql",
        "defaults-file":"/data/mysql/mysql3306/my3306.cnf",
        "ping-timeout":1000,
        "master-sysvars":"super_read_only=0;read_only=0;sync_binlog=default;innodb_flush_log_at_trx_commit=default",
        "slave-sysvars": "super_read_only=1;read_only=1;sync_binlog=1000;innodb_flush_log_at_trx_commit=2"
    },

    "replication":
    {
        "user":"repuser",
        "passwd":"repuser9slave"
    },

    "backup":
    {
        "ssh-host":"172.16.0.130",
        "ssh-user":"mysql",
        "ssh-passwd":"rrtestjianwei669",
        "ssh-port":22,
        "backupdir":"/data/mysql/mysql3306/data",
        "xtrabackup-bindir":"/usr/bin",
        "backup-iops-limits":100000,
        "backup-use-memory": "1GB",
        "backup-parallel": 2
    },

    "rpc":
    {
        "request-timeout":500
    },

    "log":
    {
        "level":"INFO"
    }
}
```

**启动命令：**
 **172.16.0.130机器操作：**

```
[mysql@mgr01 ~]$ /data/xenon/bin/xenon -c /etc/xenon/xenon.json > /data/xenon/xenon.log 2>&1 &
```

**添加xenon节点**：

```
[mysql@mgr01 xenon]$  /data/xenon/bin/xenoncli  cluster add 172.16.0.131:8801
 2019/12/08 23:13:29.937943       [WARNING]     cluster.prepare.to.add.nodes[172.16.0.131:8801].to.leader[]
 2019/12/08 23:13:29.938024       [WARNING]     cluster.canot.found.leader.forward.to[172.16.0.130:8801]
 2019/12/08 23:13:29.950792       [WARNING]     cluster.add.nodes.to.leader[].done
```

 **查看xenon节点：**

```
[mysql@mgr01 ~]$ /data/xenon/bin/xenoncli  cluster status
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
|        ID         |              Raft              | Mysqld  | Monitor |          Backup          |        Mysql        | IO/SQL_RUNNING |     MyLeader      |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
| 172.16.0.130:8801 | [ViewID:16 EpochID:1]@LEADER   | RUNNING | ON      | state:[NONE]␤            | [ALIVE] [READWRITE] | [true/true]    | 172.16.0.130:8801 |
|                   |                                |         |         | LastError:               |                     |                |                   |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
| 172.16.0.131:8801 | [ViewID:16 EpochID:1]@FOLLOWER | RUNNING | ON      | state:[NONE]␤            | [ALIVE] [READONLY]  | [true/true]    | 172.16.0.130:8801 |
|                   |                                |         |         | LastError:               |                     |                |                   |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
(2 rows)
操作完成过6s后，有最初的都是read_only变成了一个[READONLY和一个READWRITE
```

 **172.16.0.131机器操作：**

```
[mysql@mgr03 ~]$ /data/xenon/bin/xenon -c /etc/xenon/xenon.json > /data/xenon/xenon.log 2>&1 &
[mysql@mgr03 ~]$ /data/xenon/bin/xenoncli  cluster add 172.16.0.130:8801

[mysql@mgr03 ~]$ /data/xenon/bin/xenoncli  cluster status
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
|        ID         |              Raft              | Mysqld  | Monitor |          Backup          |        Mysql        | IO/SQL_RUNNING |     MyLeader      |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
| 172.16.0.131:8801 | [ViewID:16 EpochID:1]@FOLLOWER | RUNNING | ON      | state:[NONE]␤            | [ALIVE] [READONLY]  | [true/true]    | 172.16.0.130:8801 |
|                   |                                |         |         | LastError:               |                     |                |                   |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
| 172.16.0.130:8801 | [ViewID:16 EpochID:1]@LEADER   | RUNNING | ON      | state:[NONE]␤            | [ALIVE] [READWRITE] | [true/true]    | 172.16.0.130:8801 |
|                   |                                |         |         | LastError:               |                     |                |                   |
+-------------------+--------------------------------+---------+---------+--------------------------+---------------------+----------------+-------------------+
操作完成过6s后，有最初的都是read_only变成了一个[READONLY和一个READWRITE
```

**同时服务IP172.16.0.100地址绑定到了10.0.0.130 的机器上**

```
[mysql@mgr01 xenon]$ ip a|grep 172.16.0.100
    inet 172.16.0.100/16 scope global eth0
```

**通过服务ip登录mysql，然后创建测试库：**

```
[mysql@mgr01 xenon]$ mysql -ucodeuser -h172.16.0.100 -p'rrtestjianwei' -e "create database test03;show databases;"
mysql: [Warning] Using a password on the command line interface can be insecure.
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| test01             |
| test02             |
| test03             |
+--------------------+
[mysql@mgr01 xenon]$ 
```

# 第三、xenon管理mysql一主一从故障演示

**进行故障演示，kill 掉主库，尝试通过服务ip连接库，大约25s才能链接成功主库，然后在连接后的新主库进行删除数据
主库切换在25s就可以完成**

进行故障演示，
**1.登录master库，执行shutdown关掉主库，尝试通过服务ip连接库，大约17s到20s才能重新绑定服务ip到master库的机器网卡上，然后通过这个服务ip成功连接主库，然后就可以操作对数据库的进行查看，写入，更新数据了
（物理服务器多次测试得出的）**

**2.登录master库的服务器，kill -9 掉mysql的进程，  然后master机器上的xenon会在4s到11s内自动把master机器的mysql服务拉起来，然后在绑定服务ip到master的网卡上，然后通过这个服务ip成功连接主库，就可以操作对数据库的进行查看，写入，更新数据了
（物理服务器多次测试得出的）**

**3..登录master库的服务器，移走数据目录data，关闭master库的mysql服务，此时虽然经过1m分钟左右服务ip已经飘到另外一台mysql，但是此时，这个库只能读，不行写。写入时会夯筑 （物理服务器多次测试得出的）**

**4.如果只是shutdown关闭slave库的话，通过服务ip地址远程写入一条记录然后在关闭此mysql实例；**
命令如下：

```
[root@slavedb 3306]# mysql -ucodeuser -h192.168.1.100 -p'rrtestjianwei' -e "INSERT INTO test01.test1(username,password,create_time) values('tomcat', 'xiaohuahua',now());"; mysql -e "shutdown;
```

**在执行完shutdown命令后，然后立刻执行下面的插入记录的命令：**

```
mysql -ucodeuser -h192.168.1.100 -p'rrtestjianwei' -e "INSERT INTO test01.test1(username,password,create_time) values('tomcat', 'xiaohuahua',now());"
```

**此时会夯筑，连续执行多次的话都不行，持续的时间在10-15s,才可以正常写入，但是此时相同的记录会被写入2次到master库上。（物理服务器多次测试得出的）**
如下：

```
| 31 | tomcat   | xiaohuahua | 2019-12-12 17:20:11 |
| 32 | tomcat   | xiaohuahua | 2019-12-12 17:23:28 |
| 33 | tomcat   | xiaohuahua | 2019-12-12 17:23:28 |
| 34 | tomcat   | xiaohuahua | 2019-12-12 17:23:38 |
| 35 | tomcat   | xiaohuahua | 2019-12-12 17:23:40 |
| 36 | tomcat   | xiaohuahua | 2019-12-12 17:25:32 |
| 37 | tomcat   | xiaohuahua | 2019-12-12 17:25:32 |
| 38 | tomcat   | xiaohuahua | 2019-12-12 17:25:45 |
+----+----------+------------+---------------------+
```

**5.如果把slave库的data目录移走，通过服务ip地址远程写入一条记录然后在关闭此mysql实例；**
命令如下：

```
[root@slavedb ~]#  mv data data_bak
[root@slavedb 3306]# ls
binlog  data_bak  logs  my.cnf  tmp
[root@slavedb ~]# mysql -ucodeuser -h192.168.1.100 -p'rrtestjianwei' -e "INSERT INTO test01.test1(username,password,create_time)values('tomcat', 'xiaohuahua',now());";mysql -e "shutdown;"
[mysql@localhost xenon]$ mysql -ucodeuser -h192.168.1.100 -p'rrtestjianwei' -e "INSERT INTO test01.test1(username,password,create_time) values('tomcat', 'xiaohuahua',now());"
```

**持续的夯筑时间在10-15s之间，才可以正常写入，但是此时相同的记录会被写入2次到master库上。（物理服务器多次测试得出的）**

```
 39 | tomcat   | xiaohuahua | 2019-12-12 17:37:31 |
| 40 | tomcat   | xiaohuahua | 2019-12-12 17:37:31 |
| 41 | tomcat   | xiaohuahua | 2019-12-12 17:37:42 |
| 42 | tomcat   | xiaohuahua | 2019-12-12 17:37:43 |
+----+----------+------------+---------------------+
42 rows in set (0.00 sec)
```

**创建测试表，插入测试语句:**

```
CREATE TABLE `test1` (
`id` int(8) NOT NULL AUTO_INCREMENT, 
`username` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
`password` varchar(20) COLLATE utf8_unicode_ci NOT NULL, 
`create_time` varchar(20) COLLATE utf8_unicode_ci NOT NULL, 
PRIMARY KEY (`id`) #主键ID
) ENGINE=innodb AUTO_INCREMENT=0 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO test1(username,password,create_time) values('tomcat', 'xiaohuahua',now());
INSERT INTO test1(username,password,create_time) values('tomcat', 'xiaohuahua',now());
```

**下面是dellR620物理机器上配置命令：**

```
 /data/xenon/bin/xenon -c /etc/xenon/xenon.json > /data/xenon/xenon.log 2>&1 &
 /data/xenon/bin/xenoncli cluster status
 /data/xenon/bin/xenoncli cluster add 192.168.1.39:8801,192.168.1.182:8801
  /data/xenon/bin/xenoncli cluster remove 192.168.1.105:8801
 sudo /usr/sbin/ip a a 192.168.1.100/32 dev em3 && arping -c 3 -A  192.168.1.100  -I em3

 sudo /usr/sbin/ip a d 192.168.1.100/32 dev em3
```

**下面是dellR620物理机器上创建数据库账户的命令：**

```
grant replication slave on *.* to repl@'192.168.1.%' identified by 'repl4slave'; flush privileges;
grant all on *.* to root@'127.0.0.1' identified by 'rrtestjianwei';flush privileges;
grant all on *.* to codeuser@'192.168.1.%' identified by 'rrtestjianwei';flush privileges;
```

**下面是dellR620物理机器上其中一台的xenon.json配置文件内容 ：**

```
[root@slavedb ~]# cat /etc/xenon/xenon.json 
{
    "server":
    {
        "endpoint":"192.168.1.39:8801"
    },

    "raft":
    {
        "meta-datadir":"raft.meta",
        "heartbeat-timeout":1000,
        "election-timeout":3000,
        "leader-start-command":"sudo /usr/sbin/ip a a 192.168.1.100/32 dev em3 && arping -c 3 -A  192.168.1.100  -I em3",
        "leader-stop-command":"sudo /usr/sbin/ip a d 192.168.1.100/32 dev em3"
    },

    "mysql":
    {
        "admin":"root",
        "passwd":"rrtestjianwei",
        "host":"127.0.0.1",
        "port":3306,
        "basedir":"/usr/local/mysql",
        "defaults-file":"/data/mysql/3306/my.cnf",
        "ping-timeout":1000,
        "master-sysvars":"super_read_only=0;read_only=0;sync_binlog=default;innodb_flush_log_at_trx_commit=default",
        "slave-sysvars": "super_read_only=1;read_only=1;sync_binlog=1000;innodb_flush_log_at_trx_commit=2"
    },

    "replication":
    {
        "user":"repl",
        "passwd":"repl4slave"
    },

    "backup":
    {
        "ssh-host":"192.168.1.39",
        "ssh-user":"mysql",
        "ssh-passwd":"rrtestjianwei669",
        "ssh-port":22,
        "backupdir":"/data/mysql/3306/data",
        "xtrabackup-bindir":"/usr/bin",
        "backup-iops-limits":100000,
        "backup-use-memory": "1GB",
        "backup-parallel": 2
    },

    "rpc":
    {
        "request-timeout":500
    },

    "log":
    {
        "level":"INFO"
    }
}
```

以上是简单的介绍演示，记录在此，方便自己查阅，也希望可以帮助有需要的网友们