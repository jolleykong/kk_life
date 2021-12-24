# init a file name source1v2
# 载入文件，读入文件，内存中修改，写入新文件，写入完成后，替换掉源文件。
# v2里使用with的方式，看能写成啥样

import os
file_name = input('来个文件名尝尝：')
modify_name = str(file_name)+'.swp'
with open(file_name,encoding='utf-8',mode='r') as fn, \
    open(modify_name,encoding='utf-8',mode='w+') as ft:
    fn_cons = fn.read()
    fn.close()

    fn_cons = fn_cons.replace('我','wo')
    fn_cons = fn_cons.replace('们','s')
    fn_cons = fn_cons.replace('的','de')

    #ft.seek(0)
    ft.write(fn_cons)
    #ft.flush()
    ft.close()

os.remove(file_name)
os.rename(modify_name,file_name)

# read new file again
with open(file_name,encoding='utf-8',mode='r') as newfile:
    print(newfile.read())
