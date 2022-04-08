package main

import "fmt"

// 交换两个变量值

// 值传递方式swap1
func swap1(a, b int) (int, int) {
	var temp int
	temp = a
	a = b
	b = temp
	return a, b
}

// 值传递方式 m1

func m1() {
	var a int = 10
	var b int = 20
	a, b = swap1(a, b)
	fmt.Println("a=", a, "b=", b)
}

// 指针方式 swap2 地址传递
func swap2(a, b *int) {
	var tmp int
	tmp = *a // tmp == main::a
	*a = *b  // main::a == main::b
	*b = tmp // main::b == tmp
}

// 地址传递方式 m2
func m2() {
	var a int = 10
	var b int = 20
	swap2(&a, &b)
	fmt.Println("a==", a, "b==", b)

	// 一级指针
	var p *int
	p = &a
	fmt.Println(&a) //0x14000122020
	fmt.Println(p)  //0x14000122020
	fmt.Println(&p) //0x1400011c020

	var pp **int //**int，二级指针
	pp = &p
	fmt.Println(&p)  //0x1400011c020
	fmt.Println(pp)  //0x1400011c020
	fmt.Println(&pp) //0x1400011c028
}

func main() {
	// 值传递方式m1
	m1() // a= 20 b= 10

	// 指针实现地址传递方式m2
	m2() // a== 20 b== 10

}
