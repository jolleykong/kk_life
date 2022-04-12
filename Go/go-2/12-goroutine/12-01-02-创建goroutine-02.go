/*

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

	fmt.Println("main goroutine exit.") // 主goroutine退出后,所有子goroutine立即结束

	/*  主goroutine死循环部分
	i := 0
	for {
		i++
		fmt.Printf("new goroutine: i = %d \n", i)
		time.Sleep(1 * time.Second)
	}
	*/

}
