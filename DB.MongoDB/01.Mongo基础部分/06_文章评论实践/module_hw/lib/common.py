from core import src
# wrapper login
def wrapper_login(f):
    def inner(*args,**kwargs):
        if src.login_status == 0:
            src.login()
        else:
            print(f'你好{src.login_status}')
            ret = f(*args,**kwargs)
            return ret
    return inner


# wrapper login error
# 函数执行失败3次则报错或退出。
def warpper_3error(f):
    err_count = 0
    def inner(*args,**kwargs):
        war = True
        while war:
            nonlocal err_count
            if err_count < 3:
                ret = f(*args,**kwargs)
                
                if ret == True:
                    return ret
                else:
                    
                    err_count += 1
            else:
                print('错误次数过多。')
                war == False
                # 得归零，不然程序会有问题，死循环在break这一块。
                err_count = 0
                break
    return inner