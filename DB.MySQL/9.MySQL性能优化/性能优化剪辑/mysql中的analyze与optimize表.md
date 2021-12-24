analyze表分析和存储表的键值分布，mysql使用存储的键值分布来决定当进行连接的顺序，也会决定查询中使用哪个索引。 
 默认情况下会把analyze table的语句写入到二进制日志中去。 
 analyze复杂度 
 ANALYZE TABLE complexity for InnoDB tables is dependent on:

The number of pages sampled, as defined by innodb_stats_persistent_sample_pages.

The number of indexed columns in a table

The number of partitions. If a table has no partitions, the number of partitions is considered to be 1.

Using these parameters, an approximate formula for estimating ANALYZE TABLE complexity would be:

The value of innodb_stats_persistent_sample_pages * number of indexed columns in a table * the number of partitions

Typically, the greater the resulting value, the greater the execution time for ANALYZE TABLE.

optimize table是重新组织表和相关索引的物理存储的。为了减少存储空间和提高io效率。在下面的情况考虑使用： 
 After doing substantial insert, update, or delete operations on an  InnoDB table that has its own .ibd file because it was created with the  innodb_file_per_table option enabled. The table and indexes are  reorganized, and disk space can be reclaimed for use by the operating  system.

After doing substantial insert, update, or delete operations on  columns that are part of a FULLTEXT index in an InnoDB table. Set the  configuration option innodb_optimize_fulltext_only=1 first. To keep the  index maintenance period to a reasonable time, set the  innodb_ft_num_word_optimize option to specify how many words to update  in the search index, and run a sequence of OPTIMIZE TABLE statements  until the search index is fully updated.

After deleting a large part of a MyISAM or ARCHIVE table, or making  many changes to a MyISAM or ARCHIVE table with variable-length rows  (tables that have VARCHAR, VARBINARY, BLOB, or TEXT columns). Deleted  rows are maintained in a linked list and subsequent INSERT operations  reuse old row positions. You can use OPTIMIZE TABLE to reclaim the  unused space and to defragment the data file. After extensive changes to a table, this statement may also improve performance of statements that use the table, sometimes significantly.



https://blog.csdn.net/aoerqileng/article/details/54973002