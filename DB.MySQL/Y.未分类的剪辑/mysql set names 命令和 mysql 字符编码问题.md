已剪辑自: https://www.cnblogs.com/skying555/p/10383467.html

Reference: https://www.cnblogs.com/digdeep/p/5228199.html

先看下面的执行结果：

 

 

(root@localhost)[(none)]mysql>show variables like 'character%';
 +--------------------------+-------------------------------------------------------------+
 | Variable_name      | Value                            |
 +--------------------------+-------------------------------------------------------------+
 | character_set_client   | utf8                            |
 | character_set_connection | utf8                            |
 | character_set_database  | utf8mb4                           |
 | character_set_filesystem | binary                           |
 | character_set_results  | utf8                            |
 | character_set_server   | utf8mb4                           |
 | character_set_system   | utf8                            |
 | character_sets_dir    | /usr/local/mysql-5.6.26-linux-glibc2.5-i686/share/charsets/ |
 +--------------------------+-------------------------------------------------------------+
 8 rows in set (0.01 sec)
 
 (root@localhost)[(none)]mysql>set names gbk;
 Query OK, 0 rows affected (0.00 sec)
 
 (root@localhost)[(none)]mysql>show variables like 'character%';
 +--------------------------+-------------------------------------------------------------+
 | Variable_name      | Value                            |
 +--------------------------+-------------------------------------------------------------+
 | character_set_client   | gbk                             |
 | character_set_connection | gbk                             |
 | character_set_database  | utf8mb4                           |
 | character_set_filesystem | binary                           |
 | character_set_results  | gbk                             |
 | character_set_server   | utf8mb4                           |
 | character_set_system   | utf8                            |
 | character_sets_dir    | /usr/local/mysql-5.6.26-linux-glibc2.5-i686/share/charsets/ |
 +--------------------------+-------------------------------------------------------------+
 8 rows in set (0.01 sec)
 
 (root@localhost)[(none)]mysql>set names utf8mb4;
 Query OK, 0 rows affected (0.00 sec)
 
 (root@localhost)[(none)]mysql>show variables like 'character%';
 +--------------------------+-------------------------------------------------------------+
 | Variable_name      | Value                            |
 +--------------------------+-------------------------------------------------------------+
 | character_set_client   | utf8mb4                           |
 | character_set_connection | utf8mb4                           |
 | character_set_database  | utf8mb4                           |
 | character_set_filesystem | binary                           |
 | character_set_results  | utf8mb4                           |
 | character_set_server   | utf8mb4                           |
 | character_set_system   | utf8                            |
 | character_sets_dir    | /usr/local/mysql-5.6.26-linux-glibc2.5-i686/share/charsets/ |
 +--------------------------+-------------------------------------------------------------+
 8 rows in set (0.00 sec) 

 

 

**1.** [**character_set_system**](http://dev.mysql.com/doc/refman/5.6/en/server-system-variables.html#sysvar_character_set_system)

The character set used by the server for storing identifiers. **The value is always** **utf8**.

character_set_system 是系统元数据(字段名等)存储时使用的编码字符集，该字段和具体存储的数据无关。总是固定不变的——utf8. 我们可以不去管它。

**2. character_set_server** 

Use *charset_name* as the default server character set. See [Section 10.5, “Character Set Configuration”](http://dev.mysql.com/doc/refman/5.6/en/charset-configuration.html). If you use this option to specify a nondefault character set, you should also use [--collation-server](http://dev.mysql.com/doc/refman/5.6/en/server-options.html#option_mysqld_collation-server) to specify the collation.

该变量**设置的 server 级别的(mysqld级别的) 字符集**。也就是说设置的是 一个 mysqld 的，所有字符最后存储时，使用的编码字符集。

默认值为 lantin1. 我们一般设置成：utf8、utf8mb4、gbk 等值。

一同设置的还有 server 级别的排序规则：

**collation_server**:

utf8mb4_bin, utf8mb4_general_ci, utf8_bin, utf8_general_ci

ci 代表： casesensitive ignore 排序时不考虑大小写；而 _bin 结尾的排序时考虑大小写。

**3. character_set_database**

Every database has a database character set and a database collation. The [CREATE DATABASE](http://dev.mysql.com/doc/refman/5.6/en/create-database.html) and [ALTER DATABASE](http://dev.mysql.com/doc/refman/5.6/en/alter-database.html) statements have optional clauses for specifying the database character set and collation:

CREATE DATABASE *db_name*
   [[DEFAULT] CHARACTER SET *charset_name*]
   [[DEFAULT] COLLATE *collation_name*]
 
 ALTER DATABASE *db_name*
   [[DEFAULT] CHARACTER SET *charset_name*]
   [[DEFAULT] COLLATE *collation_name*] 

character_set_database 是**单个**数据库级别的 字符集设置，该参数允许我们在同一个 mysqd 下面的不同的 database 使用不同的字符集。

比如：

create database db1 **character set utf8mb4 collate utf8mb4_bin**;

这就设置了 数据库 级别的字符集。如果 create database 语句没有 character 和 collate 参数，那么他们会默认使用：

character_set_server 和 character_collation 的值作为 默认值。

同样对应有数据库级别的排序规则参数：

collation_database 

**4. character_set_client** 

The character set **for statements that arrive from the client**. The session value of this variable is set using the character set requested by the client when the client connects to the server. (Many clients support a --default-character-set option to enable this character set to be specified explicitly. See also [Section 10.1.4, “Connection Character Sets and Collations”](http://dev.mysql.com/doc/refman/5.6/en/charset-connection.html).) 

也就是 mysql client 发送 给 mysqld 的语句使用的 编码字符集。

可以使用 --default-character-set 参数来显示设置。

**5. character_set_connection**

The character set used for literals that do not have a character set introducer and for **number-to-string conversion**.

数字到字符转换时的编码字符集。

（用introducer指定文本字符串的字符集： 
 – 格式为：[_charset] 'string' [COLLATE collation] 
 – 例如： 
 • SELECT _latin1 'string'; 
 • SELECT _utf8 '你好' COLLATE utf8_general_ci; 
 – 由introducer修饰的文本字符串在请求过程中不经过多余的转码，直接转换为内部字符集处理。 ）

实际中我们一般没有人去使用 introducer ，所以其实是没有 introducer，所以都会使用 character_set_connection来编码的。

**6. character_set_results**

The character set used for returning query results such as **result sets or error messages** to the client.

mysqld 在返回 查询 结果集 或者错误信息到 client 时，使用的编码字符集。

**7. set names 'xxx' 命令**

可以看到改变的是 character_set_client、character_set_connection、character_set_results

它们都是和 client 相关的。而 真正server端的编码字符集，character_set_server 和 character_set_database ，set names 'xxx' 根本无法修改。

set names 'xxx' 命令可以使 character_set_client、character_set_connection、character_set_results 三者统一：

**client (character_set_client) -----> character_set_connection -------> mysqld  ------> client(character_set_results)**

减少编码转换的需要。

**8. character_set_server 和 character_set_database** 

二者 的作用其实是相同的，都是设置 字符最终存储到磁盘时，使用的编码字符集。只不过 二者设置的级别不一样而已。character_set_server 设置了 mysqld 级别的存储编码字符集，而character_set_database设置 mysqld 中单个 database 的存储编码字符集。而且character_set_database的默认值就是 character_set_server 的值。

存在三次编码转换过程：

1）mysql client 使用 character_set_client编码的字符------> character_set_connection 编码字符

  ------> mysqld ：这里需要从 character_set_connection 编码格式二进制流**解码成 字符**，然后使用 character_set_server/character_set_database **对字符进行再次编码**，生成二进制流，存储时，就是存储再次编码的二进制流数据。

2）读取数据时，会使用 character_set_server/character_set_database 对读取到的二级制流进行 解码成 字符，然后使用 character_set_results 对字符进行二次编码，生成二进制流，发给 mysql client.

所以 使用 set names 'xxx' 命令，结合 character_set_server 参数，可以将 整个过程的 字符集设置成相同的，就不会存在编码转换的过程。

**9. default-character-set = charset_name 配置参数
** 

Use *charset_name* **as the default character set for the client and connection(****其实还有** **character_set_results).**

A common issue that can occur when the operating system uses utf8 or another multibyte character set is that output from the [**mysql**](http://dev.mysql.com/doc/refman/5.6/en/mysql.html) **client is formatted incorrectly, due to the fact that the MySQL client uses the** latin1 character set by default. You can usually fix such issues by using this option to force the client to use the system character set instead.

See [Section 10.5, “Character Set Configuration”](http://dev.mysql.com/doc/refman/5.6/en/charset-configuration.html), for more information.

default-character-set 能够同时指定 client 端 和 connection 的字符，也就是：**character_set_client 和 character_set_connection的值，实际上还设置了 character-set-results 的值**。

**所以 default-character-set 的作用和 set names 'xxx' 的作用是一样的**。 

 