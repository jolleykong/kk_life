# p3.实现用户输入用户名和密码,当用户名为 seven 或 alex 且 密码为 123 时,显示登陆成功,否则登陆失败,失败时允许重复输入三次

n = 1
while n <= 3 :
    username = input('输入用户名额老弟：')
    password = input('输入密码额老弟：')
    if username.lower() in ['seven','alex'] and password == '123' :
        print('欢迎啊老弟！')
        break
    else :
        print('玩儿啥呢老弟？')
        n+=1
else :
    print('\n\n你可拉倒吧\n\n')