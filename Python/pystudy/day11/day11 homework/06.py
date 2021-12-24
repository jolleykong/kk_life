'''
6.看代码写结果
def func():
    return 'shaobing'

def bar():
    return 'doubi'

def base(a1,a2):
    return a1() + a2()

result = base(func, bar)
print(result)

# 'shaobingdoubi'
'''