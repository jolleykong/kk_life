/*
	channel与select配合使用
		select具备多路channel的监控状态功能.

		单流程下,一个go只能监控一个channel的状态.
			select可以完成监控多个channel的状态.
			select动作是无序的,这个需要关注.

		select {
		case <- chan1:
			// 如果chan1成功读到数据,则进行该case处理语句
		case chan2 <- 1:
			// 如果成功向chan2 写入数据,则进行该case处理语句
		default:
			// 如果上面都没有成功,则进入default处理流程
		}

		select可以和for搭配使用, 循环判断.
*/
package main

import (
	"fmt"
)

func fibonacii(c, quit chan int) {
	x, y := 1, 1 // 初始化xy
	for {        // 开启循环
		select { // select的动作是无序的,也就是会随机select一个ready的case, 这里需要注意.这并不是按照书写的case顺序去依次顺次判断的.
		case c <- x:
			// 如果c可写,该case就会进来
			x, y = y, x+y // 赋值,赋值后x传入c,本次select结束,继续下一次for循环做select判断.

		case <-quit:
			// (select是无序的)sub go中完成10次循环后,会向quit中传入0,此时quit有效,select无序选择中选中了该case,for循环结束,函数调用结束.
			fmt.Println("quit")
			return // 结束for循环,也就是结束了fibonacii() .

			//default:
			//		用来验证select是无序的.
			//	fmt.Println("default")
		}
	}
}

func main() {
	c := make(chan int)
	quit := make(chan int)

	// sub goroutine
	go func() {
		for i := 0; i < 10; i++ { // 10次循环,每次都从channel中接收一个值并打印出来
			fmt.Println(<-c)
			//quit <- 1	  // 注释掉.这个只用来验证select动作是无序的.当解开注释的时候,可发现
			//在sub goroutine未完成10次循环时(依然在向channel中传入数据\依然在从channel中读取数据时),便读取了quit,结束了运行.
			//说明并不是因为10次循环后阻塞管道而继续选择另一个case,选择另一个case的原因是随机选择中了这个刚可用的case.
		}
		quit <- 0 // 完成10次循环后,向quit传递0值
	}()

	// main goroutine
	fibonacii(c, quit) // 执行函数,直到函数return, main goroutine也就结束了.
}

/*
1
1
2
3
5
8
13
21
34
55
quit

*/
