package main

import (
	"database/sql"
	"fmt"
	"strconv"
)

// 获取slave status结果
func getSlaveStatus(ipt *DBconn) (map[string]string, error) {
	var db *sql.DB = ipt.Conn
	var ssmap = make(map[string]string)

	sql := "show slave status"

	rows, err := db.Query(sql)
	if err != nil { // 有错误信息姑且认为不是slave
		fmt.Println("getSlaveStatus err", err)
	}
	// 迭代结果
	ss := slaveStatus{}
	for rows.Next() {
		rows.Scan(&ss.Slave_IO_State,
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

		ssmap[ss.Master_Host] = fmt.Sprintf("%v|%v|%v|%q", ss.Slave_IO_Running, ss.Slave_IO_Running, strconv.Itoa(int(ss.SQL_Remaining_Delay.Int16)), ss.Executed_Gtid_Set)
	}
	// 输出结果
	// fmt.Println(ssmap)

	// 根据是否存在结果,决定结构体属性
	if len(ssmap) == 0 {
		// may be master 没有slavestatus结果.
		// fmt.Println("Maybe a Matser")
	} else {
		ipt.HasSlaveStatus = true
		// fmt.Println("IS a Slave")
	}
	//
	return ssmap, err
}
