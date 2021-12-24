'''
class Alipay:
    def pay(self,money):
        print(f'使用支付宝支付了{money}元钱。')

class Ylian:
    def pay(self,money):
        print(f'使用银联支付了{money}元钱。')

class Wxpay:
    def pay(self,money):
        print(f'使用微信支付了{money}元钱。')

# 简单调用
# pay1 = Alipay()
# pay1.pay(100)

# pay2 = Ylian()
# pay2.pay(20)

# pay3 = Wxpay()
# pay3.pay(100)

# # 使用支付宝支付了100元钱。
# # 使用银联支付了20元钱。
# # 使用微信支付了100元钱。

# 规划一下支付接口，实现归一化设计。
    # 既然三个支付类结构都是互为鸭子

# 定义支付接口函数
def pay(obj,money):
    obj.pay(money)

# 调用
pay1 = Alipay()
pay(pay1,100)

pay2 = Ylian()
pay(pay2,20)

pay3 = Wxpay()
pay(pay3,50)

# 使用支付宝支付了100元钱。
# 使用银联支付了20元钱。
# 使用微信支付了50元钱。
'''


# 在一些重要的逻辑，与用户数据相关等核心部分，要建立一种约束，避免发生混乱错误。
    # 类的约束有两种解决方式：
        # 1. 在父类建立一种约束
        # 2. 模拟抽象类（指定一种规范）的概念，建立一种约束。
'''
# 第一种解决方法，建立一个父类

class Payment:
    def pay(self,money):        # 约定俗成定义一种规范，子类要定义pay方法。
        raise Exception('subClass 必须定义pay方法！')   # 也就是如果子类未定义pay方法，
                                                      # 那么子类实例在调用pay方法时就会调用到父类定义的包含异常的pay方法。

class Alipay(Payment):
    def pay(self,money):
        print(f'使用支付宝支付了{money}元钱。')

class Ylian(Payment):
    def pay(self,money):
        print(f'使用银联支付了{money}元钱。')

class Wxpay(Payment):
    def pay(self,money):
        print(f'使用微信支付了{money}元钱。')

class Test(Payment):
    pass

def pay(obj,money):
    obj.pay(money)

objN = Test()
pay(objN,200)   # Exception: subClass 必须定义pay方法！
# 未满足约束的子类对象在调用时，会调用到父类的pay方法，然后被父类pay方法中定义的约束抛出异常。
# 但是父类中定义约束的方法不具有强制性。
# 方法一是python推荐的一种约束方式。
'''

# 第二种方法
from abc import ABCMeta,abstractclassmethod

class Payment(metaclass=ABCMeta):   # metaclass=ABCMeta以及下面装饰器都是固定写法。
    @abstractclassmethod            # 使用这个装饰器来装饰需要被约束的方法
    def pay(self,money):                  # 只需抽象一个方法就可以。
        pass  
                                                      
class Alipay(Payment):
    def pay(self,money):
        print(f'使用支付宝支付了{money}元钱。')

class Ylian(Payment):
    def pay(self,money):
        print(f'使用银联支付了{money}元钱。')

class Wxpay(Payment):
    def pay(self,money):
        print(f'使用微信支付了{money}元钱。')

class Test(Payment):
    pass


objN = Test()   # TypeError: Can't instantiate abstract class Test with abstract method pay

# 利用抽象类的概念：基类如上设置，子类如果没有定义pay方法，在实例化对象的时候就会报错。
