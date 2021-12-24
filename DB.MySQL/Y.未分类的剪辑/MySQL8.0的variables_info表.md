# MySQL8.0的variables_info表

## 前言

MySQL8.0中将很多数据库配置信息都写入了variables_info表中，查找起来非常方便。

## 实验

下面以常用的max_connections为例：

- show variables

使用variables命令，可以查看到max_connections值

```vim
mysql> show global variables like 'max_connections';
+-----------------+-------+
| Variable_name   | Value |
+-----------------+-------+
| max_connections | 151   |
+-----------------+-------+
1 row in set (0.01 sec)
1234567
```

- variables_info表

查看variables_info表：

```vim
mysql> select * from performance_schema.variables_info where VARIABLE_NAME='max_connections' \G
*************************** 1. row ***************************
  VARIABLE_NAME: max_connections
VARIABLE_SOURCE: COMPILED
  VARIABLE_PATH: 
      MIN_VALUE: 1
      MAX_VALUE: 100000
       SET_TIME: NULL
       SET_USER: NULL
       SET_HOST: NULL
1 row in set (0.01 sec)
1234567891011
```

可查看到此配置的来源是COMPILED，即默认状态。

尝试动态修改max_connections:

```vim
mysql> set global max_connections=2000;
Query OK, 0 rows affected (0.00 sec)
12
```

再次查看其状态：

- show variables

```vim
mysql> show global variables like 'max_connections';
+-----------------+-------+
| Variable_name   | Value |
+-----------------+-------+
| max_connections | 2000  |
+-----------------+-------+
1 row in set (0.01 sec)
1234567
```

- variables_info表

```vim
mysql> melect * from performance_schema.variables_info where VARIABLE_NAME='max_connections' \G
*************************** 1. row ***************************
  VARIABLE_NAME: max_connections
VARIABLE_SOURCE: DYNAMIC
  VARIABLE_PATH: 
      MIN_VALUE: 1
      MAX_VALUE: 100000
       SET_TIME: 2019-02-26 16:57:00.780719
       SET_USER: root
       SET_HOST: localhost
1 row in set (0.00 sec)
1234567891011
```

可看到状态变为了DYNAMIC（动态），并记录了修改用户，host和修改时间。

再尝试修改my.cnf，加入max_connections配置:

```vim
[root@localhost ~]# vim /etc/my.cnf

max_connections=3000
123
```

重启mysqld服务，再次查看数据库配置：

- show variables

```vim
mysql> show global variables like 'max_connections';
+-----------------+-------+
| Variable_name   | Value |
+-----------------+-------+
| max_connections | 3000  |
+-----------------+-------+
1 row in set (0.01 sec)
1234567
```

- variables_info表

```vim
mysql> select * from performance_schema.variables_info where VARIABLE_NAME='max_connections' \G
*************************** 1. row ***************************
  VARIABLE_NAME: max_connections
VARIABLE_SOURCE: GLOBAL
  VARIABLE_PATH: /etc/my.cnf
      MIN_VALUE: 1
      MAX_VALUE: 100000
       SET_TIME: NULL
       SET_USER: NULL
       SET_HOST: NULL
1 row in set (0.00 sec)
1234567891011
```

可看到来源已变为GLOBAL，且标记出了my.cnf的绝对路径