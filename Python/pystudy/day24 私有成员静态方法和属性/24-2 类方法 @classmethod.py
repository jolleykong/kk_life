# 类的其他方法
# 通常都是实例方法
# 还有其他两个： 类方法、静态方法

# 类方法：通过类名去调用的方法，并且自动将类名地址传给cls。也可以通过对象调用，但传cls的地址还是类名地址。

class A:
    # 实例方法
    def func(self):
        print(f'常见的实例方法，{self}')
    
    # 类方法。顾名思义：一般是通过类名去调用的方法。
    @classmethod
    def cls_func(cls):  # 约定俗成为cls，不是self噢
        print(f'类方法,{cls}')

# 类方法调用
A.cls_func()    # 和实例方法的区别是，通过类名调用方法，不需要传参。
    # 类方法,<class '__main__.A'>

A.func(111) # 通过类名调用实例方法，必须要传参self才能执行。

obj = A()
obj.cls_func()
    # 类方法,<class '__main__.A'> .
    # 可以看到，cls始终传的是类名
    # 而对象方法中self始终传的是类名地址（见下面这个obj.func()调用）
obj.func()
    # 常见的实例方法，<__main__.A object at 0x100354f10>

# 通过cls拿到类名有什么用？
    # 有类名就可以用来实例化对象！
        # 就可以在class A的cls_func中直接以cls() 的方式实例化对象
    # 可以通过类名操作类的属性
class B:
    # 实例方法
    def func(self):
        print(f'常见的实例方法，{self}')
    
    # 类方法。顾名思义：一般是通过类名去调用的方法。
    @classmethod
    def cls_func(cls):  # 约定俗成为cls，不是self噢
        print(f'类方法,{cls}')
        obj = cls()
        print(obj)
print('-----')
B.cls_func()
    # 类方法,<class '__main__.B'>
    # <__main__.B object at 0x100ab9b50>

# 创建学生类，只要实例化一个对象，写一个类方法，统计一下具体实例化了多少个学生。

class Student:
    count = 0

    def __init__(self,name,sex,age,id):
        self.name = name
        self.sex = sex
        self.age = age
        self.id = id
        Student.tongji()

    @classmethod
    def tongji(cls):
        cls.count += 1      # 类中定义的count。

s1 = Student('kk','M',20,'1')
s2 = Student('kk','M',20,'1')
s3 = Student('kk','M',20,'1')
s4 = Student('kk','M',20,'1')
s5 = Student('kk','M',20,'1')
s6 = Student('kk','M',20,'1')
print(Student.count)    # 6


