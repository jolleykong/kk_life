#需求：允许猜3次。猜3次失败后，询问是否继续，确认继续后，继续猜3次。回答n则退出。答对了也退出。
from datetime import datetime
import random

# 随机生成个年龄
yo = random.randint(1,99)

status = True

while status :
    enter = input('输入y进入游戏，输入n退出:')
    if enter.lower() == 'y' :
        # 初始尝试次数为1
        try_cnt = 1
        while try_cnt <= 3 :
            in_yo = int(input('猜猜我有多少岁了？>>:'))
            # 猜对了
            if in_yo == yo :
                print('你怎么这么牛逼呢！\n 还玩吗！')
                break
            # 猜小了
            elif in_yo < yo :
                print('我哪有那么年轻')
                try_cnt+=1
                continue
            # 猜大了
            elif in_yo > yo :
                print('我哪有那么老')
                try_cnt+=1
                continue
        else :
                # 结束一轮，给出答案
                print('还玩吗？\n 其实我',yo,'岁！')
    elif enter.lower() =='n' :
        # 输出告别信息。
        print('拜了个拜，结束游戏时间：',datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
        # 修改状态，结束所有while循环。
        status = False
