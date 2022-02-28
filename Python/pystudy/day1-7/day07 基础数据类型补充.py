# 基础数据类型的补充
# 1. int
# 2. string
    # 对string的任何修改操作都会创建一个新的string对象。
    # 首字母大写 string.capitalize()
    # 大小写翻转 string.swapcase()
    # 单词首字母大写 string.title()
    # 字符串居中 string.center(length,str)
        # aa = 'abcABC1'
        # aa.center(9,'*')
    # 通过元素查找字符串中的索引值 string.find(str)
        # 找到第一个就返回。找不到则返回-1
    # 通过元素查找字符串中的索引值 string.index(str)
        # 找到第一个就返回。找不到则报错
        # aa.find('a')
        # aa.index('a')

        # # 打印list中元素的所有索引 on 2021,07,15.

        # source = ['a',1,2,3,4,5,'b',2,3,4,5,'c',3,4,5,'a','b','aa']
        # dict1={}
        # for idx in range(0,len(source)):
        #     # 如果dict中存在的key，则将value取出，然后对该list做append
        #     if dict1.get(source[idx]):
        #         val = dict1.get(source[idx])
        #     # 如果dict中不存在key，则是新key，声明一个空list作为value，然后将idx值append进来。
        #     else:
        #         val=[]
        #     # 将当前idx追加到索引list并赋值给dict的key-values。
        #     val.append(idx)
        #     dict1[source[idx]]=val
        # print(dict1)

# 3. list
    # 统计元素出现次数 list.count()
        # >>> li = [1,1,1,2,2,2,3,3,3,4]
        # >>> li.co
        # li.copy(   li.count(  
        # >>> li.count(1)
        # 3
        # >>> li.count(4)
        # 1
    # 获取元素的索引（只返回命中的第一个元素所在的索引） list.index()
    # 对源列表内元素做排序 list.sort()
        # 默认从小到大排序。 倒序排序：li.sort(reverse=True)
            # >>> li.sort()
            # >>> li
            # [1, 2, 2, 2, 3, 3, 4, 4, 4, 6, 8, 9, 54, 234]
            # >>> li.sort(reverse=1)
            # >>> li
            # [234, 54, 9, 8, 6, 4, 4, 4, 3, 3, 2, 2, 2, 1]
    # 翻转排序（将源列表元素顺序倒置） list.reverse()
        # >>> li=[1,9,5,4,7,6]
        # >>> li.reverse()
        # >>> li
        # [6, 7, 4, 5, 9, 1]
    # 列表相加
        # >>> l1=[1,2,3,4]
        # >>> l2=['a','b','c','d']
        # >>> l1+l2
        # [1, 2, 3, 4, 'a', 'b', 'c', 'd']
    # 列表与数字相乘
        # >>> l1
        # [1, 2, 3, 4]
        # >>> l1*3
        # [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
    # 删除列表中索引为奇数对应的元素删除掉。
        # del + 切片
            # >>> li
            # [6, 7, 4, 5, 9, 1]
            # >>> del li[1::2]
            # >>> li
            # [6, 4, 9]
        # 倒序法。因为正序删除索引会导致数据逻辑错误
            # >>> li=[6, 7, 4, 5, 9, 1]
            # >>> for i in range(len(li)-1,-1,-1):
            # ...     if i%2 == 0:
            # ...             li.pop(i)
            # ... 
            # 9
            # 4
            # 6
            # >>> li
            # [7, 5, 1]
        # 另辟蹊跷，移花接木
            # >>> li=[6, 7, 4, 5, 9, 1]
            # >>> l2=[]
            # >>> for i in range(len(li)):
            # ...     if i%2 == 1:
            # ...             l2.append(li[i])
            # ... 
            # >>> l2
            # [7, 5, 1]
            # >>> li=l2
            # >>> li
            # [7, 5, 1]  
    # 循环一个列表时，最好不要对列表长度进行变更，否则极易出问题。因为列表长度改变后，各元素位置可能都变了。
# 4. tuple
    # 如果一个元组中只有一个元素，且不包含逗号，那么这个对象的数据类型便不是元组，而是那个元素。
        # >>> tu=('a')
        # >>> type(tu)
        # <class 'str'>
        # >>> tu=('a',)
        # >>> type(tu)
        # <class 'tuple'>
    # 但凡加一个逗号，都是元组。
# 5. dict
    # 删
        # dict.popitem()
        # 3.5 版本之前为随机删除
        # 3.6 版本开始为删除最后一个。因为3.6版本开始dict内部有序了。
        # 有返回值。
            # >>> dict1
            # {'a': 15, 1: 1, 2: 7, 3: 12, 4: 13, 5: 14, 'b': 16, 'c': 11, 'aa': 17}
            # >>> dict1.popitem()
            # ('aa', 17)
            # >>> dict1
            # {'a': 15, 1: 1, 2: 7, 3: 12, 4: 13, 5: 14, 'b': 16, 'c': 11}
    # 改/增
        # dict.update()
            # 无则添加
            # >>> dict1
            # {'a': 15, 1: 1, 2: 7, 3: 12, 4: 13, 5: 14, 'b': 16, 'c': 11}
            # >>> dict1.update(bbb='aaaaaaa')
            # >>> dict1
            # {'a': 15, 1: 1, 2: 7, 3: 12, 4: 13, 5: 14, 'b': 16, 'c': 11, 'bbb': 'aaaaaaa'}
            
            # 有则更新
            # >>> dict1.update(a=150000)
            # >>> dict1
            # {'a': 150000, 1: 1, 2: 7, 3: 12, 4: 13, 5: 14, 'b': 16, 'c': 11, 'bbb': 'aaaaaaa'}

            # 有则更新
            # >>> dict1={'a1':'aaa','b1':'bbb'}
            # >>> dict2={'na1':'n1','na2':'n2'}
            # >>> dict1.update(dict2)
            # >>> dict1
            # {'a1': 'aaa', 'b1': 'bbb', 'na1': 'n1', 'na2': 'n2'}
            # >>> 
            # >>> 
            # >>> 
            # >>> dict3={'na1':'naaaaaaa1','na2':'n2'}
            # >>> dict1.update(dict3)
            # >>> dict1
            # {'a1': 'aaa', 'b1': 'bbb', 'na1': 'naaaaaaa1', 'na2': 'n2'}
# 6. bool
# 7. set
# id() , is


# fromkeys
    # 创建一个字典，字典的所有键来自一个可迭代对象；字典的所有键共用一个值。
    # 主体是dict。*值为key共用*（非常重要）。
    # key来自于可迭代对象。
        #xx = dict.fromkeys(可迭代对象,values)#
        # >>> dic=dict.fromkeys('abc',10)
        # >>> dic
        # {'a': 10, 'b': 10, 'c': 10}

        # >>> dic=dict.fromkeys(['a','b','c','d','e',9],10)
        # >>> dic
        # {'a': 10, 'b': 10, 'c': 10, 'd': 10, 'e': 10, 9: 10}

    # 进一步证明value为key共用。
        # >>> dic=dict.fromkeys(['a','b','c','d','e',9],[])
        # >>> dic
        # {'a': [], 'b': [], 'c': [], 'd': [], 'e': [], 9: []}
        # >>> dic['a'].append(1000)
        # >>> dic
        # {'a': [1000], 'b': [1000], 'c': [1000], 'd': [1000], 'e': [1000], 9: [1000]}

# 练习
# dic = {'k1':'aaaa','k2':'bbbb','k3':'cccc','a1':'bac1','a2':'badfadf'}
# 将字典中所有key带有k字符的键值对删除。
    # 循环一个字典时，如果改变这个字典的大小，那么直接报错。因此直接循环时pop()行不通。
    # 土办法
        # dic = {'k1':'aaaa','k2':'bbbb','k3':'cccc','a1':'bac1','a2':'badfadf'}
        # tmp=[]
        # for i in dic.keys():
        #     if 'k' in i:
        #         tmp.append(i)
        # for i in tmp:
        #     dic.pop(i)
        # print(dic)
    # 高级一点的办法
        # dic = {'k1':'aaaa','k2':'bbbb','k3':'cccc','a1':'bac1','a2':'badfadf'}
        # for i in list(dic.keys()):  # 强制将结果转换为list，这样就和源dict没关系了。
        #     if 'k' in i:
        #         dic.pop(i)
        # print(dic) 

# 数据类型之间的转换
    # int bool str 三者转换
    # str list 两者转换
    # list set 两者转换: set(list) ; list(set)
    # str bytes 两者转换: bytes(str,Encoding); str(bytes,Encoding); bytes.decode(Encoding)
        # >>> bytes('牛逼','utf-8')
        # b'\xe7\x89\x9b\xe9\x80\xbc'
        # >>> str(b'\xe7\x89\x9b\xe9\x80\xbc','utf-8')
        # '牛逼'

        # >>> st='abc'
        # >>> bytes(st,'utf-8')
        # b'abc'
        # >>> by=bytes(st,'utf-8')
        # >>> by.decode('utf-8')
        # 'abc'

        # gbk to utf-8
            # >>> st='哈你好'
            # >>> s1=bytes(st,'gbk')
            # >>> s1
            # b'\xb9\xfe\xc4\xe3\xba\xc3'
            # >>> s1a=s1.decode('gbk')
            # >>> s1a
            # '哈你好'
            # >>> s2=s1a.encode('utf-8')
            # >>> s2
            # b'\xe5\x93\x88\xe4\xbd\xa0\xe5\xa5\xbd'
    # 所有数据都可以转化成bool值:  bool(anything)
        # 以下将转化为False值： '',0,(),{},[],set(),None
# 基础数据类型总结
    # 按占用存储空间从低到高
        # int，数字
        # str，字符串
        # set，集合：无序，不需要存索引相关信息
        # tuple，元组：有序，需要存索引相关信息，不可变
        # list，列表：有序，需要存索引相关信息，可变，需要处理数据的增删改
        # dict，字典，需要存key：value映射的相关信息，可变，需要处理数据的增删改。3.6之后有序。
    # 按存值个数区分
        # 原子、标量类型：int 数字，str 字符串
        # 容器类型：   list 列表，tuple 元组， dict 字典
    # 按可变不可变区分
        # 可变：list 列表，dict 字典
        # 不可变： int 数字，str 字符串， tuple 元组， bool 布尔值
    # 按访问顺序区分
        # 直接访问：int 数字
        # 顺序访问（序列类型，效率低）： str 字符串，list 列表， tuple 元组
        # key值访问（映射类型，效率高）：dict 字典

# 编码的进阶
    # 所有的字符集，除unicode之外，不能直接互相识别
    # 在内存中所有的数据必须是unicode编码存在，除去bytes
        # bytes 是py3的基础的 数据类型 ，不是”字节Bytes“的意思。
        # 数据的存储和传输，都要转换成bytes类型。
            # 基础数据类型(int\bool\tuple\list\dict\set) --》 encode to utf-8 --> str （unicode） --> bytes(非unicode) --> 网络传输/磁盘存储  --> bytes (非unicode) --> decode --> 原始数据类型及数据
            # str 类型， 由 "" 或 '' 标识
            # bytes 类型，使用 b"" 或 b'' 标识，用于网络数据传输、图像文件和保存。

