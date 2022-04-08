/*
	function - 2
	init函数与import导包 - init函数
	main --> import --> const .. --> var .. --> init() --> main()

*/
package main

/*
GOPATH/05-init
	- lib1
		- lib1.go
	- lib2
		- lib2.go
	05-init_func.go
*/

import (
	"05-init/lib1" // GOPATH
	"05-init/lib2"
)

func main() {
	lib1.Lib1Test()
	lib2.Lib2Test()
}

/*
lib1.init()
lib2.init()
lib1.Lib1Test()
lib2.Lib2Test()
*/
