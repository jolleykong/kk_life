package main

import "fmt"

// 遍历函数
func printMap(vmap map[string]string) { // 注意形参是包含map的string string类型的.
	// 遍历
	for key, value := range vmap {
		fmt.Println("key:", key)
		fmt.Println("value:", value)
	}
}

// 一个修改函数, 看传入的实参map是否为地址传递
func modifyMap(vmap map[string]string) {
	vmap["test"] = "test"
}

func main() {
	cityMap := make(map[string]string)

	// 添加
	cityMap["China"] = "Beijing"
	cityMap["U.S"] = "NewYork"

	// 遍历
	printMap(cityMap)

	// 删除
	delete(cityMap, "U.S")

	// 修改
	cityMap["China"] = "BEIJING"

	// 遍历
	printMap(cityMap)

	// 声明一个string int 类型的map,验证printMap形参对map类型的限制
	//eglsMap := make(map[string]int)
	//eglsMap["one"] = 1
	//eglsMap["two"] = 2
	//printMap(eglsMap) // 非法类型, cannot use eglsMap (variable of type map[string]int) as type map[string]string in argument to printMap
	//

	// 调用modifymap() ,验证传入的map实参是否为地址传递
	fmt.Println("----------")
	// 修改前迭代一次
	printMap(cityMap)
	fmt.Println("----------B")
	// 调用修改函数
	modifyMap(cityMap)
	fmt.Println("----------A")
	// 修改后迭代一次
	printMap(cityMap)

	/*
		----------
		key: China
		value: BEIJING
		----------B
		----------A
		key: China
		value: BEIJING
		key: test
		value: test
		验证传入的实参为地址传递,原map被函数所修改.
	*/
}
