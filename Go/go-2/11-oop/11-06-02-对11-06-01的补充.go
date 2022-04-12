/* 换一种理解方式去理解11-06-01*/
package main

import "fmt"

// 定义接口Reader
type Reader interface {
	ReadBook()
}

// 定义接口Writer
type Writer interface {
	WriteBook()
}

// 定义类Book
type Book struct {
}

// 定义类方法ReadBook()
func (this *Book) ReadBook() {
	fmt.Println("read a book")
}

// 定义类方法WriteBook()
func (this *Book) WriteBook() {
	fmt.Println("write a book")
}

func main() {
	// b pair <type: Book, value: 实例化对象的地址>
	b := &Book{} // Book类实例化对象后的指针

	// r: pair<type:null,value:null>
	var r Reader
	// fmt.Printf("%T,%v\n", r, r)	// <nil>,<nil>,即:r: pair<type:null,value:null>
	// r: pair<type:Book,value:实例化对象的地址>
	r = b

	// Book.ReadBook()
	r.ReadBook() // read a book

	// w: pair<type:null,value:null>
	var w Writer

	// 断言
	//   step 1. 得到动态类型 type
	//   step 2. 判断type是否实现了目标接口

	// 1. 得到type:Book(r的type是Book),
	// 2.Book是否实现了Writer()? 实现了 --> 断言成功.即:reader指向的Book对象,Book对象实现了Writer接口
	// w: pair<type:Book,value:实例化对象的地址>
	w = r.(Writer)

	w.WriteBook() // write a book

}
