/*
	slice声明定义方式
		1.声明,初始化定义默认值:
			slice1 := []int{1, 2, 3}
		2.声明:
			var slice2 []int
		  初始化:
			slice2 = make([]int, 3)
		3.声明,初始化分配空间
			var slice3 []int = make([]int, 3)
		4.声明,初始化分配空间
			slice4 := make([]int, 3)
*/
package main

import "fmt"

func main() {

	/* 方法1 */
	fmt.Println("==方法1==")
	// 声明slice1是一个切片,并且初始化默认值为1,2,3
	slice1 := []int{1, 2, 3}
	fmt.Printf("len=%d,slice=%v\n", len(slice1), slice1)
	// len=3,slice=[1 2 3]

	/* 方法2 */
	fmt.Println("==方法2==")
	// 声明slice2是一个切片,但没有给slice2分配空间
	var slice2 []int
	fmt.Printf("len=%d,slice=%v\n", len(slice2), slice2)
	// len=0,slice=[]

	// 此时对slice2进行迭代会报错 panic: runtime error: index out of range [0] with length 0
	//fmt.Println(slice2[0])
	//要使用slice2,需要为slice2开辟空间(长度\容量)
	slice2 = make([]int, 3) // 开辟3个空间,默认值为0
	fmt.Printf("len=%d,slice=%v\n", len(slice2), slice2)
	// len=3,slice=[0 0 0]

	/* 方法3 */
	fmt.Println("==方法3==")
	// 声明slice3是一个切片,并初始化,开辟3个空间,值0
	var slice3 []int = make([]int, 3)
	fmt.Printf("len=%d,slice=%v\n", len(slice3), slice3)
	// len=3,slice=[0 0 0]

	/* 方法4 */
	fmt.Println("==方法4==")
	// 从方法3推导
	slice4 := make([]int, 3)
	fmt.Printf("len=%d,slice=%v\n", len(slice4), slice4)
	// len=3,slice=[0 0 0]

	// 判断一个slice是否为0 --> 没有元素
	var slice_null []int
	if slice_null == nil {
		fmt.Println("slice_null 没有元素")
	} else {
		fmt.Println("slice_null 不是空的")
	}
	fmt.Println(len(slice_null)) // --> 0

}
