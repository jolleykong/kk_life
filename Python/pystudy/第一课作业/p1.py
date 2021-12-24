# p1.实现用户输入用户名和密码,当用户名为 seven 且 密码为 123 时,显示登陆成功,否则登陆失败!

status = True
while status :
    username = input('输入用户名额老弟：')
    password = input('输入密码额老弟：')
    if username.lower() == 'seven' and password == '123' :
        print('欢迎啊老弟！')
        status = False
    else :
        print('玩儿啥呢老弟？')