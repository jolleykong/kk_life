# [InnoDB多核并发设置](https://cs.xieyonghui.com/database/mysql-multi-core-configuration_62.html)

MySQL InnoDB允许调整事务存储引擎的多核并发参数。

## innodb_thread_concurrency

同时打开并发线程数的上限，最佳实践是（2 X CPU数）+磁盘数。

通常应将其设置为0，InnoDB存储引擎能根据运行环境找出最佳线程数。

## innodb_concurrency_tickets

设置可绕过并发检查的线程数，达到指定值后，会执行并发线程数的检查（免检参数设置）。

## innodb_commit_concurrency

设置可提交的并发事务的数，默认值为0，若不进行设置则允许同时提交任意数量事务。

## innodb_thread_sleep_delay

InnoDB线程重新进入InnoDB队列前可处于休眠状态的毫秒数。默认值10000(10秒)。

## innodb_read_io_threads and innodb_write_io_threads

为读写分配指定线程数，默认值为4，最大值为64。

注：MySQL 5.1.38起。

## innodb_read_ahead_threshold

允许以线性方式读取数据块大小(64 pages [page = 16K])，超过此值以异步方式读取。

InnoDB在多cpu服务器中表现良好，具有多线程操作的默认配置。

若调整它们需非常小心。

innodb_thread_concurrency参数为0，让InnoDB内部决定线程并发数最佳方案。

更多配置参考MySQL官方文档关于[InnoDB启动选项和系统参数](https://cs.xieyonghui.com/redirect?su=UozDrz)。





# InnoDB并发配置

InnoDB是为高性能而生的，但是也有不完美的情况，当InnoDB架构在内存有限，单CPU，单磁盘的系统中就会暴露出一些问题。在高并发情况下，InnoDB的某些方面的性能会有所降低，具体是什么方面并不知道。这个时候只能通过限制并发来让InnoDB降低性能的方面恢复正常。

控制并发最有效的方法就是使用innodb_thread_concurrency变量，它表示一次行能够进入内核的最大线程数。0表示不限制。并发值有一个公式：cpu*磁盘*2。这只是一个理论值，在实际操作中，更小的值会更好一些。如果内核中的线程数已经超过了允许的值，新的线程就无法再进入内核。

InnoDB通过两段处理来尝试让线程进入内核，第一次尝试，如果失败，就会进入睡眠。睡眠时间默认是10,000（10毫秒），由变量innodb_thread_sleep_delay控制。睡眠完之后再次尝试进入内核。如果再次失败，就会进入一个等待线程队列，控制权交给操作系统。



线程一旦进入内核，就会有一定数量的“票据”，这个票据可以让它免费返回内核，不再做并发检测。但也限制了一个线程回到其他等待线程之前可以做的事。票据由innodb_concurrency_tickets控制，一般很少改动。票据是按查询来的，不是按事务。一旦查询完成，没用完的票据也会被销毁。

innidb_commit_concurrency控制多少线程可以同一时间提交。