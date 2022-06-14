> 资料可能已经过时，仅供参考。

# 分析表锁定

- 查看哪些表加了锁(1代表被加了锁)

  ```
  show open tables ; 
  ```

- 分析表锁定的严重程度

  ```
  show status like 'table%' ;
  - Table_locks_immediate:可能获取到的锁数
  - Table_locks_waited:需要等待的表锁数(如果该值越大，说明存在越大的锁竞争)
  ```

  > 一般建议：Table_locks_immediate/Table_locks_waited > 5000， 建议采用InnoDB引擎，否则MyISAM引擎

- 如果索引类 发生了类型转换，则索引失效，会从行锁 转为表锁。

- 行锁分析

  ```
  show status like '%innodb_row_lock%' ;
  - Innodb_row_lock_current_waits	:当前正在等待锁的数量  
  - Innodb_row_lock_time			:等待总时长。从系统启到现在 一共等待的时间
  - Innodb_row_lock_time_avg		:平均等待时长。从系统启到现在平均等待的时间
  - Innodb_row_lock_time_max		:最大等待时长。从系统启到现在最大一次等待的时间
  - Innodb_row_lock_waits			:等待次数。从系统启到现在一共等待的次数
  ```