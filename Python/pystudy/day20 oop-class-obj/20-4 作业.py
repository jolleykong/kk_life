'''
1.完成下列功能：
    1. 创建一个人类Person，在类中创建3个静态变量：
        animal = '高级动物'
        soul = '有灵魂'
        language = '语言'
    2. 在类中定义3个方法：吃饭睡觉工作
    3. 在类中的__init__ 方法中。给对象封装5个属性：国家，姓名，性别，年龄，身高
    4. 实例化4个人类对象：
        - 第一个人类对象p1属性为：中国，alex，未知，42，175
        - 第二个人类对象p2属性为：英国，blex，男，17，190
        - 第三个人类对象p3属性为：三体人，没名字，未知，未知，10米
        - 第四个人类对象p4属性为：p1的国籍，p2的名字，p3的性别，p2的年龄，p1的身高
    5. 通过p1对象执行吃饭方法，方法里面打印：alex在吃饭
    6. 通过p2对象执行吃饭方法，方法里面打印：blex在吃饭
    7. 通过p3对象执行吃饭方法，方法里面打印：p3的名字在吃饭
    8. 通过p1对象找到Person的静态变量 animal
    9. 通过p2对象找到Person的静态变量 soul
    10. 通过p3对象找到Person的静态变量 language
'''
class Person:
    animal = '高级动物'
    soul = '有灵魂'
    language = '语言'

    def __init__(self,country,name,sex,age,height):
        self.name = name
        self.country = country
        self.sex = sex
        self.age = age
        self.height = height

    def eat(self):
        print(f'{self.name}在吃饭。')

    def work(self):
        print(f'{self.name}在工作。')

    def sleep(self):
        print(f'{self.name}在睡觉。')

p1 = Person('中国','alex','未知',42,175)
p2 = Person('英国','blex','男',17,190)
p3 = Person('三体人','没名字','未知','未知','10米')
p4 = Person(p1.country, p2.name, p3.sex, p2.age, p1.height)

p1.eat()
p2.eat()
p3.eat()
p4.eat()

print(p1.animal)
print(p2.soul)
print(p3.language)
print(p4.__dict__)

'''
2. 通过自己创建类，实例化对象
    在终端输出如下信息：
    小明，10岁，男，上山去砍柴
    小明，10岁，男，开车去东北
    小明，10岁，男，最爱大保健
    老张，11岁，女，最爱睡觉
    老王，99岁，男，最爱穿童装
    ……
'''
class Freedom:
    def __init__(self, name, age, sex, info):
        self.name = name
        self.age = age
        self.sex = sex
        self.info = info
        print(f'{self.name},{self.age}岁,{self.sex},{self.info}')

q1 = Freedom('小明',10,'男','上山去砍柴')
q2 = Freedom('小明',10,'男','开车去东北')
q3 = Freedom('小明',10,'男','最爱大保健')
q4 = Freedom('老张',11,'女','最爱睡觉')
q5 = Freedom('老王',99,'男','最爱穿童装')


'''
3. 设计一个汽车类。
    要求：
        汽车的公共属性为：动力驱动，具有四个或以上车轮，主要用途载运人员或货物
        汽车的功能：run，transfer
        具体的汽车的不同属性：颜色，车牌，类型（越野，轿车，货车）
'''
class Auto:
    drive = '动力驱动'
    wheel = 4
    purpose = '载运'

    def __init__(self,color,number,type):
        self.color = color
        self.number = number
        self.type = type
        print(f'一辆{self.color}的{self.type}正在开来。')

    def run(self):
        if self.type == '货车':
            text = '拉着货跑了'
        else:
            text = '拉着人跑了'
        print(f'{self.color}的{self.type}{text}!')


    def transfer(self):
        if self.type == '货车':
            text = '装满了货物'
        else:
            text = '坐满了美女'
        print(f'{self.color}的{self.type}{text}!')

c1 = Auto('红色','12345','货车')
c1.run()
c2 = Auto('黄色','京A00000','敞篷跑车')
c2.transfer()
c3 = Auto('绿色','京A989c6','轿车')
c3.transfer()
c4 = Auto('黑色','京临25041','越野车')
c4.run()
c5 = Auto('白色','没有号码','火车')
c5.run()


'''
4. 模拟英雄联盟写一个游戏人物的类
    要求：
        1.创造一个GameRole类
        2.构造方法中给对象封装name，ad（攻击力），hp（血量） 三个属性
        3.创建一个attack方法，此方法是实例化两个对象，互相攻击的功能：
            例如：
                实例化一个对象，盖伦，ad为10，hp为100
                实例化另一个对象，建好，ad为20，hp为80
                盖伦通过attack方法攻击剑豪，此方法要完成’谁攻击了谁，谁掉了多少血，谁还剩多少血‘的提示功能。


'''
import random

class GameRole:

    def __init__(self,name,ad,hp):
        self.name = name
        self.ad = ad
        self.hp = hp
        print(self.name,self.ad,self.hp)

    def attack(self,targetname):
        player1 = self
        player2 = targetname

        print(f'{player1.name}和{player2.name}出现在了战场。')
        players = ['player1','player2']

        # 随机取一个先手
        random_choice = random.randint(0,100) % 2 
        first = players[random_choice]
        players.remove(first)
        second = players[0]
        first = eval(first)
        second = eval(second)

        acts = ['打了','亲了','咬了','捅了','捏了','拉了','撞了']
        print(f'☆{first.name}☆ {random.choice(acts)} {second.name} 一下，{second.name} 损失 {first.ad} 点血！{second.name}剩余 {second.hp-first.ad} 点血。')
        second.hp = second.hp - first.ad


GL = GameRole('盖伦',10,100)
JH = GameRole('剑豪',20,80)
# print(GL.__dict__)
# print(JH.__dict__)
# print(GL.ad)
while GL.hp > 0 and JH.hp >0:
    GL.attack(JH)
if GL.hp == 0:
    dead = GL.name
elif JH.hp == 0:
    dead = JH.name
print(f'{dead}死了。')