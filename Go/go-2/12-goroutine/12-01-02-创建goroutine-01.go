/*
	通过go 关键字来开辟一个goroutine
		i.e: go newTask()
	通过 runtime.Goexit() 退出当前的goroutine

*/

package main

import (
	"fmt"
	"time"
)

// 子 goroutine
func newTask() {
	i := 0
	for {
		i++
		fmt.Printf("new goroutine: i = %d \n", i)
		time.Sleep(1 * time.Second)
	}
}

// 主 goroutine
func main() {
	// 创建一个goroutine ,执行newTask()流程
	go newTask()

	i := 0
	for {
		i++
		fmt.Printf("new goroutine: i = %d \n", i)
		time.Sleep(1 * time.Second)
	}
}
