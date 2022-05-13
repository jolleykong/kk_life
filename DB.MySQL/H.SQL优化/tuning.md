explain

- id

  - 同级关联，id值相同时，从上往下执行。上下的顺序一般为数据大小排序。

  - id值不同时，值越大优先级越高。

  - 包含嵌套查询的关联，一般id同时有相同和不同的情况，先执行内层。id值不同时，值越大优先级越高。

    > - 同级join 有索引
    >
    >   ```
    >   mysql> desc select u.uid,u.name,p.name,r.address from user u,part p,emp e,addr r where u.uid=e.uid and p.pid=e.pid and r.uid=u.uid;
    >   +----+-------------+-------+------------+--------+---------------+---------+---------+----------+------+----------+--------------------------------------------+
    >   | id | select_type | table | partitions | type   | possible_keys | key     | key_len | ref      | rows | filtered | Extra                                      |
    >   +----+-------------+-------+------------+--------+---------------+---------+---------+----------+------+----------+--------------------------------------------+
    >   |  1 | SIMPLE      | p     | NULL       | ALL    | PRIMARY       | NULL    | NULL    | NULL     |    2 |   100.00 | NULL                                       |
    >   |  1 | SIMPLE      | e     | NULL       | ALL    | NULL          | NULL    | NULL    | NULL     |    4 |    25.00 | Using where; Using join buffer (hash join) |
    >   |  1 | SIMPLE      | u     | NULL       | eq_ref | PRIMARY       | PRIMARY | 4       | kk.e.uid |    1 |   100.00 | NULL                                       |
    >   |  1 | SIMPLE      | r     | NULL       | eq_ref | PRIMARY       | PRIMARY | 4       | kk.e.uid |    1 |   100.00 | NULL                                       |
    >   +----+-------------+-------+------------+--------+---------------+---------+---------+----------+------+----------+--------------------------------------------+
    >   4 rows in set, 1 warning (0.00 sec)
    >   ```
    >
    > - 同级join无索引
    >
    >   ```
    >   mysql> desc select u.uid,u.name,p.name,r.address from user u,part p,emp e,addr r where u.uid=e.uid and p.pid=e.pid and r.uid=u.uid;
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+--------------------------------------------+
    >   | id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                                      |
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+--------------------------------------------+
    >   |  1 | SIMPLE      | p     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    2 |   100.00 | NULL                                       |
    >   |  1 | SIMPLE      | e     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    4 |    25.00 | Using where; Using join buffer (hash join) |
    >   |  1 | SIMPLE      | u     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    4 |    25.00 | Using where; Using join buffer (hash join) |
    >   |  1 | SIMPLE      | r     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    4 |    25.00 | Using where; Using join buffer (hash join) |
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+--------------------------------------------+
    >   4 rows in set, 1 warning (0.00 sec)
    >   ```
    >
    > - 嵌套，无索引
    >
    >   ```
    >   mysql> desc select r.address from addr r where r.uid = (select e.uid from emp e where e.pid = ( select p.pid from part p where p.name='part 2') );
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+-------------+
    >   | id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra       |
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+-------------+
    >   |  1 | PRIMARY     | r     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    4 |    25.00 | Using where |
    >   |  2 | SUBQUERY    | e     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    4 |    25.00 | Using where |
    >   |  3 | SUBQUERY    | p     | NULL       | ALL  | NULL          | NULL | NULL    | NULL |    2 |    50.00 | Using where |
    >   +----+-------------+-------+------------+------+---------------+------+---------+------+------+----------+-------------+
    >   3 rows in set, 1 warning (0.00 sec)
    >   ```
    >
    >   

    