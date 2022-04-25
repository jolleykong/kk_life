# 配合GoIM的Client
- 迭代1: 支持连接
- 迭代2: 支持输入服务器地址进行连接
- 迭代3: 支持菜单选择,使用go routine执行 RecResponse() ,以接收服务器返回信息的显示
  - 但是目前client的stdout和RecResponse()调用stdout显示会乱,后面看看有什么办法.
  - 菜单选择时直接回车会程序结束.