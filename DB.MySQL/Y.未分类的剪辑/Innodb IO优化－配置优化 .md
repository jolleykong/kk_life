## 				 [     Innodb IO优化－配置优化        ](https://www.cnblogs.com/mydriverc/p/8301826.html) 			

**作者：吴炳锡　来源：http://www.mysqlsupport.cn/ 联系方式： wubingxi#gmail.com 转载请注明作/译者和出处，并且不能用于商业用途，违者必究.**

对于数据库来讲大多瓶颈都出现在IO问题上，所以现在SSD类的设备也才能大行其道。那数据库的IO这块有什么可以优化的吗？ 我这里大致谈一下我的看法，希望能达到一个抛砖引玉的效果。
这里谈一下数据库本身的配置方面
**具体如下：**
配置方面对于IO优化的原则：尽可能能缓存，减少读对数据库的随机IO的请求；同时减少写的随机IO的随时发生，利用各种buffer去缓存。下面来看一下这块的参数：

- innodb_buffer_pool_size : 这是Innodb最重要的一个配置参数，这个参数控制Innodb本身的缓大小，也影响到，多少数据能在缓存中。建议该参数的配置在物理内存的70％－80％之间。
- innodb_flush_method: 这个控制Innodb的IO形为，什么:fsync, O_DSYNC之类的，这里不做过多介绍，  建议使用: O_DIRECT,  这样减少操作系统级别VFS的缓存使用内存过多和Innodb本身的buffer的缓存冲突，同时也算是给操作系统减少点压力。
- innodb_io_capacity: 这个参数据控制Innodb checkpoint时的IO能力，一般可以按一块SAS  15000转的磁盘200个计算，6块盘的SAS做的Raid10这个值可以配到600即可。如果是普通的SATA一块盘只能按100算。（innodb-plugin, Percona有这个参数）
- innodb_max_dirty_pages_pct :  这个参数据控制脏页的比例如果是innodb_plugin或是MySQL5.5以上的版本，建议这个参数可以设制到75%-90%都行。如果是大量写入，而且写入的数据不是太活跃，可以考虑把这个值设的低一点。 如果写入或是更新的数据也就是热数据就可以考虑把这个值设为：95%
- innodb_log_file_size :  这个可以配置256M以上，建议有两个以前的日志文件（innodb_log_files_in_group).  如果对系统非常大写的情况下，也可以考虑用这个参数提高一下性能，把文件设的大一点，减少checkpiont的发生。  最大可以设制成：innodb_log_files_in_group * innodb_log_file_size <  512G(percona, MySQL 5.6) 建议设制成: 256M ->  innodb_buffer_pool_size/innodb_log_file_in_group 即可。
- innodb_log_buffer_size : 如果没在大事务，控制在8M-16M即可。

**其它对IO有影响的参数(以5.6为准）**

- innodb_adaptive_flushing 默认即可
- innodb_change_buffer_max_size 如果是日值类服务，可以考虑把这个增值调到 50
- innodb_change_buffering 默认即可
- innodb_flush_neighors 默认是开的， 这个一定要开着，充分利用顺序IO去写数据。
- innodb_lru_scan_depth: 默认即可 这个参数比较专业。
- innodb_max_purge_lag 默认没启用，如果写入和读取都量大，可以保证读取优先，可以考虑使用这个功能。
- innodb_random_read_ahead 默认没开启，属于一个比较活跃的参数，如果要用一定要多测试一下。 对用passport类应用可以考虑使用
- innodb_read_ahead_threshold 默认开启：56 预读机制可以根据业务处理，如果是passprot可以考虑关闭。如果使用innodb_random_read_ahead,建议关闭这个功能
- innodb_read_io_threads 默认为：4 可以考虑8
- innodb_write_io_threads 默认为：4 可以考虑8
- sync_binlog 默认即可： 0
- innodb_rollback_segments 默认即可: 128

另外5.6的undo log也可以独立配置了，建议单独配置出来。