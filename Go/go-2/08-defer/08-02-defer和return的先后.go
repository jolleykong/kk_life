/*
	知识点2，defer和return的先后顺序
	return 和 defer 同时在一个函数中， return要优先于defer调用
		可以理解为：defer 紧跟在函数}前面调用，return在} 前面
			return 0 ^} ,其中^ 的位置为refer调用位置
*/
package main

import "fmt"

func deferFunc() int {
	fmt.Println("defer func called")
	return 0
}

func returnFunc() int {
	fmt.Println("return func called")
	return 0
}

func returnAndDefer() int {
	defer deferFunc()
	return returnFunc()
}

func main() {
	returnAndDefer()
}

/*
return func called
defer func called
*/
