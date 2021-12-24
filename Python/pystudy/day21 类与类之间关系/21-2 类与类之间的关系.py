# 类与类的关系
#     1.依赖关系
#     2.组合关系（关联组合聚合）

# 关系，肯定是两者及以上的多个之间才能产生的概念。

class A:
    pass

class B:
    pass

# A与B之间各自独立，如何让他们俩发生关系？
# Py中主张三种关系：
#   依赖关系、
#   组合关系（包含：组合、聚合、关联）、
#   继承关系

# 依赖关系（主从关系）
# 依赖关系：将一个类的类名或者对象传给另一个方法中。
'''
class Elephant:
    def __init__(self,name):
        self.name = name
    def open(self):
        print('要打开冰箱门')
    def close(self):
        print('要关上冰箱门')
class Fridge:
    def __init__(self,name):
        self.name = name
    def open_door(self):
        print('冰箱门开了')
    def close_door(self):
        print('冰箱门关了')

ele = Elephant('个个')
fri = Fridge('海尔')
ele.open()
fri.open_door()

# 但是案例中， 大象和冰箱两个类之间的调用是没有关联性的。
'''
class Elephant:
    def __init__(self,name):
        self.name = name
    def open(self,ref1):    # ref1 
        print(f'{self.name}要打开{ref1.name}冰箱门')
        ref1.open_door()    # 调用ref1对象的方法。
    def close(self,ref1):
        print(f'{self.name}要关上{ref1.name}冰箱门')
        ref1.close_door()
class Fridge:
    def __init__(self,name):
        self.name = name
    def open_door(self):
        print(f'{self.name}冰箱门开了')
    def close_door(self):
        print(f'{self.name}冰箱门关了')

ele = Elephant('个个')
fri = Fridge('海尔')
ele.open(fri)   # 将对象作为参数传入，在open方法中调用fri的open_door方法。
# do something.
ele.close(fri)




# 作业：
# 大象执行open方法。显示哪个大象打开了冰箱门，显示哪个冰箱门被打开了。



# 组合
# 组合关系：将一个类的对象封装成另一个类的对象的属性。
# 在py中相当于java的组合、聚合、关联关系
class Boy:
    def __init__(self,name,gf=None):
        self.name = name
        self.gf = gf
    def have_dinner(self):
        if self.gf:
            print(f'{self.name} with {self.gf.name} having dinner.')
            self.gf.shopping(self)  # 把bf生成的对象传给shopping()
        else:
            print(f'eat air de {self.name}')

class Girl:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def shopping(self,bf):  # 传入bf对象，
        print(f'{self.name} and {bf.name} go shopping.')

gg = Girl('YY',17)
kk = Boy('kk',gg)
kk.have_dinner()

# 难点：
# 一个类的方法只能有此类的对象去调用。
# 一个类的方法的第一个self只接受此类的对象。
# 前一天的英雄联盟作业其实就是这个东西。
