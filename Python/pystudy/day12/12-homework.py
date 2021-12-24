# 整理今天笔记，课上代码最少敲3遍。
#
# 用列表推导式做下列小题
#
# 过滤掉长度小于3的字符串列表，并将剩下的转换成大写字母
list1 = ['abc','asdfasdf','12vsrr2d','as','po1']
s1 = [ i.upper() for i in list1 if len(i) >= 3]
print(s1)   # ['ABC', 'ASDFASDF', '12VSRR2D', 'PO1']
#
# 求(x,y)其中x是0-5之间的偶数，y是0-5之间的奇数组成的元祖列表
s2 = [ (x,y) for x in range(6) if x % 2 == 0 for y in range(6) if y % 2 == 1]
print(s2)   # [(0, 1), (0, 3), (0, 5), (2, 1), (2, 3), (2, 5), (4, 1), (4, 3), (4, 5)]

#
# 求M中3,6,9组成的列表 M = [[1,2,3],[4,5,6],[7,8,9]]
s3 = [ [i - 2,i - 1,i] for i in range(3,10,3)]
print(s3)

# 求出50以内能被3整除的数的平方，并放入到一个列表中。
s4 = [ i**2 for i in range(51) if i % 3 == 0 ]
print(s4) # [0, 9, 36, 81, 144, 225, 324, 441, 576, 729, 900, 1089, 1296, 1521, 1764, 2025, 2304]

#
# 构建一个列表：['python1期', 'python2期', 'python3期', 'python4期',
# 'python6期', 'python7期', 'python8期', 'python9期', 'python10期']
s5 = [f'python{i}期' for i in range(1,11) if i != 5 ]
print(s5)   # ['python1期', 'python2期', 'python3期', 'python4期', 'python6期', 'python7期', 'python8期', 'python9期', 'python10期']

# 构建一个列表：[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
s6 = [(i,i+1) for i in range(6)]
print(s6)   # [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]

# 构建一个列表：[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
# s7 = [ i for i in range(18+1) if i % 2 == 0]
# print(s7)
s7 = [ i for i in range(0,18+1,2) ]
print(s7)   #  [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]



# 有一个列表l1 = ['alex', 'WuSir', '老男孩', '太白']
# 将其构造成这种列表['alex0', 'WuSir1', '老男孩2', '太白3']
l1 = ['alex', 'WuSir', '老男孩', '太白']

s8 = [ f'{l1[index]}{index}' for index in range(len(l1)) ]

print(s8)

# 有以下数据类型：
#
x = {'name':'alex',
     'Values':[{'timestamp':1517991992.94,'values':100,},
               {'timestamp': 1517992000.94,'values': 200,},
            {'timestamp': 1517992014.94,'values': 300,},
            {'timestamp': 1517992744.94,'values': 350},
            {'timestamp': 1517992800.94,'values': 280}],}

# 将上面的数据通过列表推导式转换成下面的类型：
# [[1517991992.94, 100], [1517992000.94, 200], [1517992014.94, 300], [1517992744.94, 350], [1517992800.94, 280]]

s9 = [ [{i["timestamp"]},{i["values"]}] for i in x.get('Values') ]
print(s9)   # ['[1517991992.94,100]', '[1517992000.94,200]', '[1517992014.94,300]', '[1517992744.94,350]', '[1517992800.94,280]']


# 用列表完成笛卡尔积
# 什么是笛卡尔积？ 笛卡尔积就是一个列表，
# 列表里面的元素是由输入的可迭代类型的元素对构成的元组，
# 因此笛卡尔积列表的长度等于输入变量的长度的乘积。
# [(),(),().....]

# ​	a. 构建一个列表，列表里面是三种不同尺寸的T恤衫，每个尺寸都有两个颜色（列表里面的元素为元组类型)。
#
colors = ['black', 'white']
sizes = ['S', 'M', 'L']
 
s10 = [ (x,y) for x in colors for y in sizes]
print(s10)

# ​	b. 构建一个列表,列表里面的元素是扑克牌除去大小王以后，所有的牌类（列表里面的元素为元组类型）。
#
nums = [ i for i in range(2,11)] + list('JQKA')
huas = ['草花','方片','黑桃','红桃']

poker = [ (x,y) for x in nums for y in huas ]
print(poker)


# 简述一下yield 与yield from的区别。
    # yield 返回生成器结果
    # yield from 把yield的结果作为迭代器返回其元素。



# 看下面代码，能否对其简化？说说你简化后的优点？
#
# def chain(*args):
#     # ('abc',(0,1,2))
#     for it in args:
#         for i in it:
#             yield i

# h = chain('abc',(0,1,2))

def chain(*args):
    # ('abc',(0,1,2))
            yield from [i for it in args for i in it]

g = chain('abc',(0,1,2))

# 怎么让生成器产出值？
    # next ，for 循环, 转化成list
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# print(list(g))
# print(list(g))  # 将迭代器转化成列表




# yield from 优化了内层循环，提高了效率。



# 看代码求结果（面试题）：
# v = [i % 2 for i in range(10)]
# print(v)
# 【0，1，0，1，0，1，0，1，0，1】



for i in range(5):
	print(i)
print(i)
# 4

###### 这个好好理解一下
# 看代码求结果：（面试题）
def demo():
    for i in range(4):
        yield i

g = demo()  #  生成器 ，并没有执行

g1 = (i for i in g)  # 生成器， 但是并没有执行。

g2 = (i for i in g1) #  生成器 ，没有执行。

print(list(g1))   # 生成器转为列表， 0，1，2，3 ， 此时指针停止在g1的结尾，g1被取完了、 g也被取完了。

# list((i for i in demo() ) ) [0,1,2,3]   # 生成器转为列表
print(list(g2))           # 生成器转为列表 ，不过g1被取完了，此时才执行g2= (i for i in g1)， 结果为空。
'''
# 看代码求结果：（面试题）
def demo():
    for i in range(4):
        yield i

g = demo()  # 生成器，但是没执行。执行后是0,1,2,3

g1 = (i for i in g)  	# 生成器，没执行
	
g2 = (i for i in g1) 	# 生成器，没执行

print(list(g1))  		# 开始执行g1， g1调用g， g被使用完毕--->g1生成器。 然后list() 函数将g1生成器用完。 结果为[0,1,2,3]

# list((i for i in demo() ) ) 
print(list(g2))          # 开始执行g2， g2调用g1. g1在上一步已经使用完毕，因此g2为空生成器。 转换为list后，依然为空。

'''

# 看代码求结果：（面试题）

def add(n,i):
    return n+i

def test():
    for i in range(4):
        yield i
g = test()      #list(g) = [0，1，2，3] ， 不过在调用next()之前， 这一步也没有运行。

for n in [1,10]:        # 这是个list，不是range！！
    g=(add(n,i) for i in g)     # 这一步只是上一层2个for循环生成两个生成器， 生成器并没有执行。
            # 相当于生成了
                # n = 1 
                # g=(add(n,i) for i in g) 
                # n = 10
                # g=(add(n,i) for i in g) 
            # 但是都没有执行，所以不会发生覆盖
        # 然后执行了 list(g)
            # list(g) --> n = 10, g=(add(n,i) for i in g) 
            # g=(add(10,i) for i in g) 
                # for i in g 的g 取自于上一层，n = 1 ,g=(add(n,i) for i in g) , 即：g=(add(n,i) for i in (add(n,i) for i in g)) 
                    # 问题来了，此时n = 10 ， 所以上一层的n=1 并未在生成器中生效，生成器就变成了 n=10,g=(add(n,i) for i in (add(n,i) for i in g)) 
                    # for i in g的g 取自于上一层 g = test() --> 0,1,2,3  -->  g=(add(10,i) for i in (add(10,i) for i in [0,1,2,3] )) 
                        # g=(add(10,i) for i in (add(10,i) for i in [0,1,2,3] ))  
                            # 0，1，2，3 --> 10,11,12,13
                            # g=(add(10,i) for i in [10,11,12,13] )
                                # list(g) = [20,21,22,23]




print(list(g))

# a = range(1,5)
#
# a = [i for i in a]
#
# a = [i**2 for i in a]