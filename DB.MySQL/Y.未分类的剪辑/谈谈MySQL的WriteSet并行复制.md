# 谈谈MySQL的WriteSet并行复制

转载 [weixin_34383618](https://me.csdn.net/weixin_34383618) 最后发布于2018-09-15 13:29:00 阅读数 414 收藏 

发布于2018-09-15 13:29:00

【**历史背景**】

　　岁月更迭中我已经从事MySQL-DBA这个工作三个年头，见证MySQL从“**基本可用**”，“**边缘系统可以用MySQL**”，“**哦操！你怎么不用MySQL**”;

　　正所谓！“一个数据库的境遇既取决于历史的进程，取决于它的自我奋斗！”，关于“历史的进程”在此不表，关于“自我奋斗”这里也只想谈一下

　　并行复制的几个关键时间结点

 

　　总的来说MySQL关于并行复制到目前为止经历过三个比较关键的时间结点“库间并发”，“组提交”，“写集合”；真可谓是江山代有人才出，前

　　浪死在沙滩上；总的来说就后面的比前面的不知道高到哪里去了！

 

【**库间并发**】

　　库间并发的理论依据是这样的 ---- 一个实例内可能会有多个库(schema)，不同的库之间没有什么依赖关系，所以在slave那边为

　　每一个库(schema)单独起一个SQL线程，这样就能通过多线程并行复制的方式来提高主从复制的效率。

 

　　这个理论听起来没问题，但是事实上一个实例也就一个业务库，所以这种库间并发就没什么作用了；也就是说这个方式的适用场景

　　比较少，针对这个不足直到“组提交”才解决！

 

【**组提交**】

　　组提交的理论依据是这样的 --- 如果多个事务他们能在同一时间内提交，这个就间接说明了这个几个事务锁上是没有冲突的，

　　也是就说他们各自持有不同的锁，互不影响；逻辑上我们几个事务看一个组，在slave以“组”为单位分配给SQL线程执行，这样

　　多个SQL线程就可以并行跑了；而且不在以库为并行的粒度，效果上要比“库间并发”要好一些。

 

　　这个事实上也有一些问题，因为它要求库上要有一定的并发度，不然就有可能变成每个组里面只有一个事务，这样就有串行没什么

　　区别了，为了解决这个问题MySQL提供了两个参数就是希望在提交时先等一等，尽可能的让组内多一些事务，以提高并行复制的效率。

　　“binlog_group_commit_sync_no_delay_count” 设置一个下水位，也就是说一个组要凑足多少个事务再提交；为子防止永远也凑不足

　　那么多个事务MySQL还以时间为维度给出了另一个参数“binlog_group_commit_sync_delay”这个参数就是最多等多久，

　　超过这个时间长度后就算没有凑足也提交。

　　

　　亲身经历呀！ 这两个参数特别难找到合的值，就算今天合适，过几天业务上有点变化后，又可能变的不合适了；如果MySQL能自己

　　达到一个自适应的效果就好了；这个自适用要到WriteSet才完成(WriteSet并不是通过自动调整这两个参数来完成，

　　它采用了完全不同的解决思路)。

 

 

【**WriteSet**】

　　WriteSet解决了什么问题？当然是解决了“组提交”的问题啦！ 说了和没说一个样，好下面我们来举个例子(比较学院派)；假设你第一天

　　更新了id == 1 的那一行，第二天你更新了id == 2 的那一行，第三天有个slave过来同步你的数据啦！ 以“组提交”的尿性，这两个更新

　　会被打包到不同的“组”，也就是说会有两个组；由于每个组内只有一个事务，所以逻辑上就串行了，起来！ 

 

　　身为DBA的你一可以看出来这两个事实上是可以打包到同一个组里来的，因为他们互不冲突，就算打包到同一个组也不引起数据的不

　　一致。 于是你有两个办法

 

　　**办法1):** 妹妹你大胆的把“binlog_group_commit_sync_no_delay_count”设置成 2,也就是说一个组至少要包含两个事务，并且把

　　“binlog_group_commit_sync_delay”设置成24小时以上！如果你真的做了，你就可以回家了，你的数据库太慢了(第一条update等了一天)，

　　才完成！

 

　　**办法2)**: 叫MySQL用一本小本子记下它最近改了什么，如果现在要改的数据和之前的数据不冲突，那么他们就可以把包到同一个组；还是

　　我们刚才的例子，由于第二天改的值的id==2所以它和第一天的不冲突，那么它完全可以把第二天的更新和第一天的更新打包到同一个组。

　　这样组里面就有两个事务了，在slave第三天回放时就会有一种并行的效果。

 

　　这本小本子这么牛逼可以做大一点吗？当然！binlog_transaction_dependency_history_size 这个参数就小本子的容量了；那我的MySQL

　　有这本小本子吗？ 如果你的mysql比mysql-5.7.22新的话，小本子就是它生来就有的。

 

　　也就是说“WriteSet”是站在“组提交”这个巨人的基础之间建立起来的，而且是在master上做的自“适应”打包分组，所以你只要在master上

　　新增两个参数

binlog_transaction_dependency_tracking = WRITESET         #  COMMIT_ORDER     
 transaction_write_set_extraction    = XXHASH64 

　　理论说完了，下面我们看一下实践。

 

 

【**WriteSet实践**】

 　基于WriteSet的并行复制环境怎么搭建我这里就不说了，也就是比正常的“组提交”在master上多加两个参数，不讲了；我这里想

　　直接给出两种并行复制方式下的行为变化。

　　**1):** 我们要执行的目标SQL如下

create database tempdb;
 use tempdb;
 create table person(id int not null auto_increment primary key,name int);
 
 insert into person(name) values(**1**);
 insert into person(name) values(**2**);
 insert into person(name) values(**3**);
 insert into person(name) values(**5**); 

 

　　**2):** 看一下组提交对上面SQL的分组情况

![last committed( 组  2  3  4  5  6  7  sequence_number( 组  内 id)  3  4  5  6  7  8  SQL 语 句  create database tempdb  create table person()d int not null auto_increment primary  key,name int)  insert into person(name) values(l)  insert into person(name) values(2)  insert into person(name) values(3)  insert into person(name) values(5)  ](clip_image001.jpg)

 

　　**3):** 看write_set的对“组提交”优化后的情况

![last committed( 组  2  3  4  4  4  4  sequence_number( 组  内 id)  3  4  5  6  7  8  SQL 语 句  create database tempdb  create table person()d int not n u Il auto_increment primary  key,name int)  insert into person(name) values(l)  insert into person(name) values(2)  insert into person(name) values(3)  insert into person(name) values(5)  ](clip_image002.jpg)

 　可以看到各个insert是可以并行执行的，所以它们被分到了同个组(last_committed相同）；**last_committed**，**sequence_number**，

　　这两个值在binlog里面记着就有，我在解析binlog的时候习惯使用如下选项

mysqlbinlog -vvv --base64-output='decode-rows' mysql-bin.000002 

 

 　

 【**总结**】

　　WriteSet是在“组提交”方式上建立起来的，一种新的并行复制实现；相比“组提交”来说更加灵活；当然，由于并发度上去了，相比“组提交”

　　WriteSet在性能上会更加好一些，在一些WriteSet没有办法是否冲突时，能平滑过度到“组提交”模式。

 

 [](https://blog.csdn.net/weixin_34383618/article/details/86278951)