# 函数名的运用
# 格式化输出（第三种方法，特别好用）
# 迭代器
    # 可迭代对象
    # 获取对象的方法
    # 判断一个对象是否是可迭代对象
    # 小结
    # 迭代器
    # 迭代器的定义
    # 判断一个对象是否是迭代器
    # 迭代器的取值
    # 可迭代对象如何转化成迭代器
    # while循环模拟 for循环机制
    # 小结
    # 可迭代对象与迭代器的对比


# 函数名的运用
'''
1.函数名是指向函数的内存地址。
    函数名 + () 就可以执行函数。
2.函数名就是变量，变量具备的特性函数名都具备
    变量可被赋值，
3.函数名可以作为容器数据类型的元素
    如 def func1 , func2, func3 , 而后通过对 li = [func1,func2,func3]  使用for循环迭代+() 调用，就可以依次调用容器内的元素名对应的函数。
4.函数名可以作为函数的参数
    # def func():
    #     print('in func')

    # def func1(x):
    #     x()

    # func1(func)
5. 函数名可以作为函数的返回值
    # def func():
    #     print('in func')

    # def func1(x):
    #     print('in func1')
    #     return x

    # ret = func1(func)
    # ret()   # 指向的是func()
'''


# 新的格式化输出
''' 
之前常用的2种方法： %s ，  format
 'im %s' %(name)
 'im {} ,{},{}'.format (name,age,hobby)

新特性： f''

name = 'kk'
age = 20
msg = f'im {name}, now {age}'

# 可以加表达式
dic = {'name':'kk','age':99}
msg = f'im {dic["name"]},now{dic["age"]}'
    # 也可以用列表表达式。
    # 也支持运算符

msg = f'im {age**2}'
mag = f'im {dic["name"].upper()}'


# 结合函数
def func(a,b):
    return a+b

msg = f'result is :{func(2,3)}'


# 优点：
    1. 结构简化
    2. 可以结合表达式、函数进行使用
    3. 【书写，阅读】效率提升很多

# 注意  !,: { } ; 不能出现在{}里面



'''


# 迭代器
    # 可迭代对象
        # 字面意思：
            # 对象：py中，一切皆为对象。一个实实在在存在的值，对象。
            # 迭代：重复的，循环的，一个过程。每次都有新的内容。
            # 可迭代对象： 可以进行循环更新的一个实实在在的值。
        # 专业角度：
            # 可迭代对象：对象内部含有'__iter__'方法的对象，就是可迭代对象。
        # 目前接触到过的可迭代对象： str list tuple dict set range 文件句柄

    # 获取对象的所有方法并以字符串的方式表现出来
        # s1 = 'abcde'
        # print(dir(s1))
        # ''' 以字符串的方式将所有方法作为元素添加到列表。
        # '__add__', '__class__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__mod__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmod__', '__rmul__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format', 'format_map', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zfill']
        # '''

    # 判断一个对象是否是可迭代对象
        # ‘__iter__' in dir(xxxx)
    
    # 小结
        # 可以循环更新的实实在在存在的值
        # 内部含有'__iter__'方法的对象
        # __iter__' in dir(xxxx)
        # str list tuple dict set range 文件句柄
        # 优点：
            # 可迭代对象存储的数据，直接打印就能显示，比较直观
            # 拥有的方法比较多，操作方便
        # 缺点：
            # 占用内存
            # 可迭代对象是不能直接取值的。不能直接通过for循环，不能直接取值（索引，key）
                # 之所以可以通过for循环等方法取值，是因为使用了迭代器


    # 迭代器
        # 可更新迭代的工具
        # 内部含有'__iter__' 方法且含有'__next__'方法的对象就是迭代器。
        # 只含有'__iter__' 方法的对象就是可迭代对象
        # 到目前学习内容为止，只有【文件句柄】是迭代器
            # '''
            # 迭代器要和可迭代对象做类比
            # 因为迭代器并不能“看见”
            # '''




    # 判断一个对象是否是迭代器
        # '''
        #     # '__next__' in dir(obj) && '__iter__' in dir(obj)

        #         # # 文件句柄
        #         # >>> with open('abc',mode='w') as f1:
        #         # ...     a = dir(f1)

        #         # >>> a
        #         # ['_CHUNK_SIZE', '__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__ne__', '__new__', '__next__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '_checkClosed', '_checkReadable', '_checkSeekable', '_checkWritable', '_finalizing', 'buffer', 'close', 'closed', 'detach', 'encoding', 'errors', 'fileno', 'flush', 'isatty', 'line_buffering', 'mode', 'name', 'newlines', 'read', 'readable', 'readline', 'readlines', 'reconfigure', 'seek', 'seekable', 'tell', 'truncate', 'writable', 'write', 'write_through', 'writelines']
        #         # >>>
        #         # >>> '__next__' in a
        #         # True
        #         # >>> '__iter__' in a
        #         # True

        #         # # 列表
        #         # >>> b = [1,2,3,4]
        #         # >>> '__iter__' in dir(b)
        #         # True
        #         # >>> '__next__' in dir(b)
        #         # False
        #         # >>>

        #         # # 字符串
        #         # >>> c = 'abc'
        #         # >>> '__next__' in dir(c)
        #         # False
        #         # >>> '__iter__' in dir(c)
        #         # True
        # '''

    # 可迭代对象可以转化成迭代器
        # iter()
            # s1 = iter(obj)
        # .__iter__()
            # s2.__iter__()

            # >>> b
            # [1, 2, 3, 4]
            # >>> b1 = b.__iter__()
            # >>> b1
            # <list_iterator object at 0x00000274E9706CD0>
            # >>> c
            # 'abc'
            # >>> c1 = iter(c)
            # >>> c
            # 'abc'
            # >>> c1
            # <str_iterator object at 0x00000274E9B9A400>




    # 迭代器的取值

        # 可迭代对象是不能一个一个取值的，之所以可迭代对象可以用for循环迭代，是因为for循环自己做了一个转化。
        # 使用next(obj) 方式， 对obj对象取下一个元素
            # >>> next(c1)
            # 'a'
            # >>> next(c1)
            # 'b'
            # >>> next(c1)
            # 'c'
            # >>> next(c1)
            # Traceback (most recent call last):
            #   File "<stdin>", line 1, in <module>
            # StopIteration

    # 可迭代对象如何转化成迭代器
        # new_obj = iter(obj)


    # while循环模拟for循环机制
'''
1.将可迭代对象转换为迭代器
obj = iter(li)
2.开始while循环，并捕获异常后退出循环。
while 1:
    try:
        print(next(obj))
    except StopIteration:
        break

'''


    # 小结
        # 迭代器的优点
            # 节省内存。如果是列表等可迭代对象，使用时需要一次的都读入内存。迭代器则是迭代读入，循环后这一条便在内存中销毁。
            # 惰性机制，next()一次，只取一个值。
        # 迭代器的缺点
            # 速度慢
            # 不走回头路，一直向下取。


    # 可迭代对象与迭代器的对比
        # 对于可迭代对象，每轮循环结束后，下一次继续从头开始迭代
            # li = [11,22,33,44,55,66,77,88,99,00]
            # for i in range(4):
            #     print(i)

            # for i in range(3):
            #     print(i)

            # 0
            # 1
            # 2
            # 3
            # 0
            # 1
            # 2
        # 对于迭代器，会记录上一次迭代的位置，下一次循环从这里开始。
            # li = [11,22,33,44,55,66,77,88,99,00]
            # i_li = iter(li)
            # for i in range(4):
            #     print(next(i_li))

            # for i in range(3):
            #     print(next(i_li))

            # 11
            # 22
            # 33
            # 44
            # 55
            # 66
            # 77
        # 可迭代对象是一个操作方法比较多，比较直观，存储数据相对少（几百万个对象，8G内存是可以承受的。过千万及亿的对于8G就不行了，考虑迭代器吧）的一个数据集
        # 当侧重于对于数据可以灵活处理，并且内存空间足够时，将数据集设置为可迭代对象是明确的选择。
        # 迭代器是一个非常节省内存，可以记录取值位置，可以通过循环+next()方法取值，但是不直观，操作方法比较单一的数据集。
        # 应用
            # 当数据量过大，大到足以撑爆内存或者想以节省内存为首选因素时，将数据集设置为迭代器是一个不错的选择，这也是为什么py把文件句柄设置成迭代器的一个原因。
