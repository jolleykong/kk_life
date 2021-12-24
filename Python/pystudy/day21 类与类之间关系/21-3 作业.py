'''
1.创建三个游戏人物，分别是：
    仓晶晶，女，18，ad为20，血量200
    东尼木木，男，20，ad为30，血量150
    波多多，女，19，ad为50，血量80
2.创建三个游戏武器，分别是：
    平底锅，ad为20
    斧子，ad为50
    双节棍，ad为65
3.创建三个游戏摩托车，分别是
    小踏板，速度60
    雅马哈，速度80
    宝马，速度120
完成下列需求（利用武器打人掉的血量为武器的ad+人的ad）：
    1.仓晶晶骑着小踏板开着60速度的车行驶在赛道上。
    2.东尼木木骑着宝马开着120速度的车行驶在赛道上。
    3.波多多骑着雅马哈开着80速度的车行驶在赛道上。
    4.仓晶晶赤手空拳打了波多多20点血，波多多还剩xx血。
    5.东尼木木赤手空拳打了波多多30点血，波多多还剩xx血。
    6.波多多利用平底锅打了仓晶晶，仓晶晶还剩xx血。
    7.仓晶晶骑着宝马打了骑着小踏板的东尼木木一双截棍，东尼木木哭了，还剩xx血。
    8.波多多骑着小踏板打了骑着雅马哈的东尼木木一斧子，东尼木木哭了，还剩xx血。
'''
class Role:
    def __init__(self,name,sex,ad,hp):
        self.name = name
        self.sex = sex
        self.ad = ad
        self.hp = hp
        self.weapon = None
        self.moto = None
        # 个人总ad
        self.total_ad = self.ad

    def get_weapon(self,weapon):
        self.weapon = weapon
        self.weapon_ad = weapon.ad
        # 获得武器后，刷新个人总ad
        self.total_ad = self.ad + self.weapon_ad

    def get_moto(self,moto):
        self.moto = moto
        # moto的速度目前打算直接通过对象引用速度。不声明了。
        # self.ride(moto)

    def rmv_weapon(self):
        pass

    def rmv_moto(self):
        pass

    def list_weapon(self):
        print(self.weapon.__dict__)

    def list_moto(self):
        print(self.moto.__dict__)

    # 骑车。调用后，如有获得摩托车，则打印“骑着xxx”，如没有交通工具，则不显示任何内容。
    def ride(self):
        if self.moto:
            print(f'{self.name}骑着{self.moto.name}开着{self.moto.speed}速度的车行驶在赛道上。')

    # 打人
    def hit(self,target,isride=0):  # 也可以在这里定义是否携带武器。不过感觉这样没啥意义，没做。
        # 计算被击中者损失后的生命值
        target.hp = target.hp - self.total_ad
        # 判断是否骑车
        # 骑车，则显示骑xx的角色名
        if isride == 1:
            if self.moto:
                self_info = '骑着' + self.moto.name + '的' + self.name
            if target.moto:
                target_info = '骑着' + target.moto.name + '的' + target.name
            # 加这不太合适，但是符合题意的前提下，打哭了的显示，是在显式指定骑车的状态下才显示的。
            target_action = target.name + '哭了，'
        # 未显式指定骑车，则只显示角色名
        else :
            self_info = self.name
            target_info = target.name
            target_action = target.name

        # 判断击打动作，有武器则为使用武器名，否则为赤手空拳
        if self.weapon:
            action = '用' + self.weapon.name
        else:
            action = '赤手空拳'

        print(f'{self_info}{action}打了{target_info}{self.total_ad}点血，{target_action}还剩{target.hp}血。')




class Weapon:
    def __init__(self,wea_name,wea_ad):
        self.name = wea_name
        self.ad = wea_ad

class Moto:
    def __init__(self,moto_name,moto_speed):
        self.name = moto_name
        self.speed = moto_speed

r_cjj = Role('仓晶晶','女',20,200)
r_dnmm = Role('东尼木木','男',30,150)
r_bdd = Role('波多多','女',50,80)

w_pdg = Weapon('平底锅',20)
w_fuz = Weapon('斧子',50)
w_sjg = Weapon('双节棍',65)

moto_xtb = Moto('小踏板',60)
moto_ymh = Moto('雅马哈',80)
moto_bmw = Moto('宝马',120)

# 1.仓晶晶骑着小踏板开着60速度的车行驶在赛道上。
r_cjj.get_moto(moto_xtb)
r_cjj.ride()
# 2.东尼木木骑着宝马开着120速度的车行驶在赛道上。
r_dnmm.get_moto(moto_bmw)
r_dnmm.ride()
# 3.波多多骑着雅马哈开着80速度的车行驶在赛道上。
r_bdd.get_moto(moto_ymh)
r_bdd.ride()
# 4.仓晶晶赤手空拳打了波多多20点血，波多多还剩xx血。
r_cjj.hit(r_bdd)
# 5.东尼木木赤手空拳打了波多多30点血，波多多还剩xx血。
r_dnmm.hit(r_bdd)
# 6.波多多利用平底锅打了仓晶晶，仓晶晶还剩xx血。
r_bdd.get_weapon(w_pdg)
r_bdd.hit(r_cjj)
# 7.仓晶晶骑着宝马打了骑着小踏板的东尼木木一双截棍，东尼木木哭了，还剩xx血。
r_cjj.get_weapon(w_sjg)
r_cjj.get_moto(moto_bmw)
r_dnmm.get_moto(moto_xtb)
r_cjj.hit(r_dnmm,1)
# 8.波多多骑着小踏板打了骑着雅马哈的东尼木木一斧子，东尼木木哭了，还剩xx血。
r_bdd.get_moto(moto_xtb)
r_bdd.get_weapon(w_fuz)
r_dnmm.get_moto(moto_ymh)
r_bdd.hit(r_dnmm,1)


# r_bdd.list_moto()
# r_bdd.list_weapon()


'''
2.定义一个类，计算圆的周长和面积

class Cycle:
    
    def __init__(self,r):
        self.r = r
        self.Pi = 3.14
    def zhouchang(self):
        C = 2 * self.Pi * self.r
        print(f'{self.r}为半径的圆周长为{C}')
        return C

    def mianji(self):
        S = self.Pi * self.r ** 2
        print(f'{self.r}为半径的圆面积为{S}')
        return S

cy = Cycle(5)
cy.zhouchang()
cy.mianji()
'''
'''
3.定义一个圆环类，计算圆环的周长和面积

class Ring:
    def __init__(self,br,sr=0):
        self.br = br
        self.sr = sr
        self.Pi = 3.14

    def zhouchang(self):
        bC = 2 * self.Pi * self.br
        sC = 2 * self.Pi * self.sr
        print(f'大圆周长为{bC},小圆周长为{sC}')
        return bC,sC

    def mianji(self):
        bS = self.Pi * self.br**2
        sS = self.Pi * self.sr**2
        S = bS - sS
        print(f'圆环面积为{S}')
        return S

ri = Ring(6,5)
ri.zhouchang()
ri.mianji()
'''