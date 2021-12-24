# 内置名称空间 python提供的内置函数。builtins.py
# 全局名称空间 py file 。（除去函数和类）
# 局部名称空间 functions执行时开辟，随着函数的结束而消失。存放函数内部的变量与值的对应关系。

# 三个名称空间的加载顺序
    # 内置--> 全局 --> 局部（函数执行时）

# 三个名称空间的取值顺序：就近优先原则，单向不可逆
    # 局部（函数执行时）--> 全局 --> 内置



# 作用域
    # 全局作用域
        # 内置名称空间与全局名称空间的所有内容包含在全局作用域

    # 局部作用域
        # 局部名称空间
        # 局部作用域可以从全局作用域中获取变量，反之不行。
'''
# 在局部创建一个新的变量，这不叫修改全局变量。
count = 1
def func():
    count = 100
    print(count)

func()



# 这才叫修改，但是局部作用域只能引用却不能改变全局作用域的变量，所以会报错
count = 1
def func():
    count += 100
    print(count)

func()

error： UnboundLocalError: local variable 'count' referenced before assignment
'''

# 局部作用域的不能改变全局作用域的变量，
# 当py解释器读取到局部作用域时，发现你对一个变量进行修改的操作，如：name = name + 5 ,
# 解释器会认为你在局部作用域已经定义过name这个局部变量，就从局部作用域中查找这个局部变量，就报错了。
# 但是仅做调用的时候，会单向的逐级作用域去查找变量，因此调用时却是可以成功的。（但不能修改）
# 不过，如果在局部作用域中重新声明一个叫做name的对象时，解释器会认为成这是一个新定义的对象（也因此局部作用域的取值要先于全局作用域）



# LEGB， local, eclose,global,builtins 原则（即：就近原则）
            # 再往前就是builtins.py里的内置命名空间了。
counttmp = 1                # global
def func():
    count = 1               #  eclose
    def inner():
        counts = count + 1      # local
        # count += 1  # 修改全局作用域变量会报错。这里先注释掉。
        print(counts)
        print(count)
    inner()
   # print(count)
func()


# 高级函数（函数的嵌套）