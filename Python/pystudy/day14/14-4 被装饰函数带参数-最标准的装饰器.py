# import time
# def func1_x(f):
#     def inner():
#         start = time.time()
#         r = f()     # 将f()的返回值赋值给变量r
#         end = time.time()
#         print(end - start)
#         return r    # inner返回r，便返回了f()的返回值。
#     return inner

# @func1_x
# def func1(a,b):
#     time.sleep(2)
#     return a+b

# 将a,b传入装饰后的函数
#func1(10,20)    # 报错。
    # 因为func1() == inner()， 而inner() 并没有定义参数。
# 所以就给inner定义个参数。
import time
def func1_x(f):
    def inner(*args,**kwargs):           # 也可以是单个位置参数， 在这里我懒了。
        start = time.time()
        r = f(*args,**kwargs)     # 将f()的返回值赋值给变量r
        end = time.time()
        print(end - start)
        return r    # inner返回r，便返回了f()的返回值。
    return inner

@func1_x
def func1(a,b):
    time.sleep(2)
    return a+b
print(func1(10,20))

# 其实这就是最完整的标准的装饰器
def wrapper(f):
    def inner(*args,**kwargs):
        # something before running func
        ret = f(*args,**kwargs)
        # something after running func
        return ret
    return inner

#@wrapper
    # 涉及到闭包
    # 符合开放封闭原则，拓展功能，不改源码，不变调用。
    # 不影响原逻辑和结果。