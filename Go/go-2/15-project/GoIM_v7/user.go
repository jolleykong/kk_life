// user
package main

import (
	"net"
	"strings"
)

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

// 处理消息
func (this *User) DoMessage(msg string) {
	// 响应查询请求
	// 防止空消息导致下面对msg进行切片操作引发异常.
	if len(msg) > 0 {
		// 这里定义"+"开头的消息为指令消息, 进行指令响应
		if msg[:1] == "+" {

			if msg[1:5] == "list" {
				// 查询在线清单
				this.SendMsg(this.server.ListOnline())

			} else if msg[1:7] == "change" {
				// 改名
				// 处理字符,change name ,取新名字.
				newNameTmp := strings.Split(msg, " ")
				newName := newNameTmp[len(newNameTmp)-1]

				// 检查新名字在OnlineMap中是否存在

				_, exist := this.server.OnlineMap[newName]

				if exist {
					this.SendMsg("指定的新用户名 " + newName + "已经有人使用了.\n")
				} else {
					// 将新名字更新到OnlineMap
					this.server.mapLock.Lock()
					delete(this.server.OnlineMap, this.Name)
					this.server.OnlineMap[newName] = this
					this.server.mapLock.Unlock()

					// 更新client 用户的Name
					this.Name = newName
					this.SendMsg("已经成功修改名字为 " + newName + ".\n")

				}

			}

		} else { // 非指令消息,即认为是聊天内容,目前版本按照广播去处理.
			this.server.BoardCast(this, msg)
		}
	}
}

// send message to current client.
func (this *User) SendMsg(msg string) {
	this.conn.Write([]byte(msg))
	//write, err := this.conn.Write([]byte(msg))
	//if err != nil {
	//	return
	//}
}
