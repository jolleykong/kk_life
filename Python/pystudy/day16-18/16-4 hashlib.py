# hashlib
# 加密模块。散列算法。

# 如何加密？ 将一个bytes类型的数据通过hashlib转换成一个等长度的16进制数据。过程不可逆。
# 相同的bytes类型的数据通过相同的加密方法得到的数字绝对相同。同理，不相同的页绝对不同。


# hashlib使用方法
import hashlib

# md5 ，安全系数最低但是效率很高。
ret = hashlib.md5() # 创建一个md5算法的加密对象
ret.update('abc'.encode('utf-8'))   # 将字符更新到这个加密对象
print(ret)
print(ret.hexdigest())      # 用16进制方式显示这个加密对象

## 加固定盐，在每一个加密之前加一个固定盐
ret = hashlib.md5('我是固定盐前缀'.encode('utf-8')) # 创建一个md5算法的加密对象，包含固定盐，也参与后面加密的内容的原文
ret.update('abc'.encode('utf-8'))   # 将字符更新到这个加密对象
print(ret)
print(ret.hexdigest())      # 用16进制方式显示这个加密对象

## 加动态盐，在每一个加密之前加一个动态盐，防止固定盐外泄的隐患。
username = input('username:').strip()
pwd = input('pwd').strip()

ret = hashlib.md5(username[::2].encode('utf-8')) # 创建一个md5算法的加密对象，对用户名切片参与后面加密的内容的原文
ret.update(pwd.encode('utf-8'))   # 将字符更新到这个加密对象
print(ret)
print(ret.hexdigest())      # 用16进制方式显示这个加密对象



# 一般的，用固定盐就行了。



# sha系列：安全系数高，耗时也高。
ret = hashlib.sha512()
ret.update('aaa'.encode('utf-8'))
re = ret.hexdigest()
print(re)

# sha系列也支持加盐。略。

