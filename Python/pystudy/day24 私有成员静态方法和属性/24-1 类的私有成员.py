'''
class A:
    
    company_name = '老男孩教育'  # 静态变量(静态字段)
    __iphone = '1353333xxxx'  # 私有静态变量(私有静态字段)


    def __init__(self,name,age): #特殊方法

        self.name = name  #对象属性(普通字段)
        self.__age = age  # 私有对象属性(私有普通字段)

    def func1(self):  # 普通方法
        pass

    def __func(self): #私有方法
        print(666)


    @classmethod  # 类方法
    def class_func(cls):
        """ 定义类方法，至少有一个cls参数 """
        print('类方法')

    @staticmethod  #静态方法
    def static_func():
        """ 定义静态方法 ，无默认参数"""
        print('静态方法')

    @property  # 属性
    def prop(self):
        pass
'''



# 类的私有成员(私有类属性及私有方法，私有对象属性)
    # 1.在类的内部可以访问
    # 2.类的外部不能访问
    # 3.派生类也不能访问父类的私有成员
    # 适用于密码、重要数据等不想被其他引用的属性\方法
# python所有的私有成员都是纸老虎，并不安全。
    # 实际上通过__dict__ 来查看，是可以看到私有成员只是被内部重命名了。（_类名+对象名）
    # 因此，私有成员不要去引用，约定俗成的君子协议罢了。

# 以下用私有类属性来验证。
'''
class A:
    name = 'kk' # 公有成员
    __name = 'yy'   # 私有成员

    def func(self):
        print(self.name)
        print(self.__name)

obj = A()
obj.func()
    # kk
    # yy
# 结论：在类的内部可以访问

print(obj.name)
    # kk
print(obj.__name)
    # AttributeError: 'A' object has no attribute '__name'
print(A.name)
    # kk
print(A.__name)
    # AttributeError: type object 'A' has no attribute '__name'
# 结论：类的外部不能访问。


class B(A):
    pass
obj2 = B()
print(obj2.name)
    # kk
print(obj2.__name)
    # AttributeError: 'B' object has no attribute '__name'
# 结论：派生类也不能访问父类的私有成员。
'''

# 私有对象属性：只能在类内部使用 的实际示意
'''
class Aa:
    def __init__(self,name,pwd):
        self.name = name
        self.__pwd = pwd
    def md5(self):
        self.__pwd = self.pwd + '123'
obj = Aa('kk','12345')
print(obj.name)
# kk
print(obj.__pwd)
# AttributeError: 'Aa' object has no attribute '__pwd'
'''

# python所有的私有成员都是纸老虎，并不安全。
class T:
    name = 'kk'
    __name = 'yykk'

    def __func(self):
        print('in __func')

print(T.__dict__)
    # {'__module__': '__main__', 
    #   'name': 'kk', 
    # '_T__name': 'yykk', 
    # '_T__func': <function T.__func at 0x1035d74c0>, 
    # '__dict__': <attribute '__dict__' of 'T' objects>, 
    # '__weakref__': <attribute '__weakref__' of 'T' objects>, 
    # '__doc__': None}

# 可以看到，通过__dict__ 方法查看类内所有成员后，可以看到，__name 和__func 两个私有成员只是被重命名了……
print(T._T__name)
    # yykk
T._T__func(11)
    # in __func
# 因此，私有成员不要去引用，君子协议罢了。
