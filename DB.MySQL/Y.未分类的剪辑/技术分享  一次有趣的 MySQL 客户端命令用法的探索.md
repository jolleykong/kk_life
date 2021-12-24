## 技术分享 | 一次有趣的 MySQL 客户端命令用法的探索 

以下文章来源于爱可生开源社区 ，作者陈怡 

 

[**爱可生开源社区** ](http://)

[爱可生开源社区，提供稳定的MySQL企业级开源工具及服务，每年1024开源一款优良组件，并持续运营维护。](http://)

**前言**这篇文章简单介绍了一下运维时 MySQL 客户端中经常使用的一些小技巧。这些小技巧非专业 DBA 基本不会用到，专业的 DBA 必备。希望我的分享你们也能用到。MySQL 客户端的内置命令有以下这些，我们会探索其中 6 个：

List of all MySQL commands:

Note that all text commands must be first on line and end with ';'

?     (\?) Synonym for `help'.

clear   (\c) Clear the current input statement.

connect  (\r) Reconnect to the server. Optional arguments are db and host.

delimiter (\d) Set statement delimiter.

edit   (\e) Edit command with $EDITOR.

ego    (\G) Send command to mysql server, display result vertically.

exit   (\q) Exit mysql. Same as quit.

go    (\g) Send command to mysql server.

help   (\h) Display this help.

nopager  (\n) Disable pager, print to stdout.

notee   (\t) Don't write into outfile.

pager   (\P) Set PAGER [to_pager]. Print the query results via PAGER.

print   (\p) Print current command.

prompt  (\R) Change your mysql prompt.

quit   (\q) Quit mysql.

rehash  (\#) Rebuild completion hash.

source  (\.) Execute an SQL script file. Takes a file name as an argument.

status  (\s) Get status information from the server.

system  (\!) Execute a system shell command.

tee    (\T) Set outfile [to_outfile]. Append everything into given outfile.

use    (\u) Use another database. Takes database name as argument.

charset  (\C) Switch to another charset. Might be needed for processing binlog with multi-byte charsets.

warnings (\W) Show warnings after every statement.

nowarning (\w) Don't show warnings after every statement.

resetconnection(\x) Clean session context.

**1. pager**pager 的作用类似于 Linux 的管道符，可以把输出给另外一个命令作为输入。强大之处在于这个管道符接的命令是 Linux 命令，我们可以利用我们熟悉的 Linux 命令实现各种骚操作。话不多说，直接来几个例子。

**翻页**

mysql> pager less

PAGER set to 'less'

mysql> show engine innodb status\G

1 row in set (0.00 sec)

innodb status 的输出很长，接 Linux 命令 less 实现翻页，同样地根据您个人喜好，也可以用 more。

![rOW  Type ： InnoDB  Name:  Status:  2 319 一 11 一 2 8 14 ： 35 ： 17 3x7f319839d7e3 INNODB MONITOR OUTPUT  Per second ave rages calculated from the last 15 seconds  BACKGROUND THREAD  S rv master thread 100ps ： 14915 S rv active, S rv shutdown  S rv master th read 10g flush and writes: 14915  3 s rv idle  SEMAPHORES  OS WAIT ARRAY INFO ：  OS WAIT ARRAY INFO ：  RW-shared spins ，  reservation count 4298  signal count 3839  rounds 14 ， OS waits 7  RW- excl spins ， rounds 5652 ， OS waits 1  RW 一 s x spins ， rounds @ ， OS waits 9  Spin rounds per wait ： 14 ． 33 RW-shared, 5652 ． 33 RW-excI,  9 ． 0 3 RW-sx  TRANSACTIONS  Trx id counter 63217  Purge done for t rx S n ： 0 < 63217 undo n ： 0 < 9 state:  running but idle  History list length 21  LIST OF TRANSACTIONS FOR EACH SESSION:  -TRANSACTION 421327891@65584 ， not  ted  10C s t ru c t （ s ） ， hea  row lock(s)  ](clip_image001-1598939991604.jpg)

**查找搜索**

一般来说我们想查看目前有哪些正在跑的慢 SQL，可以用以下命令查询 information_schema 中的 processlist 表，这要求你熟悉元数据表。

mysql> select * from information_schema.PROCESSLIST where COMMAND='Query';

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

| ID  | USER | HOST   | DB         | COMMAND | TIME | STATE   | INFO                                |

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

| 3508 | root | localhost | information_schema | Query  |  0 | executing | select * from information_schema.PROCESSLIST where COMMAND='Query' |

| 3463 | root | localhost | NULL        | Query  | 233 | User sleep | select sleep(1000)                         |

| 3465 | root | localhost | NULL        | Query  | 228 | User sleep | select sleep(2000)                         |

| 3439 | root | localhost | NULL        | Query  | 235 | User sleep | select sleep(1000)                         |

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

4 rows in set (0.00 sec)

但用 pager 方法的话，我们可以利用 Linux 的 grep 命令，更高效地获取。

mysql> pager grep Query

PAGER set to 'grep Query'

mysql> show processlist;

| 3439 | root    | localhost     | NULL | Query      |  23 | User sleep                          | select sleep(1000) |

| 3463 | root    | localhost     | NULL | Query      |  21 | User sleep                          | select sleep(1000) |

| 3465 | root    | localhost     | NULL | Query      |  16 | User sleep                          | select sleep(2000) |

| 3473 | root    | localhost     | NULL | Query      |   0 | starting                           | show processlist  |

17 rows in set (0.00 sec)

甚至可以直接统计数量。

mysql> pager grep Query |wc -l

PAGER set to 'grep Query |wc -l'

mysql> show processlist;

4        #<-- 看这里

17 rows in set (0.00 sec)

实时发现有 4 个正在跑的查询。**关闭 pager**用完 pager 记得取消，取消的方法也很简单，有三种方法。

\#常用方法，设置pager回原默认值(stdout)

mysql> pager

Default pager wasn't set, using stdout.


 

\#关闭pager

mysql> nopager

PAGER set to stdout


 

\#退出客户端，重新连接

mysql> quit

Bye

**2. tee**tee 和 Linux 的 tee 命令是一样的。在输出到 stdout 同时可以指定同时输出到另外一个文件。使用他主要可以实现三个功能: 导数据、审计、记录操作。

**场景一：快速导出数据**

mysql> tee /tmp/general_log

Logging to file '/tmp/general_log'

mysql> select * from general_log where event_time >'2019-11-28 00:00:00';

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

| event_time         | user_host         | thread_id | server_id | command_type | argument                             |

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

| 2019-11-28 16:49:15.459116 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:18.604167 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:19.299166 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:20.283979 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:20.844283 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:21.289261 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:49.164062 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

7 rows in set (0.00 sec)

[root@chenyi tmp]# cat general_log

mysql> select * from general_log where event_time >'2019-11-28 00:00:00';

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

| event_time         | user_host         | thread_id | server_id | command_type | argument                             |

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

| 2019-11-28 16:49:15.459116 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:18.604167 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:19.299166 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:20.283979 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:20.844283 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:21.289261 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

| 2019-11-28 16:49:49.164062 | root[root] @ localhost [] |     5 |  153307 | Query    | select * from general_log where event_time >'2019-11-28 00:00:00' |

+----------------------------+---------------------------+-----------+-----------+--------------+-------------------------------------------------------------------+

7 rows in set (0.00 sec)


 

mysql> \q

**场景二：审计**

配置 my.cnf

[mysql]

tee=/tmp/tee.log

可以当客户端审计用,记录了客户端所有屏幕输出。(当然，这不是真正意义上的 MySQL 审计 ^ _ ^ )"客户端审计日志"如下：

[root@chenyi tmp]# cat /tmp/tee.log

Welcome to the MySQL monitor. Commands end with ; or \g.

Your MySQL connection id is 6

Server version: 5.7.27-log MySQL Community Server (GPL)


 

Copyright (c) 2000, 2019, Oracle and/or its affiliates. All rights reserved.


 

Oracle is a registered trademark of Oracle Corporation and/or its

affiliates. Other names may be trademarks of their respective

owners.


 

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.


 

mysql> nihao;

ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'nihao' at line 1

mysql> \q

提醒！使用这招要小心有人误操作，select 了大量的数据，导致文件写满磁盘。

**场景三：临时记录操作**

去客户那边排查问题，可以考虑先开 tee，然后排查故障完毕后，看着 tee.log 去编写故障分析邮件。

**关闭 tee**

notee;

所以刚才上面说的用tee审计作用不大，因为可以关闭！

**3. edit**相当于在 MySQL 中使用 vi 命令来编辑 SQL 语句。这个功能比较鸡肋，即使对于 vi 党来说，效率也没有多少提升。默认打开 edit 时，是编辑上一条 SQL 命令，退出 vi 后，输入“；”后回车就会执行在 vi 中编辑的 SQL。

mysql> select * from information_schema.PROCESSLIST where COMMAND='Query';

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

| ID  | USER | HOST   | DB         | COMMAND | TIME | STATE   | INFO                                |

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

| 3508 | root | localhost | information_schema | Query  |  0 | executing | select * from information_schema.PROCESSLIST where COMMAND='Query' |

| 3463 | root | localhost | NULL        | Query  | 233 | User sleep | select sleep(1000)                         |

| 3465 | root | localhost | NULL        | Query  | 228 | User sleep | select sleep(2000)                         |

| 3439 | root | localhost | NULL        | Query  | 235 | User sleep | select sleep(1000)                         |

+------+------+-----------+--------------------+---------+------+------------+--------------------------------------------------------------------+

4 rows in set (0.00 sec)

mysql> edit

![0 巳 1 已 匚 t  f 「 [ 翮 Information schema. PROCESSLIST Where COMRAND='Query'  "/tmp/sq1DbrDqa" [ no 01 ] IL, 65 〔  ](clip_image002-1598939991604.jpg)

不过有趣的是，使用 edit 可以**隐藏客户端操作记录**，实现“黑客操作”，下面我们来看看：

mysql> edit

  -> ;

PAGER set to 'grep -v 我是黑客 >>/tmp/1.log'

mysql> edit

  -> ;

Query OK, 0 rows affected (0.00 sec)


 

Query OK, 0 rows affected (0.00 sec)


 

mysql> edit

  -> ;

6 rows in set (0.00 sec)


 

mysql> \q

上面是我在控制台执行的 SQL 命令，相信大家都不知道我执行了什么。并且下一个用户使用我的 MySQL 客户端登录时只能看到以下四条命令行：

edit;

edit;

edit;

\q

这就隐藏了我的 SQL 命令行操作了。当我们开启了前面我们说的"客户端审计日志"，我们可以看到以下内容：

[root@chenyi tmp]# cat /tmp/tee.log

Welcome to the MySQL monitor. Commands end with ; or \g.

Your MySQL connection id is 9

Server version: 5.7.27-log MySQL Community Server (GPL)


 

Copyright (c) 2000, 2019, Oracle and/or its affiliates. All rights reserved.


 

Oracle is a registered trademark of Oracle Corporation and/or its

affiliates. Other names may be trademarks of their respective

owners.


 

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.


 

mysql> edit

  -> ;

PAGER set to 'grep -v 我是黑客 >>/tmp/1.log'

mysql> edit

  -> ;

Query OK, 0 rows affected (0.00 sec)


 

Query OK, 0 rows affected (0.00 sec)


 

mysql> edit

  -> ;

+------------------+---------------+

| user       | host     |

+------------------+---------------+

| heike      | %       |

| root       | 10.168.65.%  |

| mysql.session  | localhost   |

| mysql.sys    | localhost   |

| root       | localhost   |

| chenyi      | localhost   |

+------------------+---------------+

6 rows in set (0.00 sec)


 


 

mysql> \q

这个日志，可以发现我有一个 pager 操作，并且最后一个 edit 后有查询结果输出，但具体三个 edit 里的实际操作，我们都无从得知。最后一个 edit 后有查询结果输出说明了“tee 审计方式”会忽略 pager 的过滤作用，原输出被审计下来了，但执行的原 SQL 命令躲过了审计，被隐藏起来了。现在，我揭晓一下：

\#第一个edit

pager grep -v 我是黑客 >>/tmp/1.log


 

\#第三个edit

select user,host from mysql.user;

第二个 edit 我们目前还不知道是什么操作。当然我们实在要排查，可以尝试解析 binlog 碰碰运气，看是否是写入操作。如果安装了 mcafee 的审计插件，我们在审计插件也可以看到。

mcafee：https://bintray.com/mcafee/mysql-audit-plugin/release

{

 "msg-type": "activity",

 "date": "1574932159871",

 "thread-id": "9",

 "query-id": "129",

 "user": "root",

 "priv_user": "root",

 "ip": "",

 "host": "localhost",

 "connect_attrs": {

  "_os": "linux-glibc2.12",

  "_client_name": "libmysql",

  "_pid": "6004",

  "_client_version": "5.7.27",

  "_platform": "x86_64",

  "program_name": "mysql"

 },

 "pid": "6004",

 "os_user": "root",

 "appname": "/usr/local/mysql/bin/mysql",

 "status": "0",

 "cmd": "create_user",

 "query": "create user heike@'%' identified by '***'"

}

{

 "msg-type": "activity",

 "date": "1574932159874",

 "thread-id": "9",

 "query-id": "130",

 "user": "root",

 "priv_user": "root",

 "ip": "",

 "host": "localhost",

 "connect_attrs": {

  "_os": "linux-glibc2.12",

  "_client_name": "libmysql",

  "_pid": "6004",

  "_client_version": "5.7.27",

  "_platform": "x86_64",

  "program_name": "mysql"

 },

 "pid": "6004",

 "os_user": "root",

 "appname": "/usr/local/mysql/bin/mysql",

 "status": "0",

 "cmd": "grant",

 "query": "grant all on *.* to heike@'%'"

}


 同样的，第三个 edit，由于是 select 操作，也会被审计插件记录到。

{

 "msg-type": "activity",

 "date": "1574932192709",

 "thread-id": "9",

 "query-id": "131",

 "user": "root",

 "priv_user": "root",

 "ip": "",

 "host": "localhost",

 "connect_attrs": {

  "_os": "linux-glibc2.12",

  "_client_name": "libmysql",

  "_pid": "6004",

  "_client_version": "5.7.27",

  "_platform": "x86_64",

  "program_name": "mysql"

 },

 "pid": "6004",

 "os_user": "root",

 "appname": "/usr/local/mysql/bin/mysql",

 "rows": "35",

 "status": "0",

 "cmd": "select",

 "objects": [

  {

   "db": "mysql",

   "name": "user",

   "obj_type": "TABLE"

  }

 ],

 "query": "select user,host from mysql.user"

}

可以看出，审计插件的审计功能可以审计到服务器真实执行的 SQL，这是 tee 审计方式不可比拟的。但审计插件并没有发现我的 pager 操作，所以并不知道我导出了数据，只有 tee 审计方式发现了我导出了数据。

- 前面例子，我们可以看到，审计插件的审计日志里，密码是不显示的。
- 而我们知道 binlog 里，密码也是加密的。
- MySQL 客户端的历史记录里，是不会记录带      identified by 'xxx' 语句的。

所以，以上方式都不会泄露密码。

唯一会泄露明文密码的地方，是“tee审计方式”。而经过测试，结论是使用 edit 可以让明文密码绝不泄露。**所以，edit 操作可以隐藏密码。**最后，我揭晓一下，我第二 edit 操作是：

create user heike@'%' identified by 'Heike@2019';

grant all on *.* to heike@'%';

**4. system**不退出 MySQL 客户端情况下执行 Linux 命令。

**查看服务器 IP**

我一般用来确认 IP 地址。

mysql> system ip a

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000

  link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

  inet 127.0.0.1/8 scope host lo

   valid_lft forever preferred_lft forever

  inet6 ::1/128 scope host

   valid_lft forever preferred_lft forever

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000

  link/ether 02:00:0a:ba:41:0f brd ff:ff:ff:ff:ff:ff

  inet 10.186.65.15/24 brd 10.186.65.255 scope global eth0

   valid_lft forever preferred_lft forever

  inet6 fe80::aff:feba:410f/64 scope link

   valid_lft forever preferred_lft forever

**5. status**查看 MySQL 服务器状态。

mysql> status

\--------------

/usr/local/mysql/bin/mysql Ver 14.14 Distrib 5.7.27, for linux-glibc2.12 (x86_64) using EditLine wrapper


 

Connection id:    11

Current database:

Current user:    root@localhost

SSL:      Not in use

Current pager:    stdout

Using outfile:    '/tmp/tee.log'

Using delimiter:  ;

Server version:    5.7.27-log MySQL Community Server (GPL)

Protocol version:  10

Connection:    Localhost via UNIX socket

Server characterset:  utf8mb4

Db   characterset:  utf8mb4

Client characterset:  utf8

Conn. characterset:  utf8

UNIX socket:    /tmp/mysql3307.sock

Uptime:      1 hour 15 min 32 sec


 

Threads: 1 Questions: 145 Slow queries: 0 Opens: 195 Flush tables: 1 Open tables: 188 Queries per second avg: 0.031

\--------------

基本上去客户那处理问题，登录 MySQL 后第一个执行的命令行就是这个了。一般用 \s这个快捷命令。这里可以获取大量想要的信息。

- MySQL 连接的客户端是 5.7.27
- MySQL Server 的版本是 5.7.27 社区版
- 开启了"客户端审计日志"，输出到     /tmp/tee.log
- 我连接数据库用的是 sock 方式
- 一般来说不能获取连接的数据库端口信息，但这里的命名我甚至获取了端口信息！
- 我 pager 没有设置，用的默认 stdout，标准输出到屏幕
- 数据库开机运行时间 1 小时 15 分钟，数据库被重启过了？
- 数据库连接线程为 1 个，没有程序或人连数据库，只有我
- Questions 数 145 个。
- Slow queries为 0，没有慢查询
- Opens 数 195，没有快达到 65536 的上限
- Open tables 数 188，没有快达到 65536     的上限
- Queries per second avg，这个是     QPS，但他的算法是除以 uptime 时间，所以并不能反映现在服务器的负荷，没什么用

这里我要特别说明两个信息的获取：
 \1. 连接数如果我只想知道服务器连接有没有打满，那么我并不需要 show processlist ，直接 \s ，就知道了。2. QPS我这里说的 QPS 指的是 Questions per second。**方法一**从 status 命令获取

\s select sleep(1); \s

瞬时服务器真实 QPS 等于两次 \s 输出的 Questions 差值再减 4，因为 \s 本身会造成 3 个 Questions 数，而 select sleep(1) ；会造成 1 个个 Questions 数。**方法二**show global status 获取

show global status like 'Questions';select sleep(1);show global status like 'Questions';

瞬时服务器真实 QPS 等于两次 show global status like 'Questions' ；输出的差值再减 2，因为 show global status like 'Questions' ；本身会造成 1 个 Questions 数，而  select sleep(1) ；会造成 1 个 Questions 数。**方法三**最佳实践，因为平时观察 QPS 并不是看瞬时的一个点，我们需要持续看，所以用 mysqladmin 方法是合适的。

[root@chanyi tmp]# mysqladmin -uroot -proot -P3307 -S /tmp/mysql3307.sock -r -i 1 ext |grep -i 'question'

mysqladmin: [Warning] Using a password on the command line interface can be insecure.

| Questions                   | 162                       |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

| Questions                   | 1                        |

^C

这个方法实际上也采用 show global status 。

瞬时服务器真实 QPS 其实是 0，这个数字 1 来自于每秒一次的 show global status 。

**6. prompt**

修改 MySQL 提示登录提示符。

我一般会在两个情况使用它：

**临时标记主从或 ip 地址**

\#主库上

mysql> prompt master> ;

PROMPT set to 'master> '

master>


 

\#从库上

mysql> prompt slave> ;

PROMPT set to 'slave> '

slave>

**让提示符更丰富**

修改 /etc/my.cnf 配置文件

[mysql]

prompt=\\U [[\\d](file://d)]>

修改后的效果：

root@localhost [(none)]>use test

Reading table information for completion of table and column names

You can turn off this feature to get a quicker startup with -A


 

Database changed

root@localhost [test]>

现在，MySQL 客户端登录后可以方便清楚是哪个用户登录，切换到哪个数据库了。

**最佳实践**

修改 /etc/my.cnf 配置文件

[mysql]

prompt=\\u@\\h:\\p [\\R:\\m:\\s](file:///R:/m:/s) [[\\d](file://d)]>

修改后的效果：

[root@127.0.0.1:3308](mailto:root@127.0.0.1:3308) 01:42:58 [(none)]>use test

Reading table information for completion of table and column names

You can turn off this feature to get a quicker startup with -A


 

Database changed

[root@127.0.0.1:3308](mailto:root@127.0.0.1:3308) 01:43:04 [test]>

经过这么设置，我们可以通过提示符就知道我们登录的是哪个数据库实例，还可以记录下时间。如果再配合前面所说的"客户端审计日志"的话，能记录下登录的数据库实例以及 SQL 的执行时间，简直完美。

[root@chenyi tmp]# cat /tmp/tee.log

Welcome to the MySQL monitor. Commands end with ; or \g.

Your MySQL connection id is 9

Server version: 5.7.27-log MySQL Community Server (GPL)


 

Copyright (c) 2000, 2019, Oracle and/or its affiliates. All rights reserved.


 

Oracle is a registered trademark of Oracle Corporation and/or its

affiliates. Other names may be trademarks of their respective

owners.


 

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.


 

[root@127.0.0.1:3308](mailto:root@127.0.0.1:3308) 11:42:58 [(none)]>use test

Reading table information for completion of table and column names

You can turn off this feature to get a quicker startup with -A


 

Database changed

[root@127.0.0.1:3308](mailto:root@127.0.0.1:3308) 11:43:04 [test]>


 

mysql> \q

**最后**以上是我一次有趣的 MySQL 客户端命令用法的探索，希望大家喜欢。
 
 [](http://mp.weixin.qq.com/s?__biz=MzI1OTU2MDA4NQ==&mid=2247490680&idx=1&sn=4bd6f158eaf89ef90b5c475e0282f0fd&chksm=ea765b82dd01d2940610922f0708740a2a22471442e9c9115e7327a12bb584539c4bcc58facf&mpshare=1&scene=1&srcid=&sharer_sharetime=1580772220644&sharer_shareid=4ccc32335c079a86eae33281fea18c34#rd)