所有内容在一个py文件中，会遇到：
    1.文件加载问题，所有代码一次性加载，效率不好。
    2.代码可读性差，查询麻烦。
    要将一个py文件分开，合理的按照规则分成多个py文件。
- 一些轻易不改变的变量，称为 配置选项，主要用来被引用。 一般将这些变量放入配置文件，settings.py
- 以博客作业举例，
        - 将登录和注册、功能菜单划分到一个文件划分到一个文件，作为主逻辑函数，src.py
        - 辅助功能的函数分到一个文件，公共组件部分，如装饰器、日志等不影响函数的功能代码，放入公共组件部分，common.py
        - 将启动程序入口（程序启动开关）单独分到一个文件，一般函数名为run() ，starts.py
        - 数据库文件，（用户信息、访问记录等）
        - 日志文件
bin
    starts.py
conf
    setting.py
core
    src.py
db
    xxxxx
lib
    common.py
log
    xxxxx
README


Python/pystudy/day16-18/module_hw