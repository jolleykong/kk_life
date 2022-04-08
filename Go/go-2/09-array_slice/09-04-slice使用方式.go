/*
	slice使用方式
		切片容量的追加 append(slice,n)
		切片的截取 类似python的浅copy

*/
package main

import "fmt"

func main() {
	// 声明一个切片,长度为3,容量为5
	var numbers = make([]int, 3, 5)
	fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
	// len=3,cap=5,slice=[0 0 0]

	// 结构图简介
	// [----    cap    ----]
	// [--  len  --]
	// | 0 | 0 | 0 | x | x |
	//             ^
	//            ptr

	// len 长度: 0 ~ ptr
	// ptr 尾部指针,永远指向当前切片的合法元素的最后位置
	// cap 容量
	// 后面的空间是不可以访问的,但底层已经开辟了.
	// 需要开辟这部分空间, 要使用append

	// 接下来向这个切片追加元素
	numbers = append(numbers, 1)
	fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
	// len=4,cap=5,slice=[0 0 0 1]

	// 继续追加1个元素
	numbers = append(numbers, 2)
	fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
	// len=5,cap=5,slice=[0 0 0 1 2]

	// 继续追加
	numbers = append(numbers, 1)
	fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
	// len=6,cap=10,slice=[0 0 0 1 2 1]
	// 自动扩容cap,会开辟已有cap长度的cap

	// 切片的截取,是浅copy
	s := []int{1, 2, 3}
	s1 := s[0:1] // 0
	s2 := s[0:2] // 0,1
	s3 := s[:]
	fmt.Println(s1, s2, s3) // [1] [1 2] [1 2 3]

	s2[0] = 999             // 这个需要注意,和py不同.切片截取后,实际指针指向的依然是相同的内存地址.也就是浅copy
	fmt.Println(s1, s2, s3) // [999] [999 2] [999 2 3]

	// 深copy方式将截取拷贝为副本
	// copy函数,将底层数组的slice一起拷贝
	s11 := []int{1, 2, 3}
	s22 := make([]int, 3) // 如果此时初始化的长度与s11长度不一致,短的话会截断,长的话会初始化0.

	copy(s22, s11)        // 将s11 深copy到s22
	fmt.Println(s11, s22) // [1 2 3] [1 2 3]

	s22[0] = 999
	fmt.Println(s11, s22) //[1 2 3] [999 2 3]

}
