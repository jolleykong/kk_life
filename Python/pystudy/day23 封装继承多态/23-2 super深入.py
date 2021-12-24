
# super方法的深入理解
    # super() 严格意义并不是执行父类的方法。
        # 单继承时，super() 肯定是执行父类的方法
        # 多继承时，super(S,self) 严格按照self从属于的类的mro()的顺序（即：self从属于的类.mro()）执行“S类的下一位”。
            # 下面举例
'''
class A:
    def f1(self):
        print('in A')

class Foo(A):                   # 1. 从#0的调用执行到父类Foo
    def f1(self):
        super(Foo,self).f1()    # 2. 前面一旦调用了，self就是obj。Foo的下一位，在obj的mro()结果中是Bar
        print('in Foo')         # 5. 调用完父类Bar后执行。执行后返回调用Foo之前，也就是#0

class Bar(A):                   # 3. 从#2调用执行到父类Bar
    def f1(self):
        print('In Bar')         # 4. 输出结果。然后返回调用#3之前，也就是#2

class Info(Foo,Bar):
    def f1(self):
        super(Info,self).f1()   # 0. 一旦调用了，self就是obj。 Info的下一位，在obj的mro()中，下一位是Foo
        print('in Info f1')     # 6. 调用完父类后执行。

obj = Info()
print(Info.mro())   # [<class '__main__.Info'>, <class '__main__.Foo'>, <class '__main__.Bar'>, <class '__main__.A'>, <class 'object'>]
                    # [Info,Foo,Bar,A,object] 
obj.f1()
# In Bar        # 4
# in Foo        # 5
# in Info f1    # 
'''

# 再实验验证一个
class A:
    def f1(self):
        print('in A')

class Foo(A):                   
    def f1(self):
        super(Foo,self).f1()    
        print('in Foo')         

class Bar(A):                   # 1. 从#0的调用执行到父类Foo
    def f1(self):
        print('In Bar')         # 2. 输出结果。然后返回调用#1之前，也就是#0

class Info(Foo,Bar):
    def f1(self):
        super(Foo,self).f1()   # 0. 一旦调用了，self就是obj。 Foo的下一位，在obj的mro()中，下一位是Bar
        print('in Info f1')    # 3. 调用完父类后执行。

obj = Info()
# print(Info.mro())   # [<class '__main__.Info'>, <class '__main__.Foo'>, <class '__main__.Bar'>, <class '__main__.A'>, <class 'object'>]
                    # [Info,Foo,Bar,A,object] 
obj.f1()
# In Bar
# in Info f1