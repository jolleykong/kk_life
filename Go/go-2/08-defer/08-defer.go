/*
	defer
	函数执行后、结束前触发
*/

package main

import "fmt"

func main() {
	defer fmt.Println("main::defer1")
	fmt.Println("main::1")
	fmt.Println("main::2")
	defer fmt.Println("main::defer2")
	fmt.Println("main::3")
	defer fmt.Println("main::defer3")
}

/* defer 在函数结束前执行， 多个defer会按照后进先出原则执行。
main::1
main::2
main::3
main::defer3
main::defer2
main::defer1

*/
