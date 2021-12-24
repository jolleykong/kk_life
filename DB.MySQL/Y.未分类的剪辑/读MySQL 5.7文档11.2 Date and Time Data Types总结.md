> 作者：魏新平，知数堂第5期MySQL实战班学员，第10期MySQL优化班学员，现任职助教。

# 读MySQL5.7文档11.2 Date and Time Data Types

MySQL的时间类型分为DATE, DATETIME, TIMESTAMP, TIME, YEAR五个类型。接下来为大家一一介绍下。

## DATE类型

存储YYYY-MM-DD类型的时间，取值范围是'1000-01-01' to '9999-12-31'。

## DATETIME和TIMESTAMP类型

两个类型都是用来存储YYYY-MM-DD hh:mm:ss[.fraction]格式的时间。不过在取值范围和存储方式上有些不同。

### 取值范围

DATETIME的取值范围是'1000-01-01 00:00:00' 到 '9999-12-31 23:59:59', TIMESTAMP的取值范围是'1970-01-01 00:00:01' UTC to '2038-01-19 03:14:07' UTC。可以看出来DATETIME的取值范围大很多。

### 存储方式

DATETIME是直接存储插入的时间。而TIMESTAMP是将插入的值转换为utc时间，然后存入数据库，取出来的时候再根据当前会话的时区进行转换显示。

```
admin@localhost [weixinpingtest] 10:05:51>create table testtime(a timestamp,b datetime);Query OK, 0 rows affected (0.05 sec)admin@localhost [weixinpingtest] 10:07:20>insert into testtime() values(now(),now());Query OK, 1 row affected (0.01 sec)admin@localhost [weixinpingtest] 10:07:37>select * from testtime;+---------------------+---------------------+| a | b |+---------------------+---------------------+| 2020-03-04 10:07:37 | 2020-03-04 10:07:37 |+---------------------+---------------------+1 row in set (0.00 sec)admin@localhost [weixinpingtest] 10:07:43>set timezone = '+9:00';#修改时区以后，下面显示的时间就不一样了Query OK, 0 rows affected (0.00 sec)admin@localhost [weixinpingtest] 10:07:50>select * from testtime;+---------------------+---------------------+| a | b |+---------------------+---------------------+| 2020-03-04 11:07:37 | 2020-03-04 10:07:37 |+---------------------+---------------------+1 row in set (0.00 sec)
```

可以看到只要修改时区，第二次查询的时候，timestamp类型的字段时间多了一个小时，而datetime类型的字段时间没有变化。

### 自动初始化和更新

虽然有点废话，但是还是要介绍一下这两个功能到底是什么作用。

自动初始化的关键字是DEFAULT CURRENT_TIMESTAMP。



```
CREATE TABLE t1 (a int,ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,)
```

当往表t1中插入数据时，如果没有指定ts的值，那么ts会被设置为当前时间。

自动更新的关键字是ON UPDATE CURRENT_TIMESTAMP



```
CREATE TABLE t1 (a int,ts TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);
```

当表t1的a字段更新时，ts会自动更新到修改的时间。但是如果a修改的时候值没有变化，那么ts也不会变化。

DEFAULT CURRENT_TIMESTAMP和ON UPDATE CURRENT_TIMESTAMP可以同时指定，或者只指定其中一个。两者的先后顺序不会有什么影响。

### explicit_defaults_for_timestamp变量

针对timestamp还有一个数据库变量。explicit_defaults_for_timestamp。 这个变量默认是off的。那么off的时候会有什么现象呢。

- 在创建表的时候，如果自动初始化和自动更新都没有添加。那么第一个timestamp字段会自动加上DEFAULT CURRENT_TIMESTAMP 和ON UPDATE CURRENT_TIMESTAMP。

  


```
admin@localhost [weixinpingtest] 10:07:52>show global variables like '%explicitdefaultsfortimestamp%';+---------------------------------+-------+| Variablename | Value |+---------------------------------+-------+| explicitdefaultsfortimestamp | OFF |+---------------------------------+-------+1 row in set (0.00 sec)admin@localhost [weixinpingtest] 10:15:14>create table testt3(a timestamp,b timestamp);Query OK, 0 rows affected (0.02 sec)admin@localhost [weixinpingtest] 10:15:44>show create table testt3;+---------+------------------------------------------------------------------------------+| Table | Create Table+---------+------------------------------------------------------------------------------+| testt3 | CREATE TABLE test_t3 (a timestamp NOT NULL DEFAULT CURRENTTIMESTAMP ON UPDATE CURRENT_TIMESTAMP,b timestamp NOT NULL DEFAULT '0000-00-00 00:00:00') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 |1 row in set (0.00 sec)
```

有两种方法可以阻止这种现象的发生，第一个是直接设定explicit_defaults_for_timestamp参数为on,第二个是给字段设置默认值，或者直接设置可以为可以为null。

- timestamp没有指定允许null的情况下是不能插入null的，插入null的时候会默认转换成当前时间

  


```
admin@localhost [weixinpingtest] 10:21:47>show create table testt4;+---------+--------------------------------------------+| Table | Create Table |+---------+-------------------------------------------+| test_t4 | CREATE TABLE test_t4 (a timestamp NULL DEFAULT NULL,b timestamp NOT NULL DEFAULT '0000-00-00 00:00:00') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 |+---------+-------------------------------------------+1 row in set (0.00 sec)admin@localhost [weixinpingtest] 10:21:54>insert into testt4() values(null,null);Query OK, 1 row affected (0.01 sec)admin@localhost [weixinpingtest] 10:22:03>select * from testt4;+------+---------------------+| a | b |+------+---------------------+| NULL | 2020-03-05 10:22:03 |+------+---------------------+1 row in set (0.00 sec)admin@localhost [weixinpingtest] 10:22:12>set explicitdefaultsfortimestamp=on;Query OK, 0 rows affected (0.00 sec)admin@localhost [weixinpingtest] 10:25:11>insert into testt4() values(null,null);ERROR 1048 (23000): Column 'b' cannot be null
```

test_t4表当中a字段可以为null，b字段默认，不能为null，但是插入null值都没有报错，只不过a字段变成了null，b字段变成了当前时间。后面我开启了explicit_defaults_for_timestamp,再次插入null，就报错，说b不能为null了。

至于要不要开启这个变量就看你自己了，反正是可以在线关闭和开启的。

### 秒后面的小数

DATETIME和TIMESTAMP都是可以在定义字段类型时加上(n),比如DATETIME(3)，这里的3表示秒后面的小数可以精确到几位。n的取值范围是0-6。如果不设定，默认是0。需要注意的是,当指定了初始化和自动更新时，后面的也要加上这个数字。而且必须保持一致。如下

- 
- 
- 
- 

```
admin@localhost [weixinpingtest] 10:34:53>CREATE TABLE testt5( ts TIMESTAMP(6) DEFAULT CURRENTTIMESTAMP(6) ON UPDATE CURRENTTIMESTAMP(6) );Query OK, 0 rows affected (0.01 sec)admin@localhost [weixinpingtest] 10:35:29>CREATE TABLE testt5( ts TIMESTAMP(6) DEFAULT CURRENTTIMESTAMP(6) ON UPDATE CURRENTTIMESTAMP(3) );ERROR 1294 (HY000): Invalid ON UPDATE clause for 'ts' column
```

如果不一致就会报错。

## TIME类型

存储hh:mm:ss类型的数据，取值范围是'-838:59:59.000000' to '838:59:59.000000'。范围可以取这么大的原因是time还可以表示时间差，所以范围会大于24个小时，甚至是负数。TIME也是支持秒的小数的。

## YEAR类型

存储年份的。取值范围是1901 - 2155 和 0000。

## tips

针对DATE和DATETIME，表示的范围非常大，但是mysql有一句提示语。For the DATE and DATETIME range descriptions, “supported” means that although earlier values might work, there is no guarantee.表示虽然支持那么大的时间范围，但是我不保证这个能行。