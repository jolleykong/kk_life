[TOC]

> # 简介
>
> 由于业务系统要与大数据平台进行对接，需要将Oracle DB的数据同步到异构数据库上，故选用也不得不用上了Goldengate方案
> 然鹅，OGG在RAC上的HA配置一直众说纷纭，我搜索了下发现多数为single node的配置。几经探索，在这里将OGG在RAC的HA配置整理起来，为需要的伙伴提供一点思路
>
> *半部分数据已进行脱敏。*



# 环境信息

源端数据库信息

| HOSTNAME | IP                                     | DB/schema |
| -------- | -------------------------------------- | --------- |
| dbdc1    | 10.0.24.131 (scan:10.0.24.135\136\137) | CTCN/POS  |
| dbdc2    | 10.0.24.132 (scan:10.0.24.135\136\137) | CTCN/POS  |

- 源端数据库版本：Oracle DB 12.1.0.1 RAC (SE)
- OGG版本：OGG-12.2.0.1
- 计划的OGG VIP：10.0.24.138



- 目标端：OGG for bigdata
- 目标端地址：10.18.0.41



# 安装OGG

1. 配置ACFS，mount到/u01/ogg

2. 配置oracle用户环境变量

   ```
   [root@dbdc1 ogg]#  ~oracle/.bash_profile 
   
   新增
   export OGG_HOME=/u01/ogg/gg
   PATH=$PATH:$HOME/bin:$ORACLE_HOME/bin:$ORACLE_HOME/OPatch:$OGG_HOME
   export LD_LIBRARY_PATH=$ORACLE_HOME/lib
   ```

3. 创建目录并设置权限

   ```
   [root@dbdc1 ogg]# mdkir /u01/ogg/gg
   [root@dbdc1 ogg]# chown -R oracle:oinstall /u01/ogg
   ```

4. 下载OGG 12.2.0.1 安装包并上传

   ```
   [root@dbdc1 ogg]# ls -lh /u01/software/V100692-01.zip 
   -rw-r--r-- 1 oracle oinstall 454M Sep  9 14:25 /u01/software/V100692-01.zip
   ```

5. 解压

   ```
   [root@dbdc1 software]# unzip V100692-01.zip -d ogg
   ```

6. 使用oracle用户，通过X11安装

   ```
   [oracle@dbdc1 Disk1]$ pwd
   /u01/software/ogg/fbo_ggs_Linux_x64_shiphome/Disk1
   [oracle@dbdc1 Disk1]$ ./runInstaller
   ```

7. 指定安装位置为ACFS的挂载点/u01/ogg/gg
8. 完成安装

# 配置数据库

## 开启数据库级别日志补充

```
[oracle@dbdc1 ~]$ export ORACLE_SID=CTCN1
[oracle@dbdc1 ~]$ sqlplus / as sysdba

SQL> ALTER DATABASE FORCE LOGGING;

Database altered.

SQL> ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;

Database altered.

SQL> ALTER SYSTEM ARCHIVE LOG CURRENT;

System altered.

SQL> col open_mode for a10
SQL> col FORCE_LOGGING for a10
SQL> SELECT name,open_mode,force_logging,supplemental_log_data_min FROM v$database;

NAME                OPEN_MODE  FORCE_LOGG SUPPLEMENTAL_LOG_DATA_MI
--------------------------- ---------- ---------- ------------------------
CTCN             READ WRITE YES    YES
```



## 在dbdc1为OGG单独创建TNS

这一步并不是必要的，如果OGG只负责一个database，那么可以不配置TNS

由于我这里的案例是要为多个instance做extract，因此每个extract连接不同的database，就要用到TNS

```
CTCN_OGG =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 10.0.24.136)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = CTCN)
    )
  )
```



## 创建OGG管理用户及其表空间

```
SQL> create tablespace ogg datafile '+ASM_DAT1' size 1M autoextend on maxsize 10G;

Tablespace created.

SQL> create user ogg default tablespace ogg identified by ogg;

User created.

SQL> grant connect,resource,dba to ogg;

Grant succeeded.
```



# 配置OGG

## 设置OGG全局参数

```
[oracle@dbdc1 ~]$ cd /u01/ogg/gg/
[oracle@dbdc1 gg]$ ggsci

GGSCI (dbdc1) 1> EDIT PARAMS ./GLOBALS
GGSCHEMA ogg
```



## Source端，OGG设置， 配置管理进程

```
GGSCI (dbdc1) 2> EDIT PARAM MGR
PORT 7809
AUTOSTART ER *
AUTORESTART ER *,RETRIES 3,WAITMINUTES 5,RESETMINUTES 60
LAGREPORTHOURS 1
LAGINFOMINUTES 3
LAGCRITICALMINUTES 10
PURGEOLDEXTRACTS /u01/ogg/datdir/*,USECHECKPOINTS,MINKEEPDAYS 1


GGSCI (dbdc1) 8> DBLOGIN userid ogg@CTCN1_OGG, password ogg
Successfully logged into database.
```



## 创建checkpoint表

```
GGSCI (dbdc1 as ogg@CTCN1) 9> add checkpointtable ogg.ggs_checkpoint

Successfully created checkpoint table ogg.ggs_checkpoint.
```



## 添加跟踪对象，pos下所有表

```
GGSCI (dbdc1 as ogg@CTCN1) 11> ADD TRANDATA pos.*

...
...
```



## 配置extract

> 源端是双节点RAC，此处设置参数THREADS 2

### 配置extract

```
ADD EXTRACT ext_pos1,TRANLOG,BEGIN NOW,THREADS 2
```



### 指定extract的trail位置

```
ADD EXTTRAIL /u01/ogg/datdir/po, EXTRACT ext_pos1 MEGABYTES 50
```



### 配置extract参数

```
源端是双节点RAC，此处设置参数 TRANLOGOPTIONS DBLOGREADER 

GGSCI (dbdc1 as ogg@CTCN1) 5> EDIT PARAMS ext_pos1
EXTRACT ext_pos1
USERID ogg@CTCN_OGG, PASSWORD ogg
TRANLOGOPTIONS DBLOGREADER
EXTTRAIL /u01/ogg/datdir/po
TABLE pos.*;
```



### 查看

```
GGSCI (dbdc1) 9> info all

Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                           
EXTRACT     STOPPED     EXT_pos1    00:00:00      00:00:36    


GGSCI (dbdc1) 10> start ext ext_pos1
GGSCI (dbdc1) 11> info all
Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                           
EXTRACT     RUNNING     EXT_pos1    00:00:00      00:00:07
```



### 查看trail目录

```
[oracle@dbdc1 datdir]$ pwd
/u01/ogg/datdir
[oracle@dbdc1 datdir]$ ll -h
total 1.2M
-rw-r----- 1 oracle oinstall 1.1M Sep 10 10:15 po000000000
```



### 配置投递进程，设置本地trail

```
GGSCI (dbdc1) 1> ADD EXTRACT DP_pos1 EXTTRAILSOURCE /u01/ogg/datdir/po 
EXTRACT added.
```



### 为投递进程DP_pos1 设置远程trail目标

```
GGSCI (dbdc1) 2> ADD RMTTRAIL /data/ogg_app/dirdat/po, EXTRACT DP_pos1
RMTTRAIL added.
```



### 配置DP_pos1参数文件

```
GGSCI (dbdc1) 3> edit param DP_pos1

EXTRACT DP_pos1
USERID ogg@CTCN_OGG, PASSWORD ogg
RMTHOST 10.18.0.41, MGRPORT 7809
RMTTRAIL /data/ogg_app/dirdat/po
TABLE pos.*;
```



# 启动OGG

```
GGSCI (dbdc1) 4> start dp_pos1

GGSCI (dbdc1) 5> info all
Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                           
EXTRACT     RUNNING     EXT_pos1    00:00:00      00:00:03
EXTRACT     RUNNING     DP_pos1     00:00:00      00:00:02
```

检查目标端，应用trail file，配置完成。



# 在RAC上配置OGG的高可用

> VIP：10.0.24.138
>
> VIP_name:oggvip

## 查询当前RAC网络信息

```
[grid@dbdc1 ~]$ crsctl stat res -p |grep -ie .network -ie subnet |grep -ie name -ie subnet  
REGISTRATION_INVITED_SUBNETS=
REGISTRATION_INVITED_SUBNETS=
REGISTRATION_INVITED_SUBNETS=
NAME=ora.net1.network
USR_ORA_SUBNET=10.0.24.0
```



## 在GRID中添加OGG的VIP资源

```
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/appvipcfg create -network=1 -ip=10.0.24.138 -vipname=oggvip -user=root

Production Copyright 2007, 2008, Oracle.All rights reserved
2020-09-14 15:57:52: Creating Resource Type
2020-09-14 15:57:52: Executing /u01/grid/product/12.1.0/grid/bin/crsctl add type app.appvip_net1.type -basetype ora.cluster_vip_net1.type -file /u01/grid/product/12.1.0/grid/crs/template/appvip.type
2020-09-14 15:57:52: Executing cmd: /u01/grid/product/12.1.0/grid/bin/crsctl add type app.appvip_net1.type -basetype ora.cluster_vip_net1.type -file /u01/grid/product/12.1.0/grid/crs/template/appvip.type
2020-09-14 15:57:52: Command output:
>  CRS-2728: A resource type with the name 'app.appvip_net1.type' is already registered
>  CRS-4000: Command Add failed, or completed with errors. 
>End Command output
CRS-2728: A resource type with the name 'app.appvip_net1.type' is already registered
CRS-4000: Command Add failed, or completed with errors.
2020-09-14 15:57:52: Create the Resource
2020-09-14 15:57:52: Executing /u01/grid/product/12.1.0/grid/bin/crsctl add resource oggvip -type app.appvip_net1.type -attr "USR_ORA_VIP=10.0.24.138,START_DEPENDENCIES=hard(ora.net1.network) pullup(ora.net1.network),STOP_DEPENDENCIES=hard(ora.net1.network),ACL='owner:root:rwx,pgrp:root:r-x,other::r--,user:root:r-x',HOSTING_MEMBERS=dbdc1,APPSVIP_FAILBACK="
2020-09-14 15:57:52: Executing cmd: /u01/grid/product/12.1.0/grid/bin/crsctl add resource oggvip -type app.appvip_net1.type -attr "USR_ORA_VIP=10.0.24.138,START_DEPENDENCIES=hard(ora.net1.network) pullup(ora.net1.network),STOP_DEPENDENCIES=hard(ora.net1.network),ACL='owner:root:rwx,pgrp:root:r-x,other::r--,user:root:r-x',HOSTING_MEMBERS=dbdc1,APPSVIP_FAILBACK="
```



## 将OGGVIP资源授权给oracle用户

```
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl setperm resource oggvip -u user:oracle:r-x 
```



## 查看状态并启动OGGVIP

```
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl status resource oggvip 
NAME=oggvip
TYPE=app.appvip_net1.type
TARGET=OFFLINE
STATE=OFFLINE


[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl start resource oggvip
CRS-2672: Attempting to start 'oggvip' on 'dbdc1'
CRS-2676: Start of 'oggvip' on 'dbdc1' succeeded
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl status resource oggvip
NAME=oggvip
TYPE=app.appvip_net1.type
TARGET=ONLINE
STATE=ONLINE on dbdc1


[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl stat res -t
--------------------------------------------------------------------------------
Cluster Resources
--------------------------------------------------------------------------------
oggvip
      1        ONLINE  ONLINE       dbdc1                 STABLE
```



## 在ACFS上创建适用于grid的ogg控制脚本

```
mkdir /u01/ogg/gg/scripts
vi ogg_act.scr
```

```
#!/bin/sh  
#set the Oracle Goldengate installation directory  
export OGG_HOME=/u01/ogg/gg
 
#set the oracle home to the database to ensure GoldenGate will get the  
#right environment settings to be able to connect to the database  
export ORACLE_HOME=/u01/app/oracle/product/12.1.0/db_1
 
#specify delay after start before checking for successful start  
start_delay_secs=5 
 
#Include the GoldenGate home in the library path to start GGSCI  
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:${OGG_HOME}:${LD_LIBRARY_PATH}  
 
#check_process validates that a manager process is running at the PID  
#that GoldenGate specifies.  
   
check_process () {  
if ( [ -f "${OGG_HOME}/dirpcs/MGR.pcm" ] )  
then  
  pid=`cut -f8 "${OGG_HOME}/dirpcs/MGR.pcm"`  
  if [ ${pid} = `ps -e |grep ${pid} |grep mgr |cut -d " " -f2` ]  
  then  
    #manager process is running on the PID exit success  
    exit 0  
  else  
  if [ ${pid} = `ps -e |grep ${pid} |grep mgr |cut -d " " -f1` ]  
  then  
    #manager process is running on the PID exit success  
    exit 0  
  else  
    #manager process is not running on the PID  
    exit 1  
  fi  
fi  
else  
  #manager is not running because there is no PID file  
  exit 1  
fi  
}  
   
#call_ggsci is a generic routine that executes a ggsci command  
call_ggsci () {  
  ggsci_command=$1  
  ggsci_output=`${OGG_HOME}/ggsci<<EOF 
  ${ggsci_command}  
  exit  
  EOF`  
}  
   
case $1 in  
'start')  
  #start manager  
  call_ggsci 'start manager'  
  #there is a small delay between issuing the start manager command  
  #and the process being spawned on the OS. wait before checking  
  sleep ${start_delay_secs}  
  #check whether manager is running and exit accordingly  
  check_process  
  ;;  
'stop')  
  #attempt a clean stop for all non-manager processes  
  #call_ggsci 'stop er *'  
  #ensure everything is stopped  
  call_ggsci 'stop er *!'  
  #call_ggsci 'kill er *'  
  #stop manager without (y/n) confirmation  
  call_ggsci 'stop manager!'  
  #exit success  
  exit 0  
  ;;  
'check')  
  check_process  
  ;;  
'clean')  
  #attempt a clean stop for all non-manager processes  
  #call_ggsci 'stop er *'  
  #ensure everything is stopped  
  #call_ggsci 'stop er *!'  
  #in case there are lingering processes  
  call_ggsci 'kill er *'  
  #stop manager without (y/n) confirmation  
  call_ggsci 'stop manager!'  
  #exit success  
  exit 0  
  ;;  
'abort')  
  #ensure everything is stopped  
  call_ggsci 'stop er *!'  
  #in case there are lingering processes  
  call_ggsci 'kill er *'  
  #stop manager without (y/n) confirmation  
  call_ggsci 'stop manager!'  
  #exit success  
  exit 0  
  ;;  
esac 
```



## 使用oracle用户添加oggapp，并授权给oracle用户管理

```
[oracle@dbdc1 scripts]$ ls /u01/ogg/gg/scripts/ogg_act.scr 
/u01/ogg/gg/scripts/ogg_act.scr

[oracle@dbdc1 scripts]$ chmod +x /u01/ogg/gg/scripts/ogg_act.scr 

[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl add resource oggapp -type cluster_resource \
>  -attr "ACTION_SCRIPT=/u01/ogg/gg/scripts/ogg_act.scr, \
>  CHECK_INTERVAL=30, START_DEPENDENCIES='hard(oggvip,ora.asm) \
>  pullup(oggvip)', STOP_DEPENDENCIES='hard(oggvip)'"

[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl status resource oggapp 
NAME=oggapp
TYPE=cluster_resource
TARGET=OFFLINE
STATE=OFFLINE

[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl setperm resource oggapp -o oracle
```



## 使用GRID启动OGG

```
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl status resource oggapp 
NAME=oggapp
TYPE=cluster_resource
TARGET=OFFLINE
STATE=OFFLINE

[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl start resource oggapp 
CRS-2679: Attempting to clean 'oggapp' on 'dbdc1'
CRS-2681: Clean of 'oggapp' on 'dbdc1' succeeded
CRS-2672: Attempting to start 'oggapp' on 'dbdc1'
CRS-2676: Start of 'oggapp' on 'dbdc1' succeeded


[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl status resource oggapp 
NAME=oggapp
TYPE=cluster_resource
TARGET=ONLINE
STATE=ONLINE on dbdc1


尝试一下停止
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl stop resource oggapp 
CRS-2673: Attempting to stop 'oggapp' on 'dbdc1'
CRS-2677: Stop of 'oggapp' on 'dbdc1' succeeded

GGSCI (dbdc1) 2> info all

Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     STOPPED                                           
EXTRACT     STOPPED     DP_POS1     00:00:00      00:00:03       
EXTRACT     STOPPED     EXT_POS1    00:00:02      00:00:01    
  

尝试一下启动
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl start resource oggapp 
CRS-2672: Attempting to start 'oggapp' on 'dbdc1'
CRS-2676: Start of 'oggapp' on 'dbdc1' succeeded

GGSCI (dbdc1) 3> info all

Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                           
EXTRACT     RUNNING     DP_POS1     00:00:00      00:00:03       
EXTRACT     RUNNING     EXT_POS1    00:00:01      00:00:06    

```

​	grid控制成功



## failover测试

注意将tnsnames配置同步到另一个节点上

```
[root@dbdc1 ~]# /u01/grid/product/12.1.0/grid/bin/crsctl relocate resource oggapp -f
CRS-2673: Attempting to stop 'oggapp' on 'dbdc1'
CRS-2677: Stop of 'oggapp' on 'dbdc1' succeeded
CRS-2673: Attempting to stop 'oggvip' on 'dbdc1'
CRS-2677: Stop of 'oggvip' on 'dbdc1' succeeded
CRS-2672: Attempting to start 'oggvip' on 'dbdc2'
CRS-2676: Start of 'oggvip' on 'dbdc2' succeeded
CRS-2672: Attempting to start 'oggapp' on 'dbdc2'
CRS-2676: Start of 'oggapp' on 'dbdc2' succeeded

GGSCI (dbdc1) 4> info all

Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                           
EXTRACT     STOPPED     DP_POS1     00:00:00      00:00:28     
EXTRACT     STOPPED     EXT_POS1    00:00:00      00:00:27      

GGSCI (dbdc2) 1> info all

Program     Status      Group       Lag at Chkpt  Time Since Chkpt

MANAGER     RUNNING                                               
EXTRACT     RUNNING     DP_POS1     00:00:00      00:00:01    
EXTRACT     RUNNING     EXT_POS1    00:00:00      00:00:09      
```



完成。