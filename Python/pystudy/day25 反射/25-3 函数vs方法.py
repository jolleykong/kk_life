'''
# 反射（重要）
# 函数与方法的区别
# 特殊的双下方法（对源码的研究及以后的开发都有用）
# type与object联系
'''
# 总结：函数都是显性传参，方法都是隐性传参！

def func1():
    pass

class A:
    def func(self):
        pass
# 通过打印函数名的方式 ，来区别什么是方法，什么是函数。
print(func1)    # 函数就是函数。function
    # <function func1 at 0x1049440d0>  
print(A.func)   # 通过类名调用类中的实例方法， 叫函数。function
    # <function A.func at 0x104eaf550>
obj = A()
print(obj.func) # 通过对象调用的类中的实例方法，叫方法 method
    # <bound method A.func of <__main__.A object at 0x102c9da30>>



# 借助模块 判断是方法还是函数
from types import FunctionType  # 函数类
from types import MethodType    # 方法类
print(isinstance(func1,FunctionType)) 
    # True ,func1 是 函数类 的派生
print(isinstance(A.func,FunctionType)) 
    # True ,通过类调用的方法，是函数类的派生
print(isinstance(A.func,MethodType)) 
    # False
print(isinstance(obj.func,MethodType)) 
    # True ,通过对象调用的方法，是方法类的派生

# 总结：函数都是显性传参，方法都是隐性传参！
    # python中一切皆对象，类在某种意义上也是一个对象，python中自定义的类以及大部分内置类，都是由type元类（构建类）实例化得来的，
    # python中一切皆对象，函数在某种意义上也是一个对象，函数这个对象是从FunctionType这个类实例化出来的。
    # python中一切皆对象，方法在某种意义上也是一个对象，方法这个对象是从MethodType这个类实例化出来的。

# 函数就是函数。function
# 通过类名调用类中的实例方法， 叫函数。function
# 通过对象调用的类中的实例方法，叫方法 method

# Java中只有方法， C中只有函数， C++取决于是否在类中， Python看传参！（因为有静态方法）