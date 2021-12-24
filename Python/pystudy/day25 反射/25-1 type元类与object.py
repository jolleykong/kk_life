'''
# 反射（重要）
# 函数与方法的区别
# 特殊的双下方法（对源码的研究及以后的开发都有用）
# type与object联系
'''

class A:
    pass

# py中一切皆为对象，因此类A也是一个对象。
# 那么类A是从哪实例化来的呢？——objct。

print(type('abc'))  # <class 'str'> 也就是'abc'是从str 类实例化出来的。

# type() ：真实功能是 获取对象从属于的类 。

print(type(A))  # <class 'type'>， 说明A是从type这个类实例化出来的。

print(type(str))    # <class 'type'>

print(type(list))    # <class 'type'>

# 综上，python中一切皆为对象，类在某种意义上也是一个对象。
    # python中由自己定义的类以及大部分内置类，都是由type这个元类实例化得来的。
    # 也有少部分不是由type实例化得来的，这是例外情况，如工厂类等。少见。


# type 与 objct 的关系
print(type(object))     # <class 'type'>
    # object类 是type类的一个实例。
print(issubclass(type,object))  # True
    # object类 是 type类的父类。
print(issubclass(object,type))  # False

# object类 是type类的一个实例 && object类 是 type类的父类。
    # 有些乱，但是到此为止。 鸡蛋和鸡之间的关系了。
    