# 12-1-通过函数构造生成器：生成器yield示例.py
def func():
    print(11)
    print(22)
    yield 3

func()  # 这是没有运行函数的？ 因为没有结果。
print(func())   # <generator object func at 0x104d500b0> 显示的是生成器类型
ret = func()
print(next(ret))
                # 这时返回了结果，其中
                # 11    # print动作
                # 22    # print动作
                # 3     # yield返回的值

# 此时，我们多加几个yield
def func1():
    print(11)
    print(22)
    yield 3
    yield 4
    yield 5
    yield 6

ret1 = func1()
print(next(ret1))   # 3
print(next(ret1))   # 4
print(next(ret1))   # 5
print(next(ret1))   # 6
#print(next(ret1))   # StopIteration


# 我们在yield之间加一些代码，可以观察到每一次next的停止位置。
def func2():
    print(11)
    print(22)
    yield 3
    a = 7
    b = 8
    print(a+b)
    yield 4
    print('four')
    yield 5
    print('aaa')
    yield 6

ret2 = func2()
print(next(ret2))
                    # 11
                    # 22
                    # 3
print(next(ret2))
                    # 15
                    # 4
print(next(ret2))
                    # four
                    # 5
print(next(ret2))
                    # aaa
                    # 6
print(next(ret2))
                    # StopIteration