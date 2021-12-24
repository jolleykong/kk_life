# 列表排序
l1 = ['a','b','c','g','a','p','q','z','g','j','k']
# 将列表从大到小排序
l2 = l1.copy()
l2.sort()
print(l2)
# 将列表从小到大排序
l3 = l1.copy()
l3.sort(reverse=1)
print(l3)
# 将列表反转
l4 = l1[-1::-1]
print(l1)
print(l4)

# 构建一个这样的列表
# [['_','_','_'],['_','_','_'],['_','_','_']]
li = []
lo = []
for rang in range(0,3):
    li.append('_')
    lo.append(li)
print(lo)
# print(lo[0] is lo[1]) # isTrue。 这样写法元素是一个对象，而且元素中包含多少个元素，大列表中就会存在多少个元素。



# 寻找水仙花数。是一个三位数，三位数的每一位的三次幂的和还等于这个数。如： 153 ， 1**3 + 5**3 + 3**3 == 153.
# 笨方法：遍历
results = []
for i in range(100,1000):
    if int(str(i)[0])**3 + int(str(i)[1])**3 + int(str(i)[2])**3 == i:
        results.append(i)
print(results)
# result: [153, 370, 371, 407]

# 任意长度数字判断
# num = input('a decimal:')
# count = 0
# if num.isdecimal():
#     for i in num:
#         count += int(i)**3
#     if count == int(num):
#         print(num,'is sxh')
#     else:
#         print('not')
# else:
#     print('not a decimal.')

# # 计算任意范围内的水仙花数。数字长度过长后性能很差。
# lens = input('how long?')

# results = []
# if lens.isdecimal():
#     lens = 10**int(lens)  # 范围长度
# # 对范围内的数做遍历
# for i in range(lens):
#     count = 0
#     # 对每一个数的位数做拆解
#     # 转为字符串方便做索引
#     i = str(i)
#     # print(type(i))
#     # 循环遍历数字i的每一位
#     for j in i:
#         # 每一位做三次幂运算后与count原结果相加并赋值给count
#         count += int(j)**3
#         # 如果count最终结果和数字i相等，那么就加入列表。
#     if count == int(i): # 之前这一步被缩进了，所以遇到370的时候会因为计算到第二位时即等于结果，导致值被插入了多次。
#         results.append(i)
# print(results) # 超过4位后结果状态不太对， 需要步进debug一下。



# 遍历名单列表。如果元素中包含关键字，则删除这个元素。
# names = ['马云','马化腾','马勒戈壁','白龙马','唐僧','沙和尚','沙老道','沙尼姑']
# # 包含马字全干掉。
# names_result = names.copy()
# # 这一步很关键。因为list在被remove后，改变了列表长度，元素的索引会变，而for循环是按照索引对位的，所以正序的时候会有元素被漏掉。
# for i in names_result[-1::-1]:
#     if '马' in i:
#         names_result.remove(i)
#     else:
#         print(i)
# print(names_result)

# 方法二：将符合条件的元素建立新list，然后循环这个临时list从原list中删除元素
# names_tmp = []
# names_result2 = names.copy()
# for i in names_result2:
#     if '马' in i:
#         names_tmp.append(i)
# for i in names_tmp:
#     names_result2.remove(i)
# print(names_result2)

# 统计车牌数量
cars =["鲁A32444","鲁B12333","京B8989M","黑C49678","黑C46555","沪B25041"]
locals={'沪':"上海","黑":"黑龙江","鲁":"山东","鄂":"湖北","湘":"湖南","京":"北京"}
# 输出结果为{'黑龙江':2,'xxx':m ...}
cars_dict = locals.fromkeys(locals.values(),0)      # day7的创建字典方法。
for i in cars:
    cars_dict[locals[i[0]]] += 1
print(cars_dict)


# 方法二：使用dict get()默认值的方式
'''
 提示： 当一个字典 dict = {'a':1,'b':2}时，我们对字典进行get
>>> dict.get('a')
1
>>> dict.get('b')
2
>>> dict.get('c')
None

我们可以在get方法中指定默认值，这样即使key不存在字典中，也不会返回None
>>> dict.get('c',2)
2
'''
cars_dict2 = {}
for i in cars:
    # 不存在则将默认值1赋值给key，存在则取值并+1， 完美。
    cars_dict2[locals[i[0]]] = cars_dict2.get(locals[i[0]], 1) + 1
print(cars_dict2)