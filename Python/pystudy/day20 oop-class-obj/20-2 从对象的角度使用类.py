# 4. 从对象的角度使用类
# 4. 实例化一个对象
    # - 实例化对象发生了三件事
    # - 对象调用对象的属性
    # - 对象调用类中的属性
    # - 对象调用类中的方法


class Student: 
    "I'm doc part This is a class named Student."
    daily = '学习'
    mission = '考试'

    def work(self):
        print('每天上课')
        
    def homework(self):
        print('写作业')


#   实例化一个对象
    # 类名加上() 就叫做实例化过程。会实例化一个对象出来。
obj = Student()
print(obj)  # obj在这里就是一个对象，也叫一个实例。 
            # <__main__.Student object at 0x104744fa0>

obj1 = Student()
print(obj1) # <__main__.Student object at 0x100bacf40> 

    # 两次实例化的地址不同，说明这obj和obj1不是一个对象噢。
    # 但是当前两个print() 动作都只输出了内存地址。

    # 为类Student1定义__init__ 方法
class Student1: 
    "I'm doc part This is a class named Student1."
    daily = '学习'
    mission = '考试'
    
    def __init__(self):
        print('aaa')

    def work(self):
        print('每天上课')
        
    def homework(self):
        print('写作业')

obj = Student1()
print(obj)  # aaa
            # <__main__.Student1 object at 0x102814cd0>
            # 如果Student定义了__init__ ，则会执行__init__ 的动作。未指定则无输出。

obj1 = Student1()
print(obj1) # aaa
            #<__main__.Student1 object at 0x102814fa0>
            # 将print(self) 加入到__init__中之后，可以看到print(self) 的内存地址和当前对象内存地址是一样的。




    # 再看一下__init__方法执行时，位置参数self内部传了什么东西进去？


class Student2: 
    "I'm doc part This is a class named Student1."
    daily = '学习'
    mission = '考试'
    
    def __init__(self):
        print('aaaa')
        print(self)
    
    def work(self):
        print('每天上课')
    
    def homework(self):
        print('写作业')


obj = Student2()
            # aaaa  (print aaa , in __init__)
            # <__main__.Student2 object at 0x102b65550> (print self , self的内存地址)
print(obj) 
            # <__main__.Student2 object at 0x102b65550> (print obj , obj的内存地址)
    
    # 将print(self) 加入到__init__中之后，可以看到print(self) 内容和当前对象内存地址是一样的。



# 实例化对象发生了三件事
    # 1.在内存中创建一个【对象空间】
    # 2.自动执行类中定义的__init__方法，并且将对象空间传给self参数。（相当于执行了__init__定义。）
    # 3.执行__init__方法里面的代码，给对象空间封装其属性(变量). （相当于给对象空间里调用了__init__）

# 举例证明三件事：
class Student3: 
    daily = '学习'
    mission = '考试'
    
    def __init__(self):
        self.n='kk'     # 封装2个属性。
        self.sex='M'
    
    def work(self):
        self.work = '自由人'
        print('每天上课')
    
    def homework(self):
        print('写作业')

obj = Student3()
print(obj.__dict__) # {'n': 'kk', 'sex': 'M'}

#     - 对象调用对象的属性
# 查对象的属性
print(obj.daily)    # 学习
print(obj.mission)  # 考试

# 增对象的属性
obj.hobby = 'sleep'
print(obj.__dict__) # {'n': 'kk', 'sex': 'M', 'hobby': 'sleep'}

# 改对象的属性
print(obj.daily) # 学习
obj.daily = 'sleep'
print(obj.__dict__) # {'n': 'kk', 'sex': 'M', 'hobby': 'sleep', 'daily': 'sleep'}
print(obj.daily) # sleep

# 删对象的属性
del obj.daily
print(obj.daily)    # 学习.为什么还有学习？此时再del obj.daily会报错。因为daily在类空间里。对象只能操纵对象空间里的内容。
print(obj.__dict__) # {'n': 'kk', 'sex': 'M', 'hobby': 'sleep'}
del obj.hobby
print(obj.__dict__) # {'n': 'kk', 'sex': 'M'}
# print(obj.hobby)  # error


#     - 对象调用类中的属性
# 查看类中的属性。对象对类中的属性只能做查看操作。
obj_forc = Student3()
print('obj_forc',obj_forc.daily)    # obj_forc 学习
print('obj_forc',obj_forc.__dict__) # obj_forc {'n': 'kk', 'sex': 'M'} 。可以看到在对象空间里没有daily，因此查询到的是类空间的daily。尽管尝试修改，也只是在对象空间中创建一个daily的属性罢了。


#     - 对象调用类中的方法
print('对象调用类中的方法',obj_forc.__dict__)       # 对象调用类中的方法 {'n': 'kk', 'sex': 'M'}
obj_forc.work()     # 每天上课  这是类空间中的方法被对象obj_forc调用。具体可以看下一行输出
print('对象调用类中的方法',obj_forc.__dict__)       # 对象调用类中的方法 {'n': 'kk', 'sex': 'M', 'work': '自由人'} 。 这一行中多了work=自由人， 这是在class Student3中定义方法work时的动作。


    # 进一步， 可以给work传参。
class Student4: 
    daily = '学习'
    mission = '考试'
    
    def __init__(self):
        self.n='kk'     # 封装2个属性。
        self.sex='M'
    
    def work(self,work):
        self.work = work
        print('每天上课')
    
    def homework(self):
        print('写作业')

obj_work = Student4()
print(obj_work.__dict__)    # {'n': 'kk', 'sex': 'M'}
obj_work.work('啦啦啦')
print(obj_work.__dict__)    # {'n': 'kk', 'sex': 'M', 'work': '啦啦啦'}


# 5. 什么是self？
# self就是类中方法的第一个位置参数，
#   如果通过类执行此方法，必须手动传参给self。
#   如果通过对象去执行此方法，那么解释器会自动将此对象空间（对象地址）当做实参传给self。
    # 利用self对象空间可以为所欲为，self是这个特殊的关键字。
# 约定俗成，类中的方法的第一个参数都设置成self。也可以设置到别的位置上。

# 6. 一个类可以实例化多个对象
class Student6: 
    daily = '学习'
    mission = '考试'
    
    def __init__(self,name,age,sex,hobby):
        self.name = name
        self.sex = sex
        self.age = age
        self.hobby = hobby
    
    def work(self):
        print('每天上课')
    
    def homework(self):
        print('写作业')

obj_kk = Student6('kk',30,'M','sleep')
obj_yy = Student6('yy',17,'M','run')
print(obj_kk.__dict__)  # {'name': 'kk', 'sex': 'M', 'age': 30, 'hobby': 'sleep'}
print(obj_yy.__dict__)  # {'name': 'yy', 'sex': 'M', 'age': 17, 'hobby': 'run'}

obj_kk.work()       # 每天上课   这是调用类空间里的方法。