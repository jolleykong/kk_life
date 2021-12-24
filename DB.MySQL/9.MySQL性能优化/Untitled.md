- 判断数据库的内存是否达到瓶颈，查看服务器状态，比较物理磁盘的读取和内存读取的比例，来判断缓冲池的命中率。通常InnoDB缓冲池的命中率不应该小于99%

  ```
  mysql> show global status like 'innodb%read%';
  +---------------------------------------+------------+
  | Variable_name                         | Value      |
  +---------------------------------------+------------+
  | Innodb_buffer_pool_read_ahead_rnd     | 0          |	//
  | Innodb_buffer_pool_read_ahead         | 0          |	// 预读的次数
  | Innodb_buffer_pool_read_ahead_evicted | 0          |	// 预读的页，但是没有呗读取就从缓冲池中被替换的页的数量，用来判断预读的效率。
  | Innodb_buffer_pool_read_requests      | 404052672  |	// 从缓冲池中读取页的次数
  | Innodb_buffer_pool_reads              | 166575     |	// 从物理磁盘读取页的次数
  | Innodb_data_pending_reads             | 0          |	//
  | Innodb_data_read                      | 2742243840 |	// 总共读入的字节数
  | Innodb_data_reads                     | 167452     |	// 发起读取请求的次数，每次读取可能需要读取多个页。
  | Innodb_pages_read                     | 167369     |	//
  | Innodb_rows_read                      | 17523618   |	//
  +---------------------------------------+------------+
  10 rows in set (0.00 sec)
  ```

  缓冲池命中率= `Innodb_buffer_oool_read_requests / (Innodb_buffer_pool_read_requests + Innodb_buffer_pool_read_ahead + Innodb_buffer_pool_reads)`

  平均每次读取的字节数=`innodb_data_read / Innodb_data_reads`