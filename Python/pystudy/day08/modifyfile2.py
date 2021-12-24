# 直接修改源文件
# v1 直接读取全部
file_name = input('来个文件名尝尝：')
fh = open(file_name,encoding='utf-8',mode='r+')
file_cons = fh.read()
file_cons = file_cons.replace('我','wo')
fh.seek(0)
fh.write(file_cons)
fh.close()
