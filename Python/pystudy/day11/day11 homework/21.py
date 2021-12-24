'''
21.写函数，传入一个参数n，返回n的阶乘。如cal(7) ，计算7*6*5*4*3*2*1


'''
def k_cal(n):
    count = 1
    for i in range(1,n+1):
        count *= i
    return count

print(k_cal(7))
