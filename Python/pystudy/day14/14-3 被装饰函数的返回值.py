# 场景三中，原函数的返回值在装饰器后，返回值被变化。

import time
# 通过装饰器来统计函数执行时间
def func1_x(f):
    def inner():
        start = time.time()
        end = time.time()
        print(end - start)
    return inner

def func1():
    time.sleep(2)
    return 'kk'

# 原函数的返回值：kk
print('原函数的返回值',func1())

# 装饰器后的返回值：None
func1 = func1_x(func1)
print('装饰后的返回值',func1())      # 这块返回值由kk变为了None。

'''
原函数的返回值 kk
5.9604644775390625e-06
装饰后的返回值 None
'''

# 因为这个返回值是inner的返回值。
# 真正的函数本体实际上是f()
# 而inner在这里并没有定义返回值
# 能将f()的返回值通过inner返回么？



# 场景五： 将原函数返回值通过装饰器正确返回。
def func1_x(f):
    def inner():
        start = time.time()
        r = f()     # 将f()的返回值赋值给变量r
        end = time.time()
        print(end - start)
        return r    # inner返回r，便返回了f()的返回值。
    return inner

def func1():
    time.sleep(2)
    return 'kk'

# 原函数的返回值：kk
print('原函数的返回值2',func1())

# 装饰器后的返回值：None
func1 = func1_x(func1)
print('装饰后的返回值2',func1())      # 这块返回值由kk变为了None。

'''
原函数的返回值2 kk
2.003506898880005
装饰后的返回值2 kk
'''