'''
用代码模拟博客系统
项目分析：
1. 首先程序启动，页面显示下面内容供用户选择：
    1.请登录
    2.请注册
    3.进入文章页面
    4.进入评论页面
    5.进入日记页面
    6.进入收藏页面
    7.注销账号
    8.退出整个程序

2. 必须实现的功能：
    1. 注册功能要求：
        a.用户名、密码要记录在文件中
        b.用户名要求：只能含有字母或者数字，不能含有特殊字符并且确保用户名唯一
        c.密码要求：长度在6~14字符之间
        d.超过三次登录还未成功，则退出整个程序

    2. 登录功能要求：
        a.用户输入用户名、密码进行登录验证
        b.登录成功后，才可以访问3-7选项，如果没有登录或者登录不成功，访问3-7选项时，要求登录。

    3. 进入文章页面要求：
        a.提示欢迎xx进入文章页面
        b.此时用户可以选择，直接写入内容，还是导入md文件
            # 如果选择直接写内容，让学生直接写文件名|文件内容，最后创建一个文章
            # 如果选择导入md文件，让用户输入已经准备好的md文件的文件路径，然后将此md的文件内容全部写入文章

    4.进入评论页面要求：
        # 提示欢迎xx访问评论页面

    5.进入日记页面要求：
        # 提示欢迎xx访问日记页面

    6.进入收藏页面要求：
        # 提示欢迎xx访问收藏页面

    7.注销账号要求：
        # 不退出程序，而是将已经登录的状态变成未登录状态

    8.退出程序

3.选做功能：
    1.评论页面要求：
        # 让用户选择要评论的文章。这个需要os模块实现。
        # 选择要评论的文章之后，现将原文章内容全部读一遍，然后输入要评论的内容，并过滤一些关键词。
        # 然后将评论内容写到文章的评论区的最下面
        <文章原内容>
        ...
        <评论区>：
        ---------------------
        <用户名>xx
        <评论该内容>xx
        <用户名>xx
        <评论该内容>xx
        ...

        如果原文章下面没有评论区以及分割线，则增加这两行再附上评论，否则直接在评论区最下面追加。
'''

import time
import os
from lib import common
from conf import setting
from dateutil import parser
import pymongo
# 用代码模拟博客系统
# 0 连接数据库
def conn_mongo(ip,port=27017):
    client = pymongo.MongoClient("mongodb://" + ip + ":" + str(port) + "/")
    return client

client = conn_mongo(setting.mongodb)
db = client["hw"]

# 获取当前格式化时间
def getftime():
    tm = time.time()
    st = time.localtime(tm)
    fm = time.strftime("%Y-%m-%d %H:%M:%S",st)
    return fm


# 0.load auth file.
def get_authdict():
    # db = client["hw"]
    acc_dict = {}
    result = db.account.find()
    for account in result:
        acc_dict[ account['username'] ] = account['pwd']
    return acc_dict

authdict = get_authdict()  # from get_authdict
login_status = 0    # 默认登录标记为0，登录成功则值为用户名

# 1.请登录
@common.warpper_3error
def login():
    global login_status
    if login_status == 0:
        username = input('username:').strip()
        password = input('password:').strip()
        
        if username in authdict and authdict.get(username) == password:
            login_status = username
            print(f'\n\n登录成功！ 你好{username}')
            flag = True
        else:
            print('验证失败')
            flag = False    
        return flag
    else:
        print(f'已经以{login_status}身份登录过了')
        time.sleep(2)
        print('\n\n\n')
        flag = True
        return flag


# 2.注册
#     注册功能要求：
#         a.用户名、密码要记录在文件中
#         b.用户名要求：只能含有字母或者数字，不能含有特殊字符并且确保用户名唯一
#         c.密码要求：长度在6~14字符之间
#         d.超过三次登录还未成功，则退出整个程序

def register():
    global authdict
    username = input('username:').strip()
    if username in authdict:
        print('用户名已经存在')
        return register()
    # 用户名不存在
    else:
        if username.isalnum():
            # 问询密码
            password = input('password:').strip()
            if len(password) >= 6 and len(password) <= 14:
                
                password2 = input('password again :').strip()

                if password == password2:
                    # 将注册信息写入account
                    db.account.insert_one({
                        "username":username,
                        "pwd":password,
                        "status":0,
                        "createtm":parser.parse(getftime())
                        }
                    )

                    print(f'注册成功！你的用户名为：{username}')
                    authdict = get_authdict()
                    return True
                else:
                    print('两次密码输入不一致。')
                    return register()
            else:
                print('密码长度在6~14字符之间。')
                return register()       
        else:
            print('用户名只能包含数字和字母。')
            return register()

    
# 3.进入文章页面
#     进入文章页面要求：
#         a.提示欢迎xx进入文章页面
#         b.此时用户可以选择，直接写入内容，还是导入md文件
#             # 如果选择直接写内容，让学生直接写文件名|文件内容，最后创建一个文章
#             # 如果选择导入md文件，让用户输入已经准备好的md文件的文件路径，然后将此md的文件内容全部写入文章

@common.wrapper_login
def article():
    username = login_status
    choice = input(f'欢迎{username}进入文章页面'+'''
    1.写文章
    2.导入已有的md文件
请选择功能(按q返回上一级)：''').strip()
    # 限制输入类型，为数字则进行类型转换
    if choice.upper() == 'Q':
        return 1
    elif choice.isnumeric():
        choice = int(choice)

        # 选择直接写文章
        if choice == 1:
            title = input('\n<创建新文章>'+'输入文章标题：').strip()
            if len(title) > 0:
                # 这块没判断文章是否存在。 先耍懒了。
                print(f'输入{title}的正文内容，（完成输入itsend）：\n')
                # 实现换行输入
                endstr = "itsend"
                section = ""
                for line in iter(input,endstr):
                    section += line + '\n'
                # 获取用户id，这块用对象方式实现其实更好。后续完善。
                userid = db.account.find_one({"username":login_status},{"_id":1})['_id']
                # 获取目前article最大_id ，实现自增
                articleid = int(db.article.find({},{"_id":1}).sort("_id",-1).limit(1).next()['_id']) + 1
                # 插入文档到数据库
                db.article.insert_one({
                    "_id":articleid,
                    "article":{"title":title,
                    "paragraph":section,
                    "userid":userid,
                    "createtm":parser.parse(getftime()),
                    "is_daily":False,
                    "comment_id":[]
                    }
                })


        # 选择导入md文件
        elif choice == 2:
            md_path = input('输入完整的md文件路径：').strip()
            if os.path.isfile(md_path):
                # 直接获取文件名，如果有扩展名，那就只取文件名部分
                title = md_path.split('/')[-1].split('.md')[0]
                # 读取文件内容
                with open(md_path,mode='r') as f:
                    section = f.read()
                # 写入数据库
                userid = db.account.find_one({"username":login_status},{"_id":1})['_id']
                articleid = int(db.article.find({},{"_id":1}).sort("_id",-1).limit(1).next()['_id']) + 1
                db.article.insert_one({
                    "_id":articleid,
                    "article":{"title":title,
                    "paragraph":section,
                    "userid":userid,
                    "createtm":parser.parse(getftime()),
                    "is_daily":False,
                    "comment_id":[]
                    }
                })
                print('导入完成。（如果能看到这里且没有报错，那就是成功了~）')

        # 超出范围则继续要求选择。
        else:
            return article()
    # 非数字则要求继续选择。
    else:
        return article()
# article()



#     4.进入评论页面
# 3.选做功能：
#     1.评论页面要求：
#         # 让用户选择要评论的文章。这个需要os模块实现。
#         # 选择要评论的文章之后，现将原文章内容全部读一遍，然后输入要评论的内容，并过滤一些关键词。
#         # 然后将评论内容写到文章的评论区的最下面
#         <文章原内容>
#         ...
#         <评论区>：
#         ---------------------
#         <用户名>xx
#         <评论该内容>xx
#         <用户名>xx
#         <评论该内容>xx
#         ...

#         如果原文章下面没有评论区以及分割线，则增加这两行再附上评论，否则直接在评论区最下面追加。

# 获取特定文章列表
def get_file_dict(filetype):
    search = False
    if filetype == 'dry':
        search = True
    result = db.article.find({"article.is_daily":search},{"_id":1,"article.title":1})
    # print(result)
    file_dict = {}
    for i in result:
        file_dict[ i['_id'] ] = i['article']['title']
    return file_dict

    

# choose_to_print_file 根据文章id，获取指定的文章并打印输出。
def choose_to_print_file(choice_id):
            # 获取文章
            result = db.article.find_one({"_id":choice_id},{
                "_id":0,
                "article.title":1,
                "article.paragraph":1,
                "comment_id":1
                })
            print('<文章标题>',result['article']['title'])
            print('----------')
            print('<文章正文>',result['article']['paragraph'])
            

            # 判断是否存在评论，有则输出
            if result.get('comment_id'):
                print('----------')
                print('<评论区>')
                comments = db.comment.find(
                    {
                        "_id":{
                            "$in": result['comment_id'] }},
                    {
                        "_id":0,
                        "comment_user":1,
                        "comment_section":1 })
                for n in comments:
                    print(n['comment_user'],"评论说：",n['comment_section'])
 

# 输入评论
def enter_comment(username,id):
    comments = input('输入评论（取消按q）：').strip()
    if comments.upper() == 'Q':
        return 1
    elif len(comments) > 0:
        # 实现的不优雅。回头学习了再看看有没有办法实现判断
        # 获取一下,是否存在0这个初始id
        x = db.comment.find_one({"_id":0},{"_id":1})
        if x:
            # 取_id最大值
            x = db.comment.find({},{"_id":1}).sort("_id",-1).limit(1)
            cid = x.next()['_id']+1
        else:
            # 不存在则初始化_id
            cid = 0
        db.comment.insert_one(
            {"_id":cid,
            "article_id":id,
            "comment_user":username,
            "comment_section":comments,
            "comment_time":parser.parse(getftime())
            }
        )
        db.article.update_one({"_id":id},{"$push":{"comment_id":cid}})
    else:
        print('正经点！')
        return enter_comment(username,id)

# 评论
@common.wrapper_login
def comment():
    username = login_status
    print(f'欢迎{username}进入评论页面')
    # part 1 输出文章列表
        # os.listdir
    choice = input('''
    1.显示文章列表
    2.显示日记列表
输入要查询的列表(按m回主菜单)：''').strip()

    if choice.isnumeric():
        choice = int(choice)

        # 待评论文章列表
        if choice == 1:
            ndict = get_file_dict(0)

        # 待评论日记列表
        elif choice == 2:
            ndict = get_file_dict(1)

        # 非法则重试
        else:
            return comment()
        
        # 将ndict处理并打印成文章菜单
        if len(ndict) < 1:
            print('该分类下目前没有内容噢！')
            return comment()
        else:
            print('\n' + 'ID' + '\t' + '文章标题' + '\n-----------------')
            for key in ndict:
                print(str(key) + '\t' + ndict[key])

            # 输出文章标题菜单后，调用文章选择器choose_to_print_file
            # 交互选择文章并执行文章内容输出
            choice_id = input('选择你要评论的文章id:').strip()
            if choice_id.isnumeric():
                choice_id = int(choice_id)
                if choice_id <= len(ndict):
                    choose_to_print_file(choice_id)  
                    enter_comment(username,choice_id)
                else:
                    print("非法1")
            else:
                print("非法2")


    elif choice.upper() == 'M':
        return main()

    else:
        return comment()

# comment()


#     5.进入日记页面
@common.wrapper_login
def diary():
    username = login_status
    print(f'欢迎{username}进入日记页面')


#     6.进入收藏页面
@common.wrapper_login
def favo():
    username = login_status
    print(f'欢迎{username}进入收藏页面')

#     7.注销账号
@common.wrapper_login
def logout():
    global login_status 
    login_status = 0
    print('已退出登录。')

#     8.退出整个程序
def _exit():
    global flag
    flag = 0
    # 关闭数据库会话句柄
    client.close()
    print('\n\n再见!')
    return 0


#     2. 登录功能要求：
#         a.用户输入用户名、密码进行登录验证
#         b.登录成功后，才可以访问3-7选项，如果没有登录或者登录不成功，访问3-7选项时，要求登录。


def main():
    main_menu = {
        1:{'menu':'登录','func_name':'login'},
        2:{'menu':'注册','func_name':'register'},
        3:{'menu':'文章页面','func_name':'article'},
        4:{'menu':'评论页面','func_name':'comment'},
        5:{'menu':'日记页面','func_name':'diary'},
        6:{'menu':'收藏页面','func_name':'favo'},
        7:{'menu':'注销账号','func_name':'logout'},
        8:{'menu':'退出程序','func_name':'_exit'},
    }
    print('\n\n欢迎啊老弟！')
    for idx in main_menu:
        print('\t' + str(idx) + '.' + main_menu[idx]['menu'] )

    menu_choice = input('选择功能：').strip()

    if menu_choice.isnumeric() :
        if len(menu_choice) != 0:
            if int(menu_choice) <= len(main_menu):
                menu = main_menu[int(menu_choice)]['func_name'].strip() + '()'
                exec(menu)
            else:
                return main()
        else:
            return main()        
    else:
        return main()
    # print(login_status)

flag = 1
# 程序主体运行
def run():
    while flag:
        main()