## MySQL性能瓶颈定位

- 优化耗时/逻辑读，TOP SQL
  - 找到耗时最慢的TOP SQL。via: `P_S.events_statements_history_long`
  - 排序：`timer_wait/rows_examined/rows_sent`
  - 定位这些SQL的性能瓶颈。via: `P_S.events_stages_history_long`/`profiling`
- 优化物理I/O，TOP SQL
  - 找到逻辑IO请求最多的对象。 via: `PS.table_io_waits_summary_by_table`
  - 找到物理IO请求最多的对象。 via: `sys.io_global_by_file_by_bytes`
  - 定位、优化这些请求。