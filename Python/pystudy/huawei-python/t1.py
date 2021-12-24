'''
题目描述

输入一个int型整数，按照从右向左的阅读顺序，返回一个不含重复数字的新的整数。 保证输入的整数最后一位不是0。

输入描述： 输入一个int型整数

输出描述： 按照从右向左的阅读顺序，返回一个不含重复数字的新的整数

示例1 输入： 30010733 输出： 3701

'''
num = input('input num:')   # 112233445555566780009
# 转为list
list_num = list(num)
# 去重并转为list
uniq_num = list(set(num))
# 倒序
reverse_num = list_num[::-1]
# 直接将list_num.reverse() 也可以
# 恢复元素排列位置
uniq_num.sort(key=reverse_num.index)
# 拼合元素
res = int(''.join(uniq_num))
print(res)