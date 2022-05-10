package main

import "database/sql"

type slaveStatus struct {
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

type DBconn struct {
	User           string
	Pwd            string
	Ip             string
	Port           string
	Schema         string
	Conn           *sql.DB
	HasSlaveHosts  bool
	HasSlaveStatus bool
}
