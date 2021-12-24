# 在内置数据类型dict list set tuple的基础上，collections模块提供了几个额外的数类型：
# Counter、deque、defaultdict、namedtuple和OrderedDict。
# - namedtuple : 生成可以使用名字来访问元素内容的tuple
# - deque : 双端队列，可以快速的从另外一侧追加和推出对象
# - Counter : 计数器，主要用来计数
# - OrderedDict : 有序字典
# - defaultdict : 带有默认值的字典


# namedtuple 命名元组
    # struct_time 也是命名元组。
from collections import namedtuple
Point = namedtuple('Point',['x','y'])
p = Point(1,2)
print(type(p))  # <class '__main__.Point'>
print(p)        # Point(x=1, y=2)
# 可以按元组方式用索引来取值
print(p[0])     # 1
# 也可以用命名方式来取值
print(p.x)      # 1

import time
struct_time = time.strptime('2021-12-01','%Y-%m-%d')
print(type(struct_time))    # <class 'time.struct_time'>
print(struct_time)      # time.struct_time(tm_year=2021, tm_mon=12, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=335, tm_isdst=-1)
print(struct_time[0])   # 2021
print(struct_time.tm_year)  # 2021

# 手动创建类似struct_time的命名元组
struct_time_1 = namedtuple('struct_time_1',['tm_year','tm_mon','tm_mday','tm_hour','tm_min'])
st = struct_time_1(2021,12,1,0,0)
print(type(st))     # <class '__main__.struct_time_1'>
print(st)           # struct_time_1(tm_year=2021, tm_mon=12, tm_mday=1, tm_hour=0, tm_min=0)


# deque 双端队列，类似于list的一种容器型数据
    # 列表按索引取值查询很快，但是向列表中增加或删除值时，由于是线性存储，数据量大的时候效率并不高。
    # 双端队列可以提升这方面的效率，实现高效插入和删除操作的双向列表。
from collections import deque
q = deque(['a','b','c'])
q.append('kk')  # 尾部追加
q.appendleft('first')   # 左侧增加
# 但是不能从中间增加
print(q)

q.pop() # 删除最后一个，跟list一样。先进后出
print(q)
q.popleft() # 删除最左侧的。
print(q)
# 其他的操作几乎都类似于list操作。


# OrderedDict 有序字典
    # 3.6之后的字典就是按照创建顺序存储顺序的了。 3.6之前不是。 因此3.6开始OrderedDict和默认dict一样了。


# defaultdict 默认值字典
from collections import defaultdict
# 可以设置字典的默认值
# 将l1 = [11,22,33,44,55,66,77,88,99] 所有大于66的元素保存至dic1.key1，小于66的元素保存至dic1.key2。
# 传统方法
l1 = [11,22,33,44,55,66,77,88,99] 
dic1 = {}
for i in l1:
    if i > 66:
        if 'key1' not in dic1:
            dic1['key1'] = [i,]
        else:
            dic1['key1'].append(i)
    else:
        if 'key2' not in dic1:
            dic1['key2'] = [i,]
        else:
            dic1['key2'].append(i)
print(dic1)

# 默认值字典方法
l1 = [11,22,33,44,55,66,77,88,99] 
dic2 = defaultdict(list)    # 默认将值以list形式加入到字典。
for i in l1:
    if i < 66 :
        dic2['key2'].append(i)
    else:
        dic2['key1'].append(i)

dic_a = defaultdict(list)
dic_a[1]        # key 随便指定
dic_a[2] = 'value'  # 可以指定值
dic_a[3]
print(dic_a)    # defaultdict(<class 'list'>, {1: [], 2: 'value', 3: []})

# 传统字典法
dic_b = dict.fromkeys('123',[])
print(dic_b)    # {'1': [], '2': [], '3': []}

# defaultdict() 可以传入一个可回调的对象（函数）
dic_c = defaultdict(lambda :None)   # 如：一句话函数。无值则默认为None
for i in range(1,3):
    dic_c[i]
print(dic_c)        # defaultdict(<function <lambda> at 0x100f1d430>, {1: None, 2: None})


# Counter 计数器
from collections import Counter
c = Counter('aaabaaanbbbccdef')
print(c)    # Counter({'a': 6, 'b': 4, 'c': 2, 'n': 1, 'd': 1, 'e': 1, 'f': 1})
