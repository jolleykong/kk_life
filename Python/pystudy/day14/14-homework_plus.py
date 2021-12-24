# 1.请实现一个装饰器，限制该函数被调用的频率，如：10秒一次。借助time模块，time.time()

    # 得用闭包技巧。
'''
import time

def wrappera(f):
    runlist = 0
    def inner(*args,**kwargs):
        now = time.time()
        if len(runlist) == 0:   # 第一次执行
            ret = f(*args,**kwargs)
            runlist.append(time.time())
            return ret
        else: 
            if now - runlist[0] >= 10:
                ret = f(*args,**kwargs)
                runlist[0] = time.time() 
                return ret
            else:
                print(f'时间没到. 上次执行时间：{runlist[0]} ,本次执行时间：{now}，仅仅间隔了{now - runlist[0]}')
    return inner

@wrappera
def f():
    print('I am a line from a function named f.')
    time.sleep(2)


f()                     # I am a line from a function named f.
time.sleep(10)
f()                       # I am a line from a function named f.
time.sleep(1)
f()                 # 时间没到. 上次执行时间：1632294314.38681 ,本次执行时间：1632294315.391737，仅仅间隔了1.0049269199371338
time.sleep(2)
f()                     # 时间没到. 上次执行时间：1632294314.38681 ,本次执行时间：1632294317.3927271，仅仅间隔了3.0059170722961426
'''



import time

def wrappera(f):
    runlist = 0
    def inner(*args,**kwargs):
        now = time.time()
        nonlocal runlist            # 没必要用list方式， 其实是前面自己忘了怎么用了。
        if runlist == 0:   # 第一次执行
            ret = f(*args,**kwargs)
            runlist = time.time()
            return ret
        else: 
            if now - runlist >= 10:
                ret = f(*args,**kwargs)
                runlist = time.time() 
                return ret
            else:
                print(f'时间没到. 上次执行时间：{runlist} ,本次执行时间：{now}，仅仅间隔了{now - runlist}')
    return inner

@wrappera
def f():
    print('I am a line from a function named f.')
    time.sleep(2)


f()                     # I am a line from a function named f.
time.sleep(10)
f()                       # I am a line from a function named f.
time.sleep(1)
f()                 # 时间没到. 上次执行时间：1632295112.191246 ,本次执行时间：1632295113.192721，仅仅间隔了1.0014748573303223
time.sleep(2)
f()                     # 时间没到. 上次执行时间：1632295112.191246 ,本次执行时间：1632295115.197945，仅仅间隔了3.0066990852355957

# 2.写出下列代码片段的输出结果
'''
def say_hi(func):
    def wrapper(*args,**kwargs):
        print('HI')
        ret = func(*args,**kwargs)
        print('BYE')
        return ret
    return wrapper

def say_yo(func):
    def wrapper(*args,**kwargs):
        print('YO')
        return func(*args,**kwargs)
    return wrapper

@say_hi
@say_yo
def func():
    print('rock&roll')

func()

hi
yo
rock&roll
bye

'''


# 3.编写装饰器完成下列需求
    # 31. 用户有两套账号密码，一套为京东账号密码，一套为淘宝账号密码，分别保存在两个文件中。
    # 32. 设置四个函数，分别代表京东首页，京东超市，淘宝首页，淘宝超市。
    # 33. 启动程序后，呈现用户的选项为：
        # 1.  京东首页
        # 2.  京东超市
        # 3.  淘宝首页
        # 4.  淘宝超市
        # 5.  退出程序
    # 34. 四个函数都加上认证功能，用户可任意选择。用户选择京东超市或者京东首页，只要输入一次京东的账号和密码并成功，则这两个函数都可以任意访问，
    # 用户选择淘宝超市或者淘宝首页，只需要输入一次淘宝账号密码并成功，则这两个函数都可以任意访问。
    # 相关提示：用带参数的装饰器，装饰器内部加入判断，验证不同的账户密码。

'''

dic_main = {
    1:{'name':'京东首页','fun_name':'main_jd','status':'login','company':'jd' },
    2:{'name':'京东超市','fun_name':'shop_jd','status':'login','company':'jd'  },
    3:{'name':'淘宝首页','fun_name':'main_tb','status':'login','company':'tb'  },
    4:{'name':'淘宝超市','fun_name':'shop_tb','status':'login','company':'tb'  },
    5:{'name':'退出程序','fun_name':'exit_main','status':'exit','company':None }
        }

login_status = {}
    # login_status = {company:status,company:status ...}

def auth_out(company):
    # 根据传入公司，生成对应密码字典
    auth_file_name = "./day14/"+company
    with open(auth_file_name,mode='r') as file:
            l1 = file.readlines()
            dic1 = { i.strip().split("|")[0]:i.strip().split("|")[1] for i in l1}

    def auth_wrapper(f):
        
        def inner(*args,**kwargs):

            # 登录状态存在且正确，则执行菜单动作。
            if login_status.get(company):
                if login_status[company] == True:
                    ret = f(*args,**kwargs)
                    return ret
            
            # 否则进入登录页面
            else:
                username = input('username:').strip()
                pwd = input('pwd:').strip()

                # 登录验证成功，将登录状态记录。
                if dic1.get(username):
                    if dic1[username] == pwd:
                        login_status[company] = True
                else:
                    print('密码错误')

            print(login_status)
        return inner
    return auth_wrapper


@auth_out('jd')
def main_jd():
    print('欢迎访问京东首页')

@auth_out('jd')
def shop_jd():
    print('欢迎访问京东超市')

@auth_out('tb')
def main_tb():
    print('欢迎访问淘宝首页')

@auth_out('tb')
def shop_tb():
    print('欢迎访问淘宝超市')



def login():
    # 输出功能菜单
    main_menu = [ str(i)+'.'+dic_main[i]['name'] for i in dic_main ]
    for menu in main_menu:
        print(menu)

    # 循环状态标识
    flag =  True
    while flag :
        # 这块懒了，没进一步做输入类型判断，因此输入非法会报错
        choose = input('选择程序：').strip()
        choose = int(choose)

        if choose <= len(dic_main) and dic_main.get(choose) :
            # 存在且功能不为退出，则执行对应登录函数
            if dic_main[choose]['status'] != 'exit':
                # 标记公司标识。 但是这里没用上这个逻辑，本想通过这个标识传给装饰器语法糖。不知道能否实现。
                # comp = dic_main[choose]['company']

                # 进入菜单。
                f_name = dic_main[choose]['fun_name']
                exec(f_name+'()')

            # 如果功能为退出，则执行退出。
            else :
                flag = False
                print('再见，去商场吧！')
                exit
        # else :    # 这步永远不会出现。除非dic_main定义出现错误。所以这一步注释了。
        #     print('重新选择功能。')
        else :
            print('重新选择功能。')

login()

'''

# 4. 用递归函数完成斐波那契数列：1，1，2，3，5，8，13，21..... 第三个数为前两个数的和，但是最开始的1，1是特殊情况，可以单独讨论。

'''
import sys
print(sys.setrecursionlimit(50))
def f1(a,b):
    c = a+b
    d = b+c
    print(str(a)+','+str(b)+',',end='')
    return f1(c,d)

print(f1(1,1))

#1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181,6765,10946,17711,28657,46368,75025,121393,196418,317811,514229,832040,1346269,2178309,3524578,5702887,9227465,14930352,24157817,39088169,63245986,102334155,165580141,267914296,433494437,701408733,1134903170,1836311903,2971215073,4807526976,7778742049,12586269025,20365011074,32951280099,53316291173,86267571272,139583862445,225851433717,365435296162,591286729879,956722026041,1548008755920,2504730781961,4052739537881,6557470319842,10610209857723,17167680177565,27777890035288,44945570212853,72723460248141,117669030460994,190392490709135,308061521170129,498454011879264,806515533049393,1304969544928657,2111485077978050,3416454622906707,5527939700884757,8944394323791464,14472334024676221,23416728348467685,37889062373143906,61305790721611591,99194853094755497,160500643816367088,259695496911122585,420196140727489673,679891637638612258,1100087778366101931,1779979416004714189,2880067194370816120,4660046610375530309,7540113804746346429......
'''

# 5. 给l1 = [1,1,2,2,3,3,6,6,5,5,2,2,] 去重，不能使用set集合。
# 思路，创建l2，向l2中插入l1的元素， 同时判断元素是否存在，如果存在则放弃。
l1 = [1,1,2,2,3,3,6,6,5,5,2,2,]
l2 = []
for i in l1:
    if i in l2:
        pass
    else:
        l2.append(i)

print(l2)   #[1, 2, 3, 6, 5]

# 思路，对l1的元素做count，如果大于1，则删除掉这个元素的第一个， 循环到都不大于1为止。
l3 = [1,1,2,2,3,3,6,6,5,5,2,2,]
for i in l3:
    while l3.count(i) > 1:
        l3.remove(i)
print(l3)