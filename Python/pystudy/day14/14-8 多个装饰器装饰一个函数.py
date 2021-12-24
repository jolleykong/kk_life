# 多个装饰器去装饰一个函数

def wrapper1(func1):
    def inner1():
        print('wrapper1,before func')
        func1()
        print('wrapper1,after func')
    return inner1


def wrapper2(func2):
    def inner2():
        print('wrapper2,before func')
        func2()
        print('wrapper2,after func') 
    return inner2

@wrapper2
@wrapper1
def f():
    print('in f')

f()


'''result
wrapper2,before func
wrapper1,before func
in f
wrapper1,after func
wrapper2,after func
'''

# 也就是层层包
'''
# 流程分析

def wrapper1(func1):
    def inner1():
        print('wrapper1,before func')       # 2
        func1()
        print('wrapper1,after func')        # 4
    return inner1


def wrapper2(func2):
    def inner2():
        print('wrapper2,before func')       # 1
        func2()
        print('wrapper2,after func')        # 5
    return inner2

@wrapper2               # step 1, wrapper2(f) == wrapper2(wrapper1) == inner1
@wrapper1               # step 2, wrapper1(f) == wrapper1(f) == inner2
def f():
    print('in f')           # 3     # step 3, f
                        # step 4, wrapper1(f) after
                        # step 5, wrapper2(wrapper1) after

f()
'''