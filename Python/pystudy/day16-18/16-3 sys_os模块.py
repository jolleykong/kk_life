# sys
# 这一章涉及sys模块的内容很少
# sys是与python解释器交互的模块。
'''
sys.argv
sys.exit(n)
sys.version
sys.path
sys.platform
'''



# os
    # 文件、路径相关的。

'''
当前执行这个python文件的工作目录相关的工作路径
os.getcwd() 获取当前工作目录，即当前python脚本工作的目录路径  ** 
os.chdir("dirname")  改变当前脚本工作目录；相当于shell下cd  **  # chdir(r'c:\a\b\c')   r指分隔符当做路径。
os.curdir  返回当前目录: ('.')  **
os.pardir  获取当前目录的父目录字符串名：('..') **
​
# 和文件夹相关 
os.makedirs('dirname1/dirname2')    可生成多层递归目录  ***
os.removedirs('dirname1') 若目录为空，则删除，并递归到上一级目录，如若也为空，则删除，依此类推 ***
os.mkdir('dirname')    生成单级目录；相当于shell中mkdir dirname ***
os.rmdir('dirname')    删除单级空目录，若目录不为空则无法删除，报错；相当于shell中rmdir dirname ***
# os.listdir('dirname')    列出指定目录下的所有文件和子目录，包括隐藏文件，并以列表方式打印 **
​
# 和文件相关
os.remove()  删除一个文件  ***
os.rename("oldname","newname")  重命名文件/目录  ***
os.stat('path/filename')  获取文件/目录信息 **
​
# 和操作系统差异相关
os.sep    输出操作系统特定的路径分隔符，win下为"\\",Linux下为"/" *
os.linesep    输出当前平台使用的行终止符，win下为"\t\n",Linux下为"\n" *
os.pathsep    输出用于分割文件路径的字符串 win下为;,Linux下为: *
os.name    输出字符串指示当前使用平台。win->'nt'; Linux->'posix' *

# 和执行系统命令相关
os.system("bash command")  运行shell命令，直接显示  **
os.popen("bash command).read()  运行shell命令，获取执行结果  **
os.environ  获取系统环境变量  **
​
#path系列，和路径相关
os.path.abspath(path) 返回path规范化的绝对路径  ***
os.path.split(path) 将path分割成目录和文件名二元组返回 ***
os.path.dirname(path) 返回path的目录。其实就是os.path.split(path)的第一个元素  **
os.path.basename(path) 返回path最后的文件名。如何path以／或\结尾，那么就会返回空值，即os.path.split(path)的第二个元素。 **
os.path.exists(path)  如果path存在，返回True；如果path不存在，返回False  ***
os.path.isabs(path)  如果path是绝对路径，返回True  **
os.path.isfile(path)  如果path是一个存在的文件，返回True。否则返回False  ***
os.path.isdir(path)  如果path是一个存在的目录，则返回True。否则返回False  ***
os.path.join(path1[, path2[, ...]])  将多个路径组合后返回，第一个绝对路径之前的参数将被忽略 ***
os.path.getatime(path)  返回path所指向的文件或者目录的最后访问时间  **
os.path.getmtime(path)  返回path所指向的文件或者目录的最后修改时间  **
os.path.getsize(path) 返回path的大小 ***

# os.stat('path/filename') 获取文件/目录信息 的结构说明
stat 结构:
st_mode: inode 保护模式
st_ino: inode 节点号。
st_dev: inode 驻留的设备。
st_nlink: inode 的链接数。
st_uid: 所有者的用户ID。
st_gid: 所有者的组ID。
st_size: 普通文件以字节为单位的大小；包含等待某些特殊文件的数据。
st_atime: 上次访问的时间。
st_mtime: 最后一次修改的时间。
st_ctime: 由操作系统报告的"ctime"。在某些系统上（如Unix）是最新的元数据更改的时间，在其它系统上（如Windows）是创建时间（详细信息参见平台的文档）。

print(__file__)     # 动态获取当前文件的绝对路径。
'''
