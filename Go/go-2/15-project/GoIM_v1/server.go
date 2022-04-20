// server端的基本功能
package main

import (
	"fmt"
	"net"
)

// 构建一个Server结构,一个Server有两种属性:Ip和Port.
type Server struct {
	Ip   string
	Port int
}

// 构建一个方法Handler,处理业务(连接后返回信息.)
func (this *Server) Handler(conn net.Conn) {
	// 当前连接的业务
	fmt.Println("连接建立成功.")
}

// 启动服务器的接口
func (this *Server) Start() {
	// socket 监听,拼接Ip和Port,创建一个tcp监听
	//net.Listen("tcp", "127.0.0.1:8888")
	listener, err := net.Listen("tcp", fmt.Sprintf("%s:%d", this.Ip, this.Port))

	if err != nil {
		fmt.Println("net.Listen err:", err)
		return
	}

	// 在方法结束之前关闭监听.防止遗忘.这里defer非常好用.
	// close listen socket
	defer listener.Close()

	// 接受连接请求并执行连接.
	// 这个需要循环,不停的监听\接受\连接
	// net.Listener有个方法Accept()(Conn,error) , 返回一个connection给listener.即:跟client的连接套接字.

	for {
		// accept 套接字编程相关.
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Listener accept err:", err)
			continue
		}
		// 也就是建立连接成功后,goroutine 执行 handler.这样不会阻塞本for循环,Accept()依然可以继续响应别的连接请求.
		// do handler
		go this.Handler(conn)
	}

}

// 创建一个server的接口,传入IPI和端口,返回一个Server对象.
func NewServer(ip string, port int) *Server { //*Server 返回指向Server类型的指针.
	server := &Server{ // &Server 是Server对象的内存地址指针.
		Ip:   ip,
		Port: port,
	}
	return server
}
