import pymongo,time
from dateutil import parser

mongodb = "192.168.227.128"

# 获取当前格式化时间
def getftime():
     tm = time.time()
     st = time.localtime(tm)
     fm = time.strftime("%Y-%m-%d %H:%M:%S",st)
     return fm


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
        "createtm":parser.parse(getftime())

    }
)

insert_2 = db.article.insert_one(
    {
        "_id":0,
        "article":{
            "title":"hello!",
            "paragraph":"test and initialize!",
            "userid":0,
            "createtm":parser.parse(getftime()),
            "is_daily":False,
            "comment_id":[]
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
    "comment_time":parser.parse(getftime())
    }
)