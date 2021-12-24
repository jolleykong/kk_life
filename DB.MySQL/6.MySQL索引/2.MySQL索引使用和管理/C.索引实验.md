# 实验一

工具：innblock\innodb_ruby

实验：聚集所引述什么时候1层，什么时候2层、3层

步骤：

1. 创建一个表
2. 估算一行数据长度
3. 估算什么时候1层、2层、3层
4. 动手实验并验证





 

 表DDL

```
create table tindex (
c1 int(10) unsigned not null,
c2 char(10) not null default '',
primary key (c1)
) engine=innodb default charset=utf8;
```

- 出去额外开销，叶子节点page约可用15212字节，非叶子节点16241字节
- 每条记录都至少需要5字节的record header，如果有变长数据类型或者有NULL列，还需要更多额外字节
- 大约每4条记录就需要一个directory slot，每个slot需要2字节

 



- 聚集索引长度 6+7+5+4+10+1 = 33B
- 假设叶子节点可存储N条记录，则N*33+N/4\*2=15212，N≈453
- 非叶子节点page中，每条记录消耗13字节=4(int)+4(指针)+5(header)
- 非叶子节点page可存储N*13+N/4\*2=16241，N≈1203
- 三层高度时，约可用存储9.7亿条记录

 

 

