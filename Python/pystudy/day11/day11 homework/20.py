'''
20.写函数，传入n个数，返回字典：{'max':最大值,'min':最小值}

def maxmin(*args):
    obj = list(args)
    return {'max':max(obj),'min':min(obj)}
'''

def maxmin(*args):
    obj = list(args)
    return {'max':max(obj),'min':min(obj)}

print(maxmin(1,2,3,4,5,6,7,8,9,0,0,2,4,5,7,555,1,-98))