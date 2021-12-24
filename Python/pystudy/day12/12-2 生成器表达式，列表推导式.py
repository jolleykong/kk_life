# 列表推导式 生成器表达式
# 列表推导式。（生成器表达式将列表推导式做下括号变化， 就可以了。 规则一样）


# 列表推导式：用一行代码构建一个比较复杂且有规律的列表
# 列表推导式分成两类
    # 循环模式： [变量(加工后的变量) for 变量 in iterable]
    # 筛选模式： [变量(加工后的变量) for 变量 in iterable if 条件]
    # 嵌套模式： 




# 1.生成一个1~10 的列表
    # 之前的办法
li = []
for i in range(1,11):
    li.append(i)
print(li)

    # 列表推导式方式
        # 将表达式for i in range(1,11)直接写入列表
            # lii = [for i in range(1,11)]
        # 然后将需要的成为元素的变量放在前面，就成了
            # lii = [i for i in range(1,11)]
lii = [i for i in range(1,11)]
print(lii)


# 2.将10以内所有的整数的平方写入列表
li2 = [i**2 for i in range(0,11)]
print(li2)

# 3.100以内所有的偶数写入列表
# 循环式
li3i = [i for i in range(0,101,2)]
print(li3i)

# 筛选式
li3 = [i for i in range(0,101) if i % 2 == 0]
print(li3)

# 4.从python11期到python100期写入列表
li4 = [f'python{i}期' for i in range(1,101)]
print(li4)

# 5.筛选模式，三十以内可以被3整除的数
li5 = [i for i in range(1,31) if i % 3 == 0]
print(li5)  #[3, 6, 9, 12, 15, 18, 21, 24, 27, 30]

# 6.筛选模式，过滤掉长度小于3的字符串列表，并将剩下的转换成大写字母
lsm = ['abc','asdfijbji','rivnadf','dc','ab','rwsjxvnz','asdfvg']

li6 = [ i.upper() for i in lsm if len(i) >= 3]
print(li6)

# 7.筛选模式，找到嵌套列表中名字含有两个'e'的所有名字
lnm = [ ['Petter','Jane'],['Harry','Potter'],['Teeeth','team'],['NeE','eeo']]

# 常规方法做的话：
tmp = []
for i in lnm:
    for j in i:
        print(j)
        if j.lower().count('e') == 2:
            tmp.append(j)
print(tmp)

# 写成列表推导式，将 for i in lnm ，for j in i 和 if j.lower().count('e') == 2 顺序写入，将最终需要的j变量放在最前面。
li7 = [j for i in lnm for j in i if j.lower().count('e') == 2]
print(li7)


# 生成器表达式，与列表推导式的写法几乎一样
# 列表推导式写法： 
li_a = [j for i in lnm for j in i if j.lower().count('e') == 2]
print(li_a)     # ['Petter', 'NeE', 'eeo']
# 生成器表达式写法：把中括号换成小括号就可以了。 
li_b = (j for i in lnm for j in i if j.lower().count('e') == 2)
print(li_b) # <generator object <genexpr> at 0x102e5ef90>
    # >>> next(li_b)
    # 'Petter'
    # >>> next(li_b)
    # 'NeE'
    # >>> next(li_b)
    # 'eeo'
    # >>> next(li_b)
    # Traceback (most recent call last):
    #   File "<stdin>", line 1, in <module>
    # StopIteration


# 总结：
'''
# 列表推导式缺点
    1.只能构建比较复杂而且有规律的列表。如果没有规律或者十分复杂，不行
    2.因此，尽管列表推导式很好，但是长时间想不出推导方法就放弃吧。
    3.超过3层循环才能构建成功的，就别用列表推导式了， 正常方式循环生成吧。
    4.不利于拍错。因为只有一行，所以不好排查中间过程问题。
# 列表推导式优点
    1.简单，一行构建
    2.便于装逼


'''
# 构建一个列表，存储2345678910JQKA

poker1 = [i for i in (*range(2,14),'J','Q','K','A') ]
print(poker1)

poker2 = [i for i in range(2,14)] + list('JQKA')
print(poker2)

