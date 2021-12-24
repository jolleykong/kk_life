# 生成器
    # yield
    # yield 和 return 的区别
    # yield from
# 生成器表达式，列表推导式
# 内置函数


# 生成器
    # 生成器是啥？
        # 生成器和迭代器可以理解成是一种东西。所以本质上就是迭代器
        # 生成器是自己用py代码构建的数据结构
        # 迭代器是提供的，或者转化得来的。

        # 获取生成器的三种方式
            # 生成器函数
            # 生成器表达式
            # python内部提供的一些生成器

        # 获取迭代器的方式
            # python内部提供的
            # 通过iter()转化的
            # 通过结果返回的

    # 通过函数，生成器获取函数
        # 和函数定义很像，但是不同
            # return：函数只存在一个return结束函数，并且给函数的执行者返回指定值
            # yield：只要函数中有yield，那么它就是生成器函数，而不是函数。
                # 生成器函数中可以存在多个yield，yield并不会结束生成器函数一个yield对应一个next。
                # <12-1-通过函数构造生成器：生成器yield示例.py>
    # 通过生成器表达式获取生成器
# 生成5000个包子的办法
def func():
    l1 = []
    for i in range(1,5001):
        l1.append(f'{i}#包子')
    return l1
ret = func()
print(ret)
# result : ['1#包子', ... '4999#包子', '5000#包子']
# 不过这样一来，想生成多少就要生成完多少，占据内存。
# 比如这时候拿走2个包子，要记录剩下的情况，就一直这样在内存中占据着。

# 使用生成器
def gen_func():
    for i in range(1,5001):
        yield f'{i}#包子'

ret2 = gen_func()    # 此时生成器函数也并没有运行。

print(next(ret2))       # 1#包子
# 后续想拿几个包子就执行几次就好。
for i in range(1,20):
    print(next(ret2))       # 2..20#包子

print(next(ret2))           # 21#包子



    # yield
    # yield | return
    # yield from ，把yield结果作为迭代器。
def func2():
    l1 = [1,2,3,4,5]
    yield l1

ret21 = func2()
print(ret21)
print(next(ret21))      # [1, 2, 3, 4, 5]

def func3():
    l1 = [1,2,3,4,5]
    yield from l1

ret22 = func3()
print(ret22)
print(next(ret22))      # 1 ，可以发现，l1被作为迭代器返回了元素，而不是返回整个列表。
print(next(ret22))      # 2
print(next(ret22))      # 3



def func4():
    list1 = ['a','b','c']
    list2 = ['E','F','G']
    yield from list1
    yield from list2
g = func4()
for i in range(6):
    print(next(g))

# a
# b
# c
# E
# F

def func5():
    list1 = ['a','b','c']
    list2 = ['E','F','G']
    yield list1
    yield list2
g = func5()
for i in range(6):
    print(next(g))

# ['a', 'b', 'c']
# ['E', 'F', 'G']
# StopIteration

# 生成器表达式，列表推导式

    # 列表推导式和生成器表达式的区别
        # 写法小差异
        # iterable和iterator的区别，列表推导式生成可迭代对象，生成器表达式生成迭代器。

    # 扩展知识
        # 字典推导式（了解）
            # li11 = ['aa','bb','cc']
            # li22 = ['张','王','李']
            # dic = { li22[i]:li11[i] for i in range(len(li11))}
            # print(dic)  # {'张': 'aa', '王': 'bb', '李': 'cc'}
        # 集合推导式（了解）
            # {i for i in range(1,11)}

# 内置函数

