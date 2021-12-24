# # 默写标准版本装饰器
# import time
# def func1():
#     time.sleep(2)
#     return 'kk'


# # print(func1())

# # 通过装饰器来统计函数执行时间
# def func1_x(f):
#     def inner():
#         start = time.time()
#         f()
#         end = time.time()
#         print(end - start)
#     return inner

# func1 = func1_x(func1)
# print(func1())      # 有个问题，这块返回值由kk变为了None。




#1. 看代码写结果
'''
def wrapper(f):
    def inner(*args,**kwargs):
        print(111)
        ret = f(*args,**kwargs)
        print(222)
        return ret
    return inner

def func():
    print(333)

print(444)
func()
print(555)
'''
#444,111,333,222,555…… 错了！
# 这里没调用装饰器！！所以是 444，333，555

#2. 编写装饰器，在每次执行被装饰函数之前打印一句”每次执行被装饰函数之前都得先经过这里，这里根据需求写代码“
# def wrapper(f):
#     def inner(*args,**kwargs):
#         print('每次执行被装饰函数之前都得先经过这里，这里根据需求写代码')
#         ret = f(*args,**kwargs)
#         return ret
#     return inner
# @wrapper
# def f1():
#     print('hello')

# f1()

#3. 为函数写一个装饰器， 把函数的返回值+100，然后再返回
'''
@wrapper
def func():
    return 7

result = func()
print(result)
'''
# def wrapper(f):
#     def inner(*args,**kwargs):
#         ret = f(*args,**kwargs)
#         return ret+100
#     return inner

# @wrapper
# def func():
#     return 7

# result = func()
# print(result)

#4. 请实现一个装饰器， 通过一次调用使函数重复执行5次
# def wrapper(f):
#     def inner(*args,**kwargs):
#         for i in range(5):
#             f(*args,**kwargs)
#     return inner

# @wrapper
# def func():
#     print('7')
# func()

#5. 请实现一个装饰器，每次调用函数时，将函数名以及调用此函数的时间写入文件中。
'''
可用代码：
import time
struct_time = time.localtime()
print(time.strftime("%Y-%m-%d %H:%M:%S",struct_time))   # now

def wrapper():
    pass

def func1(f):
    print(f.__name__)   # 函数名通过.__name__ 获取、
func1(wrapper)
'''
import time
# struct_time = time.localtime()
# print(time.strftime("%Y-%m-%d %H:%M:%S",struct_time))   # now

def wrapper(f):
    def inner(arg):
        struct_time = time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime())
        func_name = (arg).__name__
        # print(time.strftime("%Y-%m-%d %H:%M:%S",struct_time))   # now
        ret = f(arg)
        
        with open('./day14/record',mode='a') as file:
            file.writelines(func_name + '|' + str(struct_time) + '\n')
        return ret
    return inner

@wrapper
def func1(f):
    print(f.__name__)   # 函数名通过.__name__ 获取、
func1(wrapper)

