# p5.使用 while 循环实现输出 1,2,3,4,5, 7,8,9, 11,12


c = 0
while c <= 5:
    i = 1
    while i <= 12 :
        if i in [6,10] :
            i+=1
            print(' ',end='')
        else:
            print(i,end=',')
            i+=1
    print('\n')
    c+=1