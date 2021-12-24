import re
s = 'abcdefg abc aaabc'
print(re.findall('aaa.*',s))
re.match    # 从字符串开头匹配，如果以符合条件的字符串开头则返回，否则返回None。等同于search的'^关键字'
re.search   # 找到匹配的第一个对象就返回，返回一个'对象'。返回的对象使用group()方法取值
re.findall  # 将所有匹配的结果返回到一个list
re.finditer # 返回一个存放匹配结果的迭代器。适合匹配结果很多的时候~
re.split    # 指定多个分隔符来实现分割
re.sub      # replace
re.compile  # 制定一个规则，使其他函数以此规则进行字符串处理。

# 作业


# 相关练习题
# 1，"1-2*(60+(-40.35/5)-(-4*3))"
    # 1.1 匹配所有的整数
    # 1.2 匹配所有的数字（包含小数）
    # 1.3 匹配所有的数字（包含小数包含负号）
ss1 = '1-2*(60+(-40.35/5)-(-4*3))'
ret1 = re.findall('\d+',ss1)
print(ret1)

ret2 = re.findall('\d+\.\d*|\d+',ss1)
print(ret2)

ret3 = re.findall('-\d+\.\d*|-\d+|\d+\.\d*|\d+',ss1)
print(ret3)
ret31 = re.findall('-?\d+\.\d*|-?\d+',ss1)
print(ret31)

# 2,匹配一段你文本中的每行的邮箱
    # 邮箱地址规则， 字母开头，包含字母、数字、_、- 组成邮箱账号 ， 由@符号和邮箱主机连接， 邮箱主机地址规则为字母开头，包含数字、_、-，由.com 或.com.xx 组成完整邮箱地址
ss2 = '''
abc_123@qq.com
jjkkllcac_133MNB-po@yahoo.com.cn
bbkkookk@china.gov.cn
'''  
    
ret21 = re.findall('\w+\@\w+\.\w+\.?\w*',ss2)
print(ret21)

# 3，匹配一段你文本中的每行的时间字符串 这样的形式：'1995-04-27'

ss3 = '''
时间就是1995-04-27,2005-04-27
1999-04-27 老男孩教育创始人
老男孩老师 alex 1980-04-27:1980-04-27
2018-12-08
'''
ret31 = re.findall('[0-9]{4}\-[0-1][0-9]-[0-2][0-9]',ss3)
print(ret31)


# 4 匹配 一个浮点数
ss4 = '''
11.2 99999 6789.00 0.123 -0.1 9.987 3.1415
'''

ret41 = re.findall('-?\d+\.\d+',ss4)
print(ret41)


# 5 匹配qq号：腾讯从10000开始：
# 目前最长11位，最短5位，最小为10000
ss5 = '''
10000 9999 1113096303 2224544744 334786291 asdf8123618 1192873.123 0.123 -1144657
'''
    # [^-\d] [^]匹配除了字符组中的字符的所有字符。过滤掉负数。
ret51 = re.findall('[^-\d](\d{5,11})',ss5)
print(ret51)



# 6.
ss6 = '''
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/7459977.html" target="_blank">python基础一</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/7562422.html" target="_blank">python基础二</a></p>
<p><a style="text-decoration: underline;" href="https://www.cnblogs.com/jin-xin/articles/9439483.html" target="_blank">Python最详细，最深入的代码块小数据池剖析</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/7738630.html" target="_blank">python集合,深浅copy</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8183203.html" target="_blank">python文件操作</a></p>
<h4 style="background-color: #f08080;">python函数部分</h4>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8241942.html" target="_blank">python函数初识</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8259929.html" target="_blank">python函数进阶</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8305011.html" target="_blank">python装饰器</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8423526.html" target="_blank">python迭代器,生成器</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8423937.html" target="_blank">python内置函数,匿名函数</a></p>
<p><a style="text-decoration: underline;" href="http://www.cnblogs.com/jin-xin/articles/8743408.html" target="_blank">python递归函数</a></p>
<p><a style="text-decoration: underline;" href="https://www.cnblogs.com/jin-xin/articles/8743595.html" target="_blank">python二分查找算法</a></p>

'''
    # 1,找到所有的p标签
ret61 = re.findall('\<p\>.*\<\/p\>\n',ss6)
print(ret61)


    # 2,找到所有a标签对应的url
ret62 = re.findall('\<a.*href\=\"(http.*)" target',ss6)
print(ret62)






#---------答案
# print(relx.findall('\d+',"1-2*(60+(-40.35/5)-(-4*3))"))
# print(relx.findall(r'\d+\.?\d*|\d*\.?\d+', "1-2*(60+(-40.35/5)-(-4*3))"))
# print(relx.findall(r'-?\d+\.?\d*|\d*\.?\d+', "1-2*(60+(-40.35/5)-(-4*3))"))
# http://blog.csdn.net/make164492212/article/details/51656638 匹配所有邮箱
# print(relx.findall('\d{4}-\d{2}-\d{2}', s1))
# print(re.findall('\d+\.\d*','1.17'))
# print(re.findall('[1-9][0-9]{4,}', '2413545136'))

# ret = relx.findall('<p>.*?</p>', s1)
# print(ret)

# print(re.findall('<a.*?href="(.*?)".*?</a>',s1))