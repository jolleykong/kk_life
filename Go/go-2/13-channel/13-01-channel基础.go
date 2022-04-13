/*
	goroutine之间通信, 使用channel 管道

	channel有同步两个不同goroutine之间的能力
*/

/*
	channel 定义
	// 使用make()方法创建并初始化channel
	make(chan Type) // 等价于 make(chan Type,0) , 指定channel中互相传递的数据类型,
	make(chan Type, capacity) // 有无缓冲

	//无缓冲的channel
	//有缓冲的channel
*/

/*
	向channel中写数据
	channel <- value // 发送value到channel
	<-channel        // 接收并将其丢弃
	x := <-channel     // 从channel中接收数据,并赋值给x
	x, ok := <-channel // 功能同上,同时检查通道是否已经关闭或者是否为空
*/

package main

import "fmt"

// 定义一个channel,并简单使用一下.
func main() {
	// 定义一个channel
	c := make(chan int) // c:=make(chan int,0)

	// 开启一个goroutine
	go func() {
		defer fmt.Println("goroutine end.")
		fmt.Println("goroutine running.")

		c <- 666 // 将666发送到c
	}()

	num := <-c // 从c中接收数据并赋值给num

	fmt.Println(num)
	/*	当注释掉 num := <-c 和 fmt.Println(num) 时,也就是main永远不执行对channel传入的值,开启下面循环,会发现sub goroutine也永远被阻塞.
		for {

		}

	*/
	fmt.Println("main goroutine end.")
}

/*
goroutine running.
goroutine end.
666
main goroutine end.

// 如果main先于sub goroutine执行到num赋值,sub goroutine此时还没有将值发送给channel c
// 那么main会在num赋值这里被阻塞,等待channel 的传入后,再继续进行
// 这就是为何每次都是main 最后退出,而不会出现main先于num执行完毕的情况.

// 同理,如果sub goroutine已经执行过c<-666,defer过后即将exit,但此时main还未执行到num赋值
// 那么sub也会被阻塞,直到main从channel中拿到值,sub才会继续进行下去(完成退出),也就是sub的defer肯定在main的num动作后才会执行.
// 也就是说,如果main不执行num := <-c,sub会永远被阻塞.(试一试,是这样的.)
*/
