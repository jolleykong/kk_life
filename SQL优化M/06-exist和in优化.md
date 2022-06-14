# exist和in

- exist语法

  > ```
  > select ..from table where exist (子查询) ;
  > ```
  >
  > 将主查询的结果，放到子查需结果中进行条件校验.
  >
  > - 看子查询是否有数据，如果有数据则校验成功，如果符合校验，则保留数据；

- in

  > ```
  > select ..from table where 字段 in  (子查询) ;
  > ```

- 如果主查询的数据集大，则使用In   ,效率高。

- 如果子查询的数据集大，则使用exist,效率高。	

```
select tname from teacher where exists (select * from teacher) ; 
--等价于select tname from teacher

select tname from teacher where exists (select * from teacher where tid =9999) ;
```

