'''
1.从空间角度研究类
    1.对象操作对象属性
    2.类名操作属性
    3.类对象指针
    4.对象取值顺序
    5.类名取值顺序
2.类与类的关系
    1.依赖关系
    2.组合关系（关联组合聚合）
'''
class A:
    address = 'Beijing'

    def __init__(self,name):
        self.name = name

# 创建一个对象
obj = A('kk')

# 为对象在类外封装属性
# get_weapon = input('是否要获取武器？')
# if get_weapon == '是':
#     obj.weapon = 'AK47'



# 在类里面为对象封装属性
class B:
    address = 'Beijing'

    def __init__(self,name):
        self.name = name

    # 封装一个新属性。
    def func(self):
        if self.name == 'kk':
            self.skins = '装甲'

    def fun2(self):
        B.hegiht = '200'

obj2 = B('kk')
obj2.func()
print(obj.__dict__)
print(obj2.__dict__)


# 从类的空间研究类。
# 通过类名，在类外部增加属性
A.height = '190'
print(A.__dict__)
'''
    {'__module__': '__main__', 
    'address': 'Beijing', 
    '__init__': <function A.__init__ at 0x101438820>, 
    '__dict__': <attribute '__dict__' of 'A' objects>, 
    '__weakref__': <attribute '__weakref__' of 'A' objects>, 
    '__doc__': None, 
    'height': '190'}
'''

# 在类内部封装新属性 B.func()
B.fun2(1)   # 通过类名调用方法，需要传参。随便传一个参数即可。 指定后即在类内封装了fun2带来的新属性
print(B.__dict__)
'''
{'__module__': '__main__', 
'address': 'Beijing', 
'__init__': <function B.__init__ at 0x1028b4820>, 
'func': <function B.func at 0x10289ce50>, 
'fun2': <function B.fun2 at 0x10289cf70>, 
'__dict__': <attribute '__dict__' of 'B' objects>, 
'__weakref__': <attribute '__weakref__' of 'B' objects>, 
'__doc__': None, 
'hegiht': '200'}
'''
# 但是要实现类名调用方法与对象调用方法实现起来一致的话， 就需要将对象作为参数传入
B.fun2(obj2)
print(B.__dict__)
'''
{'__module__': '__main__', 
'address': 'Beijing', 
'__init__': <function B.__init__ at 0x103524820>, 
'func': <function B.func at 0x10350ce50>, 
'fun2': <function B.fun2 at 0x10350cf70>, 
'__dict__': <attribute '__dict__' of 'B' objects>, 
'__weakref__': <attribute '__weakref__' of 'B' objects>, 
'__doc__': None, 
'hegiht': '200'}
'''
print('**',obj2.__dict__)
# ** {'name': 'kk', 'skins': '装甲'}
# print(B.__dict__)

# 结论
# 通过类名可以在类内外封装属性
# 通过类内外可以为对象封装属性


# 对象查询一个属性：
    # 对象空间 > 类空间 > 父类空间

# 类查询一个属性：
    # 类空间 > 父类空间

# ↑ 单向不可逆原则。对象与对象之间互相独立（除去组合这种特殊的关系之外）。