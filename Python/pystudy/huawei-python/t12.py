'''
Python编程知识-电话号码验证器



如果传入的字符串是一个有效的中国电话号码格式，则返回true。 
例如： 134-4562-5655 13469587456 1314 122 9899
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''
import string
def phone():
    ava = ( 130, 131, 132,
            133, 134, 135,
            136, 137, 138,
            139, 147, 150,
            151, 152, 153,
            155, 156, 157,
            158, 159, 166,
            177, 180, 181,
            182, 183, 185,
            186, 187, 188,
            189, 197, 199 )

    ipt = input('电话号码：').strip()
    tmp = []
    # 符号清洗
    for i in ipt:
        if i in string.punctuation:
            pass
        else:
            tmp.append(i)
    ipt = ''.join(tmp)
    if len(ipt) == 11:
        if ipt.isdigit():
            if int(ipt[0:3]) in ava:
                print('True')
                return True

while 1:
    phone()
