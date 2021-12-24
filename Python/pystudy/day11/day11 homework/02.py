'''
2.看代码写结果
def func(arg):
    return arg.replace('文明用语','****')

def run():
    msg = '哈哈哈你看着文明用语变没变'
    result = func(msg)
    print(result)

run()   # '哈哈哈你看着****变没变'

########################

def func(arg):
    return arg.replace('文明用语','****')

def run():
    msg = '哈哈哈你看着文明用语变没变'
    result = func(msg)
    print(result)

data = run()
print(data)

# '哈哈哈你看着****变没变'
# None
'''