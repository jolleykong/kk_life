# 非常非常非常重要
'''
序列化：将一个数据结构（数据集）转化成一个特殊的序列的过程。
    特殊的序列：特殊的字符串。
    用于网络传输或数据的文件存取。

# 字典类型转换成str后写入文件，再读取回来后，str类型用起来不方便，但是反转不回dict类型。
# 不便于网络传输。网络传输需要转换成bytes，数据结构无法直接和bytes转换，需要数据结构-str-bytes 转换。
    # 发送后，bytes可以转换回str，但是再转回原有的数据结构，就困难了。

这就需要一种特殊的字符串，这个字符串可以与任何数据结构相互转换。
这就引出了序列化模块——将一种数据结构转化成特殊的序列，并且还可以反转。

py提供三个序列化模块
    # json模块，所有语言公认的一种序列。过于通用的结果，支持的py数据结构有限。
        # json支持的py数据结构： int、str、bool、dict、list、None、float
        # 不支持set
        # json通过转换对应类型方式实现各语言中通用性。
    # pickle模块，只能py语言中使用。支持所有py的数据类型和对象。
    # shevle模块（since v3.4），只能操作文件。
'''


'''
# json序列化
'''
# 两对四个方法。
    # dumps,loads
    # dump,load
import json

'''
dumps,loads  主要用于网络传输。也适用于存取文件
'''
dic = {'name':'啦啦啦','age':15}
ret1 = json.dumps(dic)
print(ret1,type(ret1))        # {"name": "\u5566\u5566\u5566", "age": 15} <class 'str'> <class 'str'> ,json中的字符串是双引号。

ret_dict = json.loads(ret1)
print(ret_dict,type(ret_dict))  # {'name': '啦啦啦', 'age': 15} <class 'dict'>

'''
json dumps/loads 特殊参数
'''
ret1_1 = json.dumps(dic,ensure_ascii=False)
print(ret1_1,type(ret1_1))      # {"name": "啦啦啦", "age": 15} <class 'str'>
ret1_2 = json.dumps(dic,ensure_ascii=False,sort_keys=True)
print(ret1_2,type(ret1_2))      # {"age": 15, "name": "啦啦啦"} <class 'str'>
# 更多参数自己扒文档。

# 转换成json后，就可以写入到文件、从文件读取再通过json转换出来了。

'''
dump,load 适用于单个数据的存取文件。节省一些代码，直接写入文件。
限制较多
'''
dic = {'name':'啦啦啦','age':15}
with open('json1.json',encoding='utf-8',mode='w') as f1:
    json.dump(dic,f1) 

with open('json1.json',encoding='utf-8') as f2:
    dic1 = json.load(f2) 
    print(dic1,type(dic1))

'''
多个数据如何存储到一个文件中？
'''
dic_1 = {'name':'啦啦啦','age':15}
dic_2 = {'name':'kk','age':20}
dic_3 = {'name':'yy','age':25}
with open('mutliline_1.json',encoding='utf-8',mode='a') as f1:
    f1.write(json.dumps(dic_1))
    f1.write(json.dumps(dic_2))
    f1.write(json.dumps(dic_3))
    
# 错误方法
# #或者？
# with open('mutliline_2.json',encoding='utf-8',mode='a') as f2:
#     f2.write(f'{json.dumps(dic_1)},{json.dumps(dic_2)},{json.dumps(dic_3)}')

# # 但是后者
# with open('mutliline_2.json',encoding='utf-8') as f3:
#     ret = json.loads(f3.read())     # 报错，因为不认。多个复合了。json只认一个字典结构。
#     print(ret)

# 所以，一行一个json串是最科学的
with open('mutliline_2.json',encoding='utf-8',mode='a') as f2:
    f2.write(f'{json.dumps(dic_1)}\n{json.dumps(dic_2)}\n{json.dumps(dic_3)}\n')

with open('mutliline_2.json',encoding='utf-8') as f3:
    for line in f3:
        ret = json.loads(line)
        print(ret)

