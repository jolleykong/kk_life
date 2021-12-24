'''
1. 简答题
    1.面向对象的三大特性是什么？
    2.什么是面向对象的新式类？什么是经典类？
    3.面向对象为什么要有继承？继承的好处是什么？
    4.面向对象中super的作用。

2.代码题
class A:
    def func(self):
        print('in A')
class B:
    def func(self):
        print('in B')
class C(A,B):
    def func(self):
        print('in C')   

改动上面代码，完成下列需求：对C类实例化一个对象c1，执行c1.func()
    1.让其执行C类中的func
    2.让其执行A类中的func
    3.让其执行B类中的func
    4.让其既执行C类中的func，又执行A类中的func
    5.让其既执行C类中的func，又执行B类中的func

3.下面代码的执行结果是什么？为啥

class Parent:
    def func(self):
        print('in Parent func')

    def __init__(self):
        self.func()

class Son(Parent):
    def func(self):
        print('in Son func')

son1 = Son()




4. 

class A:
    name = []

p1 = A()
p2 = A()
p1.name.append(1)
# p1.name, p2.name, A.name 分别是什么？
    # p1.name = [1]
    # p2.name = []
    # A.name = []

p1.age=12
# p1.age, p2.age, A.age 分别是什么？为什么？




5.写出下列代码执行结果：
class Base1:
    def f1(self):
        print('base1.f1')
    def f2(self):
        print('base1.f2')
    def f3(self):
        print('base1.f3')
        self.f1()

class Base2:
    def f1(self):
        print('base2.f1')

class Foo(Base1,Base2):
    def f0(self):
        print('foo.f0')
        self.f3()

obj = Foo()
obj.f0()
# foo.f0
# base1.f3
# base1.f1

MRO --> Foo,Base1,Base2. 先找foo，未找到则去找base1，继续未找到则去找base2.
所以base1.f1优先级高于base2.f1



6.看代码写结果

'''

class A:
    name = []

p1 = A()
p2 = A()
p1.name.append(1)
# p1.name, p2.name, A.name 分别是什么？
    # p1.name = [1]
    # p2.name = [1]
    # A.name = [1]
print(p1.name,p2.name,A.name)
print(p1,p2)
print(p1.name is p2.name)
print(p1.name is A.name)    # True

p1.age=12
# p1.age, p2.age, A.age 分别是什么？为什么？
