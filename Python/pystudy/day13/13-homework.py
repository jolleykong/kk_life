# 总结
# 匿名函数
    # 多与内置函数、列表推导式结合。
# 内置函数
    # 
# 闭包
    # 内层函数对外层函数的非全局变量的使用
    # 保证数据安全。自由变量不会在内存中消失，而且全局无法直接引用自由变量。
    # 一定要存在嵌套函数中

'''
作业
1. 用map来处理字符串列表，把列表中所有人都变成sb，如：jolley_sb
name = ['jolley','billy','steve']

>>> list(map(lambda x:x+'_sb',name))
['jolley_sb', 'billy_sb', 'steve_sb']


2. 用map来处理下述l，然后用list得到一个新的列表，列表中每个人的名字都是sb结尾
l = [{'name':'alex'},{'name':'y'}]

# 这是错的， 因为不是新列表，而且没用map
# >>> for i in l:
# ...     i['name'] = i['name']+'_sb'
# ...
# >>> l
# [{'name': 'alex_sb'}, {'name': 'y_sb'}]


>>> list(map(lambda x:x['name']+'_sb',l))
['alex_sb', 'y_sb']


3. 用filter来处理，得到股票价格大于20的股票名字
shares = {
    'IBM':36.6,
    'APPL':23.2,
    'PlyB':21.2,
    'SB':10.1,
}


filter(lambda x:shares[x]>20 , shares)
        # # def whot20(a):
        #         if shares[a] > 20:
        #             return a

        # filter(whot20,shares)



4. 有下面字典，得到购买每只股票的总价格，并放在一个迭代器中结果 list一下 [123.0,222.12,100.05,]


5. 有下列三种数据类型
l1 = [1,2,3,4,5,6]
l2 = ['kk','jj','gg','koko']
t1 = ('**','***','****','******')
# 写代码，最终得到 每个元组第一个元素大于2，第三个元素至少4个*
    # 如： [(3,'gg','****'),(4,'koko','******')]

# zip(l1,l2,t1) 返回了个迭代器
>>> list(filter(lambda x:x[0]>2 and len(x[-1])>=4 ,zip(l1,l2,t1)))
[(3, 'gg', '****'), (4, 'koko', '******')]



7. 有如下数据类型
l1 = [
    {'sales_volumn':0},
    {'sales_volumn':108},
    {'sales_volumn':337},
    {'sales_volumn':475},
    {'sales_volumn':396},
    {'sales_volumn':172},
    {'sales_volumn':9},
    {'sales_volumn':58},
    {'sales_volumn':272},
    {'sales_volumn':456},
    {'sales_volumn':440},
    {'sales_volumn':239},
]
将l1按照列表中的每个字典的values大小进行排序，形成一个新的列表


# sorted(iterable, /, *, key=None, reverse=False)
#     Return a new list containing all items from the iterable in ascending order.

#     A custom key function can be supplied to customize the sort order, and the
#     reverse flag can be set to request the result in descending order.


>>> sorted(l1,key=lambda x:x['sales_volumn'])   # {'sales_volumn':0},
[{'sales_volumn': 0}, {'sales_volumn': 9}, {'sales_volumn': 58}, {'sales_volumn': 108}, {'sales_volumn': 172}, {'sales_volumn': 239}, {'sales_volumn': 272}, {'sales_volumn': 337}, {'sales_volumn': 396}, {'sales_volumn': 440}, {'sales_volumn': 456}, {'sales_volumn': 475}]


8. 求结果
v = [lambda :x for x in range(10)]
print(v)
print(v[0])
print(v[0]())

剖析：
v = [lambda :x for x in range(10)]  # def了一个无参数的函数。是个列表生成式
    # v() 就是调用这个函数咯
print(v)
        # >>> v = [lambda :x for x in range(10)]
        # >>> print(v)  # 函数内存地址。此时列表生成式执行完毕，x 达到range(10)的最大值，即：x=9
        # [<function <listcomp>.<lambda> at 0x103418ee0>, <function <listcomp>.<lambda> at 0x103418f70>, <function <listcomp>.<lambda> at 0x103424040>, <function <listcomp>.<lambda> at 0x1034240d0>, <function <listcomp>.<lambda> at 0x103424160>, <function <listcomp>.<lambda> at 0x1034241f0>, <function <listcomp>.<lambda> at 0x103424280>, <function <listcomp>.<lambda> at 0x103424310>, <function <listcomp>.<lambda> at 0x1034243a0>, <function <listcomp>.<lambda> at 0x103424430>]


print(v[0])
        # >>> print(v[0])   # 第一个元素的内存地址，也就是lambda的内存地址。 此时这些函数也没执行噢！
        # <function <listcomp>.<lambda> at 0x103418ee0>

print(v[0]())
        # 相当于执行了第一个函数。
        # 结果是9 ，为何？
        # 因为执行了第一个函数。执行lambda函数会返回x， 此时x为9，为何？
        # 因为列表生成式执行的时候x已经range(10)运行结束， 此时x=9
        # 所以print(v[1]())，print(v[2]()) 的返回值也都是9，因为x=9。

9. 求结果
v = (lambda :x for x in range(10))
print(v)            # <Generator xxxxx> 生成器内存地址
print(v[0])         # 报错，生成器不是list，无法使用索引直接调用
print(v[1])         # 报错，生成器不是list，无法使用索引直接调用
print(v[0]())       # 报错，生成器不是list，无法使用索引直接调用
print(v[1]())       # 报错，生成器不是list，无法使用索引直接调用
print(next(v))      # <Function xxxxxx> 生成的第一个函数内存地址。 此时如果可以运行该函数，值为0.
print(next(v)())    # 1
print(next(v)())    # 2
print(next(v)())    # 3
print(next(v)())    # 4
print(next(v)())    # 5
print(next(v)())    # 6
print(next(v)())    # 7
print(next(v)())    # 8
print(next(v)())    # 9
print(next(v)())    # StopIteration

# 与题8的区别是， 这次是生成器表达式。
生成器表达式和列表生成式的区别在于，
需要使用next()、for或者list()去迭代。
否则不会运行。
进行next()一次，生成一个，因此不会一下都生成完成再等待调用。





12. map(str,[1,2,3,4,5,6,7,8,9] ) 输出的是什么 
# 这里str是str() ~  别迷糊
所以结果是，创建了一个迭代器，将后面的列表中的元素， 变成字符串类型。

>>> a = map(str,[1,2,3,4,5,6,7,8,9] )
>>> list(a)
['1', '2', '3', '4', '5', '6', '7', '8', '9']


13.求结果。 比较难
def num():
    return [ lambda x:i*x for i in range(4) ]

print([m(2) for m in num()])


14. 有一个数组 [34, 1,2,5,6,6,5,4, 3,3] 请写一个函数，找出该数组中没有重复的数的总和。
    # 即： 1+2 = 3

def plus(list1):
    t_list= []
    count = 0
    for i in list1:
        for j in str(i):
            t_list.append(int(j))
    uniq_list = [i for i in t_list if t_list.count(i)<2]
    for i in uniq_list:
        count = count + i
    return count
plus([34, 1,2,5,6,6,5,4, 3,3])

15. 写一个函数完成三次登录功能：
    - 用户的用户名密码从一个文件register中取出
    - register文件包含多个用户名，密码。用户名密码通过|隔开，每个人的用户名密码占用文件中的一行。
    - 完成三次验证，三次验证不成功则登录失败，登录失败返回false。
    - 登录成功返回True



16. 再写一个函数完成注册功能：
    - 用户输入用户名密码注册
    - 注册时要验证，文件中用户名是否存在，如果存在则让其重新输入用户名，如果不存在则注册成功
    - 注册成功后，将注册成功的用户名、密码写入register文件，以|隔开
    - 注册成功后，返回True，否则返回False

17. 用完成一个员工信息表的增删功能
文件存储格式如下：
id, name, age, phone, job
1. alex,22,1234567,IT


'''

'''
with open('./day13/register',mode='r') as reg:
    l1 = reg.readlines()
    # for i in l1:
    #     print(i.strip().split("|"))
# 生成用户名密码的kv字典
dic1 = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in l1}

逐行读也不错：
dict1 = {}
with open('./day13/register',mode='r') as reg:
    for line in reg:
        line_list = line.strip().split('|')
        dict1[line_list[0].strip()] = [line_list[1].strip()]

密码文本转dict的动作也可以用map对文件句柄进行操作~ 自己发挥一下。
'''
def login(username,pwd):
    with open('./day13/register',mode='r') as reg:
        l1 = reg.readlines()
        # for i in l1:
        #     print(i.strip().split("|"))
    # 生成用户名密码的kv字典
    dic1 = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in l1}

    # 用户名是否存在的判断，用get比直接dic1[key] 要好。
    if dic1.get(username) == pwd :
        login_flag = True
    else:
        login_flag = False

    return login_flag

# print(login('aa','pwd'))
# fail_count = 0
# while fail_count <= 3:
#     username = input('username:').strip()
#     password = input('password:').strip()
#     if login(username,password):
#         print(f'welcome! {username.upper()}')
#         break
#     else:
#         fail_count += 1


def register(username,pwd):
    with open('./day13/register',mode='r+') as reg:
        l1 = reg.readlines()
        # for i in l1:
        #     print(i.strip().split("|"))
    # 生成用户名密码的kv字典
        dic1 = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in l1}
        print(dic1)
        if dic1.get(username):
            print('username exists! please use another one.')
            reg_flag = None
        # if username in dic1:      # 效率其实特别高。
        else:
            newuser = username+'|'+pwd+'\n'
            reg.seek(0,2)
            reg.write(newuser)
            reg_flag = True
    return reg_flag

# register('cc','aa')
