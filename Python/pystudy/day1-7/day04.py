# # 本节大纲
# - 列表初识
# - 列表的索引切片
# - 列表的增删改查
# - 列表的嵌套
# - 元组的初识
# - 元组的简单应用


# - 列表初识
#     - str 存储相对少量的数据。
#     - str 存储的永远都是字符串。 切片还是其他操作，获取的也都是字符串。
#     - list
#         - []，承载任意数据类型，是py常用的容器型数据类型，存储大量数据。
#         - 列表是有序的，可切片。
#         - list1 = [1,2,'abc',True,[3,4,5],{},'',(7,8,9)]

# - 列表的索引切片
# - 列表的增删改查
#     - 容器型数据类型一般都支持增删改查
#     - 增
#         - append，追加
#             >>> l1 = ['aa','bb','dd','ff']
#             >>> l1.append('pp')
#             >>> l1
#             ['aa', 'bb', 'dd', 'ff', 'pp']
#             >>> l2 = []
#             >>> while flag:
#             ...     ina = input('name,or q to quit:')
#             ...     if ina.upper() == 'Q':
#             ...             break
#             ...     else:
#             ...             l2.append(ina)
#             ... 
#         - insert，插入。目标位置后的元素都向后挪一位。
#             >>> l1
#             ['aa', 'bb', 'dd', 'ff', 'pp']
#             >>> l1.insert(1,'11')
#             >>> l1
#             ['aa', '11', 'bb', 'dd', 'ff', 'pp']
#         - extend，迭代着增加（追加）。将可迭代对象拆开后追加。
#             >>> l1
#             ['aa', '11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp']
#             >>> l1.extend('abcd')
#             >>> l1
#             ['aa', '11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c', 'd']
#             >>> l1.extend(['first',])
#             >>> l1
#             ['aa', '11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c', 'd', 'first']
#     - 删
#         - pop，按照位置删除（按照索引位置删除）。返回删除的元素。只有pop动作会有返回值。默认删除最后一个元素。
#             >>> l1
#             ['aa', '11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c', 'd', 'first']
#             >>> l1.pop(0)
#             'aa'
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c', 'd', 'first']
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c', 'd', 'first']
#             >>> l1.pop()
#             'first'
#             >>> l1.pop()
#             'd'
#         - remove，按照元素删除。没有返回值。有重名元素的，默认从左向右顺序删除第一个。
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'a', 'b', 'c']
#             >>> l1.remove('a')
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'b', 'c']
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']
#             >>> l1.remove('a')
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'b', 'c', 'b', 'c', 'a', 'b', 'c']
#             >>> l1.remove('b')
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'c', 'b', 'c', 'a', 'b', 'c']
#         - clear，清空元素
#             >>> l1
#             ['11', 'bb', 'dd', 'bbbbbbb', 'ff', 'pp', 'c', 'b', 'c', 'a', 'b', 'c']
#             >>> l1.clear()
#             >>> l1
#             []
#         - del，可以按照索引删，还可以按照切片删除。
#             >>> l2
#             ['aa', 'bb', 'ee', 'ff', 'qq', 'ss', 'oo', 'pp', 'uu', 'yy', 'tt', 'hhh', 'ggg', 'fff']
#             >>> del l2[0]
#             >>> l2
#             ['bb', 'ee', 'ff', 'qq', 'ss', 'oo', 'pp', 'uu', 'yy', 'tt', 'hhh', 'ggg', 'fff']
#             >>> del l2[2::2]
#             >>> l2
#             ['bb', 'ee', 'qq', 'oo', 'uu', 'tt', 'ggg']
#     - 改
#         - 按照索引改
#             >>> l2
#             ['bb', 'ee', 'qq', 'oo', 'uu', 'tt', 'ggg']
#             >>> l2[0] = 'abcacb'
#             >>> l2
#             ['abcacb', 'ee', 'qq', 'oo', 'uu', 'tt', 'ggg']
#         - 按照切片改
#             >>> l2[0:3] = 'abcacb','aa','bb'
#             >>> l2
#             ['abcacb', 'aa', 'bb', 'oo', 'uu', 'tt', 'ggg']
#             >>> li
#             ['TaiBai ', 'alexC', 'Abc ', 'egon', ' riTiAn', 'Wusir', ' aqc']
#             >>> li[::2]='ooo','ooop','ooooi','llll'
#             >>> li
#             ['ooo', 'alexC', 'ooop', 'egon', 'ooooi', 'Wusir', 'llll']
#     - 查
#         - 使用索引查
#             for 循环迭代索引。
#         - 使用切片查
#         - index，查索引标号
#             用法 可迭代对象.index(要查询的元素[,查询的起始[,查询的结束]])
#             >>> l3
#             ['a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc']
#             >>> l3.index('a')   # 默认，从左到右开始，第一个索引就是
#             0
#             >>> l3.index('a',1)  # 那么从第二个开始再次查找，第四个元素也是a
#             3
#             >>> l3.index('a',4)  # 从第五个元素开始再次查找，第七个元素也是a
#             6
#             >>> l3.index('a',7)   # 同理，查到第十个元素也是a
#             9
#             >>> l3.index('a',10)   # 略。 因为只有15个元素，且第十三个元素是最后一个a，因此继续查找会报错了。
#             12
#     - 列表的计算
#         - 和int相乘
#             >>> l3 = ['a','b','abc']
#             >>> l3[2]*5
#             'abcabcabcabcabc'
#             >>> (l3[2]+' ')*5
#             'abc abc abc abc abc '
#             >>> l3*5
#             ['a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc', 'a', 'b', 'abc']
# - 列表的嵌套(特别重要)
#     案例，l1 = [1,2,'taibai',[1,'alex',3,]]
#         1. 将l1中的taibai变成大写
#         >>> l1[2]=l1[2].upper()
#         >>> l1
#         [1, 2, 'TAIBAI', [1, 'alex', 3]]
#         # 2. 给子列表追加一个元素
#         >>> l1[3].append('牛逼啊！')
#         >>> l1
#         [1, 2, 'TAIBAI', [1, 'alex', 3, '牛逼啊！']]
#         # 3. 给子列表的alex加上称号
#         >>> l1[3][1] = l1[3][1]+'sb'
#         >>> l1
#         [1, 2, 'TAIBAI', [1, 'alexsb', 3, '牛逼啊！']]
# - 元组的初识（了解即可）
# - 元组的简单应用



# - range
#     - 类似于列表，自定制数字范围的数字的列表。
#         >>> r1 = range(0,5)
#         >>> r1
#         range(0, 5)       # 类型是range
#         >>> for i in r1:  # 可以迭代
#         ...     print(i)
#         ... 
#         0
#         1
#         2
#         3
#         4
#         >>> r1[0]  # 也能用索引
#         0
#         >>> r1[1]
#         1
#         >>> r1[-1]
#         4
#         >>> r1[::2]   # 也能切片和设置步长
#         range(0, 5, 2)
#         >>> r1
#         range(0, 5)
#         >>> r2 = r1[::2]      # 迭代切片
#         >>> for i in r2:
#         ...     print(i)
#         ... 
#         0
#         2
#         4
#         >>> for i in range(5,0,-1):       # 倒叙迭代
#         ...     print(i)
#         ... 
#         5
#         4
#         3
#         2
#         1
#         # 无意义的倒叙
#         range(1, 5, -1)       # 无意义的倒叙。why？因为从1到5 按照-1 步长是无法迭代的。 正确的写法是(5,1,-1)
#         >>> for i in range(1,5,-1):
#         ...     print(i)
#         ... 
#         >>> for i in range(5,1,-1):
#         ...     print(i)
#         ... 
#         5
#         4
#         3
#         2
#     - 利用for循环，利用range，将列表的所有索引打印出来
#         >>> l2
#         ['abcacb', 'aa', 'bb', 'oo', 'uu', 'tt', 'ggg']
#         >>> for i in range(0,len(l2)) :
#         ...     print(i)
#         ... 
#         0
#         1
#         2
#         3
#         4
#         5
#         6



# 练习
# 1. 用for循环和range找出100以内所有的偶数并将这些偶数插入到一个新的列表中。
#     >>> target = []
#     >>> for i in range(0,101):
#     ...     if i % 2 == 0:
#     ...             target.append(i)
#     ... 

# 2. 用for循环和range找出50以内能被3整除的数，并将这些数插入到一个新的列表中。
#     >>> target = []
#     >>> for i in range(0,51):
#     ...     if i % 3 == 0:
#     ...             target.append(i)

# 3. 用for循环和range从100-1 倒序打印
#     >>> for i in range(100,0,-1):
#     ...     print(i)

# 4. 用for循环和range从100-10 ，倒叙将所有的偶数添加到一个新的列表中，然后对列表中元素进行筛选，将能被4整除的数字留下来。
#     >>> target = []
#     >>> for i in range(100,9,-1):
#     ...     if i % 2 == 0:
#     ...             target.append(i)
#     ... 
#     >>> target 
#     [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10]
#     >>> new_target = []
#     >>> for i in target:
#     ...     if i % 4 == 0:
#     ...             new_target.append(i)

# 5. 用for循环和range，将1-30的数字依次添加到一个列表中，并循环这个列表，将能被3整除的数改成*。
#     >>> t = []
#     >>> for i in range(1,31):
#     ...     t.append(i)
#     ...
#     >>> for i in t:
#     ...     if i % 3 == 0:
#     ...             t[t.index(i)] = '*'
#     ...
#     >>> print(t)
#     [1, 2, '*', 4, 5, '*', 7, 8, '*', 10, 11, '*', 13, 14, '*', 16, 17, '*', 19, 20, '*', 22, 23, '*', 25, 26, '*', 28, 29, '*']

# 6. 查找列表li中的元素，移除每一个元素的空格，并找出以A或者a开头的，并以c结尾的元素，并添加到一个新列表中，最后循环打印这个新列表
# li = ["TaiBai ","alexC","Abc ","egon"," riTiAn","Wusir"," aqc"]
#     new = []
#     for i in li :
#         i = i.strip()
#         if i[0].upper() == 'A' and i[-1] == 'C':     # 这一段可以用startwith() \ endwith() 来做。
#             new.append(i)
#     print(new)


#     new = []
#     for i in li :
#         i = i.strip()
#         if i.upper().startswith('A') or i.endswith('C'):     # 这一段可以用startwith() \ endwith() 来做。
#             new.append(i)
#     print(new)



# 7. 开发敏感词过滤系统，提示用户输入的评论内容，如果包含关键词，则将用户输入的内容中的敏感词汇替换成等长度的*号，并添加到一个列表中。如果用户如输入的内容没有敏感词汇，则直接添加到上述列表中。
# li = ["苍老师","井老师","空老师"]
# iptlist = []

# startflag = 1
# while startflag:
#     inpt = input('请输入评论：')
#     # inpt='藏苍舱苍老师哈哈大是大非123123'
#     if inpt == 'q':
#         startflag = 0
#         print(iptlist)
#         exit()
#     else:
#         flag = 1  # 1. process , 0.end

#         while flag:
#             for i in li:
#                 # 防止有多次关键词重复，所以对一个关键词的处理要反复做in判断。
#                 while i in inpt:
#                     # 替换关键词为星星，由于str不能按照list思维去修改（跟tuple同类），
#                     # 因此想到的是，通过index() 获取到关键词开始的位置，然后对评论截取[:开始位置] ，这样前面就是干净的
#                     # 然后从开始位置偏移一个len(关键词) 的长度，就是关键词结束的位置，即 开始位置+len(关键词) 就是关键词结束所在的索引位
#                     # 我们将关键词开始前的部分截取，替换关键词长度，再截取关键词结束后的部分，三者进行拼合，就是要的结果了。
#                         # 找到关键词在索引开始位置，inpt.index(i)
#                         # 从开头截取到关键字开始的位置，inpt[:inpt.index(i)]
#                         # 根据关键词i的长度换成星星,len(i)*'*'
#                         # 找到关键词在索引结束位置，inpt.index(i)+len(i)
#                         # 从关键字结束的位置截取到末尾，inpt[inpt.index(i)+len(i):]
#                     inpt = inpt[:inpt.index(i)] + len(i)*'*' + inpt[inpt.index(i)+len(i):]
#                     #藏苍舱苍老师哈哈大是大非123123
#             # 没有敏感关键词之后，将评论添加到新列表。并完成本条评论的审核。
#             iptlist.append(inpt)
#             flag = 0

# li = ["苍老师","井老师","空老师"]
# iptlist = []

# startflag = 1
# while startflag:
#     inpt = input('请输入评论：')
#     # inpt='藏苍舱苍老师哈哈大是大非123123'
#     if inpt == 'q':
#         startflag = 0
#         print(iptlist)
#         exit()
#     else:
#         flag = 1  # 1. process , 0.end

#         while flag:
#             for i in li:
#                 # 防止有多次关键词重复，所以对一个关键词的处理要反复做in判断。
#                 if i in inpt:
#                     #藏苍舱苍老师哈哈大是大非123123
#                     inpt = inpt.replace(i,'*'*len(i))   # replace()就是完全替换，所以前面不需要while了。
#             # 没有敏感关键词之后，将评论添加到新列表。并完成本条评论的审核。
#             iptlist.append(inpt)
#             flag = 0
#       # 另外，replace(source,target) 使用时，即使source不存在于源，也不会报错，只是执行后，对源没有变化而已。

# 8. 有如下列表： li = [1,3,4,"alex",[3,7,8,"TaiBai"],5,"RiTiAn"]
#     循环打印列表中的每个元素，遇到列表则再循环打印出它里面的元素。
#     目标样式：将每一个元素都迭代出来。
#     蠢法
#     li = [1,3,4,"alex",[3,7,8,"TaiBai"],5,"RiTiAn"]
#     for i in li:
#         if str(type(i)) == "<class 'list'>":
#             for l in i:
#                 print(l)
#         else:
#             print(i)

#     正常法
#     li = [1,3,4,"alex",[3,7,8,"TaiBai"],5,"RiTiAn"]
#     for i in li:
#         status = isinstance(i,list)
#         if status == True:
#             for l in i:
#                 print(l)
#         else:
#             print(i)

#     其实， 直接 if type(i) == list   也可以……

# 9. 默写列表的增删改查的方法，有几种写几种。
#     - 增:list.insert(#,value)\ list.append() \ list.extend()
#     - 删:list.pop(#)\list.clear\list.remove(value)\del list[#]
#     - 改:list[#] = newvalue\list[m:n:s] = newvalues
#     - 查:list[#]\list[m:n:step]

# 10. 计算1-2+3...+99 中除了88以外的所有数字的和。
#     >>> c = 0
#     >>> for i in range(1,100):
#     ...     if i == 88 :
#     ...             i+=1
#     ...     if i % 2 == 0:
#     ...             i = -i
#     ...     c = c + i
#     ... 
#     >>> c
#     227

# 11. 判断一行文字是否是对称文字
#     ipt = input('input:')
#     ipt_desc = ipt[::-1]
#     if ipt == ipt_desc:
#         print('一样，牛逼！')
#     else:
#         print('不一样')

# 12. 写一个自动加法计算器
#     expr = input("输入一个加法计算表达式：")
#     expr_list = expr.split('+')
#     expr_strip = []
#     counts = 0
#     # 去除前后空格。但是实际上没啥意义，因为int() 动作会自动去除。
#     for i in expr_list:
#         expr_strip.append(i.strip())

#     for i in expr_strip:
#         counts = counts + int(i)

#     print('和是:',counts)

# 13.计算用户输入的内容里有多少个是数字，并汇总出来，然后计算这些数字的和。
