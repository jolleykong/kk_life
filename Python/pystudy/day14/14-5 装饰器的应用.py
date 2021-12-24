# 典型场景
# 登录认证


# 定义一个访问记录
status = {
    'username':None,
    'login_status':False,
}

def getpwd():
    with open('./day13/register',mode='r') as reg:
        l1 = reg.readlines()
    # for i in l1:
    #     print(i.strip().split("|"))
# 生成用户名密码的kv字典
    dic1 = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in l1}
    return dic1



def login():
    dic1 = getpwd()
    fail_cnt = 0
    while fail_cnt < 3 and status['login_status'] != True:
        username = input('username:').strip()
        pwd = input('password').strip()

        # 用户名是否存在的判断，用get比直接dic1[key] 要好。
        if dic1.get(username) == pwd :
            status['login_status'] = True
            status['username'] = username
        else:
            fail_cnt += 1
    # if fail_cnt >= 3:
    #     return False
    # else:
    #     return True



def register():
    pass


# 装饰器
def auth(f):
    ''' 访问被装饰函数前，做一个三次登录认证功能，
    登录成功则允许访问被装饰函数，否则拒绝访问。'''
    def inner(*args,**kwargs):

        ''' 执行函数前的动作'''
        login()
        if status['login_status']:
            # 验证成功则允许访问被装饰的函数。
            r = f(*args,**kwargs)
            return r

        else:
            print('登录失败!')
            exit(1)

        ''' 执行函数后的动作'''
    return inner

@auth
def comments():
    print('朋友圈')

@auth
def friends():
    print('好友列表')

@auth
def diary():
    print('日记')


friends()
comments()
diary()
print(status)
