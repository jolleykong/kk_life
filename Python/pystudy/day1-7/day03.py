# 基础数据类型总览
#  数字类型，int，可以进行数学运算；
#  字符串，char，''，被''包含的表示字符串，用来存储少量的数据，可以切片及其他操作。；
#  布尔值，bool，True、False，用作判断
#  列表，list，[]，存储大量数据
#  元祖，tuple，()，存储大量只读数据
#  字典，dict，{K:V}，存储大量关联形数据（kv对），查询速度非常快。
#  集合，set。

#  查询数据类型，type()

#  int
#  不同进制间的转换
   #  二进制转十进制
   #  int(bin()，2)
   # 除了十进制之外，其他进制的相互转换都先转到十进制，再进一步转换。


#  bool
#  str 转 bool
    #  有值为True
        # >>> s = ''
        # >>> bool(s)
        # False
        # >>> s = 'a'
        # >>> bool(s)
        # True
#  s = input('type:')
#  if s:   #  只要条件能够转换为bool值即可，这里就是 如果s为True。而非空str即为True。
#      fool...


#  str
    ###  索引，切片
        #  根据索引取值
            #  >>> s = '哈啊去你大爷'
            #  >>> s[0]
            #  '哈'
            #  >>> type(s[0])
            #  <class 'str'> 
        #  根据切片取值。
        #  不可能知道每一个字符串的长度，所以需要切片取值。
        #  切片中，0可以省略书写。
            #  顾头不顾尾
                #  >>> s[0:3]  #  >>> s[:3]
                #  '哈啊去'
            #  切到尾
                #  >>> s[3:]
                #  '你大爷'
            #  加步长
                #  >>> s[:]
                #  '哈啊去你大爷'
                #  >>> s[0:4]
                #  '哈啊去你'
                #  >>> s[0:4:2]
                #  '哈去'
            #  倒叙取
            #  就是指定一个反向的步长
                #  >>> s[:]
                #  '哈啊去你大爷'
                #  >>> s[::-1]
                #  '爷大你去啊哈'
                #  >>> s[-1:-5:-1]
                #  '爷大你去'
    ###  str常用操作方法
        #  upper,lower
        #  startswith,endwith,返回bool值。
            #  >>> s = 'aBcDeFg'
            #  >>> s.startswith('a')
            #  True
            #  >>> s.startswith('A')
            #  False
            #  >>> s.startswith('c',2,5)
            #  True
        #  replace
            #  >>> s
            #  'aBcDeFgaaabc'
            #  >>> s.replace('a','A')
            #  'ABcDeFgaaabc'
            #  >>> s.replace('a','A',3)  #  替换3个。就会从左到右依次替换3个。
            #  'ABcDeFgAAabc'
            #  >>>
        #  strip，去除空白(space,\t,\n)
            #  默认为去除前后的空白
                #  >>> b
                #  '\tHi,enter\n'
                #  >>> b.strip()
                #  'Hi,enter'
            #  去除指定的字符（串），依次匹配字符串内的内容，存在则去掉，当然也是只针对前后。
                #  >>> b
                #  '\tHi,enter\n'
                #  >>> b1=b.strip()
                #  >>> b1
                #  'Hi,enter'
                #  >>> b1.strip('itr')
                #  'Hi,ente'
                #  >>> b1.strip('Hitr')
                #  ',ente'
                #  >>> b1.strip('Htr')
                #  'i,ente'
            #  lstrip,rstrip
                #  对应去除左侧或右侧空白\字符
            
        #  split，str转list
            #  默认按照空格分隔，返回一个列表。
                #  >>> c = 'a c de ef\tae,ed'
                #  >>> c.split()
                #  ['a', 'c', 'de', 'ef', 'ae,ed']
            #  指定分隔几个。
                #  >>> c.split(' ',2)
                #  ['a', 'c', 'de ef\tae,ed']
            #  指定分隔符
                #  >>> c.split(',')
                #  ['a c de ef\tae', 'ed']
        #  join
            #  拼合。
                #  >>> d = 'abcedfesdfg'
                #  >>> e = '-'.join(d)
                #  >>> e
                #  'a-b-c-e-d-f-e-s-d-f-g'
            #  可以将list转str，前提是list中每一个元素都是str类型。
                #  >>> c1 = c.split()
                #  >>> c1
                #  ['a', 'c', 'de', 'ef', 'ae,ed']
                #  >>> c2 = ''.join(c1)
                #  >>> c2
                #  'acdeefae,ed'
        #  count
            #  >>> e = 'abcdabcdabcd'
            #  >>> e.count('d')
            #  3

        #  format，格式化输出
            #  三种用法
            #  第一种
                #  >>> f = '第一个{},第二个{},第三个{}'.format('first','bbb','哈哈哈')
                #  >>> f
                #  '第一个first,第二个bbb,第三个哈哈哈'
            #  第二种，索引法
                #  >>> g = '第一个{0},第二个{2},第三个{1}'.format('first','bbb','哈哈哈')
                #  >>> g
                #  '第一个first,第二个哈哈哈,第三个bbb'
                #  >>> g = '第一个{0},第二个{2},第三个{2}'.format('first','bbb','哈哈哈')
                #  >>> g
                #  '第一个first,第二个哈哈哈,第三个哈哈哈'
            #  第三种，字典法
                #  >>> g = '第一个{one},第二个{two},第三个{three}'.format(two='first',one='bbb',three='哈哈哈')
                #  >>> g
                #  '第一个bbb,第二个first,第三个哈哈哈'
        
        #  IS判断 系列
            #isalnum，字符串由字母或数字组成
            #isalpha，字符串只由字母组成
            #isdecimal，字符串只由十进制组成
                #  >>> str1 = 'abc123'
                #  >>> str2 = 'abcABC'
                #  >>> str3 = '1234567890'
                #  >>> str1.isalnum()
                #  True
                #  >>> str2.isalnum()
                #  True
                #  >>> str2.isalpha()
                #  True
                #  >>> str2.isdecimal()
                #  False
                #  >>> str3.isdecimal()
                #  True
        #  in\not in 判断
                #  >>> str1
                #  'abc123'
                #  >>> print('1' in str1)
                #  True
                #  >>> '1' in str1
                #  True
                #  >>> 'cb' in str1
                #  False
                #  >>> 'bc' in str1
                #  True

        # while 循环 拆解str
            # >>> str1
            # 'abc123'
            # >>> idx = 0
            # >>> while idx < len(str1):
            # ...     print(str1[idx])
            # ...     idx+=1
            # ...
            # a
            # b
            # c
            # 1
            # 2
            # 3

       #  for 循环，有限循环。 拆解str
            # >>> str1
            # 'abc123'
            # >>> for i in str1 :
            # ...     print(i)
            # ...
            # a
            # b
            # c
            # 1
            # 2
            # 3

# 练习，将list中的元素拼接成字符串，用_ 连接。
    # >>> li = ['ax','wt','tb']
    # >>> '_'.join(li)
    # 'ax_wt_tb'