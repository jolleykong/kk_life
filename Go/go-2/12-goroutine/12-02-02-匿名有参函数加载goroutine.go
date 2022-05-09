package main

import (
	"fmt"
	"time"
)

func main() {
	// 有传参返回值的匿名函数 加载goroutine.
	go func(a int, b int) bool { // 定义形参和返回类型, 匿名函数
		fmt.Println("a:", a, "b", b)
		return true
	}(10, 20) // 注意这个用法,传参.

	/*
		如何得到返回的true?
		flag := go func(a int, b int) bool { ... 是不支持的, 函数不会把返回值抛给函数上一层
		无法通过返回值拿到的, 这需要后面的channel知识来实现.--> 想让两个goroutine过程中间互相通信,使用channel
	*/

	// 死循环
	for {
		time.Sleep(1 * time.Second)
	}
}

/*
a: 10 b 20
*/
