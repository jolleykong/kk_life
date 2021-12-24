## 优化系列 | 实例解析MySQL性能瓶颈排查定位                

​          

# 导读

> 从一个现场说起，全程解析如何定位性能瓶颈。

# 排查过程

收到线上某业务后端的MySQL实例负载比较高的告警信息，于是登入服务器检查确认。

## 1. 首先我们进行OS层面的检查确认

登入服务器后，我们的目的是首先要确认当前到底是哪些进程引起的负载高，以及这些进程卡在什么地方，瓶颈是什么。

通常来说，**服务器上最容易成为瓶颈的是磁盘I/O子系统**，因为它的读写速度通常是最慢的。即便是现在的PCIe SSD，其随机I/O读写速度也是不如内存来得快。当然了，引起磁盘I/O慢得原因也有多种，需要确认哪种引起的。

第一步，我们一般先看整体负载如何，负载高的话，肯定所有的进程跑起来都慢。
可以执行指令 *w* 或者 *sar -q 1* 来查看负载数据，例如（横版查看）：

> ```
> [yejr@imysql.com:~ ]# w
> 11:52:58 up 702 days, 56 min,  1 user,  load average: 7.20, 6.70, 6.47
> USER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT
> root     pts/0    1.xx.xx.xx        11:51    0.00s  0.03s  0.00s w
> ```

或者 *sar -q* 的观察结果（横版查看）：

> ```
> [yejr@imysql.com:~ ]# sar -q 1
> Linux 2.6.32-431.el6.x86_64 (yejr.imysql.com)     01/13/2016     _x86_64_    (24 CPU)
> 02:51:18 PM   runq-sz  plist-sz   ldavg-1   ldavg-5  ldavg-15   blocked
> 02:51:19 PM         4      2305      6.41      6.98      7.12         3
> 02:51:20 PM         2      2301      6.41      6.98      7.12         4
> 02:51:21 PM         0      2300      6.41      6.98      7.12         5
> 02:51:22 PM         6      2301      6.41      6.98      7.12         8
> 02:51:23 PM         2      2290      6.41      6.98      7.12         8
> ```

load average大意表示当前CPU中有多少任务在排队等待，等待越多说明负载越高，跑数据库的服务器上，一般load值超过5的话，已经算是比较高的了。

引起load高的原因也可能有多种：

1. 某些进程/服务消耗更多CPU资源（服务响应更多请求或存在某些应用瓶颈）；
2. 发生比较严重的swap（可用物理内存不足）；
3. 发生比较严重的中断（因为SSD或网络的原因发生中断）；
4. 磁盘I/O比较慢（会导致CPU一直等待磁盘I/O请求）；

这时我们可以执行下面的命令来判断到底瓶颈在哪个子系统（横版查看）：

> ```
> [yejr@imysql.com:~ ]# top
> top - 11:53:04 up 702 days, 56 min,  1 user,  load average: 7.18, 6.70, 6.47
> Tasks: 576 total,   1 running, 575 sleeping,   0 stopped,   0 zombie
> Cpu(s):  7.7%us,  3.4%sy,  0.0%ni, 77.6%id, 11.0%wa,  0.0%hi,  0.3%si,  0.0%st
> Mem:  49374024k total, 32018844k used, 17355180k free,   115416k buffers
> Swap: 16777208k total,   117612k used, 16659596k free,  5689020k cached
> 
> PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND
> 14165 mysql     20   0 8822m 3.1g 4672 S 162.3  6.6  89839:59 mysqld
> 40610 mysql     20   0 25.6g  14g 8336 S 121.7 31.5 282809:08 mysqld
> 49023 mysql     20   0 16.9g 5.1g 4772 S  4.6 10.8   34940:09 mysqld
> ```

很明显是前面两个mysqld进程导致整体负载较高。
而且，从 Cpu(s) 这行的统计结果也能看的出来，**%us** 和 **%wa** 的值较高，表示**当前比较大的瓶颈可能是在用户进程消耗的CPU以及磁盘I/O等待上**。
我们先分析下磁盘I/O的情况。

执行 *sar -d* 确认磁盘I/O是否真的较大（横版查看）：

> ```
> [yejr@imysql.com:~ ]# sar -d 1
> Linux 2.6.32-431.el6.x86_64 (yejr.imysql.com)     01/13/2016     _x86_64_    (24 CPU)
> 11:54:32 AM    dev8-0   5338.00 162784.00   1394.00     30.76      5.24      0.98      0.19    100.00
> 11:54:33 AM    dev8-0   5134.00 148032.00  32365.00     35.14      6.93      1.34      0.19    100.10
> 11:54:34 AM    dev8-0   5233.00 161376.00    996.00     31.03      9.77      1.88      0.19    100.00
> 11:54:35 AM    dev8-0   4566.00 139232.00   1166.00     30.75      5.37      1.18      0.22    100.00
> 11:54:36 AM    dev8-0   4665.00 145920.00    630.00     31.41      5.94      1.27      0.21    100.00
> 11:54:37 AM    dev8-0   4994.00 156544.00    546.00     31.46      7.07      1.42      0.20    100.00
> ```

再利用 *iotop* 确认到底哪些进程消耗的磁盘I/O资源最多（横版查看）：

> ```
> [yejr@imysql.com:~ ]# iotop
> Total DISK READ: 60.38 M/s | Total DISK WRITE: 640.34 K/s
> TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND
> 16397 be/4 mysql       8.92 M/s    0.00 B/s  0.00 % 94.77 % mysqld --basedir=/usr/local/m~og_3320/mysql.sock --port=3320
> 7295 be/4 mysql      10.98 M/s    0.00 B/s  0.00 % 93.59 % mysqld --basedir=/usr/local/m~og_3320/mysql.sock --port=3320
> 14295 be/4 mysql      10.50 M/s    0.00 B/s  0.00 % 93.57 % mysqld --basedir=/usr/local/m~og_3320/mysql.sock --port=3320
> 14288 be/4 mysql      14.30 M/s    0.00 B/s  0.00 % 91.86 % mysqld --basedir=/usr/local/m~og_3320/mysql.sock --port=3320
> 14292 be/4 mysql      14.37 M/s    0.00 B/s  0.00 % 91.23 % mysqld --basedir=/usr/local/m~og_3320/mysql.sock --port=3320
> ```

可以看到，端口号是3320的实例消耗的磁盘I/O资源比较多，那就看看这个实例里都有什么查询在跑吧。

## 2. MySQL层面检查确认

首先看下当前都有哪些查询在运行（横版查看）：

> ```
> [yejr@imysql.com(db)]> mysqladmin pr|grep -v Sleep
> +----+----+----------+----+-------+-----+--------------+-----------------------------------------------------------------------------------------------+
> | Id |User| Host     | db |Command|Time | State        | Info                                                                                          |
> +----+----+----------+----+-------+-----+--------------+-----------------------------------------------------------------------------------------------+
> | 25 | x | 10.x:8519 | db | Query | 68  | Sending data | select max(Fvideoid) from (select Fvideoid from t where Fvideoid>404612 order by Fvideoid) t1 |
> | 26 | x | 10.x:8520 | db | Query | 65  | Sending data | select max(Fvideoid) from (select Fvideoid from t where Fvideoid>484915 order by Fvideoid) t1 |
> | 28 | x | 10.x:8522 | db | Query | 130 | Sending data | select max(Fvideoid) from (select Fvideoid from t where Fvideoid>404641 order by Fvideoid) t1 |
> | 27 | x | 10.x:8521 | db | Query | 167 | Sending data | select max(Fvideoid) from (select Fvideoid from t where Fvideoid>324157 order by Fvideoid) t1 |
> | 36 | x | 10.x:8727 | db | Query | 174 | Sending data | select max(Fvideoid) from (select Fvideoid from t where Fvideoid>324346 order by Fvideoid) t1 |
> +----+----+----------+----+-------+-----+--------------+-----------------------------------------------------------------------------------------------+
> ```

可以看到有不少慢查询还未完成，从slow query log中也能发现，这类SQL发生的频率很高。
这是一个非常低效的SQL写法，导致需要对整个主键进行扫描，但实际上只需要取得一个最大值而已，从slow query log中可看到：

> ```
> Rows_sent: 1  Rows_examined: 5502460
> ```

每次都要扫描500多万行数据，却只为读取一个最大值，效率非常低。

经过分析，这个SQL稍做简单改造即可在个位数毫秒级内完成，原先则是需要150-180秒才能完成，提升了N次方。
改造的方法是：**对查询结果做一次倒序排序，取得第一条记录即可**。而原先的做法是对结果正序排序，取最后一条记录，汗啊。。。

## 写在最后，小结

在这个例子中，产生瓶颈的原因比较好定位，SQL优化也不难，实际线上环境中，通常有以下几种常见的原因导致负载较高：

1. 一次请求读写的数据量太大，导致磁盘I/O读写值较大，例如一个SQL里要读取或更新几万行数据甚至更多，这种最好是想办法减少一次读写的数据量；
2. SQL查询中没有适当的索引可以用来完成条件过滤、排序（ORDER BY）、分组（GROUP BY）、数据聚合（MIN/MAX/COUNT/AVG等），添加索引或者进行SQL改写吧；
3. 瞬间突发有大量请求，这种一般只要能扛过峰值就好，保险起见还是要适当提高服务器的配置，万一峰值抗不过去就可能发生雪崩效应；
4. 因为某些定时任务引起的负载升高，比如做数据统计分析和备份，这种对CPU、内存、磁盘I/O消耗都很大，最好放在独立的slave服务器上执行；
5. 服务器自身的节能策略发现负载较低时会让CPU降频，当发现负载升高时再自动升频，但通常不是那么及时，结果导致CPU性能不足，抗不过突发的请求；
6. 使用raid卡的时候，通常配备BBU（cache模块的备用电池），早期一般采用锂电池技术，需要定期充放电（DELL服务器90天一次，IBM是30天），我们可以通过监控在下一次充放电的时间前在业务低谷时提前对其进行放电，不过新一代服务器大多采用电容式电池，也就不存在这个问题了。
7. 文件系统采用ext4甚至ext3，而不是xfs，在高I/O压力时，很可能导致%util已经跑到100%了，但iops却无法再提升，换成xfs一般可获得大幅提升；
8. 内核的io scheduler策略采用cfq而非deadline或noop，可以在线直接调整，也可获得大幅提升。