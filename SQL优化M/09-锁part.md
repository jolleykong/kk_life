







```

11.锁机制 ：解决因资源共享 而造成的并发问题。
	示例：买最后一件衣服X
	A:  	X	买 ：  X加锁 ->试衣服...下单..付款..打包 ->X解锁
	B:	X       买：发现X已被加锁，等待X解锁，   X已售空

	分类：
	操作类型：
		a.读锁（共享锁）： 对同一个数据（衣服），多个读操作可以同时进行，互不干扰。
		b.写锁（互斥锁）： 如果当前写操作没有完毕（买衣服的一系列操作），则无法进行其他的读操作、写操作
	
	操作范围：
		a.表锁 ：一次性对一张表整体加锁。如MyISAM存储引擎使用表锁，开销小、加锁快；无死锁；但锁的范围大，容易发生锁冲突、并发度低。
		b.行锁 ：一次性对一条数据加锁。如InnoDB存储引擎使用行锁，开销大，加锁慢；容易出现死锁；锁的范围较小，不易发生锁冲突，并发度高（很小概率 发生高并发问题：脏读、幻读、不可重复度、丢失更新等问题）。
		c.页锁		

示例：

	（1）表锁 ：  --自增操作 MYSQL/SQLSERVER 支持；oracle需要借助于序列来实现自增
create table tablelock
(
id int primary key auto_increment , 
name varchar(20)
)engine myisam;


insert into tablelock(name) values('a1');
insert into tablelock(name) values('a2');
insert into tablelock(name) values('a3');
 insert into tablelock(name) values('a4');
insert into tablelock(name) values('a5');
commit;

	增加锁：
	locak table 表1  read/write  ,表2  read/write   ,...
	
	查看加锁的表：
	show open tables ;
	
	会话：session :每一个访问数据的dos命令行、数据库客户端工具  都是一个会话
	
	===加读锁：
		会话0：
			lock table  tablelock read ;
			select * from tablelock; --读（查），可以
			delete from tablelock where id =1 ; --写（增删改），不可以
	
			select * from emp ; --读，不可以
			delete from emp where eid = 1; --写，不可以
			结论1：
			--如果某一个会话 对A表加了read锁，则 该会话 可以对A表进行读操作、不能进行写操作； 且 该会话不能对其他表进行读、写操作。
			--即如果给A表加了读锁，则当前会话只能对A表进行读操作。
	
		会话1（其他会话）：
			select * from tablelock;   --读（查），可以
			delete from tablelock where id =1 ; --写，会“等待”会话0将锁释放


		会话1（其他会话）：
			select * from emp ;  --读（查），可以
			delete from emp where eno = 1; --写，可以
			结论2：
			--总结：
				会话0给A表加了锁；其他会话的操作：a.可以对其他表（A表以外的表）进行读、写操作
								b.对A表：读-可以；  写-需要等待释放锁。
		释放锁: unlock tables ;



	===加写锁：
		会话0：
			lock table tablelock write ;
	
			当前会话（会话0） 可以对加了写锁的表  进行任何操作（增删改查）；但是不能 操作（增删改查）其他表
		其他会话：
			对会话0中加写锁的表 可以进行增删改查的前提是：等待会话0释放写锁

MySQL表级锁的锁模式
MyISAM在执行查询语句（SELECT）前，会自动给涉及的所有表加读锁，
在执行更新操作（DML）前，会自动给涉及的表加写锁。
所以对MyISAM表进行操作，会有以下情况：
a、对MyISAM表的读操作（加读锁），不会阻塞其他进程（会话）对同一表的读请求，
但会阻塞对同一表的写请求。只有当读锁释放后，才会执行其它进程的写操作。
b、对MyISAM表的写操作（加写锁），会阻塞其他进程（会话）对同一表的读和写操作，
只有当写锁释放后，才会执行其它进程的读写操作。



分析表锁定：
	查看哪些表加了锁：   show open tables ;  1代表被加了锁
	分析表锁定的严重程度： show status like 'table%' ;
			Table_locks_immediate :即可能获取到的锁数
			Table_locks_waited：需要等待的表锁数(如果该值越大，说明存在越大的锁竞争)
	一般建议：
		Table_locks_immediate/Table_locks_waited > 5000， 建议采用InnoDB引擎，否则MyISAM引擎

​	

（2）行表（InnoDB）
create table linelock(
id int(5) primary key auto_increment,
name varchar(20)
)engine=innodb ;
insert into linelock(name) values('1')  ;
insert into linelock(name) values('2')  ;
insert into linelock(name) values('3')  ;
insert into linelock(name) values('4')  ;
insert into linelock(name) values('5')  ;


--mysql默认自动commit;	oracle默认不会自动commit ;

为了研究行锁，暂时将自动commit关闭;  set autocommit =0 ; 以后需要通过commit


	会话0： 写操作
		insert into linelock values(	'a6') ;
	   
	会话1： 写操作 同样的数据
		update linelock set name='ax' where id = 6;
	
	对行锁情况：
		1.如果会话x对某条数据a进行 DML操作（研究时：关闭了自动commit的情况下），则其他会话必须等待会话x结束事务(commit/rollback)后  才能对数据a进行操作。
		2.表锁 是通过unlock tables，也可以通过事务解锁 ; 行锁 是通过事务解锁。


​		

	行锁，操作不同数据：
	
	会话0： 写操作
	
		insert into linelock values(8,'a8') ;
	会话1： 写操作， 不同的数据
		update linelock set name='ax' where id = 5;
		行锁，一次锁一行数据；因此 如果操作的是不同数据，则不干扰。


	行锁的注意事项：
	a.如果没有索引，则行锁会转为表锁
	show index from linelock ;
	alter table linelock add index idx_linelock_name(name);


​	
	会话0： 写操作
		update linelock set name = 'ai' where name = '3' ;
		
	会话1： 写操作， 不同的数据
		update linelock set name = 'aiX' where name = '4' ;


​	
	会话0： 写操作
		update linelock set name = 'ai' where name = 3 ;
		
	会话1： 写操作， 不同的数据
		update linelock set name = 'aiX' where name = 4 ;
		
	--可以发现，数据被阻塞了（加锁）
	-- 原因：如果索引类 发生了类型转换，则索引失效。 因此 此次操作，会从行锁 转为表锁。
	
	b.行锁的一种特殊情况：间隙锁：值在范围内，但却不存在
	 --此时linelock表中 没有id=7的数据
	 update linelock set name ='x' where id >1 and id<9 ;   --即在此where范围中，没有id=7的数据，则id=7的数据成为间隙。
	间隙：Mysql会自动给 间隙 加索 ->间隙锁。即 本题 会自动给id=7的数据加 间隙锁（行锁）。
	行锁：如果有where，则实际加索的范围 就是where后面的范围（不是实际的值）


​	
	如何仅仅是查询数据，能否加锁？ 可以   for update 
	研究学习时，将自动提交关闭：
		set autocommit =0 ;
		start transaction ;
		begin ;
	 select * from linelock where id =2 for update ;
	
	通过for update对query语句进行加锁。
	
	行锁：
	InnoDB默认采用行锁；
	缺点： 比表锁性能损耗大。
	优点：并发能力强，效率高。
	因此建议，高并发用InnoDB，否则用MyISAM。
	
	行锁分析：
	  show status like '%innodb_row_lock%' ;
		 Innodb_row_lock_current_waits :当前正在等待锁的数量  
		  Innodb_row_lock_time：等待总时长。从系统启到现在 一共等待的时间
		 Innodb_row_lock_time_avg  ：平均等待时长。从系统启到现在平均等待的时间
		 Innodb_row_lock_time_max  ：最大等待时长。从系统启到现在最大一次等待的时间
		 Innodb_row_lock_waits ：	等待次数。从系统启到现在一共等待的次数

```

