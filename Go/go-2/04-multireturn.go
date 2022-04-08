/*
	function - 1
	函数的多返回值
*/
package main

import "fmt"

// 函数语法

//    1.返回一个值的函数
func foo1(a string, b int) int { // a b为两个形参，返回值为int类型，返回一个值
	fmt.Println("a=", a)
	fmt.Println("b=", b)

	c := 100

	return c
}

//    2.返回两个值的函数，匿名
func foo2(a string, b int) (int, int) {
	c := 101
	d := 102
	return c, d
}

//   3.允许给返回值命名，有形参名称
func foo3(a string, b int) (r1 int, r2 int) {
	r1 = 101 // 如果未对r1 r2赋值， 那么会返回为0。因为两个有名称的形参定义后，初始化的默认值是0值。
	r2 = 102
	return
}

//    4.多个返回值类型一致时，可以一次声明类型
func foo4(a string, b int) (r1, r2 int) {
	r1 = 201 // 如果未对r1 r2赋值， 那么会返回为0。因为两个有名称的形参定义后，初始化的默认值是0值。
	r2 = 202
	return
}

func main() {
	// 调用返回一个值的函数
	c := foo1("abc", 123)
	fmt.Println(c)

	// 调用返回两个值的函数
	c2, c3 := foo2("aaa", 234)
	fmt.Println(c2, c3)

	//
	r1, r2 := foo3("aa", 345)
	fmt.Println(r1, r2)

	//
	r3, r4 := foo4("a", 456)
	fmt.Println(r3, r4)
}
