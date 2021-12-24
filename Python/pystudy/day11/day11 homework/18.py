'''
18.如何判断该对象是否是可迭代对象或者迭代器？


'__iter__' in dir(obj) == True 则对象为可迭代对象
'__iter__' in dir(obj) == True && '__next__' in dir(obj) == True，则对象为迭代器

'''