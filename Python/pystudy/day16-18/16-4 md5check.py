import hashlib

# 文件的一致性校验
# hashlib只对str输入合法。所以文件需要成为str类型。
ret = hashlib.md5()
with open('mutliline_1.json',mode='rb') as file:
    content = file.read()

ret.update(content)
print(ret.hexdigest())    # 59e7fc7b4fdf7dccc2fbb0ebee2ecdd2

ret = hashlib.md5()
with open('mutliline_2.json',mode='rb') as file:
    content = file.read()

ret.update(content)
print(ret.hexdigest())      # 7b9e9abd013e4f6ac826369bb1525ad7


# 但是文件超级大的话， 超出内存大小的话， 上面这个办法就有局限性了。

# 可以通过分布update的方式
#abcdefghi
s1 = 'abc'
s2 = 'def'
s3 = 'ghi'

ret = hashlib.md5()
ret.update(s1.encode('utf-8'))
ret.update(s2.encode('utf-8'))
ret.update(s3.encode('utf-8'))
print(ret.hexdigest())  # 8aa99b1f439ff71293e95357bac6fd94


ret = hashlib.md5()
ret.update('abcdefghi'.encode('utf-8'))
print(ret.hexdigest())  # 8aa99b1f439ff71293e95357bac6fd94

# 所以文件过大的话，可以使用for循环分段去进行md5分步update。
# 但是文件不适合以行做单位去读取，按照字节去读比较合理
ret = hashlib.md5()
with open('mutliline_1.json',mode='rb') as f1:
    while 1:
        con = f1.read(10)
        if con :
            ret.update(con)
        else:   # 如果获取到的内容为None 则结束。
            print(ret.hexdigest())
            break
        # 59e7fc7b4fdf7dccc2fbb0ebee2ecdd2