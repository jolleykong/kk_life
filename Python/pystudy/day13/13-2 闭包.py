
# 保证数据的安全。（# 封闭的东西。# 私用的东西。# 只允许某些人使用。）

# 通过在全局作用域声明变量来存储私有数据对象。
'''
list1 = []

def xxx(a):
    list1.append()
    ave = sum(list1)/len(list1)
    return ave

# 如果被错误调用， 那么对list1取平均值的操作就被打乱了。
'''


# 为了数据安全，列表有时不可以放在全局变量中，防止被误更改， 或被预期外的调用所修改。
'''
def xxx(a):
    list1 = []
    list1.append()
    ave = sum(list1)/len(list1)
    return ave

# 每次调用，列表都被重新赋值， 并不能实现目的。
'''

# 闭包来实现数据安全保护
def make_xxx():
    list1 = []      # 在外部如论如何也不能直接访问到list1 变量。
    def xxx(a):
        list1.append(a)
        ave = sum(list1)/len(list1)
        return ave
    return xxx
result = make_xxx()         # == ave
print(result(10))
print(result(11))       # 问题来了。 函数执行过一次之后，list1的内容应该消失，为什么没有消失呢？ 这就是闭包现象。
                # list1在这里称为 自由变量
                # 当xxx对list1进行了引用，那么xxx函数就与list1产生了绑定关系。
                # 因此，在return ave的时候， 其实也包含了list1的内容， 一并返回、赋值给了result
# 闭包的定义： 内层函数对外层函数非全局变量的引用（使用），无论是否为可变类型（不可变类型使用nonlocal），就会形成闭包。
# 被引用的非全局变量也称作 自由变量， 
# 这个自由变量会与内层函数产生绑定关系，因此自由变量不会在内存中消失。
    # 闭包只能存在于嵌套函数中。
    # 内层函数对外层函数的非全局变量的引用
# 闭包的作用：保护数据安全

'''
这种也算闭包。 
def wrapper(a,b):
    def inner():
        print(a)
        print(b)
    return inner

a = 2
b = 3
ret = wrapper(a,b)


因为， a、b虽然在全局做的声明，
但是，在wrapper()中，a、b作为参数被传入，实际上就相当于：
def wrapper(a,b):
    a = 2           # 相当于在内部创建了变量。
    b = 3
    def inner():
        ...

'''

# 判断一个嵌套函数是不是闭包
    # 闭包是内层函数对外层函数的引用，引用的非全局变量被称为自由变量
    # 判断调用有无自由变量，就可以看出是不是闭包
def wrapper(a,b):
    def inner():
        print(a)
        print(b)
    return inner

a = 2
b = 3
ret = wrapper(a,b)
print(ret.__code__.co_freevars)     # ('a', 'b') ---> 调用中，自由变量是： a,b 

