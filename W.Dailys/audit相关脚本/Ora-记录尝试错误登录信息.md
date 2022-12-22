- 用来排查导致密码失败锁定用户的来源

```
CREATE OR REPLACE TRIGGER logon_denied_write_alertlog
  AFTER SERVERERROR ON DATABASE
DECLARE
  l_message varchar2(2000);
BEGIN
  -- ORA-1017: invalid username/password; logon denied
  IF (IS_SERVERERROR(1017)) THEN
    select '[AUD BY DBA] LOGIN Failed to the "' ||
           sys_context('USERENV', 'AUTHENTICATED_IDENTITY') || 
           ' from ' || osuser || '@' || machine || ' [' || nvl(sys_context('USERENV', 'IP_ADDRESS'), 'Unknown IP') || ']' ||
           ' via the "' || program || '" using ' || sys_context('USERENV', 'AUTHENTICATION_TYPE') ||
           ' authentication'
      into l_message
      from sys.v_$session
     where sid =
           to_number(substr(dbms_session.unique_session_id, 1, 4), 'xxxx')
       and serial# =
           to_number(substr(dbms_session.unique_session_id, 5, 4), 'xxxx');
  
    -- write to alert log
    sys.dbms_system.ksdwrt(2, l_message);
  END IF;
END;
/

```









-----

> 原文：
>
> ```
> 
> 
> CREATE OR REPLACE TRIGGER logon_denied_write_alertlog AFTER SERVERERROR ON DATABASE
> DECLARE
>  l_message varchar2(2000);
> BEGIN
>  -- ORA-1017: invalid username/password; logon denied
>  IF (IS_SERVERERROR(1017)) THEN
>  select 'LOGIN Failed to the "'|| sys_context('USERENV' ,'AUTHENTICATED_IDENTITY') ||'" schema'
>  || ' using ' || sys_context ('USERENV', 'AUTHENTICATION_TYPE') ||' authentication'
>  || ' at ' || to_char(logon_time,'dd-MON-yy hh24:mi:ss' )
>  || ' from ' || osuser ||'@'||machine ||' ['||nvl(sys_context ('USERENV', 'IP_ADDRESS'),'Unknown IP')||']'
>  || ' via the "' ||program||'" program.'
>  into l_message
>  from sys .v_$session
>  where sid = to_number(substr(dbms_session.unique_session_id,1 ,4), 'xxxx')
>  and serial# = to_number(substr(dbms_session.unique_session_id,5 ,4), 'xxxx');
>  
>  -- write to alert log
>  sys.dbms_system.ksdwrt( 2,l_message );
>  END IF;
> END;
> /
> 这样，当发生错误时，会在alert日志中记录用户名，主机名，IP地址等信息
> 如下：
> 2019-05-22T10:04:34.769140+08:00
> Failed login attempt to the "TESTER" schema using OS authentication at 22-5鏈?-19 10:04:33 from DESKTOP-6H12RFR\chenyj@WORKGROUP\DESKTOP-6H12RFR [127.0.0.1] via the "sqlplus.exe" program.
> 2019-05-22T10:06:35.735924+08:00
> 
> 
> 
> 来自 <http://blog.itpub.net/8520577/viewspace-2645197/> 
> 
> 
> 
> 
> 在实际运维过程中，我们经常碰到一台数据库服务器被众多应用连接，因为各种原因，有时候更改用户密码后，经常出现应用配置文件中密码更改不全，导致用户被锁定，这个时候如果通过监听去排查，就比较不是那么容易。
> 
> 实际上，oracle数据库是可以讲错误登录信息记录到表或者记录到alert日志的，一般通过使用SYS用户创建触发器来实现，例如记录到alert日志，直接上代码：
> 
> DECLARE
>   V_ERR_MESSAGE   VARCHAR2(168);
>   V_IP        VARCHAR2(15);
>   V_OS_USER VARCHAR2(80);
>   V_MODULE  VARCHAR2(50);
>   V_ACTION  VARCHAR2(50);
>   V_SPID     VARCHAR2(10);
>   V_SID     NUMBER;
>   V_PROGRAM VARCHAR2(48);
> BEGIN
>   IF (ora_is_servererror(1017)) THEN
>     -- get V_IP FOR remote connections :
>     IF upper(sys_context('userenv', 'network_protocol')) = 'TCP' THEN
>       V_IP := sys_context('userenv', 'V_IP_address');
>     END IF;
>     SELECT sid INTO V_SID FROM sys.v_$mystat WHERE rownum < 2;
>     SELECT p.spid, v.program
>       INTO V_SPID, V_PROGRAM
>       FROM v$process p, v$session v
>      WHERE p.addr = v.paddr
>        AND v.sid = V_SID;
>     V_OS_USER := sys_context('userenv', 'os_user');
>     dbms_application_info.read_module(V_MODULE, V_ACTION);
>     V_ERR_MESSAGE := to_char(SYSDATE, 'YYYYMMDD HH24MISS') ||
>                ' logon denied from ' || nvl(V_IP, 'localhost') || ' ' ||
>                V_SPID || ' ' || V_OS_USER || ' with ' || V_PROGRAM || ' – ' ||
>                V_MODULE || ' ' || V_ACTION;
>     sys.dbms_system.ksdwrt(2, V_ERR_MESSAGE);
>   END IF;
> END;
> /
> 你也可以在V_ERR_MESSAGE变量中定义一个自定义的ORA代码，这样可以直接进监控系统；
> 
> 例如记录到表，直接上代码：
> 
> --创建记录表
>  drop table tb_login_fail purge;
>  create table tb_login_fail(
>  c_IP VARCHAR2(15),
>  c_user VARCHAR2(100),
>  c_OS_USER VARCHAR2(100),
>  c_MODULE VARCHAR2(100),
>  c_ACTION VARCHAR2(100),
>  c_SPID VARCHAR2(10),
>  c_SID NUMBER,
>  c_PROGRAM VARCHAR2(100),
>  created_date date
>   );
>  
> --创建触发器：
> CREATE OR REPLACE TRIGGER logon_denied_to_table
>   AFTER servererror ON DATABASE
> DECLARE
>   V_IP        VARCHAR2(15);
>   V_OS_USER VARCHAR2(80);
>   V_MODULE  VARCHAR2(50);
>   V_ACTION  VARCHAR2(50);
>   V_SPID     VARCHAR2(10);
>   v_user  VARCHAR2(100);
>   V_SID     NUMBER;
>   V_PROGRAM VARCHAR2(48);
> BEGIN
>   IF (ora_is_servererror(1017)) THEN
>     -- get V_IP FOR remote connections :
>     IF upper(sys_context('userenv', 'network_protocol')) = 'TCP' THEN
>       V_IP := sys_context('userenv', 'V_IP_address');
>     END IF;
>   --  v_user :=SYS_CONTEXT('USERENV','SESSION_USER');
>     SELECT sid INTO V_SID FROM sys.v_$mystat WHERE rownum < 2;
>     SELECT p.spid, v.program,v.username
>       INTO V_SPID, V_PROGRAM,v_user
>       FROM gv$process p, gv$session v
>      WHERE p.addr = v.paddr
>        AND v.sid = V_SID;
>     V_OS_USER := sys_context('userenv', 'os_user');
>     dbms_application_info.read_module(V_MODULE, V_ACTION);
> insert into tb_login_fail values(V_IP,v_user,V_OS_USER,V_MODULE,V_ACTION,V_SPID,V_SID,V_PROGRAM,sysdate);
> commit;
>   END IF;
> END;
> /
>  
>  
> --将表授权给某个普通用户，自己可以写的 ：）
> 这样，我们就可以在alert日志或者表里面查询到什么时候，哪个客户端使用的错误的用户或者密码尝试登路了。是不是比通过监听日志排查简单很多。
> ————————————————
> 版权声明：本文为CSDN博主「小尖一步」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
> 原文链接：https://blog.csdn.net/zhougongping/article/details/123294443
> 
> 
> 
> 
> CREATE OR REPLACE TRIGGER logon_denied_to_alert
>   AFTER servererror ON DATABASE
> DECLARE
>   message   VARCHAR2(168);
>   ip        VARCHAR2(15);
>   v_os_user VARCHAR2(80);
>   v_module  VARCHAR2(50);
>   v_action  VARCHAR2(50);
>   v_pid     VARCHAR2(10);
>   v_sid     NUMBER;
>   v_program VARCHAR2(48);
> BEGIN
>   IF (ora_is_servererror(1017)) THEN
>     -- get ip FOR remote connections :
>     IF upper(sys_context('userenv', 'network_protocol')) = 'TCP' THEN
>       ip := sys_context('userenv', 'ip_address');
>     END IF;
>     SELECT sid INTO v_sid FROM sys.v_$mystat WHERE rownum < 2;
>     SELECT p.spid, v.program
>       INTO v_pid, v_program
>       FROM v$process p, v$session v
>      WHERE p.addr = v.paddr
>        AND v.sid = v_sid;
>     v_os_user := sys_context('userenv', 'os_user');
>     dbms_application_info.read_module(v_module, v_action);
>     message := to_char(SYSDATE, 'YYYYMMDD HH24MISS') ||
>                ' logon denied from ' || nvl(ip, 'localhost') || ' ' ||
>                v_pid || ' ' || v_os_user || ' with ' || v_program || ' – ' ||
>                v_module || ' ' || v_action;
>     sys.dbms_system.ksdwrt(2, message);
>   END IF;
> END;
> 
> 来自 <https://www.cnblogs.com/xinxin1994/p/6078107.html> 
> 
> ```
>
> 