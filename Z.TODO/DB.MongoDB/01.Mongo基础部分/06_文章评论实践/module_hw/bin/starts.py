import sys
import os
# 获取当前文件所在目录的目录名，即：按照命名规范，当前文件所在目录的父级目录为项目根目录。
base_path = os.path.dirname(os.path.dirname(__file__))

# 将项目根目录base_path 加入到path，作为全局作用域。
sys.path.append(base_path)

# from conf import setting


# 执行程序入口，
from core import src

if __name__ == '__main__':
    src.run()