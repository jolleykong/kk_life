/*
	关闭channel
		1. channel不像文件一样需要经常去关闭,只有确实没有任何发送数据了,或者想显式的结束range循环之类的,才会去关闭channel
		2. 关闭channel后,无法向channel再发送数据. 即:再发送会引发panic错误,(错误后导致接收立即返回0)
		3. 关闭channel后,可以继续从channel接收数据.
		4. 对于nil channel,无论收发都会被阻塞.
			// nil channel ,即没经过make的channel,只做了var chan channel 声明的通道.

*/
package main

import "fmt"

func main() {
	c := make(chan int)

	go func() {
		for i := 0; i < 5; i++ {
			c <- i
		}

		// close 关键字,关闭一个channel
		close(c)
	}()

	for {
		// ok如果为true,表示channel没有关闭,否则为已经关闭
		if data, ok := <-c; ok { // if的另一种简写方式
			fmt.Println(data)
		} else {
			break
		}
	}

	fmt.Println("main end.")
}

/* 不关闭channel,即://close(c) ,输出结果会有报错,main 并未执行完便抛出了异常
0
1
2
3
4
fatal error: all goroutines are asleep - deadlock!
	//   sub goroutine 完成了传入, main goroutine 接收完了channel中的数据,
	//   继续请求数据被阻塞,这就导致main的循环永远不会结束,进入死锁

*/

/* 关闭channel,即:close(c),main执行完成,无异常
0
1
2
3
4
main end.

*/
