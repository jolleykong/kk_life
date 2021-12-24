'''
Python编程知识-罗马数字转换器

把传入的数字转变为罗马数字。（0~9）

转换后的罗马数字字母必须都是大写。
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''

def conv():

    nums = input('nums:').strip()
    new_nums = []
    dics = {
        1:'I',
        2:'II',
        3:'III',
        4:'IV',
        5:'V',
        6:'VI',
        7:'VII',
        8:'VIII',
        9:'IX',
        0:'N'
    }

    if nums.isdigit(): 
        for i in nums:
            new_nums.append(dics[int(i)])
        print(' '.join(new_nums))
    else:
        print('能不能好好玩？')

    return 0
while 1:
    conv()
