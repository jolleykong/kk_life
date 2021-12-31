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
# 用代码模拟博客系统

flag = 1

# 0.load auth file.
def get_authdict():
    with open(setting.account_db,mode='r') as pwdfile:
        lines = pwdfile.readlines()
        authdict = { i.strip().split("|")[0] : i.strip().split("|")[1]  for i in lines }
    return authdict

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
                    # 将注册信息写入文件
                    newuser = str(username)+'|'+str(password)+'\n'
                    with open(setting.account_db,mode='a+') as pwdfile:
                        pwdfile.write(newuser)
                    print('注册成功！')
                    print(f'你的用户名为：{username}')
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
            title = input('\n<创建新文章>'+'输入文章标题：').strip()+'.arc'
            if len(title) > 0:
                # 这块没判断文章是否存在。 先耍懒了。直接覆盖吧。
                filename = os.path.join(setting.articles_path,title)
                with open(filename,mode='w') as new_article:
                    new_article.write( input(f'输入{title}的正文内容：\n') )

        # 选择导入md文件
        elif choice == 2:
            md_path = input('输入完整的md文件路径：').strip()
            if os.path.isfile(md_path):
                # 直接获取文件名，如果有扩展名，那就只取文件名部分
                title = md_path.split('/')[-1].split('.md')[0]+'.arc'
                # 生成新的文件名用来归档
                filename = os.path.join(setting.articles_path,title)

                # 文件内容复制
                imp_article = open(filename,mode='w')
                source_md = open(md_path,mode='r')

                for line in source_md:
                    imp_article.write(line)

                source_md.close()
                imp_article.close()
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
def get_file_list(path,filetype):
    dir_list = os.listdir(path)
    # 这一段可以做一下文章类型判断。 这里不判断了。
    type = '.'+filetype.strip()
    # 过滤掉非arc文件和dry文件，即：非文章文件和日记文件
    file_list = [file for file in dir_list if type in file ]
    return file_list

# choose_to_print_file 根据文章列表，打开指定的文章并打印输出，同时返回文件名。
def choose_to_print_file(nlist,filepath):
    choice_idx = input('选择你要评论的文章id:').strip()
    if choice_idx.isnumeric():
        choice_idx = int(choice_idx) - 1
        if choice_idx <= len(nlist):
            # filepath, './day15/hw/articles/'...
            # file_name = filepath + '/' + nlist[choice_idx] 
            file_name = os.path.join( filepath,nlist[choice_idx] )
            with open(file_name) as fn:
                print(fn.read())
            return nlist[choice_idx]
        else:
            # 非法则重选
            return choose_to_print_file(nlist,filepath)
    else:
        # 非法则重选
        return choose_to_print_file(nlist,filepath)

# 输入评论
def enter_comment(username,comment_file):
    comments = input('输入评论（取消按q）：').strip()
    if comments.upper() == 'Q':
        return 1
    elif len(comments) > 0:
        comments = '<' + str(username) + '>' + '  ' + str(comments) + '\n'
        with open(comment_file,mode='a+') as cf:
            cf.write(comments)
        print(comments)
    else:
        print('正经点！')
        return enter_comment(username,comment_file)

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
            nlist = get_file_list(setting.articles_path,'arc')

        # 待评论日记列表
        elif choice == 2:
            nlist = get_file_list(setting.articles_path,'dry')

        # 非法则重试
        else:
            return comment()
        
        # 将列表处理并打印
        #print(nlist)
        # 2021 10 21 修复0文章时的问题
        if len(nlist) < 1:
            print('该分类下目前没有内容噢！')
            return comment()
        else:
            for idx in range(len(nlist)):
                print( idx+1,  nlist[idx].split('.arc')[0]  )

            # 调用选择系统，并输出文章内容。
            file_name = choose_to_print_file(nlist,setting.articles_path) 
            file_name = file_name + '.comment'
            # 输出文章内容完成后，再输出该文章的评论，评论内容存放在与文章同名的.comment 文件中。
            # 如果文件存在，则正常输出文件。 如果文件不存在，说明这个文章尚未被评论过，因此要初始化评论区。
            comment_file = os.path.join(setting.comments_path,file_name)
            # print(comment_file)
            if os.path.isfile(comment_file):
                # 已有评论，输出评论文件内容
                with open(comment_file) as cf:
                    print(cf.read())

            else:
                # 没有评论过。初始化评论文件。
                with open(comment_file,mode='w+') as cf:
                    cf.write('<评论区>\n---------------------------------------------------------\n')
                    # 写完了，读一遍并输出。
                    cf.seek(0)
                    print(cf.read())

        # part 2 添加评论操作
            enter_comment(username,comment_file)

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


# 程序主体运行
def run():
    while flag:
        main()