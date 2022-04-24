package main

import (
	"fmt"
	"net"
)

type Client struct {
	Server string
	Port   int
	Name   string
	Conn   net.Conn
}

func NewClient(server string, port int) *Client {
	// 实例化对象
	client := &Client{
		Server: server,
		Port:   port,
	}
	// 创建连接
	conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", server, port))
	if err != nil {
		return nil
	}
	// 连接赋值给对象
	client.Conn = conn

	// 返回对象
	return client
}
func main() {
	// 创建连接
	client := NewClient("127.0.0.1", 8888)
	if client == nil {
		fmt.Println("连接失败.")
		return
	}
	fmt.Println("连接成功.")

	// 启动客户端业务
	select {}

	// 发送消息
	//client.Conn.Write([]byte("hello!" + "\n"))
}
