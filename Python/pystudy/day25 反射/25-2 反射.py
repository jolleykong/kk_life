'''
# 反射（重要）
# 函数与方法的区别
# 特殊的双下方法（对源码的研究及以后的开发都有用）
# type与object联系
'''

# 反射： 程序对自己内部代码的一种自省方式。
# 是通过字符串去操作对象的方式。

# 一切皆对象， 4个维度。 反射也只能用于这4个维度。
    # 实例对象  （很少）
    # 类    （最常用）
    # 本模块    （次次常用）
    # 其他模块  （次常用）

# 4个方法，组成反射
    # hasattr  (常用)
    # getattr  (常用)
    # setattr
    # delattr

# 从实例对象角度：
'''
class A:
    country = 'China'
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def func(self):
        print('in A func')

obj = A('KK',18)

# hasattr
print(hasattr(obj,'name'))  # 要以字符串的方式去操作对象，所以要用字符串的方式传入参数名
    # True
print(hasattr(obj,'func')) 
    # True
# getattr
print(getattr(obj,'name')) 
    # KK
print(getattr(obj,'func')) 
    # <bound method A.func of <__main__.A object at 0x1036f1d90>>
    # 内存地址+() 就可以执行了吧！
f = getattr(obj,'func')
f()         # get到的是obj的 func， 也就是对象的方法，因此可以直接调用，不用传self。
    # in A func
# format : getattr(object,name,default)

# setattr 用的少。
    # setattr 实现下面的结果
        # obj.sex = 'M'
        # print(obj.sex)
setattr(obj,'sex','M')
print(getattr(obj,'sex')) 
    # M

'''

# 从类的角度
'''
class A:
    country = 'China'
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def func(self):
        print('in A func')

if hasattr(A,'country'):
    print(getattr(A,'country')) # China

if hasattr(A,'func'):
    f = getattr(A,'func') # 
    print(f)    # <function A.func at 0x102a83550>
    # f()         # 需要传参self！ TypeError: func() missing 1 required positional argument: 'self'
    f(111)  # in A func

# 对类做getattr想实现对实例对象一样的效果该如何实现？
if hasattr(A,'func'):
    obj = A('kk',18)
    f = getattr(obj,'func') # 
    f() # in A func


'''

# 从其他模块
'''
# 定义一个外部模块 kk.py
import kk

print(getattr(kk,'name'))   # kk
print(getattr(kk,'func'))   # <function func at 0x100d874c0>
getattr(kk,'func')()        # in kk func

# 找到kk的B类
print(getattr(kk,'B'))      # <class 'kk.B'>
# 通过对B类这个对象反射取到area
print(getattr(kk.B,'area')) # China

# 通过kk的B类实例化一个对象objkk
objkk1 = getattr(kk,'B')('yy')   # 
print(objkk1.__dict__)       # {'name': 'yy'}

objkk2 = kk.B('yy')
print(objkk2.__dict__)       # {'name': 'yy'}

# 对通过B类实例化的对象进行反射取值
print(getattr(objkk2,'area'))   # China
'''

# 对当前模块
'''
# 需要解决*attr(obj,'name',default) 中， obj的取值问题。
# 这里就借用sys.modules[__name__])
import sys
print(sys.modules[__name__])
# <module '__main__' from '/Users/kk/Documents/gittee/kk_mysql/Typora_data/Python/pys/day25 反射/25-2 反射.py'>
values = 'kk223'
def func_kk():
    print('func_kk!')

print(getattr(sys.modules[__name__],'values'))  # kk223
print(getattr(sys.modules[__name__],'func_kk')) # <function func_kk at 0x1030fc0d0>
getattr(sys.modules[__name__],'func_kk')()      # func_kk!
'''

# 一个练习：将kk模块中所有funcN 函数名添加到列表。
'''
import kk
list_funcN = [f'func{i}' for i in range(1,7)]
for i in list_funcN:
    if hasattr(kk,i):
        print(f'kk.{i} exists')
    else:
        print(f'---kk.{i} not exists')
# print(hasattr(kk,'func1'))
# print(getattr(kk.func1,'__call__') )    # function 有__call__ 方法。
'''




# 反射带来一种全新的编程思路。
'''
回到最初的作业里。
class User:
    def login(self):
        print('login')

    def register(self):
        print('reg')

    def save(self):
        print('save')

while 1:
    choose =  input('选择功能:').strip()
    if choose == 'login':
        obj = User()
        obj.login()
    elif choose == 'register':
        obj = User()
        obj.register()
    elif choose == 'save':
        obj = User()
        obj.save()

# 高级一点：
class User:
    def login(self):
        print('login')

    def register(self):
        print('reg')

    def save(self):
        print('save')

# 但是每新增一个类或方法，都要维护一次这个choose_dic
choose_dic = {
    1:User.login,
    2:User.register,
    3:User.save
}

while 1:
    choose = input('请输入序号，\n1：登录\n2：注册\n3：保存\n').strip()
    obj = User()
    choose_dic[ int(choose) ](obj)
'''
# 用反射思路实现：

class User:
    user_list = [('login','登录'),('register','注册'),('save','保存')]

    def login(self):
        print('login')

    def register(self):
        print('reg')

    def save(self):
        print('save')

while 1:
    choose = input('请输入序号，\n1：登录\n2：注册\n3：保存\n').strip()
    obj = User()
    # 功能函数名 = obj.user_list[int(choose)-1][0]
    # 反射给obj对象，就不用传参
    getattr(obj, obj.user_list[int(choose)-1][0] )()
