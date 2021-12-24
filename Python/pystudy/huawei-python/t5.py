'''
Python编程知识-学习成绩划分


输入一个0-100之间的整数成绩，

学习成绩>=90的同学，用A表示；

学习成绩60-89分的同学，用B表示；

学习成绩<60的同学，用C表示。

例如：输入98，输出A
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''
def level():
    score = input('输入分数：').strip()
    if score.isdigit():
        score = int(score)
        if score >= 90:
            level = 'A'
        elif score >=60 and score <=89:
            level = 'B'
        else:
            level = 'C'
        print(level)
        return level
    else:
        print('好好输入！')

while 1:
    level()
