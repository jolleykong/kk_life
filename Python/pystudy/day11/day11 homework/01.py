'''
1.写出下列代码的执行结果
def func1():
    print( 'in func1')

def func2():
    print( 'in func2')

ret = func1
ret()       #' in func1'

ret1 = func2
ret1()      #'in func2'

ret2 = ret
ret3 = ret2

ret2()      #' in func1'
ret3()      #' in func1'

'''

