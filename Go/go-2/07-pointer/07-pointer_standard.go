/*
	指针
	&x 获取变量x的指针
	*x 获取变量x的值

*/

package main

import "fmt"

// example 1
func changeValue1(p int) int {
	p = 10
	return p
}

func ex1() {
	var a int = 1
	changeValue1(a)
	fmt.Println("a=", a) // a = 1
}

// example 2
func ex2() {
	var a int = 1
	var b int = changeValue1(a)
	fmt.Println("a=", b) // a = 10
}

// 使用指针的方法
func changeValue2(p *int) { // step1 ，* 表示p是一个指向int类型的指针
	*p = 10 //	step3，改变当前p所指向的内存地址的值。
}

func pointer() {
	var a int = 1
	changeValue2(&a)     // step2，&表示传递的是a的内存地址
	fmt.Println("a=", a) // a = 10
}

/*
changeValue2(p *int) ,在内存中创建p，值为初始化地址0
传参&a， 将a在内存中的地址赋值给p，即：p在内存中的数据为参数a的内存地址 p=&a
*p=10 ，修改p所指向的地址的值，即p中值指向a，修改a的值为10.此时a已经被修改。
*/

// main
func main() {
	// example 1
	ex1()
	// 想实现通过函数修改a值的话，或许可以这样土方法
	ex2()
	// 接下来才是重点
	pointer()
}

/*
var addr		value
a  0x0089AB		1			//

p1 0x0999A1		0x0089AB	//一级指针，跳转一次便拿到目标。
p2 0x0999B1		0x0999A1	//二级指针，两次
p3 0x0999C1		0x0999B1	//三级指针，三次……
*/
