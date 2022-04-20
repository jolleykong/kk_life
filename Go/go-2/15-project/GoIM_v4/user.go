// user
package main

import "net"

type User struct {
	Name string
	Addr string
	C    chan string //channel
	conn net.Conn
	// 引入Server对象
	server *Server
}

// 创建一个用户的API
func NewUser(conn net.Conn, server *Server) *User {
	// 取client地址
	userAddr := conn.RemoteAddr().String()
	user := &User{
		// 将client地址作为username
		Name:   userAddr,
		Addr:   userAddr,
		C:      make(chan string), // 创建user的channel
		conn:   conn,
		server: server,
	}

	// 启动监听当前user channel的go routine
	go user.ListenMessage()

	return user
}

// 监听当前User channel的 方法, 一旦有消息就直接发送给对应客户端
func (this *User) ListenMessage() {
	for {
		msg := <-this.C
		this.conn.Write([]byte(msg + "\n"))
	}
}

// 上线
func (this *User) Online() {
	// 用户上线,将用户加入到OnlineMap中
	this.server.mapLock.Lock()
	this.server.OnlineMap[this.Name] = this
	this.server.mapLock.Unlock()

	// 用户上线消息广播
	this.server.BoardCast(this, "上线了.")
}

// 下线
func (this *User) Offline() {
	// 用户下线,将用户从OnlineMap中移除
	this.server.mapLock.Lock()
	delete(this.server.OnlineMap, this.Name)
	this.server.mapLock.Unlock()

	// 用户下线消息广播
	this.server.BoardCast(this, "下线了.")
}

// 处理消息 目前只实现了广播
func (this *User) DoMessage(msg string) {
	this.server.BoardCast(this, msg)

}
