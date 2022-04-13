/*
	channel与range的配合使用.

	for data := range c { }// range c : 尝试从channel c 中读数据,如果c中有数据,range就返回值,否则就阻塞

*/
// 复用13-03-channel的关闭的代码
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

	/*
		for {
			// ok如果为true,表示channel没有关闭,否则为已经关闭
			if data, ok := <-c; ok { // if的另一种简写方式
				fmt.Println(data)
			} else {
				break
			}
		}
	*/
	// 这段for 可以简写. 用range来迭代,不断操作channel
	for data := range c { // range c : 尝试从c读数据,如果c中有数据,range就返回值,否则就阻塞
		fmt.Println(data)
	}

	fmt.Println("main end.")
}
