
# 单例模式
# python的设计模式之一。
# 单例模式：一个类只允许实例化一个对象。

class H:
    pass
obj1 = H()
obj2 = H()
obj3 = H()
print(obj1,obj2,obj3)
# <__main__.H object at 0x104b037c0>
# <__main__.H object at 0x104b03790> 
# <__main__.H object at 0x104b03760>

# 能不能让类实例化对象之后，再次执行实例化，则直接返回第一次实例化的对象地址？
class I:
    __instance = None
    def __new__(cls,*args,**kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)    # 非则new一个对象
        return cls.__instance
obj1 = I()
obj2 = I()
obj3 = I()
print(obj1,obj2,obj3)
# <__main__.I object at 0x102ac25e0> 
# <__main__.I object at 0x102ac25e0> 
# <__main__.I object at 0x102ac25e0>

