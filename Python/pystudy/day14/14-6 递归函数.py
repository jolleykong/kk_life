
# def func(n):
#     print(n)
#     n+=1
#     func(n)
# func(1)     # 递归996次。 不同的机器有不同的结果， 996~998之间

# 官网规定，默认的递归最大深度为1000次，防止内存炸掉。
# 如果递归超过百次还不能够解决问题，那么别用递归方式了，不合适。

#可以手动调整递归限制

# import sys
# print(sys.setrecursionlimit(1000000))   # 也不是绝对值，会根据电脑配置的原因而不同。
#     # mac上到了30828，小新2490。。。
# def func(n):
#     print(n)
#     n+=1
#     func(n)
# func(1)  


# 猜年龄
# 4. dd 说比cc大两岁
# 3. cc 说比bb大两岁
# 2. bb 说比aa大两岁
# 1. aa 说她18岁

def age(n):     # n 为询问的次数
    if n == 1:
        return 18
    else:
        return age(n-1) + 2

print(age(4))
    # age(4) --> return age(3) + 2
        # age(3) --> return age(2) + 2
            # age(2) --> return age(1) + 2
                # age(1) --> return 18.
    # age(4) == age(1) + 2 + 2 + 2

# 拆列表
l1 = [1,3,5,['aa','bb',34,[33,35,[11,23]]],[77,88],66]

tmp_list = []
def slist(list1):
    
    for i in list1:
        # if '__iter__' in dir(i):
        if type(i) == list:
            slist(i)
        else:
            tmp_list.append(i)
    return tmp_list

print(slist(l1))