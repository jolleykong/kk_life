// server端的基本功能
package main

import (
	"fmt"
	"io"
	"net"
	"strconv"
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

// 私聊功能:处理私聊请求
func (this *Server) SendToUser(from *User, to *User, msg string) {
	to.C <- "*私聊信息* " + from.Name + "对你说:" + msg
}

// 构建一个方法Handler,处理业务(连接后返回信息.)
func (this *Server) Handler(conn net.Conn) {
	// 当前连接的业务
	//
	user := NewUser(conn, this)

	// 用户上线
	user.Online()

	// 输出一下连接用户
	fmt.Println("用户 " + user.Name + " 连接建立成功.")

	// 定义一个监听用户活跃的channel
	isLive := make(chan bool)

	// 通过一个go routine接收客户端发送的消息
	go func() {
		buf := make([]byte, 4096) // buff 4k,根据需求调整.
		for {
			n, err := conn.Read(buf)
			if n == 0 {
				this.BoardCast(user, "bye bye.")
				user.Offline()
				return
			}
			if err != nil && err != io.EOF {
				fmt.Println("Conn Read err:", err)
				return
			}

			// 提取用户的消息,去除末尾的\n
			msg := string(buf[:n-1])

			// user针对msg进行消息处理
			user.DoMessage(msg)

			// 只要处理过消息,就向活跃状态的chanel isLive 发送一个信号
			isLive <- true
		}
	}()

	// 当前handler阻塞
	for {
		select {
		case <-isLive:
			// 说明存在动作
			// 客户端活跃
			// do nothing. 进入这里后便会重置下面的计时器

		// 定时器time.After() After waits for the duration to elapse and then sends the current time on the returned channel.
		// N秒后触发定时器,向channel返回当前时间,即 case会为true
		case <-time.After(time.Second * 100):
			// 进入case后,说明超时了.
			// 将当前User强制关闭.

			// 发送消息
			user.SendMsg("空闲超时,与指挥部断开了连接.")
			// 等待2秒,避免发送消息后client无法收到.
			time.Sleep(time.Second * 2)

			// 销毁user连接所使用的channel资源
			close(user.C)
			// 主动清理OnlineMap, 避免断开后ListenMessager()继续向这个channel发送消息引起panic
			delete(this.OnlineMap, user.Name)
			// 关闭连接
			conn.Close()
			// 结束当前handler,也可以用runtime.Goexit()
			return
		}
	}

}

//
func getKeys(m map[string]*User) string {
	var keys string = ""
	for k := range m {
		if len(keys) == 0 {
			keys = k
		} else {
			keys = k + "," + keys
		}
	}
	return keys
}

// 循环输出当前在线列表
func (this *Server) ListOnline() string {

	// 需要搞. var xxx string & xxx = VALUE  定义类型&赋值 | xxx := VALUE 声明并定义类型并赋值. if 里也是局部作用域.
	var msg string
	// 循环迭代OnlineMap内容[测试]
	//	this.mapLock.Lock()
	if len(this.OnlineMap) == 0 {
		msg = "[" + time.Now().Format("15:04:05") + "]" + "当前在线人数" + strconv.Itoa(len(this.OnlineMap)) + "人.\n"
	} else {
		key := getKeys(this.OnlineMap)
		//fmt.Println("当前在线用户:", key)
		// 这块string(key) 需要琢磨一下.
		msg = "[" + time.Now().Format("15:04:05") + "]" + "当前在线人数" + strconv.Itoa(len(this.OnlineMap)) + "人.\n" + "当前在线用户:" + string(key) + "\n"
	}
	//	this.mapLock.Unlock()
	return msg
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
	go func() {
		for {
			fmt.Println(this.ListOnline())
			// 间隔刷新.
			time.Sleep(60 * time.Second)
		}
	}()

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
