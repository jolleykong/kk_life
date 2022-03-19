/*
	4种变量声明方法
	- 声明全局变量可以使用方法1、2、3
	- 方法4只能在函数体内使用。

*/
package main

import "fmt"

// 声明全局变量
var vA int = 1

// 方法4不适用于声明全局变量。
// vB := 1

func main() {
	// 1 声明一个变量，指定类型。 默认值是0
	var a int
	fmt.Println("a =", a)
	fmt.Printf("type of a = %T\n", a)

	// 2 声明一个变量，指定类型， 并初始化一个值
	var b int = 1
	fmt.Println("b =", b)
	fmt.Printf("type of b = %T\n", b)

	var bb string = "bbbbb"
	fmt.Printf("bb = %s,type of bb = %T\n", bb, bb)

	// 3 声明一个变量，初始化时省去数据类型
	var c = 1
	fmt.Println("c =", c)
	fmt.Printf("type of b = %T\n", b)

	var cc = "ccccc"
	fmt.Printf("cc = %s,type of cc = %T\n", cc, cc)

	// 4 常用，省去var关键字，直接自动匹配
	// 会自动推算出类型。
	// 唯独方法4与前三者不同。方法4只能在函数体内使用。
	e := 100
	fmt.Println("e = ", e)
	fmt.Printf("type of e = %T\n", e)

	f := "ffffff"
	fmt.Println("f = ", f)
	fmt.Printf("type of f = %T\n", f)

	g := 3.1411111
	fmt.Println("g = ", g)
	fmt.Printf("type of g = %T\n", g)

	// 声明多个变量
	//   多个变量相同数据类型的
	var xx, yy int = 100, 200
	fmt.Println("xx= ", xx, " yy=", yy)
	//   多个变量不同数据类型的
	var uu, vv = 100, "abcd"
	fmt.Println("uu= ", uu, " vv=", vv)
	//    多行进行多个变量声明
	var (
		hh int    = 100
		jj bool   = true
		nn string = "bbvvccnn"
	)
	fmt.Println("hh=", hh, "jj=", jj, "nn=", nn)

}
