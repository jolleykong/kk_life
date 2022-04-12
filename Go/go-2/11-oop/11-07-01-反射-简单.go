/*
	反射
	reflect包

	pair: type&value
	反射就是通过变量,获取type或value

	ValueOf
		获取输入参数接口中的数据的值,如果接口为空则返回0
		func ValueOf(i interface{}) Value (...)
	TypeOf
		动态获取输入参数接口中的值的类型,如果接口为空则返回nil
		func TypeOf(i interface{}) Type (...)
*/
package main

import (
	"fmt"
	"reflect"
)

// 定义一个方法,传入变量后,返回变量的类型和变量的值
func relectNum(arg interface{}) {
	// 对arg进行反射处理
	fmt.Println("type:", reflect.TypeOf(arg))
	fmt.Println("value:", reflect.ValueOf(arg))

}

func main() {
	// 比较简单的反射
	var fnum float64 = 1.2345
	relectNum(fnum)
	// 		type: float64
	// 		value: 1.2345
}
