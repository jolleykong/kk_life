/*
数组 array 的长度是固定的
固定长度的数组作为参数(形参)的时候,是严格匹配数组类型的
数组作为参数传入时,传入的是值拷贝的副本

数组 array形式:
	myArray := [10]int			// 0,0,0,0,0,0,0,0,0,0
	myArray := [10]int{1,2,3,4} // 1,2,3,4,0,0,0,0,0,0
*/
package main

import "fmt"

func demo() {
	/* 固定长度的数组 */
	var myArray1 [10]int

	// for i := 0; i < 10; i++ {
	for i := 0; i < len(myArray1); i++ {
		fmt.Println(myArray1[i]) // 10个0，默认数组初始化为0
	}

	// 前4个元素指定值， 后面元素默认0
	myArray2 := [10]int{1, 2, 3, 4}

	for i := 0; i < len(myArray2); i++ {
		fmt.Println(myArray2[i]) // 1,2,3,4,0,0,0,0,0,0
	}

	// 循环,打印下标
	for index, value := range myArray2 {
		fmt.Println("index=", index, "value=", value)
	}
	/*
		index= 0 value= 1
		index= 1 value= 2
		index= 2 value= 3
		index= 3 value= 4
		index= 4 value= 0
		index= 5 value= 0
		index= 6 value= 0
		index= 7 value= 0
		index= 8 value= 0
		index= 9 value= 0
	*/

	// 查看数组的数据类型
	fmt.Printf("myArray1 types = %T\n", myArray1) // myArray1 types = [10]int
	fmt.Printf("myArray2 types = %T\n", myArray2) // myArray2 types = [10]int

	myArray3 := [4]int{11, 22, 33, 44}
	fmt.Printf("myArray3 types = %T\n", myArray3) // myArray3 types = [4]int

	/*
		myArray1 types = [10]int
		myArray2 types = [10]int
		myArray3 types = [4]int
	*/

	// 将数组作为参数传递
	// 会面临一个问题:数组形参是固定长度,不适用不同长度的数组.
	myArray10 := [4]int{11, 22, 33, 44}
	printArrayA(myArray10) // 运行正常
	//myArray20 := [8]int{88, 77, 66, 55, 44, 33, 22, 11}
	//printArrayA(myArray20) // cannot use myArray20 (variable of type [8]int) as type [4]int in argument to printArray

	// 因此,需要将数组作为参数的时候,要使用动态数组

}

// 将数组作为参数传递
func printArrayA(myArray [4]int) {
	// 值拷贝,实际传入的是实参的副本
	for idx, value := range myArray {
		fmt.Println("idx:", idx, "value:", value)
	}
}

//printArrayA 是值拷贝实现的,实际传入的是实参的副本
// 验证一下 -> demo2
func printArrayB(myArray [4]int) {
	// myArray是值拷贝,实际传入的是实参的副本
	for idx, value := range myArray {
		fmt.Println("idx:", idx, "value:", value)
	}
	myArray[0] = 999 // 修改的是拷贝的元素,并不是原数组对象.
}

func demo2() {
	myArray10 := [4]int{11, 22, 33, 44}
	printArrayB(myArray10)
	// 调用函数后, 再次打印myArray10,来观察函数中myArray[0] = 999 动作是否对数组造成了修改
	for idx, value := range myArray10 {
		fmt.Println(idx, value)
	}
}

func main() {
	// 固定长度数组demo
	demo()

	// demo2 , 验证printArray 是值拷贝实现的,实际传入的是实参的副本
	fmt.Println("---")
	demo2() //myArray[0] = 999 没有影响到myArray10 的元素
	/*
		demo2
			idx: 0 value: 11
			idx: 1 value: 22
			idx: 2 value: 33
			idx: 3 value: 44
			0 11
			1 22
			2 33
			3 44
	*/

}
