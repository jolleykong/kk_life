'''
异常处理
1.错误的分类
    1.语法错误
    2.逻辑错误
2.什么是异常
    代码发生异常错误后，程序就中断了
3.异常处理
    当代码出现异常时，通过某种方式避免程序中断，合理的跳过错误，就是异常处理。
    注意：
        try的开销很大。
        要慎用、精用异常处理。
        只有实在用if代码解决不了，或if代码解决过程很繁琐复杂时，再用异常处理。
4.为什么要有异常处理
    1.用户体验
    2.使代码更有健壮性、容错性。
5.异常处理的两种方式：
    1.if
        if只能处理简单的异常，如果异常需要考虑的方便比较多，则不合适。
        if的判定缩进层级太冗余了。
        通常，if判定不超过三个if。
    2.try
        # 单分支
        # 多分支
        # 万能异常
        # 多分支+万能异常
        # finally 异常前执行的动作
            # try...except          # except 依赖try
            # try...except...else   # else 必须依赖 try和except
            # try...except...else...finally
            # try... finally        # finally 只依赖try、
                # finally 在异常出现之前，执行finally语句。
        # raise 主动触发异常
            raise ValueError('出现了value错误')
        # 断言 一种强硬的态度 assert 条件
            条件不满足则直接报错
        # 自定义异常
            定义错误类，之后通过错误类抛出异常信息。

'''
# try方式示意1
'''
try:
    num = int(input('>>>:'))
    print(5555)
except ValueError:
    print(12345)
# >>>:abc
# 12345
# 出现错误之后，错误行直接跳转到except， 因此跳过了后面的print(5555)
'''

# try方式示意2
'''
try:
    dic = {'name':'大爸爸'}
    print(dic['age'])       # 异常1
    num = int(input('>>>:'))    # 可能异常2
    print(5555)
except ValueError:
    print(12345)
# KeyError: 'age'
'''

# try方式示意 2.1  单分支跳转
'''
try:
    num = int(input('>>>:'))    # 可能异常1
    print(5555)
    dic = {'name':'大爸爸'}
    print(dic['age'])       # 异常2
except ValueError:
    print(12345)

# >>>:abc
# 12345
# 第二个异常直接因为第一个异常的跳转而被跳过了。
'''

# try方式示意 3  多分支跳转
'''
try:
    num = int(input('>>>:'))    # 可能异常1
    print(5555)
    dic = {'name':'大爸爸'}
    print(dic['age'])       # 异常2
    l1 = [1,3]
    print(l1[3])        # 异常3
except ValueError:
    print('data 非法')
except KeyError:
    print('no key')
except IndexError:
    print('no indexed data')

# >>>:abc
# data 非法

# >>>:123
# 5555
# no key

# 可以处理多个错误异常类型了。
'''

# try方式示意 4  可能异常特别多的时候， 代码层级也非常冗余
# 万能异常
'''
try:
    dic = {'name':'大爸爸'}
    print(dic['age'])       # 异常1
    print('point 1')

    l1 = [1,3]
    print(l1[3])        # 异常2
    print('point 2')

    for i in 123:
        pass        # 异常3
    print('point 3')
except Exception:
    pass
# 不报错了。
'''

# 打印异常原因
'''
try:
    # dic = {'name':'大爸爸'}
    # print(dic['age'])       # 异常1
    # print('point 1')

    l1 = [1,3]
    print(l1[3])        # 异常2
    print('point 2')

    for i in 123:
        pass        # 异常3
    print('point 3')

except Exception as e:
    print(e)
# list index out of range
'''

# 什么时候用万能异常？ 什么时候用多分支异常处理？
    # 对错误毫不关心，不需要具体错误信息，只是想要跳过错误让程序继续执行，用万能异常
    # 对错误信息要明确的分流，让程序多元化开发，则需要用多分支异常处理。


# 之前的写法：
# num = input('>>>>').strip()
# if num.isdecimal():
#     num = int(num)
#     if 0 < num < 5:
#         print('level 1')
#         if num == 1:
#             pass
# else:
#     print('wrong num.')

# 现在写法 多分支 + 万能异常处理兜底
'''
def func1():
    print('1')
def func2():
    print('2')
def func3():
    print('3')

dic = {
    1:func1,
    2:func2,
    3:func3
}
try:
    num = int(input('>>>>').strip())
    dic[num]()
except ValueError:
    print('wrong num.')
except KeyError:
    print('wrong idx.')
except Exception as e:
    print(f'Unknow error {e}')
# >>>>0
# wrong idx.
# >>>>1
# 1

'''


'''
try:
    num = int(input('>>>:'))    # 可能异常1
    print(5555)
    dic = {'name':'大爸爸'}
    print(dic['age'])       # 异常2
    l1 = [1,3]
    print(l1[3])        # 异常3
except ValueError:
    print('data 非法')
except KeyError:
    print('no key')
except IndexError:
    print('no indexed data')
else:
    print('没有异常则执行这里')
finally:
    print('最后执行这里')
'''
# try...except          # except 依赖try
# try...except...else   # else 必须依赖 try和except
# try...except...else...finally
# try... finally        # finally 只依赖try

# finally 在异常出现之前，执行finally语句。
'''
try:
    l1 = [1,3]
    print(l1[100])
# except IndexError:        # 屏蔽掉IndexError先。迫使发生异常
#     print('no index data')
finally:
    print('finalllllllllly')
# finalllllllllly           # 异常，但是在异常发生之前，执行了finally子句的内容。
# IndexError: list index out of range   # 执行完finally子句之后才发生异常
'''
# 适用于：在出现异常时 执行关闭文件句柄、关闭数据库连接、数据保存等操作行为。
# 示意代码：
    # with open('file','utf8','w+') as f1:
    #     try:
    #         do something.
    #     finally:
    #         f1.close()

def func():
    print(111)
    return 123
    print(222)      # 永远不会被执行的东西

print(func())
    # 111
    # 123


def func1():
    try:
        print('aaa',111)
        return 123
    finally:
        print(222)      # 永远不会被执行的东西?
print(func1())

    # aaa 111
    # 222
    # 123

# 可以发现， 在return结束函数之前，执行了finally代码。

# 主动触发异常 raise。
'''
raise ValueError('主动触发异常：出现了value错误')

    # ValueError: 主动触发异常：出现了value错误
'''

# assert 断言  一种强硬的态度，出了异常必须要抛出来。
'''
name = 'kk'
n1 = input('>>').strip()
assert name == n1
print(123)
print(456)

    # >>k
    # Traceback (most recent call last):
    #   File "/Users/kk/Documents/gittee/kk_mysql/Typora_data/Python/pys/day26 oop回顾及异常处理/26-2 异常处理.py", line 257, in <module>
    #     assert name == n1
    # AssertionError

    # >>kk
    # 123
    # 456
'''

# 自定义异常
# python中提供的错误类型非常多，但是并不是全部的错误。
# 可以自创异常类型。

# 首先定义错误名字
class KkError(BaseException):    # 必须要继承BaseException。 万能异常继承自BaseException
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):          # print会触发__str__
        return self.msg         # 触发则返回错误信息

try:
    raise KkError('错误信息:这是一个自定义的错误信息asdfasdkfjbaf')  # 主动引发异常
                        # raise 异常， 必须基于错误类
except KkError as e:
    print(e)
    # 错误信息:这是一个自定义的错误信息asdfasdkfjbaf
