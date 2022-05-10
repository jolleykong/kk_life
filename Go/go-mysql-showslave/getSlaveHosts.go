package main

import (
	"database/sql"
	"fmt"
	"strconv"
)

// 获取slave hosts 结果
func getSlaveHosts(ipt *DBconn) ([]string, error) {
	var db *sql.DB = ipt.Conn
	var shlist []string

	sql := "show slave hosts"
	rows, err := db.Query(sql)
	if err != nil {
		fmt.Println("getSlaveHosts err", err)
	}
	// 迭代结果
	sh := slaveHosts{}
	// 如果能迭代,循环迭代.否则就是非master
	for rows.Next() {
		rows.Scan(&sh.Server_id, &sh.Host, &sh.Port, &sh.Master_id, &sh.Slave_UUID)
		shlist = append(shlist, sh.Host+":"+strconv.Itoa(sh.Port))
	}

	// 输出结果
	// fmt.Println(shlist)

	// 根据是否存在结果,决定结构体属性
	if shlist == nil {
		// fmt.Println("Not a Matser")
	} else {
		// fmt.Println("IS a Matser")
		ipt.HasSlaveHosts = true
	}
	// ipt.HasSlaveHosts = true
	return shlist, err

}
