'''
test
infos
'''
a = 1
b = 2

def func():
    name = 'kk'
    age = 26
    print(1,globals())
    print(1,locals())
func()
print(2,globals())
print(2,locals())


''' result
1 {'__name__': '__main__', '__doc__': '\ntest\ninfos\n', '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x104dc8310>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/Users/kk/PycharmProjects/ProjectNothing/day10/10-4 globals locals 函数.py', '__cached__': None, 'a': 1, 'b': 2, 'func': <function func at 0x104e4d430>}
1 {'name': 'kk', 'age': 26}     # 局部作用域（当前作用域）内全部内容就是函数func() 里的内容。
2 {'__name__': '__main__', '__doc__': '\ntest\ninfos\n', '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x104dc8310>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/Users/kk/PycharmProjects/ProjectNothing/day10/10-4 globals locals 函数.py', '__cached__': None, 'a': 1, 'b': 2, 'func': <function func at 0x104e4d430>}
2 {'__name__': '__main__', '__doc__': '\ntest\ninfos\n', '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x104dc8310>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/Users/kk/PycharmProjects/ProjectNothing/day10/10-4 globals locals 函数.py', '__cached__': None, 'a': 1, 'b': 2, 'func': <function func at 0x104e4d430>}
'''


# 以上得知：
    # globals() 返回字典，字典内kv对为全局作用域里的所有内容。
    # locals() 返回字典，字典内kv对为局部作用域（也就是当前作用域）里的所有内容。