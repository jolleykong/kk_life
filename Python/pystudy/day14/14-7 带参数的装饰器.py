# 一个装饰器验证不同的多套的用户名密码，最好使用带参数的装饰器
'''
def wrapper(f):
    def inner(*args,**kwargs):
        if qq:
            pass
        elif tiktok:
            pass
        ret = f(*args,**kwargs)
        return ret
    return inner

@wrapper
def qq():
    # 使用qq的验证机制
    print('using qq')

@wrapper
def tiktok():
    # 使用tiktok的验证机制
    print('using tiktok')
'''

'''
# 做一个三层嵌套函数，也就是装饰器外再套一层。
def wrapper_out(n,*args,sex='M',):
    def wrapper(f):
        def inner(*args,**kwargs):
            ret = f(*args,**kwargs)
            return ret
        return inner
    return wrapper


func = wrapper_out(1)   # func == wrapper_out(1,*args,sex='M') == return wrapper，没括号
#  func() == wrapper()

# 这里定义一个func1
def func1():
    print('func1 is me!')


fun_a = func(func1) # fun_a == wrapper(func1) == return inner，没括号
fun_a() # == inner(), f == func1



# 明白了三层嵌套的传参逻辑之后， 我们实现一下前面的例子
def wrapper_new1(n,*args,sex='M',):
    print(n)
    def wrapper(f):
        def inner(*args,**kwargs):
            ret = f(*args,**kwargs)
            return ret
        return inner
    return wrapper

@wrapper_new1('tencent')
def qq():
    # 使用qq的验证机制
    print('using qq')
qq()
    # tencent           # 可以看到对装饰器传参，被接受了。
    # using qq          # 但是为什么这一步也执行了？对wrapper_new('tencent') 并没带f参数。

    # 看到带参数的装饰器，分两步执行
        # 1.执行wrapper_new1('tencent') 这个函数，
        #   把相应的参数'tencent' 传给n，并且得到返回值 wrapper 函数名。
        # 2.将@与wrapper相结合，得到之前熟悉的标准版装饰器的调用方式。
        #   按照装饰器的执行流程执行。
'''

# 练习题，使用带参数的装饰器，实现统一登录。
    # 腾讯、网易、新浪 各自有自己的验证文件
    # 选择对应账号体系，完成登录验证后，即可完成统一登录。
'''
# 我发现这么写都不用装饰器去实现统一登录了。

def getpwd(company):
    pwdfile = './day14/' + company.strip()
    with open(pwdfile,mode='r') as f:
        infos = f.readlines()
        dic_getpwd = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in infos }
    return dic_getpwd

def login(company,user,pwd):
    dic_pwd = getpwd( company.strip() )
    if dic_pwd.get(user) :
        if dic_pwd[user] == pwd:
            print(f'欢迎使用{company}账号登录！你好{user}')
            return True

def auth():
    company = input('choose company:').strip()
    username = input('username:').strip()
    password = input('password:').strip()
    login(company,username,password)
    return None

auth()


# 不需要装饰器。
# def wrapper_out(n,*args):
#     def wrapper(f):
#         def inner(*args,**kwargs):
#             ret = f(*args,**kwargs)
#             return ret
#         return inner
#     return wrapper

'''


# 非要用带参数装饰器写， 我感觉很麻烦而且很呆， 不过就当练习装饰器了， 哈哈哈

def wrapper_out(company):
    def wrapper(f):
        def inner(*args,**kwargs):
            if company == 'qq':
                with open('./day14/qq',mode='r') as file:
                    infos = file.readlines()
            elif company == 'nete':
                with open('./day14/163',mode='r') as file:
                    infos = file.readlines()
            elif company == 'sina':
                with open('./day14/sina',mode='r') as file:
                    infos = file.readlines()

            dic_getpwd = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in infos }

            dic_pwd = dic_getpwd        # 懒得改后面登录判断的变量名。
            # print(dic_pwd)
            print(f'即将使用{company}账号登录应用程序................')

            username = input('username:').strip()
            password = input('password:').strip()

            if dic_pwd.get(username) :
                if dic_pwd[username] == password:
                    print(f'欢迎!你好{username}!')
                    ret = f(*args,**kwargs)
            return ret
        return inner
    return wrapper


@wrapper_out('qq')
def tencent():
    print('成功使用qq账号登录统一应用')
    return 1

@wrapper_out('nete')
def nete():
    print('成功使用网易账号登录统一应用')

@wrapper_out('sina')
def sina():
    print('成功使用sina账号登录统一应用')


tencent()
nete()
sina()
