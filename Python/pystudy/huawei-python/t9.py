'''
Python编程知识-凯撒密码


世界上最简单、最著名的加密方法是凯撒密码，也叫移位密码。在移位密码中，明文中的字母通过按照一个固定数目进行偏移后被替换成新的字母。

ROT13 是一个被广泛使用的编码技术，明文中的所有字母都被移动 13 位。因此，'A' ↔ 'N', 'B' ↔ 'O' 等等。

请编写一个函数，用于解码一个被 ROT13 编码的字符串，然后返回解码后的结果。

所有解码后的字母都必须为字母大写。请不要解码非字母的字符（例如，空格、标点符号），但你需要在结果中保留它们。
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''
# ord() chr()

# if i in [a-zA-Z]: ord(i)+13
import string
def encode():
    keylist = list(string.ascii_uppercase)
    # print(keylist)
    result = []
    source = input('加密前:').strip()
    for i in source:
        # 是字母则处理
        if i.isalpha():
            # 取字母在keylist的索引位
            source_idx = keylist.index(i.upper())
            # 偏移13位索引
            new_idx = source_idx + 13
            # 偏移后超出keylist长度则从头滚动
            if new_idx > len(keylist):
                new_idx = new_idx - len(keylist)
            # 将偏移后的字符输出到结果
            result.append(keylist[new_idx])
        # 不是字母则直接输出，跳过偏移加密
        else:
            result.append(str(i))
        
    # 输出结果
    print(f'密文：{"".join(result)}')
    return 0


def decode():
    keylist = list(string.ascii_uppercase)
    result = []
    source = input('密文:').strip()
    for i in source:
        if i.isalpha():
            source_idx = keylist.index(i.upper())
            new_idx = source_idx - 13
            result.append(keylist[new_idx])
        else:
            result.append(str(i))
    print(f'原文：{"".join(result)}')
    return 0


while 1:
    encode()
    decode()

