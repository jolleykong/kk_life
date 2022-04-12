/*
	变量的内置pair结构:
		类型断言的实现机制:
		golang中定义的变量,实际变量是由两部分构成:type,value.
			type和value就是变量的pair结构.每个变量都有两个指针指向type和value
			type 当前变量的类型
				类型分为两类: static type 静态类型 和 concrete type 具体类型, 一个变量只能是其中一种的类型.
					static type: 基本的类型,int float string等等等等.
					concrete type: 具体类型就是interface所指向的具体数据类型,即:系统runtime实际看到的类型.
			value 当前变量的值


	反射:
		通过变量,来得到变量的type,(变量的具体类型),也可以通过变量来得到变量具体的value.

*/
package main

import (
	"fmt"
	"io"
	"os"
)

func main() {

	// 1.
	var a string // pair < statictype:string, value:"abced">
	a = "abced"

	// 2.
	var allType interface{} // pair<type:string, value:"abced">
	allType = a

	value, ok := allType.(string)
	fmt.Println(value, ok) // abced true 变量赋值给其他变量后,变量的pair也不会变化.

	// 3.
	// tty: pair <type:*os.File,value:"/dev/tty" 文件描述符>
	tty, err := os.OpenFile("/dev/tty", os.O_RDWR, 0)

	if err != nil {
		fmt.Println("open error", err)
		return
	}

	// r:pair<type: , value: >
	var r io.Reader
	// r:pair<type: *os.File, value: "/dev/tty" 文件描述符>
	r = tty

	// w:pair<type:,value:>
	var w io.Writer
	// w:pair<type: *os.File ,value: "/dev/tty" 文件描述符>
	w = r.(io.Writer) // 断言

	w.Write([]byte("HELLO this is a test!")) // HELLO this is a test!

}
