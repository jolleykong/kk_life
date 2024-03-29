# 匿名函数， 也叫一句话函数。比较简单的函数，一行构建。
    # 匿名函数并非没有名字，名字就是设置的变量
    # lambda是定义匿名函数的关键字，相当于函数的def
    # lambda后面直接加形参，形参加多少都可以，只要用逗号隔开即可
    # 返回值在冒号后设置，返回值和正常函数一样，可以是任意数据类型
    # 匿名函数不管多复杂，只能写一行。逻辑结束后直接返回数据。

# 构建普通函数：
'''
def func(a,b,c,*args):
    return a
'''

# 构建lambda 匿名函数：
'''
lambda a,b,c,*args: a
# 返回a
# 一般就位置参数就够了。
'''

# 使用匿名函数
    #func1 = lambda a,b: a
    #函数名 = lambda 形参: 返回值

# 有部分匿名函数的应用和实验在day12-内置函数 中 被使用。

