# 类的其他方法
# 通常都是实例方法
# 还有其他两个： 类方法、静态方法


# 静态方法
class C:
    # 实例方法
    def func(self):
        print(f'常见的实例方法，{self}')
    
    # 类方法。顾名思义：一般是通过类名去调用的方法。
    @classmethod
    def cls_func(cls):  # 约定俗成为cls，不是self噢
        print(f'类方法,{cls}')

    # 静态方法。不依赖对象不依赖类，其实就是普通的函数。
    # 但是静态方法也需要使用类来调用。
    # 跟在类外定义的函数一毛一样，但是为什么在类中定义呢？ 方便管理，保证规范性，按照功能区划分规划。。
        # 类中包含所有相关功能的定义，静态方法不依赖类中任何内容罢了。
    @staticmethod
    def static_func():
        print('静态方法')

C.static_func()