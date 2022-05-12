import pymongo


'''1.创建连接'''
# 1.创建连接
moclient = pymongo.MongoClient("mongodb://192.168.227.128:27017/")

'''2.查看数据库'''
# 2.查看数据库
dblist = moclient.list_database_names()
print(dblist)
    # ['admin', 'config', 'kk', 'local']

'''3.创建数据库/ 使用数据库'''
# 3.创建数据库/ 使用数据库
kk = moclient["kk"]

'''4.查看集合'''
# 4.查看集合
kk_collist = kk.list_collection_names()
print(kk_collist)
    # ['cur', 'inventory', 'students', 'k1']

'''# 5.创建集合，插入文档'''
# 5.创建集合
    # 创建的集合需要插入文档才会真正创建。
newdb = moclient["newdb"]
newcollection = newdb["sites"]  # 集合名： sites

'''# 5.1 insert_one 插入单个文档'''
# 5.1 insert_one 插入单个文档
'''
dict = {"_id":1,"name":"kk","age":17,"hobby":["sleep","shopping","music"]}
x = newcollection.insert_one(dict)
print(x)    # <pymongo.results.InsertOneResult object at 0x101546f00>
    # insert_one方法返回InsertOneResult对象，该对象包含insert_id属性。
print(x.inserted_id)    # 1
'''

'''# 5.2 insert_many 插入多个文档'''
# 5.2 insert_many 插入多个文档
'''
dictlist = [
    {"_id":10,"name":"kk","age":17,"hobby":["shopping","music"]},
    {"_id":11,"name":"yy","age":18,"hobby":["sports"]},
    {"_id":12,"name":"gg","age":19,"hobby":["working","marry"],"edu":{"young":"小学","middle":"中学","univ":"大学"}}
]

x = newcollection.insert_many(dictlist)
print(x)                # <pymongo.results.InsertManyResult object at 0x101fdb8c0>
print(x.inserted_ids)   # [10, 11, 12]
'''

'''# 6 查询'''
# 6 查询

# 6.1 查询一条数据
db = moclient["newdb"]
col = newdb["sites"] 
x = col.find_one()
print(x)    # {'_id': ObjectId('61cbccfd448982fca83eb87d'), 'name': 'kk', 'age': 17, 'hobby': ['sleep', 'shopping', 'music']}

# 6.2 查询集合中所有数据
for y in col.find():
    print("#",y)

# 6.3 指定查询的字段条件
for z in col.find({"name":"yy"}):
    print(z)

# 也可以这样
query = {"name":"yy"}
for zz in col.find(query):
    print(zz)

# 6.3 限定查询返回字段
    # 跟mongo中find() 用法一样了。
for z in col.find({"name":"yy"},{"_id":0,"hobby":0}):
    print(z)    # {'name': 'yy', 'age': 18}

# 6.4 使用修饰符
    # 修饰符参考mongo文档
query = {"age":{ "$gt":17, "$lt":19 }}
for a in col.find(query):
    print(a)

    # 大于和小于还能用来比较ASCII。 直接传入字符就可以。

# 6.5 使用正则表达式
    # 表达式用法为python语法
query = {"name":{"$regex":"^k"},"hobby":"sleep"}
for b in col.find(query):
    print('#',b)

# 6.6 限定返回条数
result = col.find().limit(2)
for i in result:
    print(i)

# 6.7 排序
result = col.find().sort("_id",-1)  # pymongo.DESCENDING , pymongo.ASCENDING
for i in result:
    print(i)



# 7 修改数据
    # update_one 和 update_many 两个方法
query = {"name":"kk"}
change = {"$set": { "age": 30 }}
x = col.update_many(query, change)
print(x)    # <pymongo.results.UpdateResult object at 0x103c27fc0>
print(x.modified_count)

for i in col.find({"name":"kk"},{"_id":0,"age":1,"name":1}):
    print(i)
    # {'name': 'kk', 'age': 30}
    # {'name': 'kk', 'age': 30}
    # {'name': 'kk', 'age': 30}
    # {'name': 'kk', 'age': 30}

# 8 删除数据

# 8.1 删除一个文档 delete_one()
query = {"name":"kk"}
x = col.delete_one(query)
print(x)    # <pymongo.results.DeleteResult object at 0x1054d7680>
    # >>> x.
    # x.acknowledged   x.deleted_count  x.raw_result

# 8.2 删除多个文档 delete_many()
    # 和delete_one同理

# 8.3 清空一个集合 delete_many({})
    # delete_many()必须要指定条件，如果条件为空，则清空集合，删除集合内全部文档

# 8.4 删除一个集合 drop()
col.drop()
    #或
db.sites.drop()

# 9 创建索引
# db.collection.create_index( [ (col,pymongo.DESCENDING/ASCENDING)   ]  )
col.create_index([("name",pymongo.DESCENDING),("age",pymongo.ASCENDING)])
