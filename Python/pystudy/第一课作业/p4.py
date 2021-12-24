# p4.使用while循环实现输出2-3+4-5+6...+100 的和

i = 2
# c 为和
c = 0
while i <= 100:
    # 偶数则做加法
    if i % 2 == 0:
        c = c + i
    # 奇数则做减法
    elif i % 2 != 0:
        c = c - i
    # 自增
    i+=1
else:
    # 结束后输出和值
    print(c)

