# RAC 通过rman备份恢复并升级版本

## 启动伪实例

```
[root@cprac21 ~]# su - oracle
Last login: Wed Jul 27 09:59:43 CST 2022
[oracle@cprac21 ~]$ cd /u02/

[oracle@cprac21 u02]$ ls /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1
/u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1

[oracle@cprac21 u02]$ export ORACLE_SID=NMDCFARM1

[oracle@cprac21 u02]$ rman target /

Recovery Manager: Release 12.2.0.1.0 - Production on Wed Jul 27 10:23:06 2022

Copyright (c) 1982, 2017, Oracle and/or its affiliates.  All rights reserved.

connected to target database (not started)

RMAN> startup nomount;

startup failed: ORA-01078: failure in processing system parameters
LRM-00109: could not open parameter file '/u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora'

starting Oracle instance without parameter file for retrieval of spfile
Oracle instance started

Total System Global Area    1073741824 bytes

Fixed Size                     8628936 bytes
Variable Size                436208952 bytes
Database Buffers             620756992 bytes
Redo Buffers                   8146944 bytes
```



## 从备份集恢复参数文件

- 由于目标环境配置低于源环境，需要对参数文件进行一些修改，因此将参数文件恢复到`/home/oracle/`下

```
RMAN> restore spfile to '/home/oracle/spnmdc' from '/u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1';

Starting restore at 27-JUL-22
using target database control file instead of recovery catalog
allocated channel: ORA_DISK_1
channel ORA_DISK_1: SID=1474 device type=DISK

channel ORA_DISK_1: restoring spfile from AUTOBACKUP /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1
channel ORA_DISK_1: SPFILE restore from AUTOBACKUP complete
Finished restore at 27-JUL-22

RMAN> exit

Recovery Manager complete.
```



## 从spfile获取静态参数，并根据实际情况创建pfile

- 使用strings从spfile中获取参数
- 修改SGA、PGA为合适大小
- 修改`*.cluster_database=false`
- 记得手动创建`*.audit_file_dest`对应的路径。
- 此时参数文件中的控制文件名不一定准确，后面会修改。

```
[oracle@cprac21 u02]$ strings /home/oracle/spnmdc >> /home/oracle/pnmdc
[oracle@cprac21 u02]$ vi /home/oracle/pnmdc
[oracle@cprac21 u02]$ cat /home/oracle/pnmdc
NMDCFARM1.__oracle_base='/u01/app/oracle'#ORACLE_BASE set from environment
NMDCFARM2.__oracle_base='/u01/app/oracle'#ORACLE_BASE set from environment
*._report_capture_cycle_time=0
*.audit_file_dest='/u01/app/oracle/diag/adump/NMDCFARM'
*.audit_trail='NONE'
*.cluster_database=false
*.compatible='12.1.0.0.0'
*.control_files='+ASM_REDO1/NMDCFARM/CONTROLFILE/current.345.1111141873','+ASM_REDO2/NMDCFARM/CONTROLFILE/current.345.1111141873'#Restore Controlfile
*.control_management_pack_access='DIAGNOSTIC+TUNING'
*.db_block_size=8192
*.db_create_file_dest='+ASM_DAT1'
*.db_create_online_log_dest_1='+ASM_REDO1'
*.db_create_online_log_dest_2='+ASM_REDO2'
*.db_domain=''
*.db_files=1000
*.db_name='NMDCFARM'
*.db_recovery_file_dest_size=5565m
*.db_recovery_file_dest='+ASM_ARC1/'
*.diagnostic_dest='/u01/app/oracle'
*.dispatchers='(PROTOCOL=TCP) (SERVICE=NMDCFARMXDB)'
NMDCFARM1.instance_number=1
NMDCFARM2.instance_number=2
*.log_archive_dest_1='LOCATION="+ASM_ARC1/"'
*.log_archive_format='%t_%s_%r.dbf'
*.open_cursors=300
*.pga_aggregate_target=20M
*.processes=3000
*.remote_login_passwordfile='exclusive'
*.sec_case_sensitive_logon=FALSE
*.sessions=3305
*.sga_target=10G
NMDCFARM2.thread=2
NMDCFARM1.thread=1
NMDCFARM1.undo_tablespace='UNDOTBS1'
NMDCFARM2.undo_tablespace='UNDOTBS2'
```



## 恢复控制文件

```
RMAN> shutdown abort;

using target database control file instead of recovery catalog
Oracle instance shut down

RMAN>  startup nomount  pfile='/home/oracle/pnmdc';

connected to target database (not started)
Oracle instance started

Total System Global Area   10737418240 bytes

Fixed Size                    12170960 bytes
Variable Size               3154118960 bytes
Database Buffers            7549747200 bytes
Redo Buffers                  21381120 bytes

RMAN> restore controlfile from '/u02/NMDCFARM2/rman_con/NMDCFARM2_con_NMDCFARM_20220726_k013jq5d_1';

Starting restore at 27-JUL-22
allocated channel: ORA_DISK_1
channel ORA_DISK_1: SID=1702 device type=DISK

channel ORA_DISK_1: restoring control file
channel ORA_DISK_1: restore complete, elapsed time: 00:00:02
output file name=+ASM_REDO1/NMDCFARM/CONTROLFILE/current.345.1111141873
output file name=+ASM_REDO2/NMDCFARM/CONTROLFILE/current.345.1111141873
Finished restore at 27-JUL-22

RMAN> shutdown immediate;

Oracle instance shut down

RMAN> exit

Recovery Manager complete.
```



## 根据控制文件实际路径，调整pfile

```
略。
将恢复控制文件中输出的out file name 配置到pfile中。
```



## 注册备份集

- 其实放在一开始也可以。

```
[oracle@cprac21 u02]$ rman target /

Recovery Manager: Release 12.2.0.1.0 - Production on Wed Jul 27 10:33:26 2022

Copyright (c) 1982, 2017, Oracle and/or its affiliates.  All rights reserved.

connected to target database (not started)

RMAN>  startup mount  pfile='/home/oracle/pnmdc';

Oracle instance started
database mounted

Total System Global Area   10737418240 bytes

Fixed Size                    12170960 bytes
Variable Size               3154118960 bytes
Database Buffers            7549747200 bytes
Redo Buffers                  21381120 bytes

RMAN> catalog start with '/u02/NMDCFARM2/';

Starting implicit crosscheck backup at 27-JUL-22
using target database control file instead of recovery catalog
allocated channel: ORA_DISK_1
channel ORA_DISK_1: SID=1327 device type=DISK
Crosschecked 11 objects
Finished implicit crosscheck backup at 27-JUL-22

Starting implicit crosscheck copy at 27-JUL-22
using channel ORA_DISK_1
Crosschecked 2 objects
Finished implicit crosscheck copy at 27-JUL-22

searching for all files in the recovery area
cataloging files...
no files cataloged

searching for all files that match the pattern /u02/NMDCFARM2/

List of Files Unknown to the Database
=====================================
File Name: /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jm13jj2i_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jq13jmu4_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jr13jo1k_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_js13joro_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jo13jkne_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jn13jjt0_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jt13jq21_1
File Name: /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20210112_ujvkfn7k_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jp13jls6_1
File Name: /u02/NMDCFARM2/rman_con/NMDCFARM2_con_NMDCFARM_20220726_k013jq5d_1
File Name: /u02/NMDCFARM2/rman_con/NMDCFARM2_con_NMDCFARM_20210112_uuvkftpl_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0qvkhivk_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0svkhknp_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0mvkhff2_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0ovkhh7b_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20220726_jv13jq3j_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jl13jhns_1

Do you really want to catalog the above files (enter YES or NO)? yes
cataloging files...
cataloging done

List of Cataloged Files
=======================
File Name: /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20220726_k113jq5i_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jm13jj2i_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jq13jmu4_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jr13jo1k_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_js13joro_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jo13jkne_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jn13jjt0_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jt13jq21_1
File Name: /u02/NMDCFARM2/NMDCFARM2_sp_NMDCFARM_20210112_ujvkfn7k_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jp13jls6_1
File Name: /u02/NMDCFARM2/rman_con/NMDCFARM2_con_NMDCFARM_20220726_k013jq5d_1
File Name: /u02/NMDCFARM2/rman_con/NMDCFARM2_con_NMDCFARM_20210112_uuvkftpl_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0qvkhivk_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0svkhknp_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0mvkhff2_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20210113_0ovkhh7b_1
File Name: /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20220726_jv13jq3j_1
File Name: /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jl13jhns_1

```



## 恢复数据库

```
RMAN> RUN {
allocate channel D1 type disk;
allocate channel D2 type disk;
allocate channel D3 type disk;
allocate channel D4 type disk;
allocate channel D5 type disk;
allocate channel D6 type disk;
allocate channel D7 type disk;
allocate channel D8 type disk;
allocate channel D9 type disk;
allocate channel D10 type disk;
allocate channel D11 type disk;
allocate channel D12 type disk;
allocate channel D13 type disk;
allocate channel D14 type disk;
allocate channel D15 type disk;
allocate channel D16 type disk;
allocate channel D17 type disk;
allocate channel D18 type disk;
allocate channel D19 type disk;
allocate channel D20 type disk;
restore database;
recover database;
release channel D1;
release channel D2;
release channel D3;
release channel D4;
release channel D5;
release channel D6;
release channel D7;
release channel D8;
release channel D9;
release channel D10;
release channel D11;
release channel D12;
release channel D13;
release channel D14;
release channel D15;
release channel D16;
release channel D17;
release channel D18;
9> release channel D19;
release channel D20;
}

released channel: ORA_DISK_1
allocated channel: D1
channel D1: SID=1327 device type=DISK

allocated channel: D2
channel D2: SID=2838 device type=DISK

allocated channel: D3
channel D3: SID=3027 device type=DISK

allocated channel: D4
channel D4: SID=3216 device type=DISK

allocated channel: D5
channel D5: SID=3405 device type=DISK

allocated channel: D6
channel D6: SID=3595 device type=DISK

allocated channel: D7
channel D7: SID=3783 device type=DISK

allocated channel: D8
channel D8: SID=3971 device type=DISK

allocated channel: D9
channel D9: SID=4160 device type=DISK

allocated channel: D10
channel D10: SID=4348 device type=DISK

allocated channel: D11
channel D11: SID=3 device type=DISK

allocated channel: D12
channel D12: SID=193 device type=DISK

allocated channel: D13
channel D13: SID=382 device type=DISK

allocated channel: D14
channel D14: SID=571 device type=DISK

allocated channel: D15
channel D15: SID=760 device type=DISK

allocated channel: D16
channel D16: SID=949 device type=DISK

allocated channel: D17
channel D17: SID=1138 device type=DISK

allocated channel: D18
channel D18: SID=1328 device type=DISK

allocated channel: D19
channel D19: SID=2650 device type=DISK

allocated channel: D20
channel D20: SID=1516 device type=DISK

Starting restore at 27-JUL-22

channel D1: starting datafile backup set restore
channel D1: specifying datafile(s) to restore from backup set
channel D1: restoring datafile 00005 to +ASM_DAT1/NMDCFARM/DATAFILE/users.622.1012509959
channel D1: restoring datafile 00025 to +ASM_DAT1/NMDCFARM/DATAFILE/bi_pigpos_data.676.1012510023
channel D1: restoring datafile 00027 to +ASM_DAT1/NMDCFARM/DATAFILE/bi_pigpos_idx.623.1012509961
channel D1: restoring datafile 00029 to +ASM_DAT1/NMDCFARM/DATAFILE/nmglfarm_data.302.1012507901
channel D1: restoring datafile 00037 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_data.666.1012510013
channel D1: restoring datafile 00041 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_idx.670.1012510017
channel D1: restoring datafile 00043 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_data.310.1012507951
channel D1: restoring datafile 00060 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.273.1012507413
channel D1: restoring datafile 00062 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.264.1012507079
channel D1: restoring datafile 00066 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_idx.318.1012507999
channel D1: restoring datafile 00083 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_idx.326.1012508047
channel D1: restoring datafile 00097 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_idx.334.1012508095
channel D1: restoring datafile 00105 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_idx.342.1012508147
channel D1: restoring datafile 00113 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_data.350.1012508203
channel D1: restoring datafile 00121 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_idx.358.1012508247
channel D1: restoring datafile 00129 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_idx.366.1012508305
channel D1: restoring datafile 00137 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_data.374.1012508353
channel D1: restoring datafile 00145 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_idx.382.1012508409
channel D1: restoring datafile 00153 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_data.390.1012508453
channel D1: restoring datafile 00160 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_idx.682.1012510033
channel D1: restoring datafile 00164 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_data.398.1012508509
channel D1: restoring datafile 00175 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_idx.406.1012508557
channel D1: restoring datafile 00184 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_data.631.1012509977
channel D1: restoring datafile 00185 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_data.632.1012509979
channel D1: restoring datafile 00186 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_data.414.1012508609
channel D1: restoring datafile 00194 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_idx.422.1012508667
channel D1: restoring datafile 00202 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_data.430.1012508711
channel D1: restoring datafile 00210 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_idx.438.1012508767
channel D1: restoring datafile 00218 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_idx.446.1012508823
channel D1: restoring datafile 00226 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_idx.454.1012508879
channel D1: restoring datafile 00234 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_data.462.1012508923
channel D1: restoring datafile 00242 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_idx.470.1012508977
channel D1: restoring datafile 00250 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_data.478.1012509033
channel D1: restoring datafile 00258 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_idx.486.1012509081
channel D1: restoring datafile 00266 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_data.494.1012509137
channel D1: restoring datafile 00274 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_data.502.1012509193
channel D1: restoring datafile 00282 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_idx.510.1012509249
channel D1: restoring datafile 00290 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_data.518.1012509307
channel D1: restoring datafile 00298 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_data.526.1012509363
channel D1: restoring datafile 00306 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_idx.534.1012509419
channel D1: restoring datafile 00314 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_data.542.1012509475
channel D1: restoring datafile 00322 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_data.550.1012509531
channel D1: restoring datafile 00330 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_idx.558.1012509579
channel D1: restoring datafile 00338 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_data.566.1012509633
channel D1: restoring datafile 00346 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_data.574.1012509685
channel D1: restoring datafile 00354 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_idx.582.1012509733
channel D1: restoring datafile 00362 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_idx.590.1012509777
channel D1: restoring datafile 00370 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_idx.598.1012509817
channel D1: restoring datafile 00379 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_data.659.1012510007
channel D1: restoring datafile 00381 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_idx.606.1012509869
channel D1: restoring datafile 00407 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_idx.614.1012509921
channel D1: restoring datafile 00411 to +ASM_DAT1/NMDCFARM/DATAFILE/center_data.643.1012509989
channel D1: restoring datafile 00419 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_data.651.1012509999
channel D1: restoring datafile 00433 to +ASM_DAT1/NMDCFARM/DATAFILE/undotbs1.262.1012506659
channel D1: restoring datafile 00450 to +ASM_DAT1/NMDCFARM/DATAFILE/system.1190.1083164129
channel D1: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jm13jj2i_1
channel D2: starting datafile backup set restore
channel D2: specifying datafile(s) to restore from backup set
channel D2: restoring datafile 00006 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_data.293.1012507843
channel D2: restoring datafile 00019 to +ASM_DAT1/NMDCFARM/DATAFILE/std_data.300.1012507887
channel D2: restoring datafile 00035 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_idx.308.1012507937
channel D2: restoring datafile 00049 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_data.316.1012507993
channel D2: restoring datafile 00056 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.266.1012507159
channel D2: restoring datafile 00059 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.267.1012507193
channel D2: restoring datafile 00075 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_data.678.1012510027
channel D2: restoring datafile 00079 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_data.286.1012507769
channel D2: restoring datafile 00081 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_idx.324.1012508033
channel D2: restoring datafile 00095 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_data.332.1012508089
channel D2: restoring datafile 00103 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_data.340.1012508133
channel D2: restoring datafile 00111 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_data.348.1012508189
channel D2: restoring datafile 00119 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_idx.356.1012508233
channel D2: restoring datafile 00127 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_data.364.1012508291
channel D2: restoring datafile 00135 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_data.372.1012508339
channel D2: restoring datafile 00143 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_idx.380.1012508395
channel D2: restoring datafile 00151 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_idx.388.1012508439
channel D2: restoring datafile 00162 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_data.396.1012508495
channel D2: restoring datafile 00173 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_data.404.1012508547
channel D2: restoring datafile 00181 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_idx.412.1012508599
channel D2: restoring datafile 00183 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_data.630.1012509977
channel D2: restoring datafile 00192 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_idx.420.1012508653
channel D2: restoring datafile 00200 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_idx.428.1012508697
channel D2: restoring datafile 00208 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_data.436.1012508753
channel D2: restoring datafile 00216 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_idx.444.1012508809
channel D2: restoring datafile 00224 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_data.452.1012508865
channel D2: restoring datafile 00232 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_data.460.1012508913
channel D2: restoring datafile 00240 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_idx.468.1012508963
channel D2: restoring datafile 00248 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_idx.476.1012509019
channel D2: restoring datafile 00256 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_idx.484.1012509067
channel D2: restoring datafile 00264 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_data.492.1012509123
channel D2: restoring datafile 00272 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_idx.500.1012509179
channel D2: restoring datafile 00280 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_idx.508.1012509235
channel D2: restoring datafile 00288 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_data.516.1012509293
channel D2: restoring datafile 00296 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_idx.524.1012509349
channel D2: restoring datafile 00304 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_idx.532.1012509405
channel D2: restoring datafile 00312 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_data.540.1012509461
channel D2: restoring datafile 00320 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_idx.548.1012509517
channel D2: restoring datafile 00328 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_idx.556.1012509573
channel D2: restoring datafile 00336 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_data.564.1012509617
channel D2: restoring datafile 00344 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_idx.572.1012509675
channel D2: restoring datafile 00352 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_idx.580.1012509719
channel D2: restoring datafile 00360 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_idx.588.1012509763
channel D2: restoring datafile 00368 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_data.596.1012509803
channel D2: restoring datafile 00376 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_data.604.1012509855
channel D2: restoring datafile 00378 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_data.658.1012510005
channel D2: restoring datafile 00395 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_idx.664.1012510011
channel D2: restoring datafile 00398 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_idx.639.1012509985
channel D2: restoring datafile 00405 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_idx.612.1012509907
channel D2: restoring datafile 00418 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_data.650.1012509997
channel D2: restoring datafile 00423 to +ASM_DAT1/NMDCFARM/DATAFILE/nmglfarm_idx.620.1012509953
channel D2: restoring datafile 00425 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgdfarm_idx.1138.1046358557
channel D2: restoring datafile 00438 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzyfarm.1149.1048764811
channel D2: restoring datafile 00441 to +ASM_DAT1/NMDCFARM/DATAFILE/interface_farm_data.1162.1051885275
channel D2: restoring datafile 00447 to +ASM_DAT1/NMDCFARM/DATAFILE/system.1184.1073152399
channel D2: restoring datafile 00451 to +ASM_DAT1/NMDCFARM/DATAFILE/nmywfarm_data.1197.1089365901
channel D2: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jq13jmu4_1
channel D3: starting datafile backup set restore
channel D3: specifying datafile(s) to restore from backup set
channel D3: restoring datafile 00008 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_data.295.1012507857
channel D3: restoring datafile 00017 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.285.1012507745
channel D3: restoring datafile 00022 to +ASM_DAT1/NMDCFARM/DATAFILE/interface_data.617.1012509943
channel D3: restoring datafile 00030 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_data.303.1012507905
channel D3: restoring datafile 00039 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_idx.668.1012510015
channel D3: restoring datafile 00044 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_data.311.1012507957
channel D3: restoring datafile 00052 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.270.1012507309
channel D3: restoring datafile 00061 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.268.1012507229
channel D3: restoring datafile 00067 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_idx.319.1012508001
channel D3: restoring datafile 00084 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_data.327.1012508053
channel D3: restoring datafile 00087 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_data.624.1012509965
channel D3: restoring datafile 00098 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_idx.335.1012508099
channel D3: restoring datafile 00106 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_idx.343.1012508155
channel D3: restoring datafile 00114 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_data.351.1012508211
channel D3: restoring datafile 00122 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_idx.359.1012508255
channel D3: restoring datafile 00130 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_idx.367.1012508311
channel D3: restoring datafile 00138 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_data.375.1012508359
channel D3: restoring datafile 00146 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_idx.383.1012508415
channel D3: restoring datafile 00154 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_data.391.1012508461
channel D3: restoring datafile 00167 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_idx.292.1012507835
channel D3: restoring datafile 00168 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_idx.399.1012508517
channel D3: restoring datafile 00176 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_idx.407.1012508565
channel D3: restoring datafile 00187 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_data.415.1012508617
channel D3: restoring datafile 00195 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_data.423.1012508669
channel D3: restoring datafile 00203 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_data.431.1012508717
channel D3: restoring datafile 00211 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_idx.439.1012508773
channel D3: restoring datafile 00219 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_data.447.1012508831
channel D3: restoring datafile 00227 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_idx.455.1012508887
channel D3: restoring datafile 00235 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_data.463.1012508927
channel D3: restoring datafile 00243 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_data.471.1012508983
channel D3: restoring datafile 00251 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_data.479.1012509039
channel D3: restoring datafile 00259 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_idx.487.1012509087
channel D3: restoring datafile 00267 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_idx.495.1012509145
channel D3: restoring datafile 00275 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_data.503.1012509201
channel D3: restoring datafile 00283 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_idx.511.1012509257
channel D3: restoring datafile 00291 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_idx.519.1012509313
channel D3: restoring datafile 00299 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_data.527.1012509369
channel D3: restoring datafile 00307 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_idx.535.1012509425
channel D3: restoring datafile 00315 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_idx.543.1012509483
channel D3: restoring datafile 00323 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_data.551.1012509539
channel D3: restoring datafile 00331 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_idx.559.1012509583
channel D3: restoring datafile 00339 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_idx.567.1012509639
channel D3: restoring datafile 00347 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_data.575.1012509691
channel D3: restoring datafile 00355 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_idx.583.1012509739
channel D3: restoring datafile 00363 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_data.591.1012509783
channel D3: restoring datafile 00371 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_idx.599.1012509821
channel D3: restoring datafile 00380 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_data.660.1012510007
channel D3: restoring datafile 00382 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_idx.607.1012509877
channel D3: restoring datafile 00387 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_data.633.1012509979
channel D3: restoring datafile 00396 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_idx.674.1012510021
channel D3: restoring datafile 00403 to +ASM_DAT1/NMDCFARM/DATAFILE/farmbo_data.641.1012509987
channel D3: restoring datafile 00409 to +ASM_DAT1/NMDCFARM/DATAFILE/nmglfarm_data.615.1012509929
channel D3: restoring datafile 00412 to +ASM_DAT1/NMDCFARM/DATAFILE/center_data.644.1012509991
channel D3: restoring datafile 00420 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_idx.652.1012509999
channel D3: restoring datafile 00429 to +ASM_DAT1/NMDCFARM/DATAFILE/nmaksfarm_idx.1144.1048764675
channel D3: restoring datafile 00434 to +ASM_DAT1/NMDCFARM/DATAFILE/undotbs2.261.1012506753
channel D3: restoring datafile 00453 to +ASM_DAT1/NMDCFARM/DATAFILE/sysaux.1203.1096449639
channel D3: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jr13jo1k_1
channel D4: starting datafile backup set restore
channel D4: specifying datafile(s) to restore from backup set
channel D4: restoring datafile 00003 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.287.1012507785
channel D4: restoring datafile 00011 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_idx.298.1012507877
channel D4: restoring datafile 00014 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.279.1012507605
channel D4: restoring datafile 00020 to +ASM_DAT1/NMDCFARM/DATAFILE/std_idx.618.1012509945
channel D4: restoring datafile 00026 to +ASM_DAT1/NMDCFARM/DATAFILE/bi_pigpos_data.677.1012510027
channel D4: restoring datafile 00033 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_idx.306.1012507923
channel D4: restoring datafile 00047 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_idx.314.1012507979
channel D4: restoring datafile 00051 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.275.1012507483
channel D4: restoring datafile 00055 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.271.1012507343
channel D4: restoring datafile 00071 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_data.282.1012507669
channel D4: restoring datafile 00073 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_idx.322.1012508019
channel D4: restoring datafile 00089 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_data.626.1012509969
channel D4: restoring datafile 00093 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_data.330.1012508075
channel D4: restoring datafile 00101 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_data.338.1012508119
channel D4: restoring datafile 00109 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_idx.346.1012508175
channel D4: restoring datafile 00117 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_idx.354.1012508223
channel D4: restoring datafile 00125 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_data.362.1012508277
channel D4: restoring datafile 00133 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_idx.370.1012508329
channel D4: restoring datafile 00141 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_idx.378.1012508381
channel D4: restoring datafile 00149 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_data.386.1012508429
channel D4: restoring datafile 00157 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_idx.394.1012508481
channel D4: restoring datafile 00171 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_data.402.1012508537
channel D4: restoring datafile 00179 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_data.410.1012508585
channel D4: restoring datafile 00190 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_idx.418.1012508639
channel D4: restoring datafile 00198 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_idx.426.1012508683
channel D4: restoring datafile 00206 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_idx.434.1012508739
channel D4: restoring datafile 00214 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_data.442.1012508795
channel D4: restoring datafile 00222 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_data.450.1012508851
channel D4: restoring datafile 00230 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_idx.458.1012508903
channel D4: restoring datafile 00238 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_idx.466.1012508949
channel D4: restoring datafile 00246 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_idx.474.1012509005
channel D4: restoring datafile 00254 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_data.482.1012509061
channel D4: restoring datafile 00262 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_data.490.1012509109
channel D4: restoring datafile 00270 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_idx.498.1012509165
channel D4: restoring datafile 00278 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_data.506.1012509221
channel D4: restoring datafile 00286 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_data.514.1012509277
channel D4: restoring datafile 00294 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_idx.522.1012509335
channel D4: restoring datafile 00302 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_data.530.1012509391
channel D4: restoring datafile 00310 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_data.538.1012509447
channel D4: restoring datafile 00318 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_idx.546.1012509503
channel D4: restoring datafile 00326 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_data.554.1012509559
channel D4: restoring datafile 00334 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_data.562.1012509603
channel D4: restoring datafile 00342 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_idx.570.1012509661
channel D4: restoring datafile 00350 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_data.578.1012509705
channel D4: restoring datafile 00358 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_data.586.1012509757
channel D4: restoring datafile 00366 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_data.594.1012509797
channel D4: restoring datafile 00374 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_idx.602.1012509841
channel D4: restoring datafile 00390 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_data.635.1012509981
channel D4: restoring datafile 00394 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_idx.663.1012510011
channel D4: restoring datafile 00400 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_data.610.1012509893
channel D4: restoring datafile 00414 to +ASM_DAT1/NMDCFARM/DATAFILE/center_idx.646.1012509993
channel D4: restoring datafile 00422 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_idx.654.1012510001
channel D4: restoring datafile 00430 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnmgfarm.1145.1048764749
channel D4: restoring datafile 00437 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycnfarm_idx.1148.1048764787
channel D4: restoring datafile 00448 to +ASM_DAT1/NMDCFARM/DATAFILE/system.1186.1077096989
channel D4: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_js13joro_1
channel D5: starting datafile backup set restore
channel D5: specifying datafile(s) to restore from backup set
channel D5: restoring datafile 00012 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.277.1012507555
channel D5: restoring datafile 00015 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.283.1012507695
channel D5: restoring datafile 00018 to +ASM_DAT1/NMDCFARM/DATAFILE/std_data.299.1012507885
channel D5: restoring datafile 00021 to +ASM_DAT1/NMDCFARM/DATAFILE/std_idx.619.1012509949
channel D5: restoring datafile 00024 to +ASM_DAT1/NMDCFARM/DATAFILE/bi_pigpos_data.675.1012510023
channel D5: restoring datafile 00034 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_idx.307.1012507929
channel D5: restoring datafile 00036 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_data.665.1012510013
channel D5: restoring datafile 00040 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_idx.669.1012510017
channel D5: restoring datafile 00048 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_data.315.1012507985
channel D5: restoring datafile 00053 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.265.1012507123
channel D5: restoring datafile 00058 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.272.1012507379
channel D5: restoring datafile 00074 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_idx.323.1012508025
channel D5: restoring datafile 00077 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_data.680.1012510031
channel D5: restoring datafile 00090 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_idx.627.1012509971
channel D5: restoring datafile 00094 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_data.331.1012508081
channel D5: restoring datafile 00102 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_data.339.1012508127
channel D5: restoring datafile 00110 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_idx.347.1012508183
channel D5: restoring datafile 00118 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_idx.355.1012508227
channel D5: restoring datafile 00126 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_data.363.1012508283
channel D5: restoring datafile 00134 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_idx.371.1012508331
channel D5: restoring datafile 00142 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_idx.379.1012508387
channel D5: restoring datafile 00150 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_idx.387.1012508431
channel D5: restoring datafile 00158 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_idx.395.1012508489
channel D5: restoring datafile 00165 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_idx.290.1012507821
channel D5: restoring datafile 00172 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_data.403.1012508545
channel D5: restoring datafile 00180 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_idx.411.1012508593
channel D5: restoring datafile 00191 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_idx.419.1012508645
channel D5: restoring datafile 00199 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_idx.427.1012508689
channel D5: restoring datafile 00207 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_data.435.1012508745
channel D5: restoring datafile 00215 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_data.443.1012508803
channel D5: restoring datafile 00223 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_data.451.1012508859
channel D5: restoring datafile 00231 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_data.459.1012508907
channel D5: restoring datafile 00239 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_idx.467.1012508955
channel D5: restoring datafile 00247 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_idx.475.1012509011
channel D5: restoring datafile 00255 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_idx.483.1012509063
channel D5: restoring datafile 00263 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_data.491.1012509117
channel D5: restoring datafile 00271 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_idx.499.1012509173
channel D5: restoring datafile 00279 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_idx.507.1012509229
channel D5: restoring datafile 00287 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_data.515.1012509285
channel D5: restoring datafile 00295 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_idx.523.1012509341
channel D5: restoring datafile 00303 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_idx.531.1012509397
channel D5: restoring datafile 00311 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_data.539.1012509455
channel D5: restoring datafile 00319 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_idx.547.1012509511
channel D5: restoring datafile 00327 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_idx.555.1012509567
channel D5: restoring datafile 00335 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_data.563.1012509611
channel D5: restoring datafile 00343 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_idx.571.1012509667
channel D5: restoring datafile 00351 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_idx.579.1012509711
channel D5: restoring datafile 00359 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_data.587.1012509759
channel D5: restoring datafile 00367 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_data.595.1012509801
channel D5: restoring datafile 00375 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_data.603.1012509849
channel D5: restoring datafile 00391 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_data.636.1012509983
channel D5: restoring datafile 00401 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_data.611.1012509901
channel D5: restoring datafile 00415 to +ASM_DAT1/NMDCFARM/DATAFILE/center_idx.647.1012509993
channel D5: restoring datafile 00431 to +ASM_DAT1/NMDCFARM/DATAFILE/f2f_farm_data.655.1012510003
channel D5: restoring datafile 00436 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycnfarm.1147.1048764781
channel D5: restoring datafile 00439 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzyfarm_idx.1150.1048764815
channel D5: restoring datafile 00440 to +ASM_DAT1/NMDCFARM/DATAFILE/ogg.1160.1051109619
channel D5: restoring datafile 00443 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbacfarm_idx.1169.1054389963
channel D5: restoring datafile 00446 to +ASM_DAT1/NMDCFARM/DATAFILE/system.1179.1070894025
channel D5: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jo13jkne_1
channel D6: starting datafile backup set restore
channel D6: specifying datafile(s) to restore from backup set
channel D6: restoring datafile 00004 to +ASM_DAT1/NMDCFARM/DATAFILE/undotbs1.1081.1016489169
channel D6: restoring datafile 00010 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_idx.297.1012507871
channel D6: restoring datafile 00013 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.278.1012507579
channel D6: restoring datafile 00016 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_idx.284.1012507719
channel D6: restoring datafile 00032 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_data.305.1012507915
channel D6: restoring datafile 00038 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxzfarm_data.667.1012510015
channel D6: restoring datafile 00046 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_idx.313.1012507971
channel D6: restoring datafile 00057 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.260.1012507033
channel D6: restoring datafile 00063 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.274.1012507449
channel D6: restoring datafile 00072 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_idx.321.1012508011
channel D6: restoring datafile 00080 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_data.289.1012507815
channel D6: restoring datafile 00086 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_data.329.1012508067
channel D6: restoring datafile 00091 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_idx.628.1012509973
channel D6: restoring datafile 00100 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_data.337.1012508113
channel D6: restoring datafile 00108 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_idx.345.1012508169
channel D6: restoring datafile 00116 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_data.353.1012508217
channel D6: restoring datafile 00124 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_data.361.1012508269
channel D6: restoring datafile 00132 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_idx.369.1012508321
channel D6: restoring datafile 00140 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_data.377.1012508373
channel D6: restoring datafile 00148 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_data.385.1012508425
channel D6: restoring datafile 00156 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_idx.393.1012508475
channel D6: restoring datafile 00159 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_idx.681.1012510031
channel D6: restoring datafile 00170 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_idx.401.1012508531
channel D6: restoring datafile 00178 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_data.409.1012508579
channel D6: restoring datafile 00189 to +ASM_DAT1/NMDCFARM/DATAFILE/nmslfarm_idx.417.1012508631
channel D6: restoring datafile 00197 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_data.425.1012508675
channel D6: restoring datafile 00205 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_idx.433.1012508731
channel D6: restoring datafile 00213 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_data.441.1012508789
channel D6: restoring datafile 00221 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_data.449.1012508845
channel D6: restoring datafile 00229 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_idx.457.1012508901
channel D6: restoring datafile 00237 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_idx.465.1012508941
channel D6: restoring datafile 00245 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_data.473.1012508997
channel D6: restoring datafile 00253 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_data.481.1012509053
channel D6: restoring datafile 00261 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_data.489.1012509101
channel D6: restoring datafile 00269 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_idx.497.1012509159
channel D6: restoring datafile 00277 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_data.505.1012509215
channel D6: restoring datafile 00285 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_data.513.1012509271
channel D6: restoring datafile 00293 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_idx.521.1012509327
channel D6: restoring datafile 00301 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_data.529.1012509383
channel D6: restoring datafile 00309 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_data.537.1012509439
channel D6: restoring datafile 00317 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_idx.545.1012509497
channel D6: restoring datafile 00325 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_data.553.1012509553
channel D6: restoring datafile 00333 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_data.561.1012509597
channel D6: restoring datafile 00341 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_idx.569.1012509653
channel D6: restoring datafile 00349 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_data.577.1012509701
channel D6: restoring datafile 00357 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_data.585.1012509749
channel D6: restoring datafile 00365 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_data.593.1012509795
channel D6: restoring datafile 00373 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_idx.601.1012509835
channel D6: restoring datafile 00385 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_idx.672.1012510019
channel D6: restoring datafile 00392 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_data.637.1012509983
channel D6: restoring datafile 00399 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_data.609.1012509887
channel D6: restoring datafile 00402 to +ASM_DAT1/NMDCFARM/DATAFILE/farmbo_data.640.1012509987
channel D6: restoring datafile 00410 to +ASM_DAT1/NMDCFARM/DATAFILE/nmglfarm_idx.616.1012509935
channel D6: restoring datafile 00416 to +ASM_DAT1/NMDCFARM/DATAFILE/center_idx.648.1012509995
channel D6: restoring datafile 00424 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgdfarm.1137.1046358545
channel D6: restoring datafile 00428 to +ASM_DAT1/NMDCFARM/DATAFILE/nmaksfarm.1143.1048764669
channel D6: restoring datafile 00432 to +ASM_DAT1/NMDCFARM/DATAFILE/f2f_farm_idx.656.1012510003
channel D6: restoring datafile 00444 to +ASM_DAT1/NMDCFARM/DATAFILE/tbs_aud.1171.1062942803
channel D6: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jn13jjt0_1
channel D7: starting datafile backup set restore
channel D7: specifying datafile(s) to restore from backup set
channel D7: restoring datafile 00001 to +ASM_DAT1/NMDCFARM/DATAFILE/system.258.1012506923
channel D7: restoring datafile 00007 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_data.294.1012507849
channel D7: restoring datafile 00023 to +ASM_DAT1/NMDCFARM/DATAFILE/interface_idx.657.1012510005
channel D7: restoring datafile 00028 to +ASM_DAT1/NMDCFARM/DATAFILE/nmglfarm_data.301.1012507895
channel D7: restoring datafile 00042 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_data.309.1012507943
channel D7: restoring datafile 00050 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_data.317.1012507995
channel D7: restoring datafile 00065 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.276.1012507519
channel D7: restoring datafile 00076 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_data.679.1012510029
channel D7: restoring datafile 00082 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_idx.325.1012508039
channel D7: restoring datafile 00092 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_idx.629.1012509973
channel D7: restoring datafile 00096 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzmdfarm_idx.333.1012508093
channel D7: restoring datafile 00104 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyyfarm_data.341.1012508141
channel D7: restoring datafile 00112 to +ASM_DAT1/NMDCFARM/DATAFILE/nmyjfarm_data.349.1012508197
channel D7: restoring datafile 00120 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_idx.357.1012508241
channel D7: restoring datafile 00128 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxjfarm_data.365.1012508297
channel D7: restoring datafile 00136 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxffarm_data.373.1012508345
channel D7: restoring datafile 00144 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_idx.381.1012508401
channel D7: restoring datafile 00152 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_idx.389.1012508447
channel D7: restoring datafile 00163 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_data.397.1012508503
channel D7: restoring datafile 00166 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_idx.291.1012507829
channel D7: restoring datafile 00174 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsxfarm_idx.405.1012508551
channel D7: restoring datafile 00182 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_idx.413.1012508603
channel D7: restoring datafile 00193 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_idx.421.1012508659
channel D7: restoring datafile 00201 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_data.429.1012508703
channel D7: restoring datafile 00209 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_data.437.1012508759
channel D7: restoring datafile 00217 to +ASM_DAT1/NMDCFARM/DATAFILE/nmpdsfarm_idx.445.1012508817
channel D7: restoring datafile 00225 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_idx.453.1012508873
channel D7: restoring datafile 00233 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnjfarm_data.461.1012508921
channel D7: restoring datafile 00241 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_idx.469.1012508969
channel D7: restoring datafile 00249 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_data.477.1012509025
channel D7: restoring datafile 00257 to +ASM_DAT1/NMDCFARM/DATAFILE/nmmyfarm_idx.485.1012509073
channel D7: restoring datafile 00265 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlyfarm_data.493.1012509131
channel D7: restoring datafile 00273 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_data.501.1012509187
channel D7: restoring datafile 00281 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkffarm_idx.509.1012509243
channel D7: restoring datafile 00289 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjjfarm_data.517.1012509299
channel D7: restoring datafile 00297 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_data.525.1012509355
channel D7: restoring datafile 00305 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhyfarm_idx.533.1012509411
channel D7: restoring datafile 00313 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhebfarm_data.541.1012509469
channel D7: restoring datafile 00321 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_data.549.1012509525
channel D7: restoring datafile 00329 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhdfarm_idx.557.1012509577
channel D7: restoring datafile 00337 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgafarm_data.565.1012509625
channel D7: restoring datafile 00345 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_data.573.1012509681
channel D7: restoring datafile 00353 to +ASM_DAT1/NMDCFARM/DATAFILE/nmfzfarm_idx.581.1012509725
channel D7: restoring datafile 00361 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcsfarm_idx.589.1012509769
channel D7: restoring datafile 00369 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_idx.597.1012509811
channel D7: restoring datafile 00377 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_data.605.1012509863
channel D7: restoring datafile 00384 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_idx.671.1012510019
channel D7: restoring datafile 00388 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_data.661.1012510009
channel D7: restoring datafile 00397 to +ASM_DAT1/NMDCFARM/DATAFILE/icalendar_idx.638.1012509985
channel D7: restoring datafile 00404 to +ASM_DAT1/NMDCFARM/DATAFILE/farmbo_data.642.1012509989
channel D7: restoring datafile 00406 to +ASM_DAT1/NMDCFARM/DATAFILE/hnhbfarm_idx.613.1012509915
channel D7: restoring datafile 00417 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_data.649.1012509995
channel D7: restoring datafile 00427 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgsjcfarm_idx.1142.1048763885
channel D7: restoring datafile 00442 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbacfarm_data.1168.1054389955
channel D7: restoring datafile 00449 to +ASM_DAT1/NMDCFARM/DATAFILE/system.1188.1080124489
channel D7: restoring datafile 00452 to +ASM_DAT1/NMDCFARM/DATAFILE/nmywfarm_idx.1198.1089365905
channel D7: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jp13jls6_1
channel D8: starting datafile backup set restore
channel D8: specifying datafile(s) to restore from backup set
channel D8: restoring datafile 00002 to +ASM_DAT1/NMDCFARM/DATAFILE/sysaux.259.1012506849
channel D8: restoring datafile 00009 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjfarm_idx.296.1012507863
channel D8: restoring datafile 00031 to +ASM_DAT1/NMDCFARM/DATAFILE/farmxyz_data.304.1012507909
channel D8: restoring datafile 00045 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtjslfarm_idx.312.1012507965
channel D8: restoring datafile 00054 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.257.1012506989
channel D8: restoring datafile 00064 to +ASM_DAT1/NMDCFARM/DATAFILE/pigpos_data.269.1012507273
channel D8: restoring datafile 00068 to +ASM_DAT1/NMDCFARM/DATAFILE/nmkmfarm_idx.320.1012508005
channel D8: restoring datafile 00069 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_data.280.1012507629
channel D8: restoring datafile 00070 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvf_data.281.1012507655
channel D8: restoring datafile 00078 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfin_data.288.1012507799
channel D8: restoring datafile 00085 to +ASM_DAT1/NMDCFARM/DATAFILE/nmntfarm_data.328.1012508061
channel D8: restoring datafile 00088 to +ASM_DAT1/NMDCFARM/DATAFILE/planning_data.625.1012509967
channel D8: restoring datafile 00099 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_data.336.1012508105
channel D8: restoring datafile 00107 to +ASM_DAT1/NMDCFARM/DATAFILE/nmzkfarm_idx.344.1012508161
channel D8: restoring datafile 00115 to +ASM_DAT1/NMDCFARM/DATAFILE/nmycfarm_data.352.1012508213
channel D8: restoring datafile 00123 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_data.360.1012508263
channel D8: restoring datafile 00131 to +ASM_DAT1/NMDCFARM/DATAFILE/nmxmfarm_idx.368.1012508319
channel D8: restoring datafile 00139 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwuhfarm_data.376.1012508367
channel D8: restoring datafile 00147 to +ASM_DAT1/NMDCFARM/DATAFILE/nmwhfarm_data.384.1012508423
channel D8: restoring datafile 00155 to +ASM_DAT1/NMDCFARM/DATAFILE/nmtzfarm_data.392.1012508467
channel D8: restoring datafile 00161 to +ASM_DAT1/NMDCFARM/DATAFILE/ssvfbak_idx.683.1012510033
channel D8: restoring datafile 00169 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsyfarm_idx.400.1012508523
channel D8: restoring datafile 00177 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsqfarm_data.408.1012508571
channel D8: restoring datafile 00188 to +ASM_DAT1/NMDCFARM/DATAFILE/nmsjzfarm_data.416.1012508625
channel D8: restoring datafile 00196 to +ASM_DAT1/NMDCFARM/DATAFILE/nmshxfarm_data.424.1012508673
channel D8: restoring datafile 00204 to +ASM_DAT1/NMDCFARM/DATAFILE/nmscfarm_idx.432.1012508725
channel D8: restoring datafile 00212 to +ASM_DAT1/NMDCFARM/DATAFILE/nmqdfarm_idx.440.1012508781
channel D8: restoring datafile 00220 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnyfarm_data.448.1012508837
channel D8: restoring datafile 00228 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnnfarm_idx.456.1012508893
channel D8: restoring datafile 00236 to +ASM_DAT1/NMDCFARM/DATAFILE/nmncfarm_data.464.1012508933
channel D8: restoring datafile 00244 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnbfarm_data.472.1012508991
channel D8: restoring datafile 00252 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_data.480.1012509047
channel D8: restoring datafile 00260 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlzfarm_idx.488.1012509095
channel D8: restoring datafile 00268 to +ASM_DAT1/NMDCFARM/DATAFILE/nmlygfarm_idx.496.1012509151
channel D8: restoring datafile 00276 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_data.504.1012509207
channel D8: restoring datafile 00284 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjzfarm_idx.512.1012509263
channel D8: restoring datafile 00292 to +ASM_DAT1/NMDCFARM/DATAFILE/nmjlfarm_idx.520.1012509321
channel D8: restoring datafile 00300 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_data.528.1012509377
channel D8: restoring datafile 00308 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhhfarm_idx.536.1012509433
channel D8: restoring datafile 00316 to +ASM_DAT1/NMDCFARM/DATAFILE/nmhffarm_idx.544.1012509489
channel D8: restoring datafile 00324 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_data.552.1012509545
channel D8: restoring datafile 00332 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgzfarm_idx.560.1012509589
channel D8: restoring datafile 00340 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgyfarm_idx.568.1012509647
channel D8: restoring datafile 00348 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_data.576.1012509695
channel D8: restoring datafile 00356 to +ASM_DAT1/NMDCFARM/DATAFILE/nmczfarm_idx.584.1012509747
channel D8: restoring datafile 00364 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcqfarm_data.592.1012509791
channel D8: restoring datafile 00372 to +ASM_DAT1/NMDCFARM/DATAFILE/nmcdfarm_idx.600.1012509827
channel D8: restoring datafile 00383 to +ASM_DAT1/NMDCFARM/DATAFILE/nmbjfarm_idx.608.1012509883
channel D8: restoring datafile 00386 to +ASM_DAT1/NMDCFARM/DATAFILE/mq_farm_idx.673.1012510021
channel D8: restoring datafile 00389 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_data.634.1012509981
channel D8: restoring datafile 00393 to +ASM_DAT1/NMDCFARM/DATAFILE/ischedule_idx.662.1012510009
channel D8: restoring datafile 00408 to +ASM_DAT1/NMDCFARM/DATAFILE/farmbo_idx.621.1012509955
channel D8: restoring datafile 00413 to +ASM_DAT1/NMDCFARM/DATAFILE/center_data.645.1012509991
channel D8: restoring datafile 00421 to +ASM_DAT1/NMDCFARM/DATAFILE/ssdt_idx.653.1012510001
channel D8: restoring datafile 00426 to +ASM_DAT1/NMDCFARM/DATAFILE/nmgsjcfarm.1141.1048763875
channel D8: restoring datafile 00435 to +ASM_DAT1/NMDCFARM/DATAFILE/nmnmgfarm_idx.1146.1048764753
channel D8: restoring datafile 00445 to +ASM_DAT1/NMDCFARM/DATAFILE/fssc.1177.1068549121
channel D8: reading from backup piece /u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jl13jhns_1
channel D3: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jr13jo1k_1 tag=TAG20220726T180546
channel D3: restored backup piece 1
channel D3: restore complete, elapsed time: 00:20:57
channel D6: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jn13jjt0_1 tag=TAG20220726T180546
channel D6: restored backup piece 1
channel D6: restore complete, elapsed time: 00:22:06
channel D1: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jm13jj2i_1 tag=TAG20220726T180546
channel D1: restored backup piece 1
channel D1: restore complete, elapsed time: 00:22:30
channel D2: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jq13jmu4_1 tag=TAG20220726T180546
channel D2: restored backup piece 1
channel D2: restore complete, elapsed time: 00:30:07
channel D7: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jp13jls6_1 tag=TAG20220726T180546
channel D7: restored backup piece 1
channel D7: restore complete, elapsed time: 00:31:26
channel D4: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_js13joro_1 tag=TAG20220726T180546
channel D4: restored backup piece 1
channel D4: restore complete, elapsed time: 00:31:37
channel D5: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jo13jkne_1 tag=TAG20220726T180546
channel D5: restored backup piece 1
channel D5: restore complete, elapsed time: 00:31:36
channel D8: piece handle=/u02/NMDCFARM2/NMDCFARM2_db_full_NMDCFARM_20220726_jl13jhns_1 tag=TAG20220726T180546
channel D8: restored backup piece 1
channel D8: restore complete, elapsed time: 00:35:56
Finished restore at 27-JUL-22

Starting recover at 27-JUL-22

starting media recovery

channel D1: starting archived log restore to default destination
channel D1: restoring archived log
archived log thread=2 sequence=1110348
channel D1: restoring archived log
archived log thread=1 sequence=1540202
channel D1: restoring archived log
archived log thread=1 sequence=1540203
channel D1: restoring archived log
archived log thread=1 sequence=1540204
channel D1: restoring archived log
archived log thread=2 sequence=1110349
channel D1: restoring archived log
archived log thread=1 sequence=1540205
channel D1: restoring archived log
archived log thread=1 sequence=1540206
channel D1: restoring archived log
archived log thread=1 sequence=1540207
channel D1: restoring archived log
archived log thread=2 sequence=1110350
channel D1: restoring archived log
archived log thread=1 sequence=1540208
channel D1: restoring archived log
archived log thread=1 sequence=1540209
channel D1: restoring archived log
archived log thread=1 sequence=1540210
channel D1: restoring archived log
archived log thread=2 sequence=1110351
channel D1: restoring archived log
archived log thread=1 sequence=1540211
channel D1: restoring archived log
archived log thread=1 sequence=1540212
channel D1: restoring archived log
archived log thread=1 sequence=1540213
channel D1: restoring archived log
archived log thread=2 sequence=1110352
channel D1: restoring archived log
archived log thread=2 sequence=1110353
channel D1: restoring archived log
archived log thread=1 sequence=1540214
channel D1: restoring archived log
archived log thread=2 sequence=1110354
channel D1: restoring archived log
archived log thread=1 sequence=1540215
channel D1: reading from backup piece /u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20220726_jv13jq3j_1
channel D1: piece handle=/u02/NMDCFARM2/rman_arch/NMDCFARM2_arch_NMDCFARM_20220726_jv13jq3j_1 tag=TAG20220726T202834
channel D1: restored backup piece 1
channel D1: restore complete, elapsed time: 00:01:15
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110348.332.1111144347 thread=2 sequence=1110348
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540202.324.1111144335 thread=1 sequence=1540202
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540203.325.1111144335 thread=1 sequence=1540203
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540204.262.1111144299 thread=1 sequence=1540204
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110349.330.1111144345 thread=2 sequence=1110349
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540205.327.1111144335 thread=1 sequence=1540205
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540206.326.1111144335 thread=1 sequence=1540206
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540207.284.1111144299 thread=1 sequence=1540207
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110350.331.1111144347 thread=2 sequence=1110350
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540208.289.1111144299 thread=1 sequence=1540208
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540209.259.1111144299 thread=1 sequence=1540209
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540210.323.1111144299 thread=1 sequence=1540210
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110351.329.1111144345 thread=2 sequence=1110351
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540211.285.1111144299 thread=1 sequence=1540211
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540212.334.1111144349 thread=1 sequence=1540212
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540213.333.1111144349 thread=1 sequence=1540213
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110352.338.1111144351 thread=2 sequence=1110352
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110353.337.1111144349 thread=2 sequence=1110353
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540214.328.1111144337 thread=1 sequence=1540214
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_2_seq_1110354.336.1111144349 thread=2 sequence=1110354
archived log file name=+ASM_ARC1/NMDCFARM/ARCHIVELOG/2022_07_27/thread_1_seq_1540215.335.1111144349 thread=1 sequence=1540215
unable to find archived log
archived log thread=1 sequence=1540216
released channel: D1
released channel: D2
released channel: D3
released channel: D4
released channel: D5
released channel: D6
released channel: D7
released channel: D8
released channel: D9
released channel: D10
released channel: D11
released channel: D12
released channel: D13
released channel: D14
released channel: D15
released channel: D16
released channel: D17
released channel: D18
released channel: D19
released channel: D20
RMAN-00571: ===========================================================
RMAN-00569: =============== ERROR MESSAGE STACK FOLLOWS ===============
RMAN-00571: ===========================================================
RMAN-03002: failure of recover command at 07/27/2022 11:13:13
RMAN-06054: media recovery requesting unknown archived log for thread 1 with sequence 1540216 and starting SCN of 15759263077366

RMAN> exit


Recovery Manager complete.
```



## 重置redo序列

- 因为跨了小版本(12.1 -> 12.2)，因此resetlogs后， open会崩溃。

```
[oracle@cprac21 u02]$ sqlplus / as sysdba

SQL*Plus: Release 12.2.0.1.0 Production on Wed Jul 27 11:13:20 2022

Copyright (c) 1982, 2016, Oracle.  All rights reserved.


Connected to:
Oracle Database 12c Enterprise Edition Release 12.2.0.1.0 - 64bit Production

SQL> alter database open resetlogs;
alter database open resetlogs
*
ERROR at line 1:
ORA-00603: ORACLE server session terminated by fatal error
ORA-01092: ORACLE instance terminated. Disconnection forced
ORA-00704: bootstrap process failure
ORA-00604: error occurred at recursive SQL level 1
ORA-00904: "ACDRROWTSINTCOL#": invalid identifier
Process ID: 3713
Session ID: 1892 Serial number: 4982


SQL> exit
```



## 升级数据库

- 12cR2开始，升级方式永久的改变了。

```
[oracle@cprac21 u02]$ rman target /

Recovery Manager: Release 12.2.0.1.0 - Production on Wed Jul 27 11:14:20 2022

Copyright (c) 1982, 2017, Oracle and/or its affiliates.  All rights reserved.

connected to target database (not started)

SQL>   startup upgrade  pfile='/home/oracle/pnmdc';
ORA-32006: SEC_CASE_SENSITIVE_LOGON initialization parameter has been deprecated
ORACLE instance started.

Total System Global Area 1.0737E+10 bytes
Fixed Size                 12170960 bytes
Variable Size            3154118960 bytes
Database Buffers         7549747200 bytes
Redo Buffers               21381120 bytes
Database mounted.
Database opened.
SQL> exit
Disconnected from Oracle Database 12c Enterprise Edition Release 12.2.0.1.0 - 64bit Production

[oracle@cprac21 u02]$  cd $ORACLE_HOME/rdbms/admin
[oracle@cprac21 admin]$  $ORACLE_HOME/perl/bin/perl catctl.pl catupgrd.sql

Argument list for [catctl.pl]
Run in                c = 0
Do not run in         C = 0
Input Directory       d = 0
Echo OFF              e = 1
Simulate              E = 0
Forced cleanup        F = 0
Log Id                i = 0
Child Process         I = 0
Log Dir               l = 0
Priority List Name    L = 0
Upgrade Mode active   M = 0
SQL Process Count     n = 0
SQL PDB Process Count N = 0
Open Mode Normal      o = 0
Start Phase           p = 0
End Phase             P = 0
Reverse Order         r = 0
AutoUpgrade Resume    R = 0
Script                s = 0
Serial Run            S = 0
RO User Tablespaces   T = 0
Display Phases        y = 0
Debug catcon.pm       z = 0
Debug catctl.pl       Z = 0

catctl.pl VERSION: [12.2.0.1.0]
           STATUS: [production]
            BUILD: [RDBMS_12.2.0.1.0_LINUX.X64_170125]


/u01/app/oracle/product/12.2.0/dbhome_1/rdbms/admin/orahome = [/u01/app/oracle/product/12.2.0/dbhome_1]
/u01/app/oracle/product/12.2.0/dbhome_1/bin/orabasehome = [/u01/app/oracle/product/12.2.0/dbhome_1]
catctlGetOrabase = [/u01/app/oracle/product/12.2.0/dbhome_1]

Analyzing file /u01/app/oracle/product/12.2.0/dbhome_1/rdbms/admin/catupgrd.sql

Log file directory = [/tmp/cfgtoollogs/upgrade20220727111648]

catcon: ALL catcon-related output will be written to [/tmp/cfgtoollogs/upgrade20220727111648/catupgrd_catcon_9043.lst]
catcon: See [/tmp/cfgtoollogs/upgrade20220727111648/catupgrd*.log] files for output generated by scripts
catcon: See [/tmp/cfgtoollogs/upgrade20220727111648/catupgrd_*.lst] files for spool files, if any

Number of Cpus        = 24
Database Name         = NMDCFARM
DataBase Version      = 12.1.0.1.0
catcon: ALL catcon-related output will be written to [/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649/catupgrd_catcon_9043.lst]
catcon: See [/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649/catupgrd*.log] files for output generated by scripts
catcon: See [/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649/catupgrd_*.lst] files for spool files, if any

Log file directory = [/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649]

Parallel SQL Process Count            = 4
Components in [NMDCFARM]
    Installed [CATALOG CATPROC OWM RAC XDB]
Not Installed [APEX APS CATJAVA CONTEXT DV EM JAVAVM MGW ODM OLS ORDIM SDO WK XML XOQ]

------------------------------------------------------
Phases [0-115]         Start Time:[2022_07_27 11:16:49]
------------------------------------------------------
***********   Executing Change Scripts   ***********
Serial   Phase #:0    [NMDCFARM] Files:1    Time: 32s
***************   Catalog Core SQL   ***************
Serial   Phase #:1    [NMDCFARM] Files:5    Time: 17s
Restart  Phase #:2    [NMDCFARM] Files:1    Time: 1s
***********   Catalog Tables and Views   ***********
Parallel Phase #:3    [NMDCFARM] Files:19   Time: 5s
Restart  Phase #:4    [NMDCFARM] Files:1    Time: 0s
*************   Catalog Final Scripts   ************
Serial   Phase #:5    [NMDCFARM] Files:6    Time: 7s
*****************   Catproc Start   ****************
Serial   Phase #:6    [NMDCFARM] Files:1    Time: 5s
*****************   Catproc Types   ****************
Serial   Phase #:7    [NMDCFARM] Files:2    Time: 6s
Restart  Phase #:8    [NMDCFARM] Files:1    Time: 0s
****************   Catproc Tables   ****************
Parallel Phase #:9    [NMDCFARM] Files:69   Time: 7s
Restart  Phase #:10   [NMDCFARM] Files:1    Time: 0s
*************   Catproc Package Specs   ************
Serial   Phase #:11   [NMDCFARM] Files:1    Time: 17s
Restart  Phase #:12   [NMDCFARM] Files:1    Time: 0s
**************   Catproc Procedures   **************
Parallel Phase #:13   [NMDCFARM] Files:97   Time: 3s
Restart  Phase #:14   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:15   [NMDCFARM] Files:118  Time: 4s
Restart  Phase #:16   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:17   [NMDCFARM] Files:13   Time: 1s
Restart  Phase #:18   [NMDCFARM] Files:1    Time: 0s
*****************   Catproc Views   ****************
Parallel Phase #:19   [NMDCFARM] Files:33   Time: 6s
Restart  Phase #:20   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:21   [NMDCFARM] Files:3    Time: 3s
Restart  Phase #:22   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:23   [NMDCFARM] Files:24   Time: 40s
Restart  Phase #:24   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:25   [NMDCFARM] Files:11   Time: 25s
Restart  Phase #:26   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:27   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:28   [NMDCFARM] Files:3    Time: 2s
Serial   Phase #:29   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:30   [NMDCFARM] Files:1    Time: 0s
***************   Catproc CDB Views   **************
Serial   Phase #:31   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:32   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:34   [NMDCFARM] Files:1    Time: 0s
*****************   Catproc PLBs   *****************
Serial   Phase #:35   [NMDCFARM] Files:283  Time: 10s
Serial   Phase #:36   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:37   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:38   [NMDCFARM] Files:1    Time: 2s
Restart  Phase #:39   [NMDCFARM] Files:1    Time: 0s
***************   Catproc DataPump   ***************
Serial   Phase #:40   [NMDCFARM] Files:3    Time: 24s
Restart  Phase #:41   [NMDCFARM] Files:1    Time: 0s
******************   Catproc SQL   *****************
Parallel Phase #:42   [NMDCFARM] Files:13   Time: 27s
Restart  Phase #:43   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:44   [NMDCFARM] Files:12   Time: 7s
Restart  Phase #:45   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:46   [NMDCFARM] Files:2    Time: 0s
Restart  Phase #:47   [NMDCFARM] Files:1    Time: 0s
*************   Final Catproc scripts   ************
Serial   Phase #:48   [NMDCFARM] Files:1    Time: 2s
Restart  Phase #:49   [NMDCFARM] Files:1    Time: 0s
**************   Final RDBMS scripts   *************
Serial   Phase #:50   [NMDCFARM] Files:1    Time: 9s
************   Upgrade Component Start   ***********
Serial   Phase #:51   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:52   [NMDCFARM] Files:1    Time: 0s
****************   Upgrading Java   ****************
Serial   Phase #:53   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:54   [NMDCFARM] Files:1    Time: 0s
*****************   Upgrading XDK   ****************
Serial   Phase #:55   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:56   [NMDCFARM] Files:1    Time: 0s
*********   Upgrading APS,OLS,DV,CONTEXT   *********
Serial   Phase #:57   [NMDCFARM] Files:1    Time: 1s
*****************   Upgrading XDB   ****************
Restart  Phase #:58   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:60   [NMDCFARM] Files:3    Time: 4s
Serial   Phase #:61   [NMDCFARM] Files:3    Time: 2s
Parallel Phase #:62   [NMDCFARM] Files:9    Time: 1s
Parallel Phase #:63   [NMDCFARM] Files:24   Time: 3s
Serial   Phase #:64   [NMDCFARM] Files:4    Time: 3s
Serial   Phase #:65   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:66   [NMDCFARM] Files:30   Time: 1s
Serial   Phase #:67   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:68   [NMDCFARM] Files:6    Time: 1s
Serial   Phase #:69   [NMDCFARM] Files:2    Time: 8s
Serial   Phase #:70   [NMDCFARM] Files:3    Time: 17s
Restart  Phase #:71   [NMDCFARM] Files:1    Time: 0s
*********   Upgrading CATJAVA,OWM,MGW,RAC   ********
Serial   Phase #:72   [NMDCFARM] Files:1    Time: 22s
****************   Upgrading ORDIM   ***************
Restart  Phase #:73   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:75   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:76   [NMDCFARM] Files:2    Time: 0s
Serial   Phase #:77   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:78   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:79   [NMDCFARM] Files:2    Time: 0s
Serial   Phase #:80   [NMDCFARM] Files:2    Time: 0s
*****************   Upgrading SDO   ****************
Restart  Phase #:81   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:83   [NMDCFARM] Files:1    Time: 1s
Serial   Phase #:84   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:85   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:86   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:87   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:88   [NMDCFARM] Files:3    Time: 0s
Restart  Phase #:89   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:90   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:91   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:92   [NMDCFARM] Files:1    Time: 1s
Restart  Phase #:93   [NMDCFARM] Files:1    Time: 0s
Parallel Phase #:94   [NMDCFARM] Files:4    Time: 0s
Restart  Phase #:95   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:96   [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:97   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:98   [NMDCFARM] Files:2    Time: 0s
Restart  Phase #:99   [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:100  [NMDCFARM] Files:1    Time: 0s
Restart  Phase #:101  [NMDCFARM] Files:1    Time: 0s
***********   Upgrading Misc. ODM, OLAP   **********
Serial   Phase #:102  [NMDCFARM] Files:1    Time: 0s
****************   Upgrading APEX   ****************
Restart  Phase #:103  [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:104  [NMDCFARM] Files:1    Time: 1s
Restart  Phase #:105  [NMDCFARM] Files:1    Time: 0s
***********   Final Component scripts    ***********
Serial   Phase #:106  [NMDCFARM] Files:1    Time: 0s
*************   Final Upgrade scripts   ************
Serial   Phase #:107  [NMDCFARM] Files:1    Time: 42s
**********   End PDB Application Upgrade   *********
Serial   Phase #:108  [NMDCFARM] Files:1    Time: 0s
*******************   Migration   ******************
Serial   Phase #:109  [NMDCFARM] Files:1    Time: 57s
Serial   Phase #:110  [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:111  [NMDCFARM] Files:1    Time: 55s
*****************   Post Upgrade   *****************
Serial   Phase #:112  [NMDCFARM] Files:1    Time: 12s
****************   Summary report   ****************
Serial   Phase #:113  [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:114  [NMDCFARM] Files:1    Time: 0s
Serial   Phase #:115  [NMDCFARM] Files:1     Time: 62s

------------------------------------------------------
Phases [0-115]         End Time:[2022_07_27 11:26:05]
------------------------------------------------------

Grand Total Time: 556s

 LOG FILES: (/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649/catupgrd*.log)

Upgrade Summary Report Located in:
/u01/app/oracle/product/12.2.0/dbhome_1/cfgtoollogs/NMDCFARM/upgrade20220727111649/upg_summary.log

Grand Total Upgrade Time:    [0d:0h:9m:16s]
```



## 修改pfile内容，并存放在pfile默认位置

- 在前面pfile的内容基础上，主要修改`*.cluster_database=true`
- 方案采用spfile存放在ASM中，有备无患将pfile存放在默认位置做备。

```

[oracle@cprac21 admin]$ cp ~/pnmdc /u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora.bak
[oracle@cprac21 admin]$ sqlplus / as sysdba

SQL*Plus: Release 12.2.0.1.0 Production on Wed Jul 27 11:27:36 2022

Copyright (c) 1982, 2016, Oracle.  All rights reserved.

Connected to an idle instance.

SQL> startup pfile='/u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora.bak';
ORA-32006: SEC_CASE_SENSITIVE_LOGON initialization parameter has been deprecated
ORACLE instance started.

Total System Global Area 1.0737E+10 bytes
Fixed Size                 12170960 bytes
Variable Size            3355445552 bytes
Database Buffers         7348420608 bytes
Redo Buffers               21381120 bytes
Database mounted.
Database opened.
```



## 将spfile创建到asm

```
SQL> create spfile='+ASM_DAT1/NMDCFARM/spfilenmdcfarm.ora' from  pfile='/u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora.bak';

File created.

SQL> shutdown immediate;
Database closed.
Database dismounted.
ORACLE instance shut down.
SQL> exit
```



## 在所有节点上编写pfile，指向spfile

```
# mkdir /u01/app/oracle/diag/adump/NMDCFARM' on cprac22
[oracle@cprac21 admin]$ vi /u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora
[oracle@cprac21 admin]$ cat /u01/app/oracle/product/12.2.0/dbhome_1/dbs/initNMDCFARM1.ora
spfile='+ASM_DAT1/NMDCFARM/spfilenmdcfarm.ora'
# cprac22 同理
```



## 注册实例到RAC

```
[oracle@cprac21 admin]$  srvctl add database -d NMDCFARM -o /u01/app/oracle/product/12.2.0/dbhome_1/
[oracle@cprac21 admin]$ srvctl add instance -d NMDCFARM -i NMDCFARM1 -n cprac21
[oracle@cprac21 admin]$ srvctl add instance -d NMDCFARM -i NMDCFARM2 -n cprac22
```



## 启动实例并查看状态

```
[oracle@cprac21 admin]$ srvctl start database -d NMDCFARM

[oracle@cprac21 admin]$ /u01/app/12.2.0/grid/bin/crsctl stat res -t
--------------------------------------------------------------------------------
Name           Target  State        Server                   State details
--------------------------------------------------------------------------------
Local Resources
--------------------------------------------------------------------------------
ora.ASMNET1LSNR_ASM.lsnr
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ASM_ARC1.dg
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ASM_DAT1.dg
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ASM_OCR.dg
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ASM_REDO1.dg
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ASM_REDO2.dg
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.LISTENER.lsnr
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.chad
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.net1.network
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
ora.ons
               ONLINE  ONLINE       cprac21                  STABLE
               ONLINE  ONLINE       cprac22                  STABLE
--------------------------------------------------------------------------------
Cluster Resources
--------------------------------------------------------------------------------
ora.LISTENER_SCAN1.lsnr
      1        ONLINE  ONLINE       cprac21                  STABLE
ora.MGMTLSNR
      1        ONLINE  ONLINE       cprac21                  169.254.69.221 10.0.
                                                             52.134,STABLE
ora.asm
      1        ONLINE  ONLINE       cprac21                  Started,STABLE
      2        ONLINE  ONLINE       cprac22                  Started,STABLE
      3        OFFLINE OFFLINE                               STABLE
ora.cpgcnxl.db
      1        ONLINE  ONLINE       cprac21                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
      2        ONLINE  ONLINE       cprac22                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
ora.cprac21.vip
      1        ONLINE  ONLINE       cprac21                  STABLE
ora.cprac22.vip
      1        ONLINE  ONLINE       cprac22                  STABLE
ora.ctcnzqf.db
      1        ONLINE  ONLINE       cprac21                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
      2        ONLINE  ONLINE       cprac22                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
ora.cvu
      1        ONLINE  ONLINE       cprac21                  STABLE
ora.mgmtdb
      1        ONLINE  ONLINE       cprac21                  Open,STABLE
ora.nmdcfarm.db
      1        ONLINE  ONLINE       cprac21                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
      2        ONLINE  ONLINE       cprac22                  Open,HOME=/u01/app/o
                                                             racle/product/12.2.0
                                                             /dbhome_1/,STABLE
ora.qosmserver
      1        ONLINE  ONLINE       cprac21                  STABLE
ora.scan1.vip
      1        ONLINE  ONLINE       cprac21                  STABLE
--------------------------------------------------------------------------------


[oracle@cprac21 admin]$ lsnrctl status

LSNRCTL for Linux: Version 12.2.0.1.0 - Production on 27-JUL-2022 11:34:35

Copyright (c) 1991, 2016, Oracle.  All rights reserved.

Connecting to (ADDRESS=(PROTOCOL=tcp)(HOST=)(PORT=1521))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 12.2.0.1.0 - Production
Start Date                26-JUL-2022 22:54:43
Uptime                    0 days 12 hr. 39 min. 51 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /u01/app/12.2.0/grid/network/admin/listener.ora
Listener Log File         /u01/app/grid/diag/tnslsnr/cprac21/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=LISTENER)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=10.0.52.20)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=10.0.52.22)(PORT=1521)))
Services Summary...
Service "+ASM" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "+ASM_ASM_ARC1" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "+ASM_ASM_DAT1" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "+ASM_ASM_OCR" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "+ASM_ASM_REDO1" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "+ASM_ASM_REDO2" has 1 instance(s).
  Instance "+ASM1", status READY, has 1 handler(s) for this service...
Service "CPGCNXL" has 1 instance(s).
  Instance "CPGCNXL1", status READY, has 1 handler(s) for this service...
Service "CPGCNXLXDB" has 1 instance(s).
  Instance "CPGCNXL1", status READY, has 1 handler(s) for this service...
Service "CTCNZQF" has 1 instance(s).
  Instance "CTCNZQF1", status READY, has 1 handler(s) for this service...
Service "CTCNZQFXDB" has 1 instance(s).
  Instance "CTCNZQF1", status READY, has 1 handler(s) for this service...
Service "NMDCFARM" has 1 instance(s).
  Instance "NMDCFARM1", status READY, has 1 handler(s) for this service...
Service "NMDCFARMXDB" has 1 instance(s).
  Instance "NMDCFARM1", status READY, has 1 handler(s) for this service...
The command completed successfully
[oracle@cprac21 admin]$
```



结束。