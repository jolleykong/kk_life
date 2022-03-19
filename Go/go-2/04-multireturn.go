/*
	函数的多返回值
*/
package main

import "fmt"

// 函数语法

func foo1(a string, b int) int { // a b为两个形参，返回值为int类型
	fmt.Println("a=", a)
	fmt.Println("b=", b)

	c := 100

	return c

}

func main() {
	c := foo1("abc", 123)
	fmt.Println(c)
}
