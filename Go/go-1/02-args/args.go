/*
	os.Args() , slice
*/
package main

import (
	"fmt"
	"os"
)

func main() {
	commands := os.Args[:]
	for idx, arg := range commands {
		fmt.Printf("%d:%v,%T,%T\n", idx, arg, arg, commands)
	}
	// fmt.Println(commands)

}

// $ go run args.go 1 2 3 a b 'abc!@#'
// 1:1,string,[]string
// 2:2,string,[]string
// 3:3,string,[]string
// 4:a,string,[]string
// 5:b,string,[]string
// 6:abc!@#,string,[]string
