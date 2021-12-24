# init a file name source1v2
# 载入文件，读入文件，内存中修改，写入新文件，写入完成后，替换掉源文件。
# v2里使用with的方式，但是依然是一次性读取所有文件内容， 在文件内容较大时会出现性能问题
# v3在v2的基础上， 采用逐行修改并写入的方式来实现。

import os
file_name = input('来个文件名尝尝：')
modify_name = str(file_name)+'.swp'

with open(file_name,encoding='utf-8',mode='r') as fn, \
    open(modify_name,encoding='utf-8',mode='w') as ft:
    # 对源文件的每行做读出，读出后直接修改，修改后直接写入临时文件。
    # with 语句会在适当的时候自己关闭文件句柄。我觉得需要的话可以在后面手动flush或close。
    for lines in fn:
        linedata = lines
        linedata = linedata.replace('wo','我我我')
        ft.write(linedata)

os.remove(file_name)
os.rename(modify_name,file_name)