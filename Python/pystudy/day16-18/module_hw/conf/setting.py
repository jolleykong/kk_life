# account database file
import os
# 获取当前文件所在目录的目录名，即：按照命名规范，当前文件所在目录的父级目录为项目根目录。
base_path = os.path.dirname(os.path.dirname(__file__))
# print(base_path)
account_db = os.path.join(base_path,'db','acc_db')

articles_path = os.path.join(base_path,'articles')

comments_path = os.path.join(base_path,'comments')
