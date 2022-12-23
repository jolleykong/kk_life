/*
数据库用户登录审计。
version 1. 2022-12-22 by KK.
version 2. 2022-12-22 by KK. exclude: ZABBIX2019
*/


--创建表用于存储登陆或登出的统计信息
--drop table sys.CPAUDIT_LOGON;
CREATE TABLE sys.CPAUDIT_LOGON
(
   user_id           VARCHAR2 (100),
   session_id        NUMBER (20),
   host              VARCHAR2 (200),
   ipaddr            VARCHAR2 (50),
   os_user           VARCHAR2 (50),
   terminal          VARCHAR2 (200),
   module            VARCHAR2 (200),
   last_program      VARCHAR2 (200),
   last_action       VARCHAR2 (200),
   last_module       VARCHAR2 (200),
   logon_day         DATE,
   logon_time        VARCHAR2 (10),
   logoff_day        DATE,
   logoff_time       VARCHAR2 (10),
   elapsed_seconds   NUMBER (38)
) tablespace tbs_aud
nologging;

--创建登陆之后的触发器
CREATE OR REPLACE TRIGGER sys.tt_logon
   AFTER LOGON
   ON DATABASE
BEGIN
   if (   SYS_CONTEXT('USERENV','SESSION_USER')  not in ('ZABBIX2019')) then
      INSERT INTO sys.CPAUDIT_LOGON
         VALUES (USER,
                  SYS_CONTEXT('USERENV', 'SESSIONID'),
                  SYS_CONTEXT('USERENV', 'HOST'),
                  SYS_CONTEXT('userenv', 'IP_ADDRESS'),
                  SYS_CONTEXT('USERENV', 'OS_USER'), 
                  SYS_CONTEXT('USERENV', 'TERMINAL'),
                  SYS_CONTEXT('USERENV', 'module'),
                  NULL,
                  NULL,
                  NULL,
                  SYSDATE,
                  TO_CHAR (SYSDATE, 'hh24:mi:ss'),
                  NULL,
                  NULL,
                  NULL);
   end if;
END;
/

--创建登出之后的触发器
CREATE OR REPLACE TRIGGER sys.tt_logoff
   BEFORE LOGOFF
   ON DATABASE
BEGIN
   if (  SYS_CONTEXT('USERENV','SESSION_USER')  not in ('ZABBIX2019')) then
      -- ***************************************************
      -- Update the last action accessed
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET last_action =
               (SELECT action
                  FROM v$session
                  WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

      --***************************************************
      -- Update the last program accessed
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET last_program =
               (SELECT program
                  FROM v$session
                  WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

      -- ***************************************************
      -- Update the last module accessed
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET last_module =
               (SELECT module
                  FROM v$session
                  WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

      -- ***************************************************
      -- Update the logoff day
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET logoff_day = SYSDATE
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

      -- ***************************************************
      -- Update the logoff time
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET logoff_time = TO_CHAR (SYSDATE, 'hh24:mi:ss')
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

      -- ***************************************************
      -- Compute the elapsed seconds
      -- ***************************************************
      UPDATE sys.CPAUDIT_LOGON
         SET elapsed_seconds = ROUND ( (logoff_day - logon_day) * 1440 * 60 )
      WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;
   end if;
END;
/

/*
--查看用户的登入登出信息
SQL> select * from sys.sys.CPAUDIT_LOGON where rownum<3;

USER_ID    SESSION_ID HOST            LAST_PROGRAM     LAST_MODULE     LOGON_DAY LOGON_TIME LOGOFF_DA LOGOFF_TIM  ELP_MINS
---------- ---------- --------------- ---------------- ---------------- --------- ---------- --------- ---------- --------
GX_ADMIN    5409517   v2012DB01u      JDBC Thin Client JDBC Thin Client 24-OCT-13 12:20:30   24-OCT-13 16:20:30   240
GX_ADMIN    5409518   v2013DB01u      JDBC Thin Client JDBC Thin Client 24-OCT-13 12:22:23   24-OCT-13 16:22:30   240

--汇总用户登陆时间     
SQL> SELECT user_id, TRUNC (logon_day) logon_day, SUM (elapsed_seconds) total_time
  2  FROM sys.sys.CPAUDIT_LOGON
  3  GROUP BY user_id, TRUNC (logon_day) ORDER BY 2;

USER_ID                        LOGON_DAY TOTAL_TIME
------------------------------ --------- ----------
GX_ADMIN                       24-OCT-13        960
SYS                            24-OCT-13
GX_ADMIN                       25-OCT-13       2891
GX_WEBUSER                     25-OCT-13
SYS                            25-OCT-13
GX_WEBUSER                     26-OCT-13
GX_ADMIN                       26-OCT-13       2880
SYS                            26-OCT-13
GX_WEBUSER                     27-OCT-13
GX_ADMIN                       27-OCT-13       2640
GX_WEBUSER                     28-OCT-13

--Author : Leshami
--Blog   : http://blog.csdn.net/leshami

--基于日期时间段的用户登陆数
SQL> select trunc (logon_day) logon_day,substr(logon_time,1,2) hour,count(user_id) as number_of_logins
  2  from sys.sys.CPAUDIT_LOGON
  3  group by trunc (logon_day) ,substr(logon_time,1,2)  order by 1,2;

LOGON_DAY HOUR   NUMBER_OF_LOGINS
--------- ------ ----------------
24-OCT-13 12                    2
24-OCT-13 16                    3
24-OCT-13 20                    2
24-OCT-13 22                    2
24-OCT-13 23                    1
25-OCT-13 00                    2
25-OCT-13 03                  104
25-OCT-13 04                    2
25-OCT-13 06                    2
25-OCT-13 10                    2
25-OCT-13 14                    2
   .............


 select 
  SYS_CONTEXT('USERENV','module') module,
  SYS_CONTEXT('USERENV','CURRENT_SQL') current_SQL,
 SYS_CONTEXT('USERENV','CURRENT_SCHEMA') current_schema,
  SYS_CONTEXT('USERENV','CLIENT_INFO') client_info,
 SYS_CONTEXT('USERENV','ACTION') action,
  SYS_CONTEXT('USERENV','TERMINAL') terminal, 
  SYS_CONTEXT('USERENV','LANGUAGE') language, 
  SYS_CONTEXT('USERENV','SESSIONID') sessionid, 
  SYS_CONTEXT('USERENV','INSTANCE') instance, 
  SYS_CONTEXT('USERENV','ENTRYID') entryid, 
  SYS_CONTEXT('USERENV','ISDBA') isdba, 
  SYS_CONTEXT('USERENV','NLS_TERRITORY') nls_territory, 
  SYS_CONTEXT('USERENV','NLS_CURRENCY') nls_currency, 
  SYS_CONTEXT('USERENV','NLS_CALENDAR') nls_calendar, 
  SYS_CONTEXT('USERENV','NLS_DATE_FORMAT') nls_date_format, 
  SYS_CONTEXT('USERENV','NLS_DATE_LANGUAGE') nls_date_language, 
  SYS_CONTEXT('USERENV','NLS_SORT') nls_sort, 
  SYS_CONTEXT('USERENV','CURRENT_USER') current_user, 
  SYS_CONTEXT('USERENV','CURRENT_USERID') current_userid, 
  SYS_CONTEXT('USERENV','SESSION_USER') session_user, 
  SYS_CONTEXT('USERENV','SESSION_USERID') session_userid, 
  SYS_CONTEXT('USERENV','PROXY_USER') proxy_user, 
  SYS_CONTEXT('USERENV','PROXY_USERID') proxy_userid, 
  SYS_CONTEXT('USERENV','DB_DOMAIN') db_domain, 
  SYS_CONTEXT('USERENV','DB_NAME') db_name, 
  SYS_CONTEXT('USERENV','HOST') host, 
  SYS_CONTEXT('USERENV','OS_USER') os_user, 
  SYS_CONTEXT('USERENV','EXTERNAL_NAME') external_name, 
  SYS_CONTEXT('USERENV','IP_ADDRESS') ip_address, 
  SYS_CONTEXT('USERENV','NETWORK_PROTOCOL') network_protocol, 
  SYS_CONTEXT('USERENV','BG_JOB_ID') bg_job_id, 
  SYS_CONTEXT('USERENV','FG_JOB_ID') fg_job_id, 
  SYS_CONTEXT('USERENV','AUTHENTICATION_TYPE') authentication_type, 
  SYS_CONTEXT('USERENV','AUTHENTICATION_DATA') authentication_data 
  from dual ;

https://blog.51cto.com/lhrbest/2698775

  
*/