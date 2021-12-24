**作者  董红禹
** 
**沃趣科技MySQL高级工程师**

------




​	一、参数描述

​	

​	MySQL中不同的版本优化器会有很多新特性，比如MRR、BKA等，其中optimizer_switch这个参数就是控制查询优化器怎样使用这些特性。很多情况下我们会根据自身的需求去设置optimizer_switch满足我们的需求。

​	

​	前段时间客户的环境中遇到一个奇怪的问题，select count(*)显示返回是有数据，但select *  返回是空结果集，最终的原因就是因为optimizer_switch设置引起了一个让我们难以察觉的BUG。这里和大家分享一下，希望大家在以后的工作如果遇到类似的问题能够轻松应对。

​	



​	二、案例分析

​	

​	

#### 	2.1 环境描述

​	

​	数据库版本MySQL5.6.35

#### 	 

#### 	2.2 SQL语句

​	

> ​		select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= ‘2017-03-01  01:40:03’ and o.orderdatetime <= ‘2017-03-25 01:40:03’  ) as  tab  where  tab.organcode = ‘805000’ order by orderdatetime desc limit 10; 

​	2.3 分析过程

#### 

​	凌晨4点左右客户打来电话告知数据库查询不到数据，显得非常着急，刻不容缓，我们第一时间赶到了现场，当时的现象是这样的:

​	

> ​		select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= ‘2017-03-01  01:40:03’ and o.orderdatetime <= ‘2017-03-25 01:40:03’  ) as  tab  where  tab.organcode = ‘805000’ order by orderdatetime desc limit 10; 

​	这条语句查询返回的结果集是空，但是开发人员和我们说数据库中是有数据的，我抱着怀疑的态度尝试着执行了一下:

> ​		select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= ‘2017-03-01  01:40:03’ and o.orderdatetime <= ‘2017-03-25 01:40:03’  ) as  tab  where  tab.organcode = ‘805000’ order by orderdatetime desc limit 10; 
>
> ​		Empty set (0.41 sec) 
>
> ​		
>  
>
> ​		select count(*) from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= ‘2017-03-01  01:40:03’ and o.orderdatetime <= ‘2017-03-25 01:40:03’  ) as  tab  where  tab.organcode = ‘805000’ order by orderdatetime desc limit 10; 
>
> ​		+—————+ 
>
> ​		| count(*) | 
>
> ​		+—————+ 
>
> ​		|    475 | 
>
> ​		+—————+ 
>
> ​		1 row in set (0.41 sec) 

​	

​	一看结果当时也有点慌了，count(*)显示返回475条记录，但是select *却返回空结果集……

​	

​	想了一下SQL语句有一层嵌套，我看看里面这个SQL是否有问题，测试后发现内层语句可以正常返回，加上外层语句时就会出现这种情况。询问了应用人员系统刚迁移过来，在原系统没有这种情况，快速连到原系统上执行同样的语句对比一下两边的执行计划: 

​	
 **原系统**

​	

> ​		explain  select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= '2017-03-01  01:40:03' and o.orderdatetime <= '2017-03-25 01:40:03'  ) as  tab  where  tab.organcode = '805000' order by orderdatetime desc limit 10; 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+-----------------------------+ 
>
> ​		| id | select_type | table    | type  | possible_keys      | key         | key_len | ref        | rows  | Extra             | 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+-----------------------------+ 
>
> ​		|  1 | PRIMARY   | <derived2> | ref   | <auto_key0>        | <auto_key0>    | 153   | const       |   10 |  Using where; Using filesort | 
>
> ​		|  2 | DERIVED   | o      | range  | idx_orderdatetime    | idx_orderdatetime | 6    | NULL        | 46104 | **Using index condition**    | 
>
> ​		|  2 | DERIVED   | mm     | eq_ref | PRIMARY,idx_memberid  |  PRIMARY      | 8    | mall.o.buyerid   |   1 | NULL              | 
>
> ​		|  2 | DERIVED   | ms     | ref   | idx_userid       |  idx_userid     | 9    | mall.o.salerid   |   1 | NULL              | 
>
> ​		|  2 | DERIVED   | mmt     | eq_ref | PRIMARY,idx_merchantid |  PRIMARY      | 8    | mall.o.salerid   |   1 | NULL              | 
>
> ​		|  2 | DERIVED   | ma     | eq_ref | PRIMARY         |  PRIMARY      | 8    | mall.o.activityid |   1 | NULL              | 
>
> ​		|  2 | DERIVED   | md     | ref   | idx_activityid     |  idx_activityid   | 8    | mall.ma.actid   |   1 | NULL              | 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+-----------------------------+ 
>
> ​		7 rows in set (0.00 sec) 

​	

​	**新系统**

​	

> ​		explain  select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= '2017-03-01  01:40:03' and o.orderdatetime <= '2017-03-25 01:40:03'  ) as  tab  where  tab.organcode = '805000' order by orderdatetime desc limit 10; 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+----------------------------------+ 
>
> ​		| id | select_type | table    | type  | possible_keys      | key         | key_len | ref        | rows  | Extra                | 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+----------------------------------+ 
>
> ​		|  1 | PRIMARY   | <derived2> | ref   | <auto_key0>        | <auto_key0>    | 153   | const       |   10 |  Using where; Using filesort    | 
>
> ​		|  2 | DERIVED   | o      | range  | idx_orderdatetime    | idx_orderdatetime | 6    | NULL        | 46104 | **Using index condition; Using MRR** | 
>
> ​		|  2 | DERIVED   | mm     | eq_ref | PRIMARY,idx_memberid  |  PRIMARY      | 8    | mall.o.buyerid   |   1 | NULL                | 
>
> ​		|  2 | DERIVED   | ms     | ref   | idx_userid       |  idx_userid     | 9    | mall.o.salerid   |   1 | NULL                | 
>
> ​		|  2 | DERIVED   | mmt     | eq_ref | PRIMARY,idx_merchantid |  PRIMARY      | 8    | mall.o.salerid   |   1 | NULL                | 
>
> ​		|  2 | DERIVED   | ma     | eq_ref | PRIMARY         |  PRIMARY      | 8    | mall.o.activityid |   1 | NULL                | 
>
> ​		|  2 | DERIVED   | md     | ref   | idx_activityid     |  idx_activityid   | 8    | mall.ma.actid   |   1 | NULL                | 
>
> ​		+----+-------------+------------+--------+------------------------+-------------------+---------+-------------------+-------+----------------------------------+ 
>
> ​		7 rows in set (0.00 sec) 

​	

​	两边的执行计划不同的地方就是新系统使用了MRR，数据库的版本都是5.6.20之后的小版本号没有相差很多，应该不会出现这种情况。 

​	

​	想到了optimizer_switch这个参数可以设置mrr特性，是不是有人对其做了修改，对比了两边optimizer_switch这个参数发现mrr_cost_based这个值设置的不同。快速的将参数设置为一样再次查询:

​	

> ​		set optimizer_switch='mrr_cost_based=on'; 
>
> ​		Query OK, 0 rows affected (0.00 sec) 
>
> ​		select * from (select  o.orderid,o.orderdatetime,o.orderstatus,o.price,o.expway,o.paytype,o.fee,o.ordertype,o.realid,mm.account,ms.shopname,mmt.organcode,  o.activitype,o.channelcode, ma.activitytag,md.tagtip from mall_order o  left join mall_member mm on o.buyerid=mm.memberid left join mall_shop  ms on o.salerid=ms.userid  left join mall_merchant mmt on  mmt.merchantid=o.salerid left join mall_activity ma on  o.activityid=ma.actid  left join mall_direct_activity md on  ma.actid=md.actid where  1=1  and o.orderdatetime >= '2017-03-01  01:40:03' and o.orderdatetime <= '2017-03-25 01:40:03'  ) as  tab  where  tab.organcode = '805000' order by orderdatetime desc limit 10; 

​	

​	立刻就能够返回数据，一切搞定。

​	



​	三、总结

​	

​	mrr_cost_based代表是否使用基于代价的方式去计算使用MRR特性，新的系统中将他设置为off代表不使用基于代价方式而是使用基于规则的，这样设置的原因是考虑到MySQL基于代价的方式比较保守，不能使用到MRR这个特性。本身设置这个参数是没有任何问题，只不过正好遇到mrr_cost_based设置为off时碰到了这么诡异BUG，希望可以帮助到遇到同样问题的朋友们。



​                                                    来自 “ ITPUB博客 ”  ，链接：http://blog.itpub.net/28218939/viewspace-2140197/，如需转载，请注明出处，否则将追究法律责任。                                            