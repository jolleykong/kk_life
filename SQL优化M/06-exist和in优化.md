# exist和in



```
select ..from table where exist (子查询) ;
select ..from table where 字段 in  (子查询) ;

如果主查询的数据集大，则使用In   ,效率高。
如果子查询的数据集大，则使用exist,效率高。	

exist语法： 将主查询的结果，放到子查需结果中进行条件校验（看子查询是否有数据，如果有数据 则校验成功）  ，
如果 复合校验，则保留数据；

select tname from teacher where exists (select * from teacher) ; 
--等价于select tname from teacher

select tname from teacher where exists (select * from teacher where tid =9999) ;

in:
select ..from table where tid in  (1,3,5) ;

```

