'''
1.面向对象的三大特征：封装，继承，多态
2.什么是继承？
3.继承的优点
4.单继承
5.多继承
'''

# 继承
# 专业角度： B继承A类，B就叫做A的子类、派生类。 A叫做B的父类，基类，超类。
# B类及B类对象使用A类的所有的属性以及方法。



# class Person:
#     def __init__(self,name,sex,age):
#         self.name = name
#         self.sex = sex
#         self.age = age
# class Dog:
#     def __init__(self,name,sex,age):
#         self.name = name
#         self.sex = sex
#         self.age = age
# class Cat:
#     def __init__(self,name,sex,age):
#         self.name = name
#         self.sex = sex
#         self.age = age
# 人、猫、狗三个类，都有名字、性别、年龄这三个属性。
# 这样来看，动物，都有名字、性别、年龄这三个属性，
# 我们可以定义一个动物类，再使Person、Dog、Cat继承动物类的属性。

class Animal:
    live = '活的'
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        self.age = age
    def eat(self):
        print('吃')
        print(self)
class Person(Animal):   # 括号里表示继承于。
    pass
class Dog(Animal):
    pass
class Cat(Animal):
    pass
# 继承优点：
#     1.减少代码量
#     2.提升耦合性
#     3.代码规范化

# 单继承： 只有一个父类。使用.调用
    # 子类以及对象，可以调用父类的属性及方法。（也只能调用，不能操作父类的属性及方法。）
        # 从类名执行父类的属性
            # print(Person.__dict__)  #{'__module__': '__main__', '__doc__': None}
            # print(Person.live)  #活的
            # Person.eat(111)     #吃
        # 从对象执行父类的一切
            # p1 = Person('kk','M',29)   # 虽然Person类定义时没指定参数，但是父类有__init__ ，则需要满足init的要求传参。即使所有父类都没有__init__ ，python最顶层也有一个object（也就是类名定义时，不指定父类，则隐藏为(object)）。
            # print(p1.live)  #活的
            # p1.eat()        #吃
            # print(p1.__dict__)  #
            # print(p1)       # 和eat()中的self地址一样。 <__main__.Person object at 0x101448fd0>
        # 子类将父类方法覆盖重写
            # p1 = Person('kk','M',29)
            # # 此时p1 有从父类Animal继承来的方法eat。
            # p1.eat()    # 吃
            # # 这里声明一个p1的eat属性，覆盖继承自父类的方法名
            # p1.eat = '吃吃吃'
            # # 再次调用
            # p1.eat() # 报错。因为先从对象空间找的名字eat并不是方法。
# 如何既要执行父类方法，又要执行子类方法呢？
'''
class Animal:
    live = '活的'
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        self.age = age
    def eat(self):
        print('动物要吃')

class Person(Animal): 
    def __init__(self,hobby):
        self.hobby = hobby
    def eat(self):
        print('人要吃')
'''
# 此时实例化对象Person，传参则只能传一个hobby的位置参数。
'''
# p1 = Person('kk','M',29)  # 报错
p1 = Person('sleep')
print(p1.__dict__)  # {'hobby': 'sleep'}
'''
# 如何让子类和父类都被对象继承？

# 方法一：未用到继承
    # 在子类Person的__init__ 中调用父类Animal.__init__() 方法
'''
        class Person(Animal): 
            def __init__(self,hobby):
                self.hobby = hobby
                Animal.__init__()
            ...
'''
    # 但是调用Animal.__init__() 时需要传参，如何传？
    # 依然使用位置参数。
'''
        class Person(Animal): 
            def __init__(self,name,sex,age,hobby):
                self.hobby = hobby
                Animal.__init__(self,name,sex,age)
            ...
        p1 = Person('kk','M',29,'sleep')
'''

class Animal:
    live = '活的'
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        self.age = age
    def eat(self):
        print('动物要吃')

class Person(Animal): 
    def __init__(self,name,sex,age,hobby):
        self.hobby = hobby
        Animal.__init__(self,name,sex,age)
    def eat(self):
        print('人要吃')

p1 = Person('kk','M',29,'sleep')
print(p1.__dict__)  # {'hobby': 'sleep', 'name': 'kk', 'sex': 'M', 'age': 29}
print(p1.name,p1.sex,p1.age,p1.hobby)   # kk M 29 sleep




# 方法二：继承。super()方法： super().__init__()
'''
        class Person(Animal): 
            def __init__(self,name,sex,age,hobby):
                super(Person,self).__init__(name,sex,age)
                # 可以简写为super().__init__(name,sex,age)
                self.hobby = hobby
            ...
        p1 = Person('kk','M',29,'sleep')
'''
class Animal:
    live = '活的'
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        self.age = age
        print('animal step')
    def eat(self):
        print('动物要吃')

class Person(Animal): 
    def __init__(self,name,sex,age,hobby):
        super(Person,self).__init__(name,sex,age)
        # 可以简写为super().__init__(name,sex,age)
        self.hobby = hobby
        print('person step')
    def eat(self):
        print('人要吃')

p2 = Person('kk','M',29,'sleep')
print(p2.__dict__)  # {'hobby': 'sleep', 'name': 'kk', 'sex': 'M', 'age': 29}

# 利用super() 让eat() 先执行子类eat再执行父类eat

class Animal:
    live = '活的'
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        self.age = age
        print('animal step')
    def eat(self):
        print('动物要吃')

class Person(Animal): 
    def __init__(self,name,sex,age,hobby):
        super(Person,self).__init__(name,sex,age)
        # 可以简写为super().__init__(name,sex,age)
        self.hobby = hobby
        print('person step')
    def eat(self):
        print('人要吃')
        super().eat()

p3 = Person('kk','M',29,'sleep')
p3.eat()
# 人要吃
# 动物要吃


'''
# 1
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)

class Foo(Base):
    pass
obj = Foo(123)
obj.func1() # 123 运⾏的是Base中的func1  

# 2      
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)
class Foo(Base):
    def func1(self):
        print("Foo. func1", self.num)
obj = Foo(123)
obj.func1() # Foo. func1 123 运⾏的是Foo中的func1       

# 3         
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)
class Foo(Base):
    def func1(self):
        print("Foo. func1", self.num)
obj = Foo(123)
obj.func1() # Foo. func1 123 运⾏的是Foo中的func1     
# 4
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)
        self.func2()
    def func2(self):
        print("Base.func2")
class Foo(Base):
    def func2(self):
    print("Foo.func2")
obj = Foo(123)
obj.func1() # 123 Foo.func2 func1是Base中的 func2是⼦类中的 
# 再来
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)
        self.func2()
    def func2(self):
        print(111, self.num)
class Foo(Base):
    def func2(self):
        print(222, self.num)
lst = [Base(1), Base(2), Foo(3)]
for obj in lst:
    obj.func2() # 111 1 | 111 2 | 222 3

# 再来
class Base:
    def __init__(self, num):
        self.num = num
    def func1(self):
        print(self.num)
        self.func2()
    def func2(self):
        print(111, self.num)
class Foo(Base):
    def func2(self):
        print(222, self.num)
lst = [Base(1), Base(2), Foo(3)]
for obj in lst:
 obj.func1() # 那笔来吧. 好好算
 
 
 '''