'''
14.看代码写结果
def func():
    count = 1
    def inner():
        nonlocal count
        count += 1
        print(count)
    print(count)
    inner()
    print(count)


func()



'''

# #1
# #2
# def func():
#     count = 1
#     def inner():
#         nonlocal count
#         count += 1
#         print(count)
#     print(count)    # 1
#     inner()         # print 2
#     print(count)    # print 2


# func()