'''
1.规范化开发
2.time模块
3.datetime模块
4.random模块
5.collections模块

'''


'''
1.规范化开发

所有内容在一个py文件中，会遇到：
    1.文件加载问题，所有代码一次性加载，效率不好。
    2.代码可读性差，查询麻烦。
    要将一个py文件分开，合理的按照规则分成多个py文件。
- 一些轻易不改变的变量，称为 配置选项，主要用来被引用。 一般将这些变量放入配置文件，settings.py
- 以博客作业举例，
        - 将登录和注册、功能菜单划分到一个文件划分到一个文件，作为主逻辑函数，src.py
        - 辅助功能的函数分到一个文件，公共组件部分，如装饰器、日志等不影响函数的功能代码，放入公共组件部分，common.py
        - 将启动程序入口（程序启动开关）单独分到一个文件，一般函数名为run() ，starts.py
        - 数据库文件，（用户信息、访问记录等）
        - 日志文件
bin
    starts.py
conf
    setting.py
core
    src.py
db
    xxxxx
lib
    common.py
log
    xxxxx
README




将博客作业使用规范化结构改写重建。
'''








'''
2.time模块
时间相关的模块，三种形式：
- 时间戳timestamp time.time()    ，时差，计时等。
- 人类可读的格式化时间format_string  time.strftime("%Y-%m-%d %H:%M:%S")    ，字符串类型，但格式化中只能包含ascii字符。要使用中文需要结合{} 以及format方法进行处理。
- 结构化时间struct_time  time.localtime()   ，本地的结构化时间。

三种形式时间的转换：
- 格式化 --> 结构化 : strptime
- 结构化 --> 格式化 : strftime

- 时间戳 --> 结构化 : localtime /  gmtime
- 结构化 --> 时间戳 : mktime

格式化和时间戳的转换需要通过结构化来中转。



- 时间戳转换成格式化时间
tm = time.time()
st = time.localtime(tm)         # 时间戳转换成结构化时间
fm = time.strftime("%Y-%m-%d %H:%M:%S",st)      # 结构化时间转换成格式化时间

- 格式化时间转换成时间戳 strptime
fm = time.strftime("%Y-%m-%d %H:%M:%S") 
st = time.strptime(fm,"%Y-%m-%d %H:%M:%S")  # 格式化时间转换成结构化时间
tm = time.mktime(st)        # 结构化时间转换成时间戳

- 计算时间差
转换成时间戳进行数学运算，

import time
true_time=time.mktime(time.strptime('2017-09-11 08:30:00','%Y-%m-%d %H:%M:%S'))
time_now=time.mktime(time.strptime('2017-09-12 11:00:00','%Y-%m-%d %H:%M:%S'))
dif_time=time_now-true_time
struct_time=time.gmtime(dif_time)
print('过去了%d年%d月%d天%d小时%d分钟%d秒'%(struct_time.tm_year-1970,struct_time.tm_mon-1,
                                       struct_time.tm_mday-1,struct_time.tm_hour,
                                       struct_time.tm_min,struct_time.tm_sec))

'''



'''
3.datetime模块
可以“调节”时间

from datetime import datetime
# import datetime
time_now = datetime.now()
>>> time_now
datetime.datetime(2021, 10, 10, 11, 53, 24, 993023)
>>> type(time_now)
<class 'datetime.datetime'>


# datatime模块
import datetime
now_time = datetime.datetime.now()  # 现在的时间
# 只能调整的字段：weeks days hours minutes seconds
print(datetime.datetime.now() + datetime.timedelta(weeks=3)) # 三周后
print(datetime.datetime.now() + datetime.timedelta(weeks=-3)) # 三周前
print(datetime.datetime.now() + datetime.timedelta(days=-3)) # 三天前
print(datetime.datetime.now() + datetime.timedelta(days=3)) # 三天后
print(datetime.datetime.now() + datetime.timedelta(hours=5)) # 5小时后
print(datetime.datetime.now() + datetime.timedelta(hours=-5)) # 5小时前
print(datetime.datetime.now() + datetime.timedelta(minutes=-15)) # 15分钟前
print(datetime.datetime.now() + datetime.timedelta(minutes=15)) # 15分钟后
print(datetime.datetime.now() + datetime.timedelta(seconds=-70)) # 70秒前
print(datetime.datetime.now() + datetime.timedelta(seconds=70)) # 70秒后

current_time = datetime.datetime.now()
# 可直接调整到指定的 年 月 日 时 分 秒 等

print(current_time.replace(year=1977))  # 直接调整到1977年
print(current_time.replace(month=1))  # 直接调整到1月份
print(current_time.replace(year=1989,month=4,day=25))  # 1989-04-25 18:49:05.898601

# 将时间戳转化成时间
print(datetime.date.fromtimestamp(1232132131))  # 2009-01-17
'''



'''
4.random模块
random.randomint(1,5)
random.random()
random.uniform(1,5)
random.randrange(1,10,2) # step
random.choice(['a','b','c'])    # list or tuple,not only number.
random.sample(['a','b','c'],2)  # choice more than 1, like 2.
random.shuffle(list)        # 将原列表打乱顺序。

'''


'''
5.collections模块

'''