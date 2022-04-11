/*
	OOP-01-结构体的定义与使用
	type
	type xxx struct  定义结构体
*/
package main

import "fmt"

// 1.声明一种新的数据类型 myint， 是int的一个别名
type myint int

// 2.定义一个结构体Book
type Book struct {
	title string
	auth  string
}

// 3.传递的是book的副本？(尝试修改book的内容来验证)
func changeBook(book Book) {
	book.auth = "new_auth"
}

// 4.传入指针
func changeBook2(book *Book) {
	book.auth = "new_auth"
}

func main() {
	// 1.type 自定义类型
	var a myint = 10
	fmt.Println("a:", a)                // a: 10
	fmt.Printf("a is type of :%T\n", a) // a is type of :main.myint

	// 2.type定义结构体
	var book1 Book
	book1.title = "Learning Golang"
	book1.auth = "kk"
	fmt.Printf("book1 type is :%T\n", book1) // book1 type is :main.Book
	fmt.Printf("%v\n", book1)                // {Learning Golang kk}

	// 3.验证实参传入type时，传入的是副本
	changeBook(book1)         // 传入book1，看book1.auth是否会被函数修改。
	fmt.Printf("%v\n", book1) // {Learning Golang kk}， 未被修改。

	// 4.传入指针
	changeBook2(&book1)       // 注意传入的是指针
	fmt.Printf("%v\n", book1) // {Learning Golang new_auth}
}
