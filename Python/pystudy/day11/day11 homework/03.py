'''
3.看代码写结果
DATA_LIST = []
def func(arg):
    return DATA_LIST.insert(0, arg)

data = func('绕不死你')
print(data)             # None
print(DATA_LIST)        # ['绕不死你']

'''