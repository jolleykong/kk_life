# p12.求1-2+3-4+5 ... 99的所有数的和
c = 0
for i in range(1,100) :
    if i % 2 == 0 :
        c = c - i
    else :
        c = c + i
    i+=1
print(c)