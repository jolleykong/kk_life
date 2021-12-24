'''
Python编程知识-HZF的魔法棒

HZF有一个魔法棒，魔法棒有很多功能，
其中最简单的是对字母的改变：
    可以将大写字母变成小写字母(A->a,B->b,C->c…Z->z)，
    将小写字母变成大写字母(a->A…z->Z)，魔法对数字不生效。
    
    HZF让你告诉他改变之后的字符串是什么样的。

输入 输入一个字符串(只包含大小写字母和数字)。每个字符串字符数(0 < n <= 1000)。

输出 输出改变后的字符串。

样例 输入样例 1

abC02 输出样例 1

ABc02

输入样例 2

aceACE 输出样例 2

ACEace 提示样例 2
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''
import string
def magic():
    ipt = input('来！：').strip()
    result = []
    for i in ipt:
        if i in string.ascii_lowercase:
            i = i.upper()
        elif i in string.ascii_uppercase:
            i = i.lower()
        # else: i = i
        result.append(str(i))
    print(f'{ipt} 变成了 {"".join(result)} !')
    return 0

while 1:
    magic()