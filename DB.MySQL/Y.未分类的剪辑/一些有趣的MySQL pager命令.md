#                  [     介绍一些有趣的MySQL pager命令        ](https://www.cnblogs.com/linuxprobe/p/10230653.html)             

**一、分页结果集**

在Linux系统中中，我们经常也会使用一些分页查看命令，例如less、more等。同样，MySQL客户端也提供了类似的命令，用来帮助我们对查询结果集进行分页。比如，SHOW ENGINE INNODB STATUS时通过分页看锁信息时是非常有用的，这样就不用一屏到底了。

```
mysql> pager less
PAGER set to 'less'
mysql> show engine innodb status\G
[...]
```

现在你可以轻松浏览结果集了（使用q退出，空格向下滚动等）。

如果你想离开你的自定义pager，这很容易，只需运行pager命令：

```
mysql> pager
Default pager wasn't set, using stdout.
```

或者

```
mysql> \n
PAGER set to stdout
```

但是pager命令并不局限于这种基本用法！你可以将查询输出传递给大多数能够处理文本的Unix程序。这里有一些例子。

**二、丢弃结果集**

有时你不关心结果集，只想查看时间信息。如果你通过更改索引为查询尝试不同的执行计划，则可能会出现这种情况。使用pager可以丢弃结果：

```
mysql> pager cat > /dev/null
PAGER set to 'cat > /dev/null'

# Trying an execution plan
mysql> SELECT ...
1000 rows in set (0.91 sec)

# Another execution plan
mysql> SELECT ...
1000 rows in set (1.63 sec)
```

现在，在一个屏幕上查看所有时间信息要容易得多。

**三、比较结果集**

假设你正在重写查询，并且想要在重写之前和之后检查结果集是否相同。不幸的是，它有很多行：

```
mysql> SELECT ...
[..]
989 rows in set (0.42 sec)
```

你可以计算校验和，只比较校验和，而不是手动比较每一行：

```
mysql> pager md5sum
PAGER set to 'md5sum'
 
# Original query
mysql> SELECT ...
32a1894d773c9b85172969c659175d2d  -
1 row in set (0.40 sec)
 
# Rewritten query - wrong
mysql> SELECT ...
fdb94521558684afedc8148ca724f578  -
1 row in set (0.16 sec)
```

嗯，[Linux系统](https://www.linuxprobe.com/)的校验和不匹配，出了点问题。我们重试一下：

```
# Rewritten query - correct
mysql> SELECT ...
32a1894d773c9b85172969c659175d2d  -
1 row in set (0.17 sec)
```

校验和是相同的，重写的查询很可能产生与原始查询相同的结果。

**四、结合系统命令**

如果MySQL上有很多连接，那么很难读取SHOW PROCESSLIST的输出。例如，如果你有几百个连接，并且你想知道有多少连接处于Sleep状态，手动计算SHOW PROCESSLIST输出中的行可能不是最佳解决方案。使用pager，它很简单：

```
mysql> pager grep Sleep | wc -l
PAGER set to 'grep Sleep | wc -l'

mysql> show processlist;
337
346 rows in set (0.00 sec)
```

这应该被解读为346个连接中337正处于Sleep状态。

现在稍微复杂一点：你想知道每个状态的连接数

```
mysql> pager awk -F '|' '{print $6}' | sort | uniq -c | sort -r
PAGER set to 'awk -F '|' '{print $6}' | sort | uniq -c | sort -r'
mysql> show processlist;
    309  Sleep
      3
      2  Query
      2  Binlog Dump
      1  Command
```

当然，这些问题可以通过查询INFORMATION_SCHEMA来解决。例如，计算Sleep连接的数量可以通过以下方式完成：

```
mysql> SELECT COUNT(*) FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND='Sleep';
+----------+
| COUNT(*) |
+----------+
|      320 |
+----------+
```

并计算每个状态的连接数可以通过以下方式完成：

```
mysql> SELECT COMMAND,COUNT(*) TOTAL FROM INFORMATION_SCHEMA.PROCESSLIST GROUP BY COMMAND ORDER BY TOTAL DESC;
+-------------+-------+
| COMMAND     | TOTAL |
+-------------+-------+
| Sleep       |   344 |
| Query       |     5 |
| Binlog Dump |     2 |
+-------------+-------+
```

但是，有些人可能对编写SQL查询感觉更舒服，而其他人则更喜欢使用命令行工具。

如你所见，pager是你的朋友！它非常易于使用，它可以以优雅和高效的方式解决问题。你甚至可以编写自定义脚本（如果它太复杂而无法放在一行中）并将其传递给pager。总之，多使用pager命令能让你的工作事半功倍。