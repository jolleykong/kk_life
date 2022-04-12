package main

import (
	"fmt"
	"reflect"
)

// 定义User类
type User struct {
	Id   int
	Name string
	Age  int
}

// 打印对象信息
func (this *User) Call() { // 传入指针的方法不被记入inputType.NumMethod(),回头研究一下为什么.
	// 据说在go 1.17开始 NumMethod() 只能导出接口的不公共的方法.
	fmt.Println("user is called..")
	fmt.Printf("%v\n", this)
}
func (this User) Call2() {
	fmt.Println("user is called..")
	fmt.Printf("%v\n", this)
}

func DofiledAndMethod(input interface{}) {
	// 获取input的type
	inputType := reflect.TypeOf(input)
	fmt.Println("type :", inputType)

	// 获取input的value
	inputValue := reflect.ValueOf(input)
	fmt.Println("value:", inputValue)

	// 通过type获取里面的属性
	//  1.获取interface的reflect.Type,通过Type 得到NumField,即:属性数量,进行遍历
	//  2.得到每一个Field,数据类型
	//  3.通过field的Interface()方法,得到对应的value.
	for i := 0; i < inputType.NumField(); i++ {
		field := inputType.Field(i)              // 获取字段类型,type
		value := inputValue.Field(i).Interface() // 获取字段值,value
		//fmt.Println(field, value)
		fmt.Printf("type: %s:%v=%v\n", field.Name, field.Type, value)
	}

	// 通过type,获取里面的方法method
	// go 1.17开始,Call()方法传入指针的话不会被统计. 回头研究这块细节.
	// 临时完成实验的方法是使用Call2(),即:不使用指针传入,该为值传入.
	for i := 0; i < inputType.NumMethod(); i++ {
		m := inputType.Method(i)
		fmt.Printf("method: %s:%v\n", m.Name, m.Type)
	}
}

func main() {
	user := User{1, "kk", 21}
	user.Call()
	fmt.Println("----------------------")
	DofiledAndMethod(user)
	/*
		type : main.User
		value: {1 kk 21}
		{Id  int  0 [0] false} 1
		Id:int=1
		{Name  string  8 [1] false} kk
		Name:string=kk
		{Age  int  24 [2] false} 21
		Age:int=21

	*/
}
