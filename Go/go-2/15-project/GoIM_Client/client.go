package main

import (
	"flag"
	"fmt"
	"io"
	"net"
	"os"
	"time"
)

type Client struct {
	Server string
	Port   int
	Name   string
	Conn   net.Conn
	choose string
}

func (this *Client) menu() bool {
	var choose string
	for {
		fmt.Println("==========你怎么才来?==========")
		fmt.Println("/\"+Menu\"返回菜单/")
		fmt.Println("1.世界广播")
		fmt.Println("2.窃窃私语")
		fmt.Println("3.查看在线")
		fmt.Println("4.改名")
		fmt.Println("0.再见")
		time.Sleep(1 * time.Second)

		fmt.Printf("输入传送密码:")
		fmt.Scanln(&choose)

		if choose >= "0" && choose <= "4" {
			this.choose = choose
			return true
		}
	}
}

func (this *Client) World() {
	var msg string
	for {
		fmt.Printf("对 *世界* 说:")
		if msg == "+Menu" {
			return
		} else {
			fmt.Scanln(&msg)
			_, err := this.Conn.Write([]byte(msg + "\n"))
			if err == nil {
				// 完成发送后，清除消息变量缓存
				msg = ""
			}
		}
	}
}

func (this *Client) Whisper() {
	var target string
	var msg string
	// 输出在线名单
	this.List()
	time.Sleep(1 * time.Second)
	for {
		fmt.Printf("消息发送给:")
		fmt.Scanln(&target)
		fmt.Printf("对 %s 说:", target)
		fmt.Scanln(&msg)
		this.Conn.Write([]byte("+to " + target + " " + msg + "\n"))
	}

}

func (this *Client) List() {
	this.Conn.Write([]byte("+list\n"))

}

func (this *Client) ChangeName() {
	var newName string
	fmt.Printf("输入新名字:")
	fmt.Scanln(&newName)

	this.Conn.Write([]byte("+change " + newName + "\n"))

}

func (this *Client) Quit() {
	return

}

func (this *Client) Run() {
	for this.choose != "0" {
		for this.menu() != true {
			// do what
		}
		switch this.choose {
		case "1":
			// 世界广播 World()
			this.World()
			break
		case "2":
			// 窃窃私语 Whisper()
			this.Whisper()
			break
		case "3":
			// 查看在线 List()
			this.List()
			break
		case "4":
			// 改名 ChangeName()
			this.ChangeName()
			break
		case "0":
			// 退出 Quit()
			this.Quit()
			break
		default:
			// do nothine
			fmt.Println("what")
			break
		}
	}
}

func (this *Client) RecResponse() {
	io.Copy(os.Stdout, this.Conn)
}
func NewClient(server string, port int) *Client {
	// 实例化对象
	client := &Client{
		Server: server,
		Port:   port,
		choose: "1024",
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

var server string
var port int

func init() {
	flag.StringVar(&server, "server", "127.0.0.1", "服务器地址.")
	flag.IntVar(&port, "port", 9998, "服务器端口.")
}

func main() {
	flag.Parse()
	// 创建连接
	client := NewClient(server, port)
	if client == nil {
		fmt.Printf("%s:%d 连接失败.\n", server, port)
		return
	}
	fmt.Printf("%s:%d 连接成功.\n", server, port)

	// 启动接收
	go client.RecResponse()
	// 启动客户端业务
	client.Run()

	// 发送消息,需要接收输入.
	//client.Conn.Write([]byte("hello!" + "\n"))
}
