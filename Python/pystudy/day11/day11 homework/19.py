'''
19.写代码，用while循环模拟for的循环机制


'''
in_obj = [1,2,34,5,6,7,7]
obj = iter(in_obj)      # 转换为迭代器这一步， 需要在循环之外。 不然就无限循环1了。
while 1:
    try:
        print(obj.__next__())
    except StopIteration:
        break
