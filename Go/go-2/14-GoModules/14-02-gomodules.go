/*
	GoModules模式基础说明
	// 为了与gopath区分开,不要将项目创建在gopath/src下

	- go mod 命令
		go mod init			生成go.mod文件
		go mod download		下载go.mod文件中指明的所有依赖
		go mod tidy			整理现有的依赖
		go mod graph		查看现有的依赖结构
		go mod edit			编辑go.mod文件
		go mod vendor		导出项目所有的依赖到vendor目录
		go mod verify		校验一个模块是否被篡改过
		go mod why			查看为什么需要依赖该模块

	- go mod 环境变量
		// 命令设置环境变量:  go env -w KEY=value
		$ go env
			GO111MODULE="on"						// 作为go modules模式的开关,auto:项目包含go.mod则启用,默认值. on 启用. off 禁用.
			GOARCH="arm64"
			GOENV="xxx"
			GONOPROXY=""			// 这三个用在当前项目依赖了私有模块时,要进行设置,否则会拉取失败.即:sumdb和proxy都无法访问到这些模块的场景,设置后符合规则的都不会通过proxy和sumdn去处理.
			GONOSUMDB=""			// 这三个用在当前项目依赖了私有模块时,要进行设置,否则会拉取失败.
			GOPRIVATE=""			// 这三个用在当前项目依赖了私有模块时,要进行设置,否则会拉取失败.goprivate可以被作为其他两个的默认值,go env -w GOPRIVATE="github.com/kk/yy" ,设置后前缀符合的模块都被认为成私有.支持通配符.
			GOPROXY="https://goproxy.io,direct"		// go modules proxy, 支持以逗号分隔设置多个,加上direct表示当proxy找不到资源时,会转为重定向到真实源的地址去查找,再找不到才抛出错误.
			GOROOT="/usr/local/go"
			GOSUMDB="sum.golang.org"				// 保证无论从源站还是proxy拉取到的模块版本数据未经过篡改,如果发现不一致则会中止.sumdb会使用goproxy的配置.可以设置为off禁止校验.

*/
package main
