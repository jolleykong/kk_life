# 文件操作初识
    # 操作文件的三个问题
        # 文件路径：path
        # 打开方式：读、写、追加、读写、写读
        # 编码方式：utf-8、GBK、GB2312等

# f1 = open(r'fileexercise/file1',encoding='utf-8',mode='r')
# content = f1.read()
# print(content)
# f1.close

# '''
# f1,file_handler,f_h：文件句柄。对文件进行的任何操作，都要通过文件句柄。
# open：py内置函数，底层调用的是操作系统的接口。
# r'path'， r表示''路径中所有\为分隔符，无特殊含义。可以不写r。
# encoding：编码。可以不写，默认为操作系统的默认编码集。
# '''


# 文件操作读
    # r ,rb ,r+ ,r+b 。 b means bytes。rb操作的是非文本文件。
    # r的话可以默认不写。

    # 全部读出来
        # f = open('fileexercise/file1')
        # content = f.read()
        # print(content)
        # f.close()

    # 按照字符读取
        # 文本模式时，read()代表读取n个字符
        # b模式时，read() 代表读取n个字节
        # f = open('fileexercise/file1',encoding='utf-8')
        # content = f.read(5)   # 读5个字符
        # print(content)
        # f.close()

    # 按行读
        # f = open('fileexercise/file1',encoding='utf-8')
        # print(f.readline())  # 读1行，此时光标在第二行行首
        # print(f.readline())  # 再读1行，此时光标在第三行行首
        # print(f.readline())  # 再读1行，此时光标在第四行行首
        # f.close()

    # 按多行读
        # f = open('fileexercise/file1',encoding='utf-8')
        # l1 = f.readlines()  # readlines() ，返回一个list，list中的每一个元素是源文件中的每一行。
        # print(l1)
        # f.close()

    # 循环读取（王道！）
        # f = open('fileexercise/file1',encoding='utf-8')
        # for line in f:      #  readlines()，然后对list做元素遍历。 但是 for 方式里， 对文件句柄的循环， 实际上是每次循环，读取一行。
        #     print(line)
        # f.close()

    # 用rb模式读一个图片文件
        # f = open('fileexercise/img1.png',mode='rb')
        # content = f.read()
        # print(content)
        # f.close()
# 文件操作写
    # w
        # f = open('fileexercise/newfile',encoding='utf-8',mode='w')
        # f.write('I\'m kk.')
        # f.close

        # # 先清空文件，后写入。（不叫覆盖）
        # f = open('fileexercise/newfile',encoding='utf-8',mode='w')
        # f.write('Fiona is so cute.')
        # f.close

        # # 读一下内容
        # f = open('fileexercise/newfile',encoding='utf-8',mode='r')
        # print(f.read())
        # f.close()

    # wb
        # 其实也可以用来操作文本文件。但是主要用来做非文本文件的写入。
        # 用rb读入一个二进制文件， 然后用wb写到另一个文件
            # f = open('fileexercise/img1.png',mode='rb')
            # content = f.read()
            # # 读完文件，就可以关闭这个文件句柄了。
            # f.close()
            # ft = open('fileexercise/img2.png',mode='wb')
            # ft.write(content)
            # ft.close()

# 文件操作追加
    # 没有文件则创建文件并写入，有文件存在则在文件末尾追加内容。
    # a,ab,a+ 追加并可读,a+b
    # a
        # f = open('fileexercise/newfile',encoding='utf-8',mode='r')
        # co = f.read()
        # print(co)
        # f.close()
        # f1 = open('fileexercise/newfile',encoding='utf-8',mode='a')
        # f1.write('it\'s truth.')
        # f1.close()
# 文件操作的其他模式
    # r+ ,w+ ,a+ 
        # r+ ，读写。虽然能写，但是要求文件必须存在。
            # f = open('fileexercise/newfile2',encoding='utf-8',mode='r+')
            # # 报错，找不到文件。
            # f.write('aaa')
            # f.close()

            # f = open('fileexercise/newfile',encoding='utf-8',mode='r+')
            # print(f.read())
            # f.write('\n I love this world.')
            # f.close()
            # '''
            #  Fiona is so cute.it's truth.

            #  Fiona is so cute.it's truth.

            #  I love this world.
            # '''

            # 但是如果不read，直接write，可以发现：从起始光标位置开始直接覆盖（字符换字符）了源文件。
            # f = open('fileexercise/newfile',encoding='utf-8',mode='r+')
            # f.write('I love this world.')
            # f.close()
            # '''
            # Fiona is so cute.it's truth.
            
            # I love this world.it's truth.
            # '''

        # 指定\更改换行符
            ## 先复制几行
            # f = open('fileexercise/newfile',encoding='utf-8',mode='r+',newline='\n')
            # content = f.read()
            # new_content = content * 8
            # f.write(new_content)
            # f.close()

            ## 貌似只能指定为\r,\n,\r\n,\n\r 。指定换行符后，写入时也会自动转换写入内容的换行符到指定的换行符。
            # f = open('fileexercise/newfile',encoding='utf-8',mode='r+',newline='\r\n')
            # content = f.read()
            # f.write(content*8)
            # f.close()

# 文件操作的其他功能

# 读取
    # read([n]) ,读取n个字符。不指定则读取全部。
    # readline([n]) ,读取n行。不指定n则读取一行。
    # readlines() ,读取文件的所有行，并返回list。
'''
f = open('fileexercise/newfile',encoding='utf-8',mode='r')
fc = f.readlines()
print(fc[0])
f.close()
'''

# 写入
    # write() ,将提供的字符串都写入到（当前光标位置|文件）的后面。
    # writelines(lines) ,将一个字符串list或任何可迭代对象、序列，写入到文件。写入时不会添加换行符。
    # 没有writeline，因为write()就够了。

# 光标位置
    # seek(offset[,whence]) ,将当前位置移到offset和whence指定的地方。
        # offset 指定了字节（字符）数，
        # whence 默认为0，即：io.SEEK_SET(0) ，意味着偏移量是相对于文件开头的（偏移量不能为负数）。
            # 可以设置为1，即：io.SEEK_CUR(1) ，相对于当前位置进行移动（偏移量可以为负）
            # 2，即：io.SEEK_END(2)，相对于文件末尾进行移动。
            # 即：移动到开头:seek(0)；移动到结尾:seek(0,2) seek的第二个参数表示的是从哪个位置进行偏移,默认是0,表示开头,1表示当前位置,2表示结尾
    # tell()，返回当前位于文件的什么位置。
    # 位置需要考虑编码和字符的长度。tell\seek的单位是字节。

# flush 强制刷新
    # ctrl + s 类似， 先刷新一次。
    

# 文件关闭
    # 程序退出时将自动关闭文件对象。
    # close() 
    # 确保文件得以关闭，可以使用 try/finally ，在finally字句中调用close。
'''
try:
    # do something and write to file.
finally:
    file.close()
'''
    # 也可以用with语句，打开文件并将其赋给一个变量。在语句体中，将数据写入文件或进行其他动作，当到达语句末尾时，会自动关闭文件（即使出现异常也会如此。）
'''
with open('file') as somefile:
    dosomething(somefile)
'''
        # with 支持同时打开多个文件
'''
with open('file1') as somefile1,open('file2') as somefile2:
    dosomething(somefile...)

with open('file1') as somefile1,\
    open('file2') as somefile2:
    dosomething(somefile...)    
'''

        # with的缺点
            # 待补充
            # 这里要注意一个问题，虽然使用with语句方式打开文件，不用你手动关闭文件句柄，比较省事儿，但是依靠其自动关闭文件句柄，是有一段时间的，这个时间不固定，所以这里就会产生问题，如果你在with语句中通过r模式打开t1文件，那么你在下面又以a模式打开t1文件，此时有可能你第二次打开t1文件时，第一次的文件句柄还没有关闭掉，可能就会出现错误,他的解决方式只能在你第二次打开此文件前，手动关闭上一个文件句柄。

# readable()
# writable()
    # 判断文件是否可读可写
'''
>>> fh = open('fileexercise/file1')
>>> fh.readable()
True
>>> fh.writable()
False
>>> fh.close()
'''


# 文件操作的改
# 方法一： 文件整个读入到内存，在内存中修改后，刷新到文件。
'''
import os  # 调用系统模块

with open('a.txt') as read_f,open('.a.txt.swap','w') as write_f:
    data=read_f.read() #全部读入内存,如果文件很大,会很卡
    data=data.replace('alex','SB') #在内存中完成修改

    write_f.write(data) #一次性写入新文件

os.remove('a.txt')  #删除原文件
os.rename('.a.txt.swap','a.txt')   #将新建的文件重命名为原文件

方法一
'''
# 方法二： 将文件逐行读入并修改后，刷新到新文件，完成全部修改后，将新文件替换给老文件。
'''
import os

with open('a.txt') as read_f,open('.a.txt.swap','w') as write_f:
    for line in read_f:
        line=line.replace('alex','SB')
        write_f.write(line)

os.remove('a.txt')
os.rename('.a.txt.swap','a.txt') 

方法二
'''



# 文件清空
    # 只要句柄没有关闭，那么文件可以一直被写入
    # 只有句柄关闭后重新以w打开，才会清空原来文件内容。

# 练习题
'''
1. 文件a.txt内容：每一行内容分别为商品名字，价钱，个数。

apple 10 3

tesla 100000 1

mac 3000 2

lenovo 30000 3

chicken 10 3

通过代码，将其构建成这种数据类型：[{'name':'apple','price':10,'amount':3},{'name':'tesla','price':1000000,'amount':1}......] 并计算出总价钱。

2，有如下文件：

-------

alex是老男孩python发起人，创建人。

alex其实是人妖。

谁说alex是sb？

你们真逗，alex再牛逼，也掩饰不住资深屌丝的气质。

----------

将文件中所有的alex都替换成大写的SB。

相关练习题
'''