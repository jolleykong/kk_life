/*
	new(T)
	创建一个T类型变量，初始化为T类型的零值，返回其地址(*T)

	每次调用new(T) 返回的都是不同的地址
*/
package main

import "fmt"

func main() {
	st := new(string)
	fmt.Printf("%v,%T\n", *st, *st)

	in := new(int)
	fmt.Printf("%v,%T\n", *in, *in)

	sl := new([]string)
	fmt.Printf("%v,%T\n", *sl, *sl)

	// 重复调用new() ,地址也不相同
	a := new(int)
	b := new(int)
	fmt.Println(a == b) // false
	fmt.Println(&a, &b) // 0x1400012e020 0x1400012e028
	fmt.Println(*a, *b) // 0 0 返回的是指针,所以需要*
	// 对比
	var c int = 0
	var d int = 0
	fmt.Println(c == d) // true
	fmt.Println(&c, &d) // 0x14000134030 0x14000134038
	fmt.Println(c, d)   // 0 0
	//
	e := []int{0}
	f := []int{0}
	fmt.Println(&e == &f) // false
	fmt.Println(e, f)     //[0] [0]

	// 指针的赋值
	fmt.Println(*a)
	*a = 99
	fmt.Println(*a)

}

// ,string
// 0,int
// [],[]string
