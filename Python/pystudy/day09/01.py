# 一个函数就是一个功能。以完成一件事为导向。
# 函数减少代码的重复性，增强代码的可读性
# 函数只有被调用的时候才执行。
'''
- 函数的返回值 return
    - 终止函数
    - return 单个值
    - return 多个值

- 函数的参数
    - 实参角度： 位置参数，关键字参数，混合参数
    - 形参角度： 位置参数，默认参数，
'''

# 形参 实参

# 位置参数
    # 数量和顺序都是从左至右，多一少一都不行

    # 写个函数，接受两个int参数，并返回输出较大的那个值
def maax(x,y):
    if x > y:
        return x
    elif y > x:
        return y
    else:
        return 0
    return 1

print(maax(10,11),maax(11,11),maax(12,11))

# 三元运算符
'''
当 
if a > b :
    return b
else:
    return a
时， 可以理解成：
c = 0
if a > b :
    c = b
    return c
else:
    c = a
    return c
此时，可以写成三元运算符:
c = a if a > b else b
'''
# 使用三元运算符改写
def maax2(x,y):
    result = x if x > y else y
    return result

print(maax2(10,11),maax2(11,11),maax2(12,11))

# 进一步简写
def maax3(x,y):
    return x if x > y else y

print(maax3(10,11),maax3(11,11),maax3(12,11))



# 关键字参数
# 混合传参： 位置参数一定要在最前面，关键字参数放在位置参数后面

# 默认参数 ，常用的值。
    # def foo(v,x,y,p='default')




''' 作业
1.写函数，检查获取传入列表或元组对象的所有奇数位索引对应的元素，并将其作为新列表返回给调用者。

2.写函数，判断用户传入的对象（字符串、列表、元组）长度是否大于5。

3.写函数，检查传入列表的长度，如果大于2，那么仅保留前面两个长度的内容，并将新内容返回给调用者。

4.写函数，计算传入函数的字符串中 数字、字母 以及 其他 的个数，并返回结果。

5.写函数，接受两个数字参数，返回比较大的那个数字。

6.写函数，检查传入字典的每一个value的长度，如果大于2，那么仅保留前两个长度的内容，并将新内容返回给调用者。

7.写函数，此函数只接受一个参数，且此参数必须是列表类型。此函数完成的功能是返回给调用者一个字典，字典的kv为此列表的索引及对应元素。

8.写函数，接受4个参数：姓名，性别，年龄，学历。用户输入四个内容，将四个内容传入给函数，函数将内容追加到一个student_msg文件中。

9.升级8题，支持用户持续输入，输入q退出。性别默认为男，遇到女则输入女。

10.写函数，用户传入修改的文件名，与要修改的内容，执行函数，完成整个文件的批量修改操作。
'''
# 1
def findodd(list):
    return list[0::2]

li = [1,2,3,4,5,6,7,8,9,0,]
print(findodd(li))

# 2
def morethan5(obj):
    if len(obj) > 5:
        result = 'yes'
    else:
        result = 'no'
    return result

ob1 = [1,2,3,4,5,6,7,8,9]
ob2 = 'abcdedf'
ob3 = 'abc'
print(morethan5(ob1),morethan5(ob2),morethan5(ob3))

# 3
def just2(obj):
    if len(obj) > 2:
        result = obj[0:2]
    else:
        result = obj
    return result
    # result = obj[:2] if len(obj) > 2 else obj
    # return result
ob1 = [1,2,3,4,5,6,7,8,9]
ob2 = 'abcdedf'
ob3 = 'abc'
print(just2(ob1),just2(ob2),just2(ob3))


# 4.写函数，计算传入函数的字符串中 数字、字母 以及 其他 的个数，并返回结果。
def counts(obj):
    tmp_dict = {}
    for i in obj:
        # tmp_dict[type(i)] = tmp_dict.get(type(i),0) + 1  # 识别的全是str
        if i.isdecimal():
            tmp_dict['int'] = tmp_dict.get('int',0) + 1
        elif i.isalpha():
            tmp_dict['alpha'] = tmp_dict.get('alpha',0) + 1
        else:
            tmp_dict['others'] = tmp_dict.get('others',0) + 1
    return tmp_dict

ob4 = 'ab134a8fb!@*#'
print(counts(ob4))

# 6.写函数，检查传入字典的每一个value的长度，如果大于2，那么仅保留前两个长度的内容，并将新内容返回给调用者。
def mkdc(key,value):
    dic = {}
    if len(value) > 2:
        value = value[:2]
    dic[key] = value
    return dic

na = mkdc(key='name',value='kongyan')
nb = mkdc('age','30')
print(na,nb)

# 6.传入一个字典，检查字典的value长度，如果大于2，那么仅保留前两个长度的内容，并将新内容返回给调用者。


#7.写函数，此函数只接受一个参数，且此参数必须是列表类型。此函数完成的功能是返回给调用者一个字典，字典的kv为此列表的索引及对应元素。
def list2dict(lists):          
    dict = {}
    if type(lists) == list:             # if isinstance(lists,list):
        for index in range(len(lists)):
            dict[index] = lists[index]
    return dict
li = ['a','b','c','d','ee','ff','ggg','h','j','i']
ld = list2dict(li)
print(ld)

#8.写函数，接受4个参数：姓名，性别，年龄，学历。用户输入四个内容，将四个内容传入给函数，函数将内容追加到一个student_msg文件中。
# def typein(name,sex,age,edu):
#     data = '姓名：%s，性别：%s，年龄：%s，学历：%s\n' %(name,sex,age,edu)
#     with open('student_msg',encoding='utf-8',mode='a') as filesm:
#         filesm.write(data)
#     # print(data)
#     return 0

# typein('a','b','c','d')

#9.升级8题，支持用户持续输入，输入q退出。性别默认为男，遇到女则输入女。
# def student_msg(name,age,sex,edu):
#     with open('student_msg.txt',encoding='utf-8',mode='a') as filesm:
#         filesm.write('name:{},age:{},sex:{},edu:{}\n'.format(name,age,sex,edu))
#     return 0

# flag = True
# while flag:
#     name = input('name:')
#     if name.upper() == 'Q' :
#         flag = False
#         break
#     sex = input('sex:')
#     if sex != '女':
#         sex = '男'
#     age = input('age:')
#     edu = input('edu:')
#     student_msg(name,sex,age,edu)

#10.写函数，用户传入修改的文件名，与要修改的内容，执行函数，完成整个文件的批量修改操作。
# rep(filename,sor,target)
def rep(filename,source,target):
    import os
    tmpfile = filename+'.swp'
    with open(filename,mode='r+') as sourcefile, open(tmpfile,mode='w') as tmp:
        for line in sourcefile:
            cons = line
            cons = cons.replace(source,target)
            tmp.write(cons)
    os.rename(filename,filename+'.bak')
    os.rename(tmpfile,filename)
    return 0

rep('student_msg','学历','aa')