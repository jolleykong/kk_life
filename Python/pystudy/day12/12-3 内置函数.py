# python 提供了68个内置函数。
'''
黄色一带而过（相对不重点）：all()  any()  bytes() callable() chr() complex() divmod() eval() exec() format() frozenset() globals() hash() help() id() input() int()  iter() locals() next()  oct()  ord()  pow()    repr()  round()

红色重点讲解（重点）：abs() enumerate() filter()  map() max()  min() open()  range() print()  len()  list()  dict() str()  float() reversed()  set()  sorted()  sum()    tuple()  type()  zip()  dir() 

蓝色未来会讲（也是重点）： classmethod()  delattr() getattr() hasattr()  issubclass()  isinstance()  object() property()  setattr()  staticmethod()  super()

上面的黄色，红色的内置函数是在这两天讲完的（讲过的就不讲了），蓝色的讲完面向对象会给大家补充，剩余还有一些课上就不讲了，课下练习一下就可以。
'''

# eval() 很强大，但是很危险。剥去字符串的外衣，运算里面的代码。
f1 = '1+3'
print(f1,type(f1))   #1+3,str
print(eval(f1),type(eval(f1))) #4,int

# 字符串转换成字典……
s = '{"name":"gege"}'
print(s,type(s))    #{"name":"gege"} <class 'str'>
print(eval(s),type(eval(s)))    #{'name': 'gege'} <class 'dict'>

# 网络传输的str，input输入的时候，sql注入等情况下，一定不要用eval。
# 所以通常情况下不要用eval

# exec() ，与eval几乎一样，但是用来处理代码流。
msg = '''
for i in range(10):
    print(i)
'''
print(msg)
exec(msg)



# hash()， 获取一个对象的hash。只能操作不可变的数据类型。
# a = []
# hash(a) # 报错。 只能操作不可变数据类型。

# help() 获取对象的使用帮助


# callable() 检查一个对象是否可以被调用。（是否可以被call）

# int()

# bin()
# oct()
# hex()

#float()

#complex() 返回一个复数
# 一个数的平方是-1 ，这个数则是复数。
# 

# divmod() 计算除数与被除数的结果，返回一个包含商和余数的元组。

# round() 保留浮点数的小数位数，默认保留整数。

# pow() 求x**y次幂

# bytes() 不同编码之间的转化

# ord() 返回字符在编码中的位置

# chr() 输入位置找出对应编码的字符  #unicode

# repr() 返回对象的string形式（原形毕露函数） ，对应的， 格式化输出中使用%r 来返回原形毕露格式。

# all() 一个可迭代对象中所有元素全为True才为True
# any() 一个可迭代对象中有元素为True就为True

# reversed() 倒置函数

# zip() 拉链函数

# min() 支持对可迭代对象做迭代对比。
    # 循环什么类型就返回什么类型。
    #min(*args,key=None) , key可以指定为函数名。
        #有什么用？ 
            # 比如， l1 = [10,20,30,4,5,6,7,99,-100,-27]
            # 常规求l1中最小值， 可以用print(min(l1))
            # 但是如果想求绝对值最小的元素呢？
            # 可以用 print(min(l1,key=abs))
        # 凡是可以加key的，它会自动的将可迭代对象的每一个元素按照顺序传入到key指定的函数中。
        # 在这里，最后以函数的返回值比较大小。
            # 循环过程模拟
                # min(l1,key=abs)
                # 第一次循环， value=10, abs(10)=10
                # 第二次循环， value=20, abs(20)=20， 20>10， 20在内存中消失
                # 第三次循环， value=30, abs(30)=30,  30>10, 30在内存中消失
                # 第四次循环， value=4, abs(4)=4 , 4<10 , 10在内存中消失……
                # ……
                # 完成循环后，只剩下最小的值。

        # 对dict类型做min()查找
            # 默认情况下，min()会按照dict对象的key做大小比较。
            # 如果要求出value最小的key，d1 = {'a':1,'b':2,'c':3}
                # 按照上面的理解，定制一个函数
                    # d1 = {'a':10,'b':2,'c':3}

                    # def retminv(v):
                    #     return d1[v]    # 返回字典中该变量作为key的value。

                    # print(min(d1,key=retminv))
                # 写成lambda函数来实现
                    # d1 = {'a':10,'b':2,'c':3}
                    # ret = lambda v:d1[v]
                    # print(min(d1,key=ret))
                # 再简单点
                    # d1 = {'a':10,'b':2,'c':3}
                    # print(min(d1,key=lambda v:d1[v]))


# min()循环一个元组组成的列表
lt1 = [('哈哈',10),('who',12),('you',9),('can',8),('aqq',100)]
print(min(lt1)) # ('aqq', 5) ,是按第一个元素的第一个字符排序？
# 求序号最小的那个元组
print(min(lt1,key=lambda x:x[1]))       # ('can', 8)
    # 第一次循环， 元组为('哈哈',10)，返回值10
    # 第二次循环，元组为('who',12)，返回值12，该元组消失
    # ...
    # 最后循环结束后，留下的元组为('can',8) ，返回该结果。
    # 加纲，求最小年龄的名字
        # print(min(lt1,key=lambda x:x[1])[0])

# sorted() ， 对列表排序时，创建一个新列表。
# sorted() ，对lt1中按照年龄大小排序
print(sorted(lt1,key=lambda x:x[1]))
print(sorted(lt1,key=lambda x:x[1],reverse=1))



# filter() 类似于列表推导式的筛选模式
l2 = [3,4,5,6,7,8,9,10,13,15,16,18,21,22]
# 列表推导式的方式筛选出不能被3整除的元素
print([i for i in l2 if i % 3 != 0])
# filter() 方式实现
res = filter(lambda x: x % 3 != 0,l2) # 这是个迭代器
print(list(res))
    # 每次从l2中取一个元素传入filter，做内部函数运算， 只留下返回为True的结果。
    # 二者效率没啥区别，列表推导式性能和内置函数之间没有啥确认的效率区别。


# map() 类似于列表推导式的循环模式
    # 列表推导式方式，将l2的元素作平方运算并返回列表
print([i**2 for i in l2])
# map() 方式实现
red = map(lambda x:x**2 , l2)   # 也是迭代器
print(list(red))


# reduce() py2算内置函数，py3被踢出了内置函数，算模块了
from functools import reduce
nl1 = [1,2,3,4,5]
def func(x,y):
    return x + y

print(reduce(func,nl1)) # 15
    # 第一次循环， x=1, y=2 ,  return = 3
    # 第二次循环， x=3, y=3 , return = 6    # 这里的x=3 ，3取自于第一次的return。下同。
    # 第三次循环， x=6, y=4 , return = 10
    # 第四次循环， x=10,y=5 , return = 15




