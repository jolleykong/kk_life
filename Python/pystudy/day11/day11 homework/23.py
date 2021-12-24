'''
23.写代码完成99乘法表。
'''

for a in range(1,10):
    for b in range(1,a+1):
        print(f'{a}x{b}={a*b}\t',end='')
    print('\n',end='')

