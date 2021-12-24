'''

15.看代码写结果
def extendList(val,list=[]):
    list.append(val)
    return list

list1 = extendList(10)
list2 = extendList(123,[])
list3 = extendList('a')

print('list1=%s' %list1)    # [10]
print('list2=%s' %list2)    # [123]
print('list3=%s' %list3)    # [10,'a']      # 这个有大坑，仔细想想。

'''
