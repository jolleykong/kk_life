// 主入口
package main

func main() {
	server := NewServer("127.0.0.1", 8888) // 创建一个Server
	server.Start()                         // 启动Server
}
