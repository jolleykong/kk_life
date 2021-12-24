# dict 字典
#- 字典初识
    # 列表可以存储大量的数据，但是数据之间的关联性并不强。
    # 列表的查询速度相对比较慢。数量越大，for越慢。
    # dict 用来解决这个问题。
    # dict 也是容器型数据类型。
        # 数据类型的分类（可变与不可变类型），即：该对象本身是否可变。
            # 可变类型（不可哈希）： list dict set
            # 不可变类型（可哈希）： str bool int tuple
        # dict， 以{} 表示，以KV对的形式存储的容器型数据类型。
            # Key 必须是不可变的数据类型，int、str。 bool和tuple较少用。
            # value 可以是任意数据类型、对象。
            # dict 在3.5版本之前是无序的。3.6开始会按照初次建立字典的顺序排列。但在学术上不认为是有序的。 3.7开始都是有序的。
    # dict是典型的以空间换时间。查询速度飞快，比列表快很多，存储关联性的数据。


#- 字典的使用
    #- 创建方式
        # 看源码。
        # 方式1：元组方式
            # >>> dic = dict( ( ('one',1),('two',2),('three',3)   ) )
            # >>> print(dic)
            # {'one': 1, 'two': 2, 'three': 3}
        # 方式2：kv对方式
            # >>> dic2 = dict(one=1,two=2,three=3)
            # >>> print(dic)
            # {'one': 1, 'two': 2, 'three': 3}
        # 方式3：kv方式
            # >>> dic3 = dict( {'one':1,'two':2,'three':3} )
            # >>> dic3
            # {'one': 1, 'two': 2, 'three': 3}
    #- 验证字典的合法性
        #- key 在同一个字典里应具有唯一性。否则只有最后一个才会被查询到。
        #- key 要可哈希。

    #- 字典的增
        #- 新声明一个key:value 即可。但如果key已经存在，则value会被覆盖。
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3}
            # >>> dic['four'] = 4
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4}
            # >>> dic['four'] = 4444
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444}
        #- setdefault()，无则新增，有则不变，且返回原值。
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444}
            # >>> dic.setdefault('job','sleep')
            # 'sleep'
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444, 'job': 'sleep'}
            # >>> dic.setdefault('job','run')
            # 'sleep'
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444, 'job': 'sleep'}
    #- 字典的删
        #- pop(key)，按照key去删除key:value，并返回删除的value。
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444, 'job': 'sleep'}
            # >>> dic.pop('job')
            # 'sleep'
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444}
        #- pop(key,return)，如果存在key，则删除。不存在则返回return。
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3, 'four': 4444}
            # >>> dic.pop('four','no-four')
            # 4444
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3}
            # >>> dic.pop('four','no-four')
            # 'no-four'
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3}
        #- clear()，清空dict
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3}
            # >>> dic.clear()
            # >>> dic
            # {}
        #- del dic[key]，也是按照key去删除。如果key不存在，则报错。
            # >>> dic
            # {'one': 1, 'two': 2, 'three': 3}
            # >>> del dic['one']
            # >>> dic
            # {'two': 2, 'three': 3}
            # >>> del dic['one']
            # Traceback (most recent call last):
            # File "<stdin>", line 1, in <module>
            # KeyError: 'one'
    #- 字典的改
        #- dic['key'] = value
    #- 字典的查
        #- dic['key']，key不存在则报错。
        #- dic.get(key) key不存在则返回none
        #- dic.get(key,return) 可以不存在则返回return

        #- keys() 输出所有key，可以循环，返回值类似list，但是没有索引，但可以转换成列表。
            # >>> dic.keys()
            # dict_keys(['two', 'three'])
            # >>> li = dic.keys()
            # >>> type(li)
            # <class 'dict_keys'>
            # >>> list(li)
            # ['two', 'three']
            # >>> li = list(li)
            # >>> type(li)
            # <class 'list'>
        #- values() 输出所有value。和keys() 类似，不过内容是values。

        #- items() 输出所有kv对，每一对kv都是一个tuple。
            # >>> dic
            # {'two': 2, 'three': 3}
            # >>> dic.items()
            # dict_items([('two', 2), ('three', 3)])
            # >>> list(dic.items())
            # [('two', 2), ('three', 3)]

                # 元组的拆包（也就是将items里的kv分别赋值）
                # >>> for i in dic.items():
                # ...     print(i)
                # ... 
                # ('two', 2)
                # ('three', 3)
                # >>> for i,j in dic.items():
                # ...     print(i,j)
                # ... 
                # two 2
                # three 3

                    # 也就是说
                        # >>> a = 18
                        # >>> b = 12
                        # >>> a,b = b,a
                        # >>> a
                        # 12
                        # >>> b
                        # 18
#- 字典的嵌套
    #- 即：字典中嵌套了字典或列表。






#- 练习
# dic = {'k1':'v1','k2':'v2','k3':[11,22,33]}
# 1. 在字典中添加一个键值对 k4:v4，输出添加完成后的字典
    #>>> dic['k4'] = 'v4'
    # >>> dic
    # {'k1': 'v1', 'k2': 'v2', 'k3': [11, 22, 33], 'k4': 'v4'}
# 2. 修改字典中k1对应的值为kk，输出修改后的字典
    # >>> dic['k1'] = 'kk'
    # >>> dic
    # {'k1': 'kk', 'k2': 'v2', 'k3': [11, 22, 33], 'k4': 'v4'}
# 3. 在k3对应的值中追加一个元素44，输出修改后的字典
    # >>> dic['k3'].append(44)
    # >>> dic
    # {'k1': 'kk', 'k2': 'v2', 'k3': [11, 22, 33, 44], 'k4': 'v4'}
    # 也可以这样，更优雅。
        # >>> dic = {'k1':'v1','k2':'v2','k3':[11,22,33]}
        # >>> t1 = dic.get('k3')
        # >>> t1.append(44)
        # >>> dic
        # {'k1': 'v1', 'k2': 'v2', 'k3': [11, 22, 33, 44]}
# 4. 在k3对应的值的第一个位置插入元素18，输出修改后的字典
    # >>> dic['k3'].insert(0,18)
    # >>> dic
    # {'k1': 'kk', 'k2': 'v2', 'k3': [18, 11, 22, 33, 44], 'k4': 'v4'}

'''
# 
dic = {
    'name':    '汪峰',
    'age':     38,
    'wife':    [{'name':'郑爽','age':73},],
    'children': {'g_1st':'美美','g_2nd':'方方','g_3rd':'小灰灰'}
}
1. 获取汪峰的名字
    >>> dic.get('name')
    '汪峰'
2. 获取wife这个字典
    >>> dic.get('wife')[0]
    {'name': '郑爽', 'age': 73}
3. 获取wife的名字
    >>> dic.get('wife')[0].get('name')
    '郑爽'
4. 获取第三个孩子的名字
    >>> dic.get('children').get('g_3rd')
    '小灰灰'
'''

'''
dic1 = {
    'name':['alex',2,3,4,5],
    'job':'teacher',
    'oldboy':{'alex':['py1','py2',100]}
}

1. 将name对应的列表加一个元素， kk
    >>> dic1.get('name').append('kk')
    >>> dic1
    {'name': ['alex', 2, 3, 4, 5, 'kk'], 'job': 'teacher', 'oldboy': {'alex': ['py1', 'py2', 100]}}
2. 将name对应的列表中的alex的首字母大写
    >>> dic1.get('name')[0] = dic1.get('name')[0][0].upper()+dic1.get('name')[0][1:]
    >>> dic1
    {'name': ['Alex', 2, 3, 4, 5, 'kk'], 'job': 'teacher', 'oldboy': {'alex': ['py1', 'py2', 100]}}
3. oldboy对应的字典加一个kv对  ' 老男孩',' linux'
    >>> dic1.get('oldboy')[' 老男孩'] = ' linux'
    >>> dic1
    {'name': ['Alex', 2, 3, 4, 5, 'kk'], 'job': 'teacher', 'oldboy': {'alex': ['py1', 'py2', 100], ' 老男孩': ' linux'}}
4. 将oldboy对应的字典中alex对应的列表中的py2删除。
    # remove()最贴切
    >>> dic1.get('oldboy')['alex'].remove('py2')
    >>> dic1
    {'name': ['Alex', 2, 3, 4, 5, 'kk'], 'job': 'teacher', 'oldboy': {'alex': ['py1', 100], ' 老男孩': ' linux'}}

    # 索引位有些作弊取巧。
    >>> dic1.get('oldboy')['alex'].pop(1)
    'py2'
    >>> dic1
    {'name': ['alex', 2, 3, 4, 5], 'job': 'teacher', 'oldboy': {'alex': ['py1', 100]}}

    # 最逗比但是绝对找不出逻辑问题的方法
    >>> dic1.get('oldboy')['alex'].pop(dic1.get('oldboy')['alex'].index('py2')
    ... )
    'py2'
    >>> dic1
    {'name': ['alex', 2, 3, 4, 5], 'job': 'teacher', 'oldboy': {'alex': ['py1', 100]}}
'''
