# 配合GoIM的Client
- 迭代1: 支持连接
- 迭代2: 支持输入服务器地址进行连接
- 迭代3: 支持菜单选择,使用go routine执行 RecResponse() ,以接收服务器返回信息的显示
  - 但是目前client的stdout和RecResponse()调用stdout显示会乱,后面看看有什么办法.
  ~- 菜单选择时直接回车会程序结束.~
- 迭代4：将菜单选择由int改为string，避免了直接回车导致退出的情况。
  - 世界频道输出消息后，重复按回车不会再重复发送上一条消息了。
