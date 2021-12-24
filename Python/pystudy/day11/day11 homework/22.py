'''
22.写函数，返回一个扑克牌列表，里面有52项，每一项是一个元组，如[('红心',2),('草花','A')...]
'''
def apoker():
    # 花色
    colors = ['红桃','黑桃','梅花','方片']
    # 牌
    turns = ['A',2,3,4,5,6,7,8,9,10,'J','Q','K']
    jokers = ['大王','小王']

    poker = []

    for color in colors :
        for turn in turns:
            poker.append((color,turn))
    poker = poker + jokers

    return poker

print(apoker())