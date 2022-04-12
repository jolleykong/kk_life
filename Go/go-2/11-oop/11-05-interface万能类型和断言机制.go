/*
	interface 属于通用万能类型,
	interface{} 空接口
		int\string\float32\float64\struct 都实现了interface{},可以用interface{}类型引用任意的数据类型.

	interface 使用类型断言机制,对引用的数据进行类型判断.

	// 断言
	//   step 1. 得到动态类型 type (动态类型,11-06-01 pair结构)
	//   step 2. 判断type是否实现了目标接口
*/
package main

import "fmt"

// interface{} 是万能数据类型
func myFunc(arg interface{}) {
	fmt.Println(arg)
	// interface{} 如何区分此时引用的底层数据类型是什么类型?

	// 给interface{}提供"类型断言"机制,
	//    即:允许interface进行类型判断
	// 判断arg是否为字符串
	// 		arg.(string)   判断arg是否为string类型
	value, ok := arg.(string)
	if !ok {
		fmt.Println("arg is not string.")
		fmt.Printf("value type : %T\n", value) // 这一步实现是有问题的,因为结果显示都是string, mark 后续搞懂了回来补充.
	} else {
		fmt.Println("arg is string type,value=", value)
	}
}

type Books struct {
	auth string
}

func main() {
	myFunc(23) // 23
	// 				arg is not string.
	// 				value type : string

	book := Books{"kk"}
	myFunc(book) // {kk}
	//				arg is not string.
	//				value type : string

	myFunc("ss") // ss
	//				arg is string type,value= ss

}
