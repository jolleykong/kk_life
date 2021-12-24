5.7开始存在，但是至今为止依然有些bug

 

 mysqlpump的一致性备份

```
mysqlpump -S ... --single-transaction --default-parallelism=4 -A > db_$port_`date +%Y%m%d`.sql
```

- --single-transaction    基于RR的读一致性
- --default-parallelism   每个并行队列可以有几个thread，默认为2.如果指定为0且未指定parallel-schemas则回退到single thread。
  - --parallel-schemas=[N:]dblist 队列启动N个thread备份dblist。如果N为生命，使用default-parallelism定义的并行度。如果参数中带有多个parallel-schemas，则创建多个队列。



并行度选择上，SAS磁盘建议4个并行写，SSD磁盘建议16个并行写。

parallels<cpu cores

数据量小的时候并行反而会慢。



mysqlpump本身不会备份4个系统库。 备份为表级别。

当然作为容灾、备份的话， 全库备份是有必要的。

作为迁移等场景做的备份，可以不备份4个系统库

 

 

 