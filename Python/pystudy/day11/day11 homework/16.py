'''

16.看代码写结果
def extendList(val,list=[]):
    list.append(val)
    return list
print('list1=%s' %extendList(10))           # list1='[10]'
print('list2=%s' %extendList(123,[]))       # list2='[123]'
print('list3=%s' %extendList('a'))          # list3='[10,'a']'

'''
def extendList(val,list=[]):
    list.append(val)
    return list
print('list1=%s' %extendList(10))           # list1=[10]
print('list2=%s' %extendList(123,[]))       # list2=[123]
print('list3=%s' %extendList('a'))          # list3=[10,'a']