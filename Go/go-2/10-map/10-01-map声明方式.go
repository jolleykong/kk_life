/*
	map,kv结构
	声明方式
		1.声明,再开辟空间
			var myMap1 map[string]int
			myMap1 = make(map[string]int, 10)
		2.声明并开辟空间,但不初始化值
			myMap2 := make(map[string]string)
		3.声明并初始化值
			myMap3 := map[string]string{ "one": "php","two": "golang",}
*/
package main

import "fmt"

func main() {
	/* 方法1 */
	// 声明myMap1是一种map类型, key为string,value为int
	var myMap1 map[string]int
	// 此时myMap 为 nil
	if myMap1 == nil {
		fmt.Println("空map")
	} else {
		fmt.Println("不是空map")
	}
	// 为空map开辟空间,分配10个kv对
	myMap1 = make(map[string]int, 10)
	fmt.Printf("type = %T,len = %d,map = %v\n", myMap1, len(myMap1), myMap1) // type = map[string]int,len = 0,map = map[]

	myMap1["one"] = 1
	myMap1["two"] = 2
	fmt.Printf("type = %T,len = %d,map = %v\n", myMap1, len(myMap1), myMap1) // type = map[string]int,len = 2,map = map[one:1 two:2]

	/* 方法2 */
	// 不初始化值
	myMap2 := make(map[string]string)
	myMap2["name"] = "kk"
	myMap2["addr"] = "Beijing,China"
	fmt.Printf("type = %T,len = %d,map = %v\n", myMap2, len(myMap2), myMap2) // type = map[string]string,len = 2,map = map[addr:Beijing,China name:kk]

	/* 方法3 */
	// 初始化值
	myMap3 := map[string]string{
		"one": "php",
		"two": "golang",
	}
	fmt.Printf("type = %T,len = %d,map = %v\n", myMap3, len(myMap3), myMap3) // type = map[string]string,len = 2,map = map[one:php two:golang]

}
