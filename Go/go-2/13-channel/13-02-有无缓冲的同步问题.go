/*
	无缓冲的channel在goroutine之间同步的过程:
		1. 两个goroutine都到达通道,但都没有执行发送或接收
		2. 发送端goroutine向通道发送数据,此时该goroutine被锁住
		3. 接收端goroutine从通道接收数据,此时该goroutine被锁住
		4. 数据交换ing
		5. 直到交换完成,发送和接收端goroutine的锁被释放,
		6. goroutine们可以做其他事情了
*/
/*
	有缓冲channel同步的过程:
		1. 接收端goroutine从channel中接收一个值,独立接收
		2. 发送端goroutine向channel中发送新值,独立发送
		3. 发送端向channel中发送新值,接收端从channel中接收另一个值,彼此之间不同步,也不阻塞
		4. 当所有的发送和接收都完成时,通道里还有几个值,也有一些空间可以存放更多的值.
		5. 当channel为空时,从channel中接收数据会阻塞,同理,当channel满时,向channel中发送数据会被阻塞.
*/
package main

import (
	"fmt"
	"time"
)

func main() {
	// 初始化一个带有缓冲的channel c,
	c := make(chan int, 3)
	fmt.Println("len:", len(c), "cap:", cap(c)) // len: 0 cap: 3

	// 开启一个子goroutine
	go func() {
		defer fmt.Println("sub goroutine end.")

		for i := 0; i <= 5; i++ {
			c <- i
			fmt.Println("in len:", len(c), "cap:", cap(c), "current:", i)
		}
	}()

	time.Sleep(1 * time.Second)

	for i := 0; i <= 5; i++ {
		num := <-c
		fmt.Println("num:", num)
	}

	fmt.Println("main goroutine end.")
}

/*
	len: 0 cap: 3
	in len: 1 cap: 3 current: 0
	in len: 2 cap: 3 current: 1
	in len: 3 cap: 3 current: 2	// 缓冲容量满
	num: 0
	num: 1
	num: 2
	num: 3						// 缓冲消耗的同时,新值被插入,这一块没法同时打印,因此有顺序的误解
	in len: 3 cap: 3 current: 3	// 同上
	in len: 0 cap: 3 current: 4
	in len: 1 cap: 3 current: 5
	sub goroutine end.		// 同上
	num: 4
	num: 5
	main goroutine end.

*/
