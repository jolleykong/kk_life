[TOC]

一、使用mysqldump导出/导入sql数据文件

二、使用infile/outfile导入/导出txt/csv数据文件

# 存储过程&函数操作

- 只导出存储过程和函数(不导出结构和数据，要同时导出结构的话，需要同时使用-d)
    ```
    mysqldump -R -ndt dbname1 -u root -p > xxx.sql
    ```

# 事件操作

- 只导出事件
    ```
    mysqldump -E -ndt dbname1 -u root -p > xxx.sql
    ```

# 触发器操作

- 不导出触发器（触发器是默认导出的–triggers，使用–skip-triggers屏蔽导出触发器）
    ```
    mysqldump --skip-triggers dbname1 -u root -p > xxx.sql
    ```

# 导入
    source xxx.sql


# 总结一下：

PS:如果可以使用相关工具，比如官方的MySQL Workbench，则导入导出都是极为方便的，如下图。（当然为了安全性，一般情况下都是屏蔽对外操作权限，所以需要使用命令的情况更多些）




# 下面为使用infile/outfile导入/导出txt/csv数据文件操作

1. 首先使用语句看一下可以导入/导出的路径在哪里
    ```
    show variables like '%secure%';
    ```


表示导入/导出只能存放在E:/下面。

2. 如果不按照对应路径进行操作的话，将报如下错误：
    ```
    Error Code: 1290. The MySQL server is running with the --secure-file-priv option so it cannot execute this statement
    ```

3. 如果还有权限问题，请修改my.ini将secure_file_priv设置到有权限的路径下

# 对csv/txt数据导入和导出

1. 导出csv数据
    ```
    select *

    into outfile 'E:/table1_data.csv'

    character set gb2312

    fields terminated by ',' optionally enclosed by '"' escaped by '"'

    lines terminated by '\r\n'

    from table1;
    ```

2. 导入csv数据
    ```
    load data infile 'E:/table1_data.csv'

    into table table1 character set gb2312

    fields terminated by ',' optionally enclosed by '"' escaped by '"'

    lines terminated by '\r\n';
    ```

3. 导出txt数据

    默认使用空格作为分隔符，需要其它参数请参考上面的csv操作   

    ```
    select *
    into outfile 'E:/table1_data.txt'
    from table1;
    ```

4. 导入txt数据
    ```
    load data infile 'E:/table1_data.txt'

    into table table1;
    ```


以上。

 

来自 <https://www.cnblogs.com/chevin/p/5683281.html> 