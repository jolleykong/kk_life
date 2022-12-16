import pymysql.cursors
import time

# connect to db
connection = pymysql.connect( 
                                host='-',
                                user='-',
                                password='-',
                                charset='utf8mb4',
                                database='zabbix',
                                cursorclass=pymysql.cursors.DictCursor
                                )
with connection:
    # create db
    with connection.cursor() as cursor:
        sql1 = "select min(clock) as start from events;"
        sql2 = "select unix_timestamp(subdate(now(),90)) as end;"
        sql_1 = "delete from zabbix.events where clock<(%s);"

        cursor.execute(sql1)
        result1 = cursor.fetchone()

        v_startline = result1['start'] # 1643686379


        cursor.execute(sql2)
        result2 = cursor.fetchone()

        v_endline = result2['end']

        print('begin: ',v_startline)
        print('end: ',v_endline)

        print('<--Start. ',time.strftime("%Y-%m-%d %H:%M:%S") )
        while v_startline + 100000 < v_endline:
            v_startline = v_startline + 100000
            cursor.execute(sql_1,(v_startline))
            result = cursor.fetchone()
            print(result)
            print( time.strftime("%Y-%m-%d %H:%M:%S") )
            connection.commit()

        cursor.execute(sql1)
        result_final = cursor.fetchone()
        print('Done. ',result_final)
        print('-->Done.' ,time.strftime("%Y-%m-%d %H:%M:%S"), '\n' )


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