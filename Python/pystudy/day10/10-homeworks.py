# 1.写函数，函数可以支持接收任意数字，并将所有数据相加。
# def sums(*args):
#     count = 0
#     for i in args:
#         count += i
#     return count
# print(sums(1,2,34,5,6,6,1,2,31,2,3,1))

# 2.看代码写结果
'''
def func():
    return 1,2,3

val = func()
print( type(val) == tuple )
print( type(val) == list )
'''# True, False

# 3.看代码写结果
'''
def func(*args,**kwargs):
    pass

    # def func(*args,**kwargs):
    #     print(args)
    #     print(kwargs)

# a. 执行函数，实现让args的值为 (1,2,3,4)
func(1,2,3,4)
func(*[1,2,3,4])

# b. 执行函数，实现让args的值为 ([1,2,3,4],[11,22,33])
func([1,2,3,4],[11,22,33])
func(*[[1,2,3,4],[11,22,33]])

# c. 执行函数，实现让args的值为 ([11,22],33)，且kwargs的值为({'k1':'v1','k2':'v2'})
func([11,22],33,**{'k1':'v1','k2':'v2'})
func([11,22],33,'k1'='v1','k2'='v2')

# d. 如执行 func(*{'abc','aa','bb'}), args和kwargs的结果分别为什么？
args:('abc','aa','bb'),kwargs:None

# e. 如执行 func({'abc','aa','bb'},[11,22,33]), args和kwargs的结果分别为什么？
args:({'abc','aa','bb'},[11,22,33]),kwargs:None

# f. 如执行 func({'abc','aa','bb'},[11,22,33],**{'k1':'v1'}), args和kwargs的结果分别为什么？
args:({'abc','aa','bb'},[11,22,33]),kwargs:{'k1':'v1'}

'''


# 4.看代码写结果
'''
def func(name,age=19,email='123@qq.com'):
    pass

# a.执行 func('abc') ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=19,email='123@qq.com'

# b.执行 func('abc'，20) ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=20,email='123@qq.com'

# c.执行 func('abc'，20，30) ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=20,email=30

# d.执行 func('abc'，email='a@qq.com') ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=19,email='a@qq.com'

# e.执行 func('abc'，email='a@qq.com', age=99) ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name'abc',age=99,email='a@qq.com'

# f.执行 func('abc',99) ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=99,email='123@qq.com'

# g.执行 func('abc',99,'aaaa@qq.com') ，判断是否可执行，如可以，name、age、email的值分别是什么？
可以，name='abc',age=99,email='aaaa@qq.com'

'''


# 5.看代码写结果
'''
def func(users,name):
    users.append(name)
    return users

result = func(['abc','aaa'],'bbb')
print(result)
'''
# ['abc','aaa','bbb']


# 6.看代码写结果
'''
def func(v1):
    return v1 * 2

def bar(arg):
    return "%s is what?" %(arg,)

val = func('you')
data = bar(val)
print(data)
'''
# youyou is what?


# 7.看代码写结果
'''
def func(v1):
    return v1 * 2

def bar(arg):
    msg = "%s is what?" %(arg,)
    print(msg)

val = func('you')
data = bar(val)
print(data)
'''
# bar() 没有返回值， 所以返回值是None。

# 8.看代码写结果
'''
v1 = 'abc'
def func():
    print(v1)

func()
v1 = 'bbb'
func()
'''
# 'abc', 'bbb'

# 9.
'''
v1 = 'abc'
def func():
    v1 = 'aaa'
    def inner():
        print(v1)
    v1 = 'bbb'
    inner()

func()
v1 = 'ccc'
func()
'''
# 'bbb',  'bbb'


# 10.
'''
def func():
    data = 2 * 2
    return data

new_name = func
val = new_name()
print(val)
'''
# 4


# 11.
'''
def func():
    data = 2*2
    return data

data_list = [func,func,func]
for item in data_list:
    v = item()
    print(v)
'''
# 4 4 4

# 12.
''' 函数可以做参数进行传递
def func(arg):
    arg()

def show():
    print('show functions')

func(show)
'''
# 相当于执行了 show() 。show functions
# func (show)  --> show()  --> print('show functions')

# 13. 写函数，接收n个数字，求这些参数数字的和。（动态传参）
# 跟1 一样。


# 14. 读代码，回答：代码中打印出来的值a，b，c分别是什么？
'''
a = 10
b = 20
def test5(a,b):
    print(a,b)

c = test5(b,a)
print(c)
'''
# None。 因为没有返回值。

# 15. 读代码，回答 代码中打印出来的值a，b，c分别是什么？
'''
a = 10
b = 20
def test5(a,b):
    a = 3
    b = 5
    print(a,b)

c = test5(b,a)
print(c)
'''
# None。 因为没有返回值。


# 16. 传入函数中多个列表和字典，如何将每个列表的每个元素依次添加到函数的动态参数args里面？如何将每个字典的所有键值对依次添加到kwargs里面？
# 直接用* 释放
def foo(*args,**kwargs):
    print(args)
    print(kwargs)

foo(*[1,2,3],*[3,4,5],*[5,6,7],**{'a':1},**{'b':2})


# 17. 写函数，接受两个数字参数，将较小的数字返回。

# 18.写函数，接受一个参数，参数类型必须是可迭代对象。将可迭代对象的每个元素以'_'项链，形成新的字符串并返回。
    # 例如 传入的可迭代对象为[1,'aaa','bbb']，结果为1_aaa_bbb

# 19. 有如下函数，可以任意添加代码，执行inner函数
'''
def wrapper():
    def inner():
        print(666)

wrapper()
'''


# 20.写出下列代码结果
'''
def foo(a,b,*args,c,sex=None,**kwargs):
    print(a,b)
    print(c)
    print(sex)
    print(args)
    print(kwargs)

# foo(1,2,3,4,c=6)
1,2
6
None
3,4
{}

# foo(1,2,sex='M',name='alex',hobby='old')
报错，缺少仅限关键字参数c的传参。

# foo(1,2,3,4,name='ale',sex='M')
报错，缺少仅限关键字参数c的传参。

# foo(1,2,c=18)
1,2
18
None
None
None

# foo(2,3,[1,2,3],c=13,hobby='eat')
2,3
13
None
[1,2,3]
{'hobby':'eat'}


# foo(*[1,2,3,4],**{'name':'a','c':12,'sex':'F'})
1,2
12
F
3,4
{'name':'a'}
'''