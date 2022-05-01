package main

import (
	"fmt"
	"os"
)

func main() {
	for2()
}

// for mode 2
// 这是for循环的第二种形式。循环在字符串或slice数据上迭代，
func for2() {
	s, sep := "", ""                  // 短的变量声明法，初始化变量
	for _, arg := range os.Args[1:] { // 每一次迭代，range产生一对值： 索引和这个索引对应的元素
		// 虽然例子里没使用索引，但是语法上range循环需要处理，因此
		// 使用空标识符 _ 来做“临时变量“，go不允许临时变量，
		// 空标识符_可以用在任何语法需要变量名，但程序逻辑不需要的地方
		// 如，丢弃每次迭代产生的无用索引。
		// 大多数go 程序员喜欢搭配range和_ 来写这个程序，
		// 因为索引在os.Args上是隐式的，使用_和range更不易犯错。
		s += sep + arg
		sep = " "
	}
	fmt.Println(s)
}

// 数据量大时，s += sep + arg 方法效率很低，可以使用strings包的Join函数
// fmt.Println(strings.Join(os.Args[1:]," "))
