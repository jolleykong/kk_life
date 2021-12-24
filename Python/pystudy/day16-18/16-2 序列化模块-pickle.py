# pickle
# 与json是str不同，pickle是bytes
'''
dumps,loads ， 只能是网络传输
'''
import pickle
l1 = ['abc','aaa','!!#!',123]
ret = pickle.dumps(l1)
print(ret,type(ret))        # b'\x80\x04\x95\x1a\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x03abc\x94\x8c\x03aaa\x94\x8c\x04!!#!\x94K{e.' <class 'bytes'>

'''
dump,load ， 数据结构存取文件
'''
l1 = ['abc','aaa','!!#!',123]
# with open('pickle1.pickle',encoding='utf-8',mode='w') as f1:
#     pickle.dump(l1,f1)  # TypeError: write() argument must be str, not bytes

with open('pickle1.pickle',mode='wb') as f1:
    pickle.dump(l1,f1)  # 当然，二进制的文件就不可阅读了。


with open('pickle1.pickle',mode='rb') as f1:
    ret = pickle.load(f1)  
    print(ret,type(ret))    # ['abc', 'aaa', '!!#!', 123] <class 'list'>

'''
多个数据写入
'''
l1 = ['abc','aaa','!!#!',123]
l2 = ['abcd','bbb','!!#!',321]
l3 = ['abcde','ccc','!!#!',000]
with open('pickle1.pickle',mode='wb') as f1:
    pickle.dump(l1,f1) 
    pickle.dump(l2,f1) 
    pickle.dump(l3,f1) 

with open('pickle1.pickle',mode='rb') as f1:
    ret1 = pickle.load(f1)
    print(ret1)
    ret2 = pickle.load(f1)
    print(ret2)
    ret3 = pickle.load(f1)
    print(ret3)

# 总结