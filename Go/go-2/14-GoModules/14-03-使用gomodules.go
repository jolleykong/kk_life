/*
	使用Go Modules初始化一个项目
	1. 开启GoModules
	// go env -w GO111MODULE=on
	2. 初始化项目
		- 任意文件夹下创建项目目录(不要求在GOPATH/src下)
		// mkdir gotest && cd gotest

		- 执行Go modules初始化
		// go mod init [当前模块名称,后面引用也会用到该名称]
		// go mod init gotest
		// go mod init github.com/jolleykong/gotest

			//$ mkdir gotest
			//$ cd gotest
			//$ go mod init gotest
			//	go: creating new go.mod: module gotest
			//$ ls
			//	go.mod
			//$ cat go.mod
			//	module gotest
			//	go 1.18

	3. 编写项目程序
		- main.go
		// balabala.........
		// 这里可以import一个外部的包来方便下面的观察,待补充.
		- 当程序引用了其他的包,那么这些包的校验信息会记录到go.sum文件中
			- 手动down包: go get [模块名]
			- 自动down包
		- 这些包实际的下载位置存放在了GOPATH/pkg/mod/下,可能包含包的很多版本号
		- go.mod文件会新增一些信息,require xxxx // indirect , 含义为当前模块依赖xxx,依赖版本yyy,
			- indirect 表示间接依赖:项目直接依赖a包,a依赖xxx包,所以项目间接依赖xxx包.
		- go.sum文件中罗列了当前项目直接或间接依赖的所有模块及版本,保证今后项目依赖的版本不会被篡改.
			- h1:hash 表示整体项目的zip文件释放后全部文件的hash checksum,如果不存在可能表示依赖的库可能用不上.
			- go.mod ha1:hash go.mod文件做的hash,大多数都会存在.
*/
package main
