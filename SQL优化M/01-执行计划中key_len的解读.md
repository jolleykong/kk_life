# explain key_len

- 正常的，key_len等于索引列字节长度

- 如果允许NULL，+1 Byte

  - 举例：
  - INT NOT NULL = 4 Bytes
  - INT = 5 Bytes

- 字符串类型的key_len需要考虑字符集

  - 举例：字符集如果是多字节字符集如UTF8MB4
  - CHAR(10)  NOT NULL = 40 Bytes
    - CHAR(10) = 41 Bytes

- 如果为变长类型， + 2 Bytes

  - 举例：字符集如果是多字节字符集如UTF8MB4
  - VARCHAR(10)  NOT NULL = 4*10 + 2 = 42 Bytes
    - VARCHAR(10) = 4*10 + 2 + 1 = 43 Bytes

 

# key_len长度与innodb存储所消耗字节数 是不同的

- 内存空间出于高效，innodb会直接**申请内存分配定长空间**

  - 例如：varchar(300) not null 就按 1202Bytes申请，不管实际数据长度是几位）。

- 存储空间，在实际长度超出255时，会多分配2字节，否则只多分配1个字节用来标记变长类型

  - 例如：
    - varchar(300) not null ，实际存储了1位，就按4*1+1=5 Bytes申请
    - varchar(300) not null ，实际存储了256位，就按4*256+2=1026 Bytes申请

 

- key_len只计算利用索引作为index key + index filter时的索引长度

- key_len计算范围中不包括用于group by 和order by的索引的长度

  - 如果order by 也使用了索引，不会将利用的索引列的长度计算在key_len之内
    
  - 例如

    ```
    idx_abc(a,b,c) :
    
    	a int not null
    	b int not null
    	c int not null
    
    where a=? and b=? order by c3
    ```

    此时ley_len=length(a)+length(b) = 4 + 4 = 8 Bytes

  - 因此可以利用key_len判断索引效率（是否完全使用了索引，是否使用了ICP等）

  - 一般建议key_len不超过100 Bytes

传送门：[相似的SQL执行计划key_len为什么不同](../DB.MySQL/6.MySQL索引/2.MySQL索引使用和管理/相似的SQL执行计划key_len为什么不同.md)

 

# 实验：

利用key_len判断，来佐证innodb如何分配内存空间，以及SQL的执行计划走了ICP、没走ICP、完全利用了索引、只利用了前x个索引前导列等场景。

```
mysql> show create table k1\G
*************************** 1. row ***************************
    Table: k1
Create Table: CREATE TABLE `k1` (
 `id` int NOT NULL,
 `name1` varchar(1) NOT NULL,
 `name1n` varchar(1) DEFAULT NULL,
 `name10` varchar(10) NOT NULL,
 `name10n` varchar(10) DEFAULT NULL,
 `name254` varchar(254) NOT NULL,
 `name254n` varchar(254) DEFAULT NULL,
 `name255` varchar(255) NOT NULL,
 `name255n` varchar(255) DEFAULT NULL,
 `name256` varchar(256) NOT NULL,
 `name256n` varchar(256) DEFAULT NULL,
 PRIMARY KEY (`id`),
 KEY `name1` (`name1`),
 KEY `name1n` (`name1n`),
 KEY `name10n` (`name10n`),
 KEY `name10` (`name10`),
 KEY `name254` (`name254`),
 KEY `name254n` (`name254n`),
 KEY `name255` (`name255`),
 KEY `name255n` (`name255n`),
 KEY `name256` (`name256`),
 KEY `name256n` (`name256n`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```

- 1(字段长度)*4Bytes(utf8mb4编码长度)  + 2Bytes(变长型) = 6

  ![image-20220614104410075](.pics/image-20220614104410075.png)

- 1(字段长度)*4Bytes(utf8mb4编码长度)  + 2Bytes(变长型) + 1Byte(允许NULL) = 7

  ![image-20220614104756019](.pics/image-20220614104756019.png)

- 254(字段长度)*4Bytes(utf8mb4编码长度)  + 2Bytes(变长型)  = 1018

  ![image-20220614105000045](.pics/image-20220614105000045.png)

- 254(字段长度)*4Bytes(utf8mb4编码长度)  + 2Bytes(变长型)  + 1Byte(允许NULL) = 1019

  ![image-20220614105200241](.pics/image-20220614105200241.png)

- 255(字段长度)*4Bytes(utf8mb4编码长度)  + 2Bytes(变长型)  + 1Byte(允许NULL) = 1023

  ![image-20220614105300673](.pics/image-20220614105300673.png)



走了覆盖索引

```
mysql> show create table k2\G
*************************** 1. row ***************************
    Table: k2
Create Table: CREATE TABLE `k2` (
 `id` int NOT NULL,
 `name` varchar(10) DEFAULT NULL,
 `dtl` varchar(20) NOT NULL,
 PRIMARY KEY (`id`),
 KEY `name` (`name`,`dtl`)   #长度为：(4*10+2+1)+(4*20+2)=125
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```

- 完全用了idx_name,且是覆盖索引

  ![image-20220614105553221](.pics/image-20220614105553221.png)

  ![image-20220614105657188](.pics/image-20220614105657188.png)

- 利用最左匹配原则，部分利用联合索引，实现了索引覆盖。key_len=name列的长度=4*10+2+1=43

  ![image-20220614105743240](.pics/image-20220614105743240.png)

- 没利用上联合索引的最左匹配，使用filesort进行排序

  ![image-20220614105835495](.pics/image-20220614105835495.png)

至此，明白怎么回事了吧。

关于ICP和多列key_len，道理一样，不在这里占用篇幅和时间了。

 

 

练习：

计算key_len

1. varchar(10) 且允许null
2. varchar(10) 且不允许null
3. char(10)且允许null
4. char(10)且不允许null
5. int not null
6. int
7. bigint

 

 

| 答案                      | utf8  3b           | utf8mb4  4b        | gbk  2b            | latin  1b          |
| ------------------------- | ------------------ | ------------------ | ------------------ | ------------------ |
| varchar(10)  且允许null   | 10*3+2+1=33  bytes | 10*4+2+1=43  bytes | 10*2+2+1=23  bytes | 10*1+2+1=13  bytes |
| varchar(10)  且不允许null | 10*3+2=32  bytes   | 10*4+2=42  bytes   | 10*2+2=22  bytes   | 10*1+2=12  bytes   |
| char(10)且允许null        | 10*3+1=31  bytes   | 10*4+1=41  bytes   | 10*2+1=21  bytes   | 10*1+1=11  bytes   |
| char(10)且不允许null      | 10*3=30  bytes     | 10*4=40  bytes     | 10*2=20  bytes     | 10*1=10  bytes     |
| int not  null             | 4 bytes            | --                 | --                 | --                 |
| int                       | 4+1=5  bytes       | --                 | --                 | --                 |
| bigint                    | 8+1=9  bytes       | --                 | --                 | --                 |
