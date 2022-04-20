// user
package main

import "net"

type User struct {
	Name string
	Addr string
	C    chan string //channel
	conn net.Conn
}

// 创建一个用户的API
func NewUser(conn net.Conn) *User {
	// 取client地址
	userAddr := conn.RemoteAddr().String()
	user := &User{
		// 将client地址作为username
		Name: userAddr,
		Addr: userAddr,
		C:    make(chan string), // 创建user的channel
		conn: conn,
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
