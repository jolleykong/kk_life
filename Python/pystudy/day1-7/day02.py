# 如何中止/终止while循环？
## 通过改变条件来中止while循环：
sign = True
while sign:
    print(1)
    sign = False   ## 改变条件。
    print(2)       ## 改变条件后，这一行依然会执行，因为while的判断会在程序段执行完这一次后，才再次进行判断。

## 通过break 直接终止循环

## 通过continue 终止本次循环，继续下一次循环。

# while ... else
## 如果while循环没有被break中断，那么会执行else段内容。

# while 1 比 while True 性能好。因为True需要转换成1，直接写成1就不用转换了。

# 格式化输出
## 让字符串变为动态可传入的。
## ./格式化输出.py


# 字符编码

# 文件操作
# 数据类型