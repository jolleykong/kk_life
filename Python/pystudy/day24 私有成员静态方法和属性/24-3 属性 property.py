# 属性 property ， 是一种特殊的属性。
# 访问它时会执行一段功能（函数），然后返回值。

# 一些情况下 方法名看起来像属性时， 就可以用property来将方法名伪装成属性。

# 计算BMI
# BMI听起来像是一个属性而非方法。将其做成一个属性更便于理解。
# 成人的BMI数值
    # 偏瘦 低于18.5
    # 正常 18.5 ~ 23.9
    # 过重 24 ~ 27
    # 肥胖 28 ~ 32
    # 非常肥胖 大于32
    # BMI 体质指数 = 体重（kg） / 身高^2(m)

class Human:
    def __init__(self,name,age,height,weight):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
    def bmi(self):
        bmi = self.weight / self.height ** 2
        return bmi

me = Human('kk',30,1.93,85)
print(me.bmi())
# 22.819404547773097

# 上面的实现没有任何问题，很标准
# 但是有一个感觉有些奇怪，那就是 在逻辑上，BMI应该跟name，age，height等一样，属于”属性“，
# 但在上面的实现中，BMI被“调用”， 这有些不符合逻辑。

# 将BMI方法做成property 
class Human2:
    def __init__(self,name,age,height,weight):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
    @property           # 就加这么个东西就行了。
    def bmi(self):
        bmi = self.weight / self.height ** 2
        return bmi

me2 = Human2('kk',30,1.93,85)
me2.bmi  # 可以直接调用。
# 22.819404547773097
print(me2.bmi,me2.name)  # 也可以就像调用其他属性一样。
# 22.819404547773097 kk

# 尝试像操作属性一样继续操作bmi
# me2.bmi = 777   # 报错


# property将执行一个函数需要 函数名() 直接变成 函数名执行
# property将动态方法伪装成了一个属性，在代码层面上没有提升，但是看起来会更加合理。


# property 是一个组合
class Foo:
    @property
    def aaa(self):      # 三个方法同名，配合三个装饰器，就是一个组合。
        print('get')
    
    @aaa.setter             # 依赖@property
    def aaa(self,value):
        print('set')
        print(value)

    @aaa.deleter            # 依赖@property
    def aaa(self):
        print('delete')

obj = Foo()
obj.aaa
    # get
obj.aaa = 777
    # set
    # 777   # print(value) 输出。
obj.aaa # 此时再查询这个伪装的属性，依然是get。 
        # 因此可以知道，上面这个命令并不改变aaa原本的值，
        # 而是去调用由aaa.setter 装饰器装饰的函数。

del obj.aaa 
    # delete , print('delete')输出。
    # 跟 setter一样， 这个是在对伪装属性执行del时，去调用由aaa.deleter 装饰器装饰的函数。



# 设置组合的两种方式：
    # 1.装饰器
    # 2.实例化对象