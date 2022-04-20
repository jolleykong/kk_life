// server端的基本功能
package main

import (
	"fmt"
	"io"
	"net"
	"sync"
	"time"
)

// 构建一个Server结构,一个Server有两种属性:Ip和Port.
type Server struct {
	Ip   string
	Port int

	// OnlineMap
	OnlineMap map[string]*User
	mapLock   sync.RWMutex //

	// Message channel
	Message chan string
}

// 广播用户登录消息
func (this *Server) BoardCast(user *User, msg string) {
	sendMsg := "[" + user.Addr + "]" + user.Name + "说:" + msg

	// 将 sendMsg 发送给 Message channel
	this.Message <- sendMsg
}

// 监听Message广播消息channel的go routine,一旦有消息就发送给全部的在线的user
func (this *Server) ListenMessager() {
	for {
		msg := <-this.Message
		// send msg to all user who online.
		this.mapLock.Lock()
		for _, cli := range this.OnlineMap {
			cli.C <- msg

		}
		this.mapLock.Unlock()
	}
}

// 构建一个方法Handler,处理业务(连接后返回信息.)
func (this *Server) Handler(conn net.Conn) {
	// 当前连接的业务
	fmt.Println("连接建立成功.")
	//
	user := NewUser(conn)

	// 用户上线,将用户加入到OnlineMap中
	this.mapLock.Lock()
	this.OnlineMap[user.Name] = user
	this.mapLock.Unlock()

	// 用户上线消息广播
	this.BoardCast(user, "上线了.")

	// 通过一个go routine接收客户端发送的消息
	go func() {
		buf := make([]byte, 4096) // buff 4k,根据需求调整.
		for {
			n, err := conn.Read(buf)
			if n == 0 {
				this.BoardCast(user, "bye bye.")
				return
			}
			if err != nil && err != io.EOF {
				fmt.Println("Conn Read err:", err)
				return
			}

			// 提取用户的消息,去除末尾的\n
			msg := string(buf[:n-1])

			// 广播用户发送的消息
			this.BoardCast(user, msg)
		}
	}()

	// 当前handler阻塞
	select {}

}

//
func getKeys(m map[string]*User) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// 循环输出当前在线列表
func (this *Server) ListOnline() {
	// 循环迭代OnlineMap内容[测试]
	for {
		fmt.Printf("[%s]当前在线人数%d人.\n", time.Now().Format("15:04:05"), len(this.OnlineMap)) // 这块可以加上时间戳,更高级一些.
		if len(this.OnlineMap) >= 1 {
			key := getKeys(this.OnlineMap)
			fmt.Println("当前在线用户:", key)
		}
		time.Sleep(60 * time.Second)

	}
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

	// 启动Message的goroutine
	go this.ListenMessager()

	// 启动一个go routine,用来循环刷新在线人数和列表.
	go this.ListOnline()

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

// 创建一个server的接口,传入IP和端口,返回一个Server对象.
func NewServer(ip string, port int) *Server { //*Server 返回指向Server类型的指针.
	server := &Server{ // &Server 是Server对象的内存地址指针.
		Ip:   ip,
		Port: port,
		// v2
		OnlineMap: make(map[string]*User),
		Message:   make(chan string),
	}
	return server
}
