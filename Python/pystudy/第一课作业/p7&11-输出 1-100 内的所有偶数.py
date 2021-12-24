# p7.使用 while 循环实现输出 1-100 内的所有偶数
i = 1
while i <= 100:
    if i % 2 == 0 :
        print(i,end=',')
    i+=1


# p11.输出 1-100 内的所有偶数
for i in range(1,101) :
    if i % 2 == 0 :
        print(i,end=' ')
