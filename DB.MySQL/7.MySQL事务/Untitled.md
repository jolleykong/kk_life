MySQL语法错误在哪里检测？





RR隔离级别下怎样避免幻读

防止产生幻读： InnoDB -- "Next-key locking"

a Next-key = index-record lock + a gap lock

1. InnoDB执行行级别锁定，以使其在搜索或扫描表索引时，对遇到的索引记录设置共享或排它锁。因此，行级锁实际上是索引记录锁
2. 索引记录上的next-key locking也会影响该索引记录之前的gap。即，next-key locking是index-record lock 加上gap lock。

达到效果：一个会话在索引记录中加了共享或独占锁，另一个会话不能再索引顺序之前的间隙中插入新的索引记录，最后达到避免幻读的效果。

-  标准nextkey-lock只会锁定记录和记录前的gap，但是实际使用时，会对后面的值前面的gap也加gap lock