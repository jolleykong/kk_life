/*
	反射解析结构体标签
		结构体标签,就是结构体属性的注释,类json
		格式: `info:"name"` kv结构,支持多个kv,用空格间隔
*/
package main

import (
	"fmt"
	"reflect"
)

// 定义结构体,定义结构体标签
type resume struct {
	Name string `info:"name"`         // kv结构
	Sex  string `info:"sex" doc:"性别"` // 可以有多个kv
}

// 通过反射获取结构体标签
func findTag(str interface{}) {
	// 反射获取结构体全部元素,Elem() 表示获取当前结构体元素
	t := reflect.TypeOf(str).Elem()

	for i := 0; i < t.NumField(); i++ {
		taginfostring := t.Field(i).Tag.Get("info")
		fmt.Println("info:", taginfostring)
		//
		tagdocstring := t.Field(i).Tag.Get("doc")
		fmt.Println("doc:", tagdocstring)
	}
}

func main() {
	var kk resume // 实例化对象
	findTag(&kk)  // findTag()中使用了.Elem(),因此这里要传入指针.
	/*
	   info: name
	   doc:
	   info: sex
	   doc: 性别
	*/

}
