# 装饰器：装饰，装修。如果装修，体验更加，增加更多功能。
# 开放封闭原则：
    # 开放：对代码的拓展是开放的。——更新新功能。不影响现有功能的前提下，拓展新功能。扩展新功能后，之前的功能完全没有变化。
    # 封闭：对源码的修改是封闭的。——轻易不会动已有的，如一个函数，被多处调用，如果修改则牵一发而动全身，因此很少使用。

# 装饰器完全遵循开放封闭原则。
# 装饰器在不改变原函数的代码以及调用方式的前提下，为其增加新的功能。
# 装饰器就是一个函数。
# 装饰器完美的呈现了开放封闭原则。

# 场景一： 写一些代码测试一下某函数的执行效率。
    # 这一块就需要在开始和结束的时候加上计时，用来统计执行时间
    # 场景一的问题： 如果测试别人的代码，必须重新赋值粘贴。

def idx():
    '''
    codes。 这里有很多执行代码。
    '''
    time.sleep(2)
    print('codes')

import time
start = time.time()  # 格林威治时间
idx()
end = time.time()
print( end - start )        # 2.005232095718384

# 如果要测试更多的函数， 就把同样的动作复制n次。

# 场景二： 利用函数， 解决代码重复使用的问题
    # 场景二的问题：原来函数的源码没有改变（只是被调用），给原函数添加了一个新的功能：测试原函数执行效率。
        # 但是未满足开放封闭方式： 未改变原函数代码，增加了新功能，但是改变了调用方式（单独摘出来独立调用的，并不体现原项目工程中的实际调用逻辑。）
import time
def idx():
    '''
    codes。 这里有很多执行代码。
    '''
    time.sleep(2)
    print('codes')

def fun1():
    pass

def fun2():
    pass

def timer(f):
    start_time = time.time()
    f()
    end_time = time.time()
    print(end_time - start_time)

timer(idx)  # 原有的调用方式为idx()
timer(fun1)
timer(fun2)


# 场景三：
    # 原函数代码不能变
    # 要增加执行时间统计
    # 调用方式也不能改变
def timer(f):
    def inner():    # 闭包，将统计时间放入内层嵌套。
        start_time = time.time()
        f()         # 未执行inner() ，这里也未执行f()
        end_time = time.time()
        print(end_time - start_time)
    return inner    # 一定是返回函数名，不要括号！这里也没执行
                    # 所以timer(f) == inner，没有括号。
ret = timer(idx)    
# 先运行timer —— 将idx传入，
# idx传入inner后， 并不执行
# 到return inner时，将inner返回给timer
# 所以，timer(idx) == inner
# 最终ret是inner
# ret() == inner()
# 其实这就是最标准版本的装饰器。

# 再次示意，这个装饰器如何做到不调整调用方式便实现功能拓展的。
def timer(f):       # f = idx (function addr: idx123)
    def inner():    # inner : (function addr: inner123)
        start_time = time.time()
        f()         # idx() (function addr: idx123)
        end_time = time.time()
        print(end_time - start_time)
    return inner    # inner : (function addr: inner123)
                   
ret = timer(idx)  # inner : (function addr: inner123)
idx = timer(idx)  # inner : (function addr: inner123)   此时idx指向的函数地址已经不是最开始的地址了， 但是函数的代码并没有被更改，而且实现了功能拓展。
idx()               # inner : (function addr: inner123)  但是原有的调用方式没有任何改动。
print(idx())        # 但是这一步的返回值是None，为什么？
    # 场景三中，原函数的返回值在装饰器后，返回值被变化。

# 场景四：语法糖，python的一个优化概念。
    # 场景三中，必须要有一行idx = timer(idx) ， 但是引用原函数次数过多的话，也需要很多工作。
# 使用语法糖方式，在程序头部首先定义装饰器，
# 在后面的代码中，在需要被装饰的函数上一行， 使用@装饰器名   这一语法糖，简化装饰器的使用。




