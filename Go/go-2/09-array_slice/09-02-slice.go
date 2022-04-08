/*
动态数组 slice, 也叫切片
长度是不定的
切片作为参数(形参)的时候,形参类型是一致的-->  如: []int
切片作为参数传入时,是引用传递,传递的是本身

动态数组\切片 slice 形式:
	myArray := []int{}			// 什么也没有
	myArray := []int{1,2,3,4} // 1,2,3,4
*/

package main

import "fmt"

func slicedemo() {
	myArray0 := []int{}
	myArray1 := []int{1, 2, 3, 4} // 给几个元素,就多长.
	myArray2 := []int{1, 2, 3, 4, 5, 6, 7}
	fmt.Printf("%T\n", myArray1) //[]int
	fmt.Printf("%T\n", myArray2) //[]int
	printArray(myArray0)         // 什么也没有
	printArray(myArray1)
	printArrayValue(myArray1)
}

// 动态数组做形参,类型是一致的,如[]int
// 传入一个切片,迭代切片内容,打印索引.
func printArray(myArray []int) {
	for idx, value := range myArray {
		fmt.Println("idx=", idx, "value:", value)
	}
}

// 传入一个切片,迭代切片内容,不打印索引.
func printArrayValue(myArray []int) {
	for _, value := range myArray { // 将索引匿名
		fmt.Println("value:", value)
	}
}

// 验证这里的printArray 的实参为引用传递,而不是值拷贝副本
func printArray2(myArray []int) {
	for idx, value := range myArray {
		fmt.Println("idx=", idx, "value:", value)
	}
	myArray[0] = 999
}

// 验证这里的printArray 的实参为引用传递
func slicedemo2() {
	myArray1 := []int{1, 2, 3, 4}      // 给几个元素,就多长.
	fmt.Printf("%T\n", myArray1)       //[]int
	printArray2(myArray1)              // 输出数组元素,调用printArray2 ,并对原数组尝试修改
	for idx, value := range myArray1 { // 输出原数组,用来比对是否被成功修改.
		fmt.Println(idx, value)
	}
}

func main() {
	slicedemo()

	// 验证这里的printArray 不是值拷贝副本
	fmt.Println("---")
	slicedemo2()
	/*
		slicedemo2
			idx= 0 value: 1
			idx= 1 value: 2
			idx= 2 value: 3
			idx= 3 value: 4
			0 999	// 原数组被修改.说明printArray2中传入的实参数组为原数组本身.
			1 2
			2 3
			3 4
	*/
}
