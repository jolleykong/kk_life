/*
	function - 3
	init函数与import导包 - import导包
	main --> import --> const .. --> var .. --> init() --> main()

从 init函数 一环节可以看到，在import包之后，调用函数时会先执行包的init()，
有一种情况就是，如果import了包，但只需要包的init()，除此之外在程序中并不需要
用到包中任何一个function，此时直接使用，在编译运行阶段会抛出错误，提示引用的包未被使用。

此时可以用_ 匿名的方式导入包，这样便无法使用包内方法，但会执行包的init方法。

语法：
import 别名 包名
*/
package main

import (
	// 方法1 匿名
	_ "06-import/lib1" // 以_作为别名给lib1，相当于以匿名方式导入lib1包

	// 方法2 常规导入
	"06-import/lib2" // 常规导入包

	// 方法3 命名别名
	kklib3 "06-import/lib3" // 以kklib3作为别名给lib3，方便后面以别名引用包。

	// 方法4 导入当前命名空间，尽量少用
	. "06-import/lib4" // 导入到当前命名空间，引用时无需加包名
)

func main() {
	// lib1.Lib1Test() // 匿名方式导入lib1包后，也无法使用lib1. 的方式调用包内函数。

	lib2.Lib2Test()

	kklib3.Lib3Test()

	Lib4Test() // 导入到当前命名空间后，引用时无需加包名
}

/*
lib1.init()		// 依然调用了lib1的init() 方法
lib2.init()
lib3.init()
lib4.init()
lib2.Lib2Test()
lib3.Lib3Test()
lib4.Lib4Test()
*/
