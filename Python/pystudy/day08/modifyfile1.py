# init a file name source1
# 载入文件，读入文件，内存中修改，写入新文件，写入完成后，替换掉源文件。

import os
## 读入文件
file_name = input('输入源文件名：')
fh = open(str(file_name),encoding='utf-8',mode='r')

## 将文件内容赋值给临时变量
source_contents = fh.read()

## 关闭句柄
fh.close()

## 修改变量内容，将所有’我‘ 替换成'wo','你’ 替换成‘ni’
source_contents = source_contents.replace('我','wo')
source_contents = source_contents.replace('你','ni')
source_contents = source_contents.replace('们','s')

## 创建临时文件并将变动写入临时文件
modify_name = str(file_name)+'.swp'
fh = open(modify_name,encoding='utf-8',mode='w+')
fh.write(source_contents)

# 读一遍并输出
fh.seek(0)
print(fh.read())
# 关闭临时文件句柄
fh.close()

# 替换文件
os.remove(file_name)
os.rename(modify_name,file_name)