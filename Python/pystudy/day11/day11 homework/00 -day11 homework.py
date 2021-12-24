'''
1.写出下列代码的执行结果
def func1():
    print(** 'in func1'**)

def func2():
    print(** 'in func2'**)

ret = func1
ret()

ret1 = func2
ret2()

ret2 = ret
ret3 = ret2

ret2()
ret3()


2.看代码写结果
def func(arg):
    return arg.replace('文明用语','****')

def run():
    msg = '哈哈哈你看着文明用语变没变'
    result = func(msg)
    print(result)

run()


def func(arg):
    return arg.replace('文明用语','****')

def run():
    msg = '哈哈哈你看着文明用语变没变'
    result = func(msg)
    print(result)

data = run()
print(data)

3.看代码写结果
DATA_LIST = []
def func(arg):
    return DATA_LIST.insert(0, arg)

data = func('绕不死你')
print(data)
print(DATA_LIST)

4.看代码写结果
def func():
    print('hello')
    return 'sb'

func_list = [func,func,func]
for item in func_list:
    val = item()
    print(val)


5.看代码写结果
def func():
    print('hello')
    return 'sb'

func_list = [func,func,func]
for i in range(len(func_list)):
    val = func_list[i]()
    print(val)


6.看代码写结果
def func():
    return 'shaobing'

def bar():
    return 'doubi'

def base(a1,a2):
    return a1() + a2()

result = base(fun, bar)
print(result)


7.看代码写结果
for item in range(10):
    print(item)

print(item)

8.看代码写结果
def func():
    for item in range(10):
        pass
    print(item)

func()

9.看代码写结果
item = 'kk'
def func():
    item = 'kongyan'
    def inner():
        print(item)
    for item in range(10):
        pass
    inner()
func()

10.看代码写结果
l1 = []
def func(args):
    l1.append(args)
    return l1
print(func(1))
print(func(2))
print(func(3))


11.看代码写结果
name = 'kk'
def func():
    global name
    name = 'kongyan'
print(name)
func()
print(name)

12.看代码写结果
name = 'kk'
def func():
    print(name)
func()

13.看代码写结果
name = 'kk'
def func():
    print(name)
    name = 'kongyan'
func()

14.看代码写结果
def func():
    count = 1
    def inner():
        nolocal count
        count += 1
        print(count)
    print(count)
    inner()
    print(count)
func()

15.看代码写结果
def extendList(valmlist=[]):
    list.append(val)
    return list

list1 = extendList(10)
list2 = extendList(123,[])
list3 = extendList('a')

print('list1=%s' %list1)
print('list2=%s' %list2)
print('list3=%s' %list3)

16.看代码写结果
def extendList(val,list=[]):
    list.append(val)
    return list
print('list1=%s' %extendList(10))
print('list2=%s' %extendList(123,[]))
print('list3=%s' %extendList('a'))

17.用你的理解解释一下什么是可迭代对象，什么是迭代器
18.如何判断该对象是否是可迭代对象或者迭代器？
19.写代码，用while循环模拟for的循环机制
20.写函数，传入n个数，返回字典：{'max':最大值,'min':最小值}
21.写函数，传入一个参数n，返回n的阶乘。如cal(7) ，计算7*6*5*4*3*2*1
22.写函数，返回一个扑克牌列表，里面有52项，每一项是一个元组，如[('红心',2),('草花','A')...]
23.写代码完成99乘法表。



'''