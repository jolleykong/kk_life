auto-inc 持久化

- Before MySQL 8.0

```
mysql> create table t2(id int auto_increment primary key,dtl varchar(10));
Query OK, 0 rows affected (0.03 sec)
 
mysql> insert into t2(dtl) values('a');
Query OK, 1 row affected (0.02 sec)
…
mysql> select max(id) from t2;
+---------+
| max(id) |
+---------+
|    3 |
+---------+
1 row in set (0.00 sec)
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int(11) NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4
1 row in set (0.00 sec)
 
mysql> alter table t2 auto_increment=10;
Query OK, 0 rows affected (0.02 sec)
Records: 0 Duplicates: 0 Warnings: 0
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int(11) NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4
1 row in set (0.00 sec)
 
reset mysqld
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int(11) NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4
1 row in set (0.00 sec)
```

 

- Since MySQL8.0

```
mysql> create table t2(id int auto_increment primary key,dtl varchar(10));
Query OK, 0 rows affected (0.03 sec)
 
mysql> insert into t2(dtl) values('a');
Query OK, 1 row affected (0.01 sec)
…
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
 
mysql> alter table t2 auto_increment=10;
Query OK, 0 rows affected (0.03 sec)
Records: 0 Duplicates: 0 Warnings: 0
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
 
reset mysqld
 
mysql> show create table t2\G
*************************** 1. row ***************************
    Table: t2
Create Table: CREATE TABLE `t2` (
 `id` int NOT NULL AUTO_INCREMENT,
 `dtl` varchar(10) DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```