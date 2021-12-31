# account database file
import os
import pymongo
# 获取当前文件所在目录的目录名，即：按照命名规范，当前文件所在目录的父级目录为项目根目录。
# base_path = os.path.dirname(os.path.dirname(__file__))
# # print(base_path)
# account_db = os.path.join(base_path,'db','acc_db')

# articles_path = os.path.join(base_path,'articles')

# comments_path = os.path.join(base_path,'comments')

mongodb = "192.168.227.128"
'''
from dateutil import parser
# 时间戳转换成格式化时间
tm = time.time()
st = time.localtime(tm)
fm = time.strftime("%Y-%m-%d %H:%M:%S",st)

client = pymongo.MongoClient("mongodb://"+mongodb)
db = client["hw"]

truncate_1 = db.account.drop()
truncate_2 = db.article.drop()
truncate_3 = db.comment.drop()

insert_1 = db.account.insert_one(
    {
        "_id":0,
        "username":"admin",
        "pwd":"admin",
        "status":0,
        "createtm":parser.parse(fm)

    }
)

insert_2 = db.article.insert_one(
    {
        "_id":0,
        "article":{
            "title":"hello!",
            "paragraph":"test and initialize!",
            "userid":0,
            "createtm":parser.parse(fm),
            "is_daily":False
        },
        "comment_id":[0]
    }
)

insert_3 = db.comment.insert_one(
    {
    "_id":0,
    "article_id":0,
    "comment_user":"nobody",
    "comment_section":"Hi,",
    "comment_time":parser.parse(fm)
    }
)
'''