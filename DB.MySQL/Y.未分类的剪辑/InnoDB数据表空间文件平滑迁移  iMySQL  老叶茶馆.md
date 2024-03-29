#           InnoDB数据表空间文件平滑迁移        

​                  

​            Submitted by yejr on 周三, 2008/12/17 - 16:05    

作/译者：叶金荣（imysql#imysql.com>），来源：http://imysql.com，欢迎转载。

# 前言

InnoDB存储引擎满足了MVCC和ACID特性，在需要支持事务的环境下必不可少。有些环境下，采用InnoDB可能效果比MyISAM还要来的好。不过，在很多人眼中看来，InnoDB表空间文件由于无法实现跨服务器平滑迁移，因此不愿意使用。实际情况真是这样吗？本文就来探讨一下InnoDB表空间文件的平滑迁移可能性。

# 如何迁移？

从MySQL文档中我们了解到，InnoDB的表空间可以是共享的或独立的。如果是共享表空间，则所有的表空间都放在一个文件里：ibdata1,ibdata2..ibdataN，这种情况下，目前应该还没办法实现表空间的迁移，除非完全迁移，因此不在本次讨论之列；我们只讨论独立表空间的情况。

不管是共享还是独立表空间，InnoDB每个数据表的元数据(metadata)总是保存在 ibdata1  这个共享表空间里，因此该文件必不可少，它还可以用来保存各种数据字典等信息。数据字典中，会保存每个数据表的ID号，每次发生数据表空间新增时，都会使得该ID自增一个值(++1)，例如：CREATE TABLE xx ENGINE = InnoDB / ALTER TABLE xx ENGINE = InnoDB 都会使得ID值增加。
 有了上面的理解，想要实现InnoDB表空间文件的平滑迁移就很容易了，呵呵。下面是一些例子：
 假定我们有2台DB主机，一个是A，一个B；现在想把A上的某个InnoDB表空间文件迁移到B上直接用。

## 一、迁移失败的例子

直接从A上把表空间文件 yejr.ibd 拷贝到 B 上后，导入表空间，报错，无法使用。这是由于A，B上创建该表时的顺序不一致，导致表的ID不一样，无法导入。
**注意：**，在这里，表空间文件直接拷贝的前提是该表空间处于"干净"状态下，也就是所有的数据均已经刷新到磁盘中，否则可能导致无法使用或部分数据丢失。
 \1. 在B上将旧的表空间废弃

```
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr DISCARD TABLESPACE;
Query OK, 0 rows affected (0.00 sec)
```

\2. 拷贝到目标机器

```
scp yejr.ibd B:/home/mysql/yejr/yejr.ibd
....
```

\3. 启用该表空间

```
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr IMPORT TABLESPACE;
ERROR 1030 (HY000): Got error -1 from storage engine
```

\4. 查看错误

```
InnoDB: Operating system error number 13 in a file operation.
InnoDB: The error means mysqld does not have the access rights to
InnoDB: the directory.
InnoDB: Error: trying to open a table, but could not
InnoDB: open the tablespace file './test/b.ibd'!
InnoDB: Error: cannot reset lsn's in table `test/b`
InnoDB: in ALTER TABLE ... IMPORT TABLESPACE
```

\5. 很明显，是权限的问题，修正过来，然后重新导入

```
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr DISCARD TABLESPACE;
ERROR 1030 (HY000): Got error -1 from storage engine
```

\6. 怎么还是错误？继续看日志

```
InnoDB: Error: tablespace id in file './yejr/yejr.ibd' is 15, but in the InnoDB
InnoDB: data dictionary it is 13.
InnoDB: Have you moved InnoDB .ibd files around without using the
InnoDB: commands DISCARD TABLESPACE and IMPORT TABLESPACE?
InnoDB: Please refer to
InnoDB: http://dev.mysql.com/doc/refman/5.0/en/innodb-troubleshooting.html
InnoDB: for how to resolve the issue.
InnoDB: cannot find or open in the database directory the .ibd file of
InnoDB: table `yejr/yejr`
InnoDB: in ALTER TABLE ... IMPORT TABLESPACE
```

从上面的日志得知，由于在A服务器上，yejr表的ID是15，而在B服务器上，yejr表的ID却是13，二者不一致，因此迁移失败。
 既然只是因为ID不一样，而且有了上面的理论基础，我们完全可以人为的让它们的ID一致嘛，请看下面的第2次尝试。

## 二、人工干预下的成功迁移

\1. 上面的例子中，B上面的yejr表ID为13，而A上面为15；因此只需要让B上的yejr表ID增加2就可以了。

```
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr RENAME TO yejr1;
Query OK, 0 rows affected (0.00 sec)
#这个时候,yejr的ID变为14
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr1 RENAME TO yejr;
Query OK, 0 rows affected (0.00 sec)
#这个时候,yejr的ID变为15
```

\2. 然后，我们再导入

```
(root@imysql.cn/17:52:47)[yejr]>ALTER TABLE yejr IMPORT TABLESPACE;
Query OK, 0 rows affected (0.00 sec)
(root@imysql.cn/17:52:47)[yejr]>select count(*) from yejr;
+----------+
| count(*) |
+----------+
|        3 |
+----------+
1 row in set (0.00 sec)
```

看到了吧，成功了，呵呵。想要让他ID增加的方式也可以重复创建表，根据实际情况或者个人喜好而定了。
 以上测试均在mysql 5.0.67版本下通过，只不过显示数据稍作处理了。

### 