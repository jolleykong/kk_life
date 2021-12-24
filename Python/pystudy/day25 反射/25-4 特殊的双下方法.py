'''
# 反射（重要）
# 函数与方法的区别
# 特殊的双下方法（对源码的研究及以后的开发都有用）
# type与object联系
'''
# 双下方法， 就是 双下划线+方法名+双下划线 的特殊方法
    # 双下方法主要是python源码程序员使用的，我们在开发中尽量不要使用双下方法，
    # 但是深入研究双下方法，更有益于我们阅读源码。

        # object 中有大量的双下方法， 
        # 如果我们定义的内容中使用了双下方法来定义， 
        # 就有可能重写了父类object的同名双下方法，引发问题。
        # 因此 双下方法要慎用。

    # 调用：不同的双下方法有不同的触发方式，
    # 就好比盗墓时触发的机关一样，不知不觉就触发了双下方法，
    # 例如：__init__

# __len__
    # len 一个字符串时，就是触发了字符串从属于的类中定义的__len__ 方法
class A:
    def __len__(self):
        print('hello')
        return 0
b = A()
len(b)  # hello

# 定义一个__len__ ，让对实例化对象执行len() 操作时，返回实例化对象包含的属性数。
class B:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def __len__(self):
        return len(self.__dict__)   
        # 此时len，调用的是哪个len？
        # 将self这个实例化对象执行__dict__ 后，
        # 结果是由内置函数list 实例化生成的对象， 
        # 因此调用的是list类或其父类中定义的__len__。

ob = B('kk',20)
ob.country = 'china'
print(len(ob))      # 3

# __str__
class C:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def __str__(self):
        return f'{self.name}今年{self.age}岁'

k = C('yy',20)
print(k)    # yy今年20岁

# print 触发 __str__
# str() 触发 __str__
o = str(k)
print(o)    # yy今年20岁
print(type(o))  # <class 'str'>


# __repr__
print('我是%s' %(o))    # 我是yy今年20岁
print('我是%r' %(o))    # 我是'yy今年20岁'
# 原形毕露。

class D:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def __repr__(self):
        return f'{self.name}今年{self.age}岁'
kk = D('oo',17)
print(kk)   # oo今年17岁

# repr和 str 很像， 也被print触发。
# 那么str和repr的优先级 ———— str优先级高于repr


# __call__
# 对象名+() 会自动触发对象从属于类或父类的__call__ 方法
class E:
    def __init__(self):
        pass

    def __call__(self):
        print('in __call__')

ee = E()
ee()    # in __call__


# __eq__
class F:
    def __init__(self,a,b):
        self.a = a
        self.b = b

    def __eq__(self,obj):   # 捣乱，相等则false，否则true
        if self.a == obj.a and self.b == obj.b:
            flag = False
        else:
            flag = True
        return flag
ff = F(1,2)
fg = F(1,2)
print(ff == fg) # False
ff = F(2,2)
fg = F(1,1)
print(ff == fg) # True   


# __new__  十分重要。 new一个对象。
# 类名+() 就会产生一个对象，然后对象执行__init__
# __new__ 在内存中开辟一块对象空间，然后将__init__ 执行，创建在对象空间内。


class G:
    def __init__(self):
        self.a = 1
        self.b = 2
        print('in init')
    def __new__(cls,*args,**kwargs):
        print('in new func')
        # return 1
        return object.__new__(G,*args,**kwargs)

gg = G() 
# in new func
# in init

# __item__系列
# 对对象进行字典类操作，会触发__item__系列方法

class J:
    def __init__(self,name):
        self.name = name
    
    def __getitem__(self,item):
        print('aaa')
        print(self.__dict__[item])

    def __setitem__(self,key,value):
        print('bbb')
        self.__dict__[key] = value

    def __delitem__(self,key):
        print('ccc')
        del self.__dict__[key]
        print('ddd')


    def __delattr__(self,item):     # 删除对象要触发的__delattr ， 
        print(f'del {item}了哈！ from delattr')

jj = J('kk')
jj['name']  # 触发__getitem__
# aaa
# kk
# jj['nohave']    # 触发__getitem__ ，尽管并没有nohave这个key
# aaa
# nohave error
jj['nohave'] = 2    # 触发__setitem__
# bbb
print(jj.__dict__)
# {'name': 'kk', 'nohave': 2}
del jj['nohave']    # 触发__delitem__
# ccc
# ddd
print(jj.__dict__)
# {'name': 'kk'}
del jj.name
# del name了哈！ from delattr


# 上下文管理器相关 __enter__、 __exit__

class K:
    def __init__(self,name):
        self.name = name

# k = K('yy')

#with K('yy') as k:  # 逻辑上等同于k = K('yy')， 这是实例化对象的第二种方式
#    pass
# 但是会报错。
# AttributeError: __enter__

class L:
    def __init__(self,name):
        self.name = name
    def __enter__(self):
        print('enter')
        return self    # 不然后面生成的对象无法操作，必须要返回self

    def __exit__(self,exc_type,exc_val,exc_tb):
        print('exit')

with L('yy') as l:  # 实例化对象的第二种方式，必须基于__enter__和__exit__ 两种方法
    print('something')
# 不报错了。
# enter         # __enter__  
# something     # with.... sub clause
# exit          # __exit__ 
print(l)    # <__main__.L object at 0x1027afd00>
print(l.__dict__)   # {'name': 'yy'}


# __iter__
# 是否可迭代。
class M:
    def __init__(self,name):
        self.name = name
    def __iter__(self):
        yield 1
        yield 2
m = M('gg')
print('__iter__' in dir(m))
# True
for i in m:     
    print(i)        # __iter__ 
# 1                 # __iter__中定义的yield
# 2

class N:
    def __init__(self,name):
        self.name = name
    def __iter__(self):
        for i in range(10):
            yield i
n = N('gg')     # n只是一个可迭代对象
print('__iter__' in dir(n))
for i in n:
    print(i)
# 0
# 1
# 2
# 3
# 4
# 5
# 6
# 7
# 8
# 9

# 变为可迭代对象
print('--------')
nn = iter(n)
print(next(nn))
#0
print(next(nn))
#1
print(next(nn))
#2
print(next(nn))
#3
