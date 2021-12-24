# 默认参数时可变的数据类型时， 有陷阱。
    # 如果默认参数指向的是可变的数据类型，那么无论调用多少次这个默认参数，这个数据对象指向的都是同一个内存对象。
'''
def func(name,alist=[]):
    alist.append(name)
    return alist

ret1 = func('abc')
print(ret1)         # ['abc']
ret2 = func('bcd')
print(ret2)         # 按理说，重复执行函数，默认参数为alist=[] ，结果应该只是['bcd']，实际上并不是
                        # 因为这两个结果是一个list对象（id相等），结果为['abc','bcd']
'''
# 所以想调用一个新的列表，那就要指定参数，而不是使用默认参数的列表对象。
def func(name,alist=[]):
    alist.append(name)
    return alist

ret1 = func('abc')
print(ret1)      # ['abc']
ret2 = func('bcd')
print(ret2) 
ret3 = func('def',[])           # 指定参数，而不是默认参数。
print(ret3)   
#['abc']
#['abc', 'bcd']
#['def']





# 局部作用域的坑
'''
# 本该调用全局作用域的变量值，但是py解释器认为局部作用域中声明的变量写在后面了，因此报错。
# 因此，应该在使用前先定义。

count = 1
def func():
    print(count)    # 查询全局作用域的count值
    count = 2       # 声明局部作用域的count值
    print(count)    # 输出局部作用域的count值

func()  # UnboundLocalError: local variable 'count' referenced before assignment

'''


# global
# global关键字用来在函数或其他局部作用域中使用全局变量。
# 1. 在局部作用域中声明一个全局变量。
'''
def func():
    global name
    name = 'kk'
    print(name)

func()
print(name)     # 在全局作用域中输出了局部作用域中声明的全局变量。
'''

# 2.修改一个全局变量
'''
count = 1
def func():
    # print(count)
    # count += 1 # 会报错。
    global count
    print(count)
    count += 1
    print(count)

'''

# nonlocal
# nonlocal声明的变量不是局部变量,也不是全局变量,而是外部嵌套函数内的变量。
# 1.不能够操作全局变量
'''
count = 1
def func():
    nonlocal count      # 不能操作全局变量。
    count += 1
'''

# 2.局部作用域：内层函数对外层函数的局部变量进行修改
'''
count = 2
def func():
    count = 1
    def inner():
        count += 1      # 正常是不可以的。 
    inner()

func()


# 但是换一种方式 用nonlocal实现
count = 33
def func():
    count = 1
    def inner():
        nonlocal count  # nonlocal指定后，就可以修改引用的（上一层）的变量了。 但不适用于全局变量，只适用于“E”级别的。
        count += 1
        print(count)
    inner()
    print(count)
func()
# 结果是： 2 \n 2
'''













