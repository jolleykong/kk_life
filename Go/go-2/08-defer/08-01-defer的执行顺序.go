/*
	知识点1，defer的执行顺序
	后进先出
*/
package main

import "fmt"

func func1() {
	fmt.Println("A")
}

func func2() {
	fmt.Println("B")
}

func func3() {
	fmt.Println("C")
}

func main() {
	defer func1()
	defer func2()
	defer func3()
}

/*
C
B
A
*/
