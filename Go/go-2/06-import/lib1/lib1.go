package lib1 // 一般包名和文件名一致

import "fmt"

// 当前lib1包提供的API
func Lib1Test() { // 函数名首字母大写 代表对外可以调用。小写表示内部调用。
	fmt.Println("lib1.Lib1Test()")
}

func init() {
	fmt.Println("lib1.init()")
}
