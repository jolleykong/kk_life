'''
5.看代码写结果
def func():
    print('hello')
    return 'sb'

func_list = [func,func,func]
for i in range(len(func_list)):
    val = func_list[i]()
    print(val)

# hello # func print
# sb    # func return , print(val)
# hello
# sb
# hello
# sb
'''

