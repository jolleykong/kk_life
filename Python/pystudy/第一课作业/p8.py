# p8.使用while循环输出1 2 3 4 5 6     8 9 10
# 方法1：
i = 1
while i <= 10 :
    if i == 7 :
        i+=1
        print(' ',end=' ')  
        #pass   # 也可以直接 pass后i+=1
    else :
        print(i,end=' ')
        i+=1

# 方法2：
# 也可以直接 pass后i+=1
i = 1
while i <= 10 :
    if i == 7 :
        pass   
    print(i,end=' ')
    i+=1

# 方法3：
i = 1
while i <= 10 :
    if i == 7 :
        i+=1  
    print(i,end=' ')
    i+=1