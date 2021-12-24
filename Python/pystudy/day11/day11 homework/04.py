'''
4.看代码写结果
def func():
    print('hello')
    return 'sb'

func_list = [func,func,func]
for item in func_list:
    val = item()
    print(val)

# hello # func print
# sb    # func return , print(val)
# hello
# sb
# hello
# sb
'''