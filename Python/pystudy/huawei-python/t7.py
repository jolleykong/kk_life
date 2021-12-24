'''
Python编程知识-回文检查器


如果给定的一个字符串是回文，那么返回true，否则返回false。

palindrome（回文），指在忽略标点符号、大小写和空格的前提下，正着读和反着读一模一样。
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。
'''
def huiwen():
    ipt = input('输入：').strip()
    # 过滤掉标点符号和空格
    tmp = []
    for i in ipt:
        if i.isalnum(): tmp.append(i.upper())
    tmp_1 = tmp[:int(len(tmp)/2)]
    tmp_2 = tmp[-1:-int(len(tmp)/2)-1:-1]
    # print(tmp_1,tmp_2)
    if tmp_1 == tmp_2:
        print(f'{ipt} IS HuiWen.')
    else:
        print(f'{ipt} ISNoT HuiWen.')




while 1:
    huiwen()

