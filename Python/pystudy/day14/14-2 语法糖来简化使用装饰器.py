# 场景四：语法糖，python的一个优化概念。
    # 场景三中，必须要有一行idx = timer(idx) ， 但是引用原函数次数过多的话，也需要很多工作。
# 使用语法糖方式，在程序头部首先定义装饰器，
# 在后面的代码中，在需要被装饰的函数上一行， 使用@装饰器名   这一语法糖，简化装饰器的使用。




# 先定义装饰器
import time
def timer(f):
    def inner():
        start_time = time.time()
        f()
        end_time = time.time()
        print(end_time - start_time)
    return inner

# 再定义函数等程序部分

# 在需要被装饰器处理的函数前使用语法糖
@timer      # @timer == idx = timer(idx)
def idx():
    '''
    codes。 这里有很多执行代码。
    '''
    time.sleep(2)
    print('codes')

def fun1():
    pass

@timer      # @timer == fun2 = timer(fun2)
def fun2():
    pass

idx()
fun1()
fun2()
