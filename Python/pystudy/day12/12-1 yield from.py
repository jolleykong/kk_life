#把yield结果作为迭代器。
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




# yield from 优化了内循环效率 提升性能
