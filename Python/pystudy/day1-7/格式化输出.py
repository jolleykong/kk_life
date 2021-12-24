name = input('name:')
age = input('age:')
job = input('job:')

msg = '''-=-=-=-=-=-=-=-=-
Hi, %s
You are %s years old.
Do your work of %s.
Point is %s%%.
Bye!
''' % (name,age,job,age)
# %s .... % (foo1,...,fooN) 按顺序替换字符串类型。
# %d  数字

print(msg)



# 这种方法， 所有%都会被认为是占位符，如果想表达单纯的百分号时，如想表达1%，需要用%% 来表达。 就是转义了。



# bool 和int之间的转换
## int --> bool， 非0则True，为0则False
## bool --> int， True为1，False为0


# 整数做or运算
# x or y，x为真则为x，为假则为y。

# 整数做and运算
# x and y, x为False则返回x，否则返回y
# 因为非0为True，所以 整数之间and 总是返回y

# 优先级  not > and > or


