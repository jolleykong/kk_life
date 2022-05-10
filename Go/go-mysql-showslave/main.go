package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
)

// 初始化数据库连接
// 连接数据库,获取slave hosts
// 如果没获取到,尝试获取 slave slave,再找到master.
// 获取到slave hosts后,开启hosts数量的go去连接slave.
// 一阶段: 在所有slave延迟为0的情况下, 随机一个延迟为0的升为新的master

// 初始化db连接
func (this *DBconn) InitDB() error {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", this.User, this.Pwd, this.Ip, this.Port, this.Schema)
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return err
	}
	this.Conn = db
	return err
}

// 连接任意数据库,如果为master则查询到所有slave并输出信息.
func getSlave(ipt DBconn) {
	slavestatus, _ := getSlaveStatus(&ipt)
	slavehosts, _ := getSlaveHosts(&ipt)
	// slavestatus输出错误则可能是主 , show slave hosts不为空则至少承担了主角色.
	if ipt.HasSlaveHosts == true && ipt.HasSlaveStatus == false {
		fmt.Printf("%s:%s maybe the master.\n", ipt.Ip, ipt.Port)
		// 输出slave信息.
		if len(slavestatus) != 0 {
			fmt.Println("slavestatus:", slavestatus)
		}
		// 输出slave host
		if len(slavehosts) != 0 {
			fmt.Println("slaves:", slavehosts)
		}
	} else {
		// 则为从
		fmt.Printf("%s:%s is NOT the master, maybe a slave.\n", ipt.Ip, ipt.Port)
		fmt.Println(ipt.HasSlaveHosts, ipt.HasSlaveStatus)
	}
}

func main() {
	sampleDB := DBconn{
		User:   "test",
		Pwd:    "test",
		Ip:     "127.0.0.1",
		Port:   "3306",
		Schema: "test",
	}
	// 定义一个db对象
	err := sampleDB.InitDB()
	if err != nil {
		fmt.Println(err)
	}
	defer sampleDB.Conn.Close()

	// 尝试获取slave信息
	getSlave(sampleDB)
}
