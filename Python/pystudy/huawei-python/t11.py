'''
Python编程知识-扫雷

大家都玩过扫雷游戏吧，给定一个矩形方正区域，里面有若干个地雷，
用鼠标点击，点击后如果出现一块区域，那么说明这个点周围8个方向没有地雷，
如果出现数字，数字是几，那么就表示这个区域周围8个方向有几颗地雷，
如果是地雷，那你很不幸就输掉了。 

现在告诉你这个图里地雷的分布，你来给出每个点上面的数字应该是多少？

输入 数据的第一行有2个整数n, m(1 <= n, m <= 50)，
表示一个n * m的区域，n行m列，接下来n行每行有一个长度为m的字符串，
字符串只包含2种字母，”.”和”X”，其中”.”表示这个地方不是地雷，”X”表示这个地方是地雷。

输出 请输出n行内容，每一行是一个长度为m的字符串，
由数字和符号”X”组成，如果这个点不是地雷，那么就表示这个点周围有几颗地雷，
否则这个点存放符号”X”，表示这个点是地雷。

样例 输入样例 1

3 5 ..... ..XX. ..... 输出样例 1

01221 01XX1 01221
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''