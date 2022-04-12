package main

import (
	"fmt"
	"runtime"
	"time"
)

// 无传参无返回值的匿名函数 加载goroutine.
func main() {
	// 用go创建一个形参为空 返回为空的匿名函数
	go func() { //#1
		defer fmt.Println("A.defer")

		func() { //#2
			defer fmt.Println("B.defer")
			// 运行完便结束了,退出当前goroutine
			// return	return的话,只退出当前子函数(#2).也就是B不会被打印,但不影响外层循环的执行
			runtime.Goexit() // runtime.Goexit() 会退出整个goroutine(#2,#1),也就是B不会打印,A也不会打印.
			fmt.Println("B")
		}() // 注意这个用法

		fmt.Println("A")
	}() // 注意这个用法

	// 死循环
	for {
		time.Sleep(1 * time.Second)
	}
}

/*

 */
