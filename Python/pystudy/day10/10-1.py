# 继续形参角度：
    # （位置参数，默认参数），万能参数，仅限关键字参数
    # *的魔术用法
    # 仅限关键字参数（了解）
    # 形参的最终顺序

# 名称空间
    # 全局名称空间，局部名称空间
    # 加载顺序与取值顺序
    # 作用域

# 函数的嵌套（高阶函数）
# 内置函数  globals locals
# 关键字 nonlocal global





# 万能参数
# 急需要一种形参，去接受所有的实参。 
# *args ， 约定俗成：args ， 接受所有的位置参数。
    # 函数定义时，*代表聚合。它将所有的位置参数聚合成了一个元组，赋值给args。

# 写一个函数，计算传入函数的所有数字的和。
def sums(*args):
    count = 0
    for i in args:
        if isinstance(i,int):
            count = count+i #count += i
    return count
print(sums(1 ,2 ,3 ,4 ,5 ,6 ,6 ,7 ,818,'a'))

# **kwargs ，接受所有的关键字参数。将所有的关键字参数聚合到一个字典中，然后将字典赋值给kwargs
'''
def funckw(**kwargs):
    print(kwargs)

funckw(name='kk',age=10,sex='M',edu='abc')
# result {'name': 'kk', 'age': 10, 'sex': 'M', 'edu': 'abc'}

# 改写day9练习题8
#8.写函数，接受4个参数：姓名，性别，年龄，学历。用户输入四个内容，将四个内容传入给函数，函数将内容追加到一个student_msg文件中。
def typein(**kwargs):
    data = '姓名：'+kwargs['name']+'，性别：'+kwargs['sex']+'，年龄：'+kwargs['age']+'学历：'+kwargs['edu']+'\n'
    print(data)
    return 0
typein(name='a',sex='b',age='c',edu='d')
'''

# 形参角度的参数顺序
# *args要放在位置参数的最后面。否则位置参数都被args接收了。
# 默认参数要放在*args后面，不然args接收的东西会覆盖默认参数（关键字参数）的值。
# **kwargs要放在默认参数（关键字参数）的后面，不然关键字参数就被kwargs收走了
# def func(a,b,*args,c='default',**kwargs)

# 形参角度的第四个参数：仅限关键字参数（since 3.4）
    # def func(a,b,*args,c='default',d,**kwargs)
    # 其中，d 参数就是「仅限关键字参数」，只能在args和kwargs之间放置。
    # 调用时可以这样用 func(v_a,v_b,arg1,arg2,arg3...,c='xxx',d='xxx',kw1,kw2...)
# 因此，形参角度，最终的位置顺序是 
    # 位置参数-->*args --> 默认参数 / 仅限关键字参数（二者顺序无所谓）--> **kwargs


# * 的魔法
    # 在定义函数时，*代表聚合
    # 在函数调用时，*代表打散。在可迭代对象前加*，
    # 对于可迭代对象：*
    # 对于字典：**
    
''' * 对于可迭代对象
def funcs(*args):       # args是一个元组
    print(args)

funcs([1,2,3],[22,33])

使用魔法
>>> funcs([1,2,3],[22,33])
([1, 2, 3], [22, 33])       # 是一个元组
>>> funcs([1,2,3],*[22,33]) 
([1, 2, 3], 22, 33)             # 元组的元素被打散出来了
>>> funcs(*[1,2,3],*[22,33])
(1, 2, 3, 22, 33)
'''

''' ** 对于字典
def funcs(**kwargs):
    print(kwargs)

funcs({'name':'kk'},{'age':'1000'})

使用魔法
>>> funcs({'name':'kk'},{'age':'1000'})     # 并未传入关键字参数，因此会报错
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: funcs() takes 0 positional arguments but 2 were given

>>> funcs(**{'name':'kk'},**{'age':'1000'})     # 打散字典对象，拆开后就变成了关键字参数。等同于('name'='kk','age'='100')
{'name': 'kk', 'age': '1000'}
'''