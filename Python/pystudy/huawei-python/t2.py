'''
Python编程知识-简单的加法

受限于篇幅原因，本课程未完全覆盖 Python 中的全部语法，欢迎你将更全面的 Python 学习笔记分享到 AI Gallery Notebook 版块获得成长值，分享方法请查看此文档。
题目描述

输入一个数组和一个数字，在数组中查找两个数，使得它们的和正好是输入的那个数字。

如果有多对数字的和等于输入的数字，输出任意一对即可。

例如：输入数组1 2 4 7 11 15和数字15。

由于4+11=15，因此输出4和11。

l = input()  # 输入字符串，以空格为间隔，请自行实现将字符串转换为数组的代码

n = input()  # 输入数字

def func():
    # 在此编写代码
    print(a,b)
func()

'''

l = input("some nums")  # 输入字符串，以空格为间隔，请自行实现将字符串转换为数组的代码
list_l = l.split()
n = input("a number")  # 输入数字
def func():
    for i in range(len(list_l)):
        if str(int(n) - int(list_l[i])) in list_l:
            a = list_l[i]
            b = int(n) - int(a)
            print(a, b)
            break

func()