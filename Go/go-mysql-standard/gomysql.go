package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
)

// 定义用来接收结果的结构体.
type rs struct {
	id int
	nn string
}

func main() {
	var kk rs
	var user string = "test"
	var pwd string = "test"
	var ip string = "127.0.0.1"
	var port string = "3306"
	var db string = "test"

	DB := ConnDB(user, pwd, ip, port, db)
	defer DB.Close()

	// simple query.
	sql1 := "select id,nn from t1 where id = ? "
	result := DB.QueryRow(sql1, 2).Scan(&kk.id, &kk.nn)
	fmt.Println(result)
	fmt.Println(kk)

	// prepare & query
	sql2 := "select id,nn from t1 where id > ? "
	stmt, errp := DB.Prepare(sql2)
	if errp != nil {
	}
	rows, errQ := stmt.Query(0)
	if errQ != nil {
	}
	// 迭代结果.
	for rows.Next() {
		row := rs{}
		rows.Scan(&row.id, &row.nn)
		fmt.Println(row)
	}

}

func ConnDB(user, pwd, ip, port, db string) *sql.DB {
	// mysqlUrl := "test:test@tcp(127.0.0.1:3306)/test"
	mysqlUrl := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", user, pwd, ip, port, db)
	DB, err := sql.Open("mysql", mysqlUrl)
	if err != nil {
		panic(err)
	}

	return DB
}
