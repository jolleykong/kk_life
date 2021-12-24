'''
题目描述

输入一个字符串，求最大的没有重复字符的子字符串长度

比如：输入huaweicloudaigallery

输出 9 （huaweiclo或aweicloud或weiclouda）
代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

string = input()  # 手动输入字符串

def func():
    # 在此编写代码



    print(maxlength)


func()

'''
# string = input()  # 手动输入字符串 # huaweicloudaigallery
string = 'huaweicloudaigallery'

def func():
    # 在此编写代码
    # 将字符串转为list，即：拆为字母。
    list_l = list(string)
    result = ''
    tmp = []
    res = []

    for idx in range(len(list_l)):
        i = list_l[idx]
        j = idx + 1
        # 比较元素i是否在tmp有重复出现，也就是判断之前是否重复出现过。 如果没有重复出现，则将这个元素追加到tmp中。
        if i not in tmp:
            tmp.append(i)

        else:
            # 如果元素在tmp有重复出现，在则拼接当前tmp list内的所有元素并输出结果，
            result = ''.join(tmp)
            # 再获取tmp list中该元素的位置，并将该位置以前的元素全部清理掉，再插入这个重复元素。
            del tmp[:tmp.index(i) + 1]
            # print(tmp)
            tmp.append(i)
        # 如果有拼接结果，则将拼接结果插入到res中
        if len(result) > 0 :
            # 直接去重
            if result not in res:
                res.append(result)
    # # 完成循环，对res去重后输出详情
    # res = set(res)
    # # print(res)

    # 获取最长结果
    maxlength = max([len(x) for x in res ])
    maxeles = [ eles for eles in res if len(eles) == maxlength  ]

    print(maxlength)
    print(maxeles)

func()
