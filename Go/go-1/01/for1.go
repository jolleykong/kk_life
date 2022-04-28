package main

import (
	"fmt"
	"os"
)

func main() {
	for1()
}

// for mode 1
func for1() {
	var s, sep string
	for i := 1; i < len(os.Args); i++ { // os.Args[0]为程序本身的命令，因此从1开始取命令行参数
		s += sep + os.Args[i] // 此时sep未赋值，默认为''空字符串
		sep = " "             // 第一个索引使用之后，显式赋值为空格字符。
	}
	fmt.Println(s)
}
