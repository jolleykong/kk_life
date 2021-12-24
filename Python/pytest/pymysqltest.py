import pymysql.cursors

# connect to db
connection = pymysql.connect( 
                                host='192.168.227.129',
                                user='kk',
                                password='kk',
                                charset='utf8mb4',
                                database='kk',
                                cursorclass=pymysql.cursors.DictCursor
                                )
with connection:
    # create db
    with connection.cursor() as cursor:
        sql1 = "show master status;"
        # sql2 = "create database yy"
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        print(result1)
        # cursor.execute(sql2)
        # result2 = cursor.fetchall()
        # print(result2)
        # result3 = cursor._get_db()
        # print(result3)
    # connection.commit()



    # with connection.cursor() as cursor:
    #     sql = "insert into k1(id,name) values(%s,%s)"
    #     cursor.execute(sql,('1','ky'))
    # connection.commit()
    # tbname='k1'
    # with connection.cursor() as cursor:
    #     sql = "select * from %s" %tbname
    #     cursor.execute(sql)
    #     result = cursor.fetchone()
    #     print(result)
    # # connection.commit()