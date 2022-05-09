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

type slaveStatus struct {
	IsSlave                       bool // 仅供判断使用.
	Slave_IO_State                string
	Master_Host                   string
	Master_User                   string
	Master_Port                   int
	Connect_Retry                 int
	Master_Log_File               string
	Read_Master_Log_Pos           int
	Relay_Log_File                string
	Relay_Log_Pos                 int
	Relay_Master_Log_File         string
	Slave_IO_Running              string
	Slave_SQL_Running             string
	Replicate_Do_DB               string
	Replicate_Ignore_DB           string
	Replicate_Do_Table            string
	Replicate_Ignore_Table        string
	Replicate_Wild_Do_Table       string
	Replicate_Wild_Ignore_Table   string
	Last_Errno                    string
	Last_Error                    string
	Skip_Counter                  string
	Exec_Master_Log_Pos           string
	Relay_Log_Space               string
	Until_Condition               string
	Until_Log_File                string
	Until_Log_Pos                 string
	Master_SSL_Allowed            string
	Master_SSL_CA_File            string
	Master_SSL_CA_Path            string
	Master_SSL_Cert               string
	Master_SSL_Cipher             string
	Master_SSL_Key                string
	Seconds_Behind_Master         string
	Master_SSL_Verify_Server_Cert string
	Last_IO_Errno                 string
	Last_IO_Error                 string
	Last_SQL_Errno                string
	Last_SQL_Error                string
	Replicate_Ignore_Server_Ids   string
	Master_Server_Id              string
	Master_UUID                   string
	Master_Info_File              string
	SQL_Delay                     string
	SQL_Remaining_Delay           sql.NullInt16
	Slave_SQL_Running_State       string
	Master_Retry_Count            string
	Master_Bind                   string
	Last_IO_Error_Timestamp       string
	Last_SQL_Error_Timestamp      string
	Master_SSL_Crl                string
	Master_SSL_Crlpath            string
	Retrieved_Gtid_Set            string
	Executed_Gtid_Set             string
	Auto_Position                 string
	Replicate_Rewrite_DB          string
	Channel_Name                  string
	Master_TLS_Version            string
	Master_public_key_path        string
	Get_master_public_key         string
	Network_Namespace             string
}

type slaveHosts struct {
	IsSlave    bool
	Server_id  string
	Host       string
	Port       int
	Master_id  string
	Slave_UUID string
}

type t1 struct {
	id int
	dt string
}

type dbconn struct {
	User   string
	Pwd    string
	Ip     string
	Port   string
	Schema string
	Conn   *sql.DB
}

// 初始化db连接
func (this *dbconn) InitDB() error {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", this.User, this.Pwd, this.Ip, this.Port, this.Schema)
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return err
	}
	this.Conn = db
	return err
}

// 获取slave status结果
func getSlaveStatus(db *sql.DB) (slaveStatus, error) {
	sql := "show slave status"
	var ss slaveStatus
	err := db.QueryRow(sql).Scan(&ss.Slave_IO_State,
		&ss.Master_Host,
		&ss.Master_User,
		&ss.Master_Port,
		&ss.Connect_Retry,
		&ss.Master_Log_File,
		&ss.Read_Master_Log_Pos,
		&ss.Relay_Log_File,
		&ss.Relay_Log_Pos,
		&ss.Relay_Master_Log_File,
		&ss.Slave_IO_Running,
		&ss.Slave_SQL_Running,
		&ss.Replicate_Do_DB,
		&ss.Replicate_Ignore_DB,
		&ss.Replicate_Do_Table,
		&ss.Replicate_Ignore_Table,
		&ss.Replicate_Wild_Do_Table,
		&ss.Replicate_Wild_Ignore_Table,
		&ss.Last_Errno,
		&ss.Last_Error,
		&ss.Skip_Counter,
		&ss.Exec_Master_Log_Pos,
		&ss.Relay_Log_Space,
		&ss.Until_Condition,
		&ss.Until_Log_File,
		&ss.Until_Log_Pos,
		&ss.Master_SSL_Allowed,
		&ss.Master_SSL_CA_File,
		&ss.Master_SSL_CA_Path,
		&ss.Master_SSL_Cert,
		&ss.Master_SSL_Cipher,
		&ss.Master_SSL_Key,
		&ss.Seconds_Behind_Master,
		&ss.Master_SSL_Verify_Server_Cert,
		&ss.Last_IO_Errno,
		&ss.Last_IO_Error,
		&ss.Last_SQL_Errno,
		&ss.Last_SQL_Error,
		&ss.Replicate_Ignore_Server_Ids,
		&ss.Master_Server_Id,
		&ss.Master_UUID,
		&ss.Master_Info_File,
		&ss.SQL_Delay,
		&ss.SQL_Remaining_Delay,
		&ss.Slave_SQL_Running_State,
		&ss.Master_Retry_Count,
		&ss.Master_Bind,
		&ss.Last_IO_Error_Timestamp,
		&ss.Last_SQL_Error_Timestamp,
		&ss.Master_SSL_Crl,
		&ss.Master_SSL_Crlpath,
		&ss.Retrieved_Gtid_Set,
		&ss.Executed_Gtid_Set,
		&ss.Auto_Position,
		&ss.Replicate_Rewrite_DB,
		&ss.Channel_Name,
		&ss.Master_TLS_Version,
		&ss.Master_public_key_path,
		&ss.Get_master_public_key,
		&ss.Network_Namespace)

	// fmt.Printf("%v,%T", ss, ss)
	if err != nil { // 有错误信息姑且认为不是slave
		// fmt.Println(err)
		ss.IsSlave = false
	} else {
		ss.IsSlave = true
	}
	return ss, err
}

// 获取slave hosts 结果
func getSlaveHosts(db *sql.DB) (slaveHosts, error) {
	sql := "show slave hosts"
	var sh slaveHosts
	err := db.QueryRow(sql).Scan(&sh.Server_id, &sh.Host, &sh.Port, &sh.Master_id, &sh.Slave_UUID)
	if err != nil { // 有错误信息姑且认为是slave,但不严谨,级联复制时该逻辑存在问题.
		// fmt.Println(err)
		sh.IsSlave = true
	}
	return sh, err

}

// 连接任意数据库,如果为master则查询到所有slave并输出信息.
func getSlave(ipt dbconn) {
	var db *sql.DB = ipt.Conn
	slavestatus, _ := getSlaveStatus(db)
	slavehosts, _ := getSlaveHosts(db)
	// slavestatus输出错误则可能是主 , show slave hosts不为空则至少承担了主角色.
	if slavestatus.IsSlave == false && slavehosts.IsSlave == false {
		fmt.Printf("%s:%s maybe the master.\n", ipt.Ip, ipt.Port)
	} else {
		// 则为从
		fmt.Printf("%s:%s is NOT the master, maybe a slave.\n", ipt.Ip, ipt.Port)
	}
}

func main() {
	sampleDB := dbconn{
		User:   "test",
		Pwd:    "test",
		Ip:     "127.0.0.1",
		Port:   "3307",
		Schema: "test",
	}
	// 定义一个db对象
	err := sampleDB.InitDB()
	if err != nil {
		fmt.Println(err)
	}

	defer sampleDB.Conn.Close()

	// testsql := "select id,dt from t1"
	// var testresult t1
	// err := db.QueryRow(testsql).Scan(&testresult.id, &testresult.dt)
	// if err != nil {
	// 	fmt.Println("err", err)
	// 	return
	// }
	// fmt.Println(testresult)

	// slavestatus := getSlaveStatus(db)
	// fmt.Printf("%v", slavestatus)
	// fmt.Printf("%q", slavestatus.Executed_Gtid_Set)

	// 尝试获取slave信息
	getSlave(sampleDB)
}
