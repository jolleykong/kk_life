// const 常量
package main

import "fmt"

func main() {
	// 把var换成const 就是声明常量。
	// 常量是只读属性噢。
	const length int = 10
	fmt.Println(length)

	/* 对常量进行修改会报错。
	length := 1000
	fmt.Println(length)
	*/

	// 用const来定义枚举类型
	const (
		beijing  = 0
		shanghai = 1
		liaoning = 2
		jilin    = 3
	)
	// 当枚举内容过多时，可以用iota
	// 在const中添加一个关键字iota，每行的iota都会累加1
	// 第一行的iota默认值为0

	const (
		bj = iota
		sh
		ln
		jl
	)

	fmt.Println(beijing, shanghai, liaoning, jilin, bj, sh, ln, jl)

	// iota可以参加数学运算，但是会有个小问题
	// 参加数学运算后，iota依然只对自己进行自增，
	// 因此在乘除时可能会出现预期之外的结果，如
	const (
		b = 10 * iota // 0
		c             // 10*1 = 10
		d             // 10*2 = 20
	)
	fmt.Println(b, c, d) // 0 10 20

	// iota是以行作为单位进行自增的
	const (
		aa, bb = iota + 1, iota + 2 // iota=0,0 -> 0+1,0+2
		cc, dd                      // iota=1,1 --> 1+1,1+2
		ee, ff                      // iota=2,2 ---> 2+1,2+2
		gg, hh = iota * 2, iota * 3 // iota=3,3 ----> 3*2,3*3
		ii, jj                      // iota=4,4 -----> 4*2,4*3
	)
	fmt.Println(aa, bb, cc, dd, ee, ff, gg, hh, ii, jj) // 1 2 2 3 3 4 6 9 8 12
}
