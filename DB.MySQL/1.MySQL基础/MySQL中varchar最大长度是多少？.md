已剪辑自: https://www.iteye.com/blog/dinglin-914276

[阅读更多](https://www.iteye.com/blog/dinglin-914276) 

  被问到一个问题：MySQL中varchar最大长度是多少？这不是一个固定的数字。本文简要说明一下限制规则。

**1、限制规则**

字段的限制在字段定义的时候有以下规则：

 

a)         存储限制

varchar 字段是将实际内容单独存储在聚簇索引之外，内容开头用1到2个字节表示实际长度（长度超过255时需要2个字节），因此最大长度不能超过65535。

 

b)         编码长度限制

字符类型若为gbk，每个字符最多占2个字节，最大长度不能超过32766; 

字符类型若为utf8，每个字符最多占3个字节，最大长度不能超过21845。

若定义的时候超过上述限制，则varchar字段会被强行转为text类型，并产生warning。

 

c)          行长度限制

导致实际应用中varchar长度限制的是一个行定义的长度。 MySQL要求一个行的定义长度不能超过65535。若定义的表长度超过这个值，则提示

ERROR 1118 (42000): Row size too large. The maximum row size for the used table type, not counting BLOBs, is 65535. You have to change some columns to TEXT or BLOBs。

 

**2、计算例子**

举两个例说明一下实际长度的计算。

 

a)         若一个表只有一个varchar类型，如定义为

create table t4(c varchar(N)) charset=gbk;

则此处N的最大值为(65535-1-2)/2= 32766。

减1的原因是实际行存储从第二个字节开始’;

减2的原因是varchar头部的2个字节表示长度;

除2的原因是字符编码是gbk。

 

b)         若一个表定义为

create table t4(c int, c2 char(30), c3 varchar(N)) charset=utf8;

则此处N的最大值为 (65535-1-2-4-30*3)/3=21812

减1和减2与上例相同;

减4的原因是int类型的c占4个字节;

减30*3的原因是char(30)占用90个字节，编码是utf8。

 

​    如果被varchar超过上述的b规则，被强转成text类型，则每个字段占用定义长度为11字节，当然这已经不是“varchar”了。