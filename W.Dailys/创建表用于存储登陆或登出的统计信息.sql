--创建表用于存储登陆或登出的统计信息
CREATE TABLE stats$user_log
(
   user_id           VARCHAR2 (30),
   session_id        NUMBER (8),
   HOST              VARCHAR2 (30),
   last_program      VARCHAR2 (48),
   last_action       VARCHAR2 (32),
   last_module       VARCHAR2 (32),
   logon_day         DATE,
   logon_time        VARCHAR2 (10),
   logoff_day        DATE,
   logoff_time       VARCHAR2 (10),
   elapsed_minutes   NUMBER (8)
);

--创建登陆之后的触发器
CREATE OR REPLACE TRIGGER logon_audit_trigger
   AFTER LOGON
   ON DATABASE
BEGIN
   INSERT INTO stats$user_log
        VALUES (USER,
                SYS_CONTEXT ('USERENV', 'SESSIONID'),
                SYS_CONTEXT ('USERENV', 'HOST'),
                NULL,
                NULL,
                NULL,
                SYSDATE,
                TO_CHAR (SYSDATE, 'hh24:mi:ss'),
                NULL,
                NULL,
                NULL);
END;
/

--创建登出之后的触发器
CREATE OR REPLACE TRIGGER logoff_audit_trigger
   BEFORE LOGOFF
   ON DATABASE
BEGIN
   -- ***************************************************
   -- Update the last action accessed
   -- ***************************************************
   UPDATE stats$user_log
      SET last_action =
             (SELECT action
                FROM v$session
               WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

   --***************************************************
   -- Update the last program accessed
   -- ***************************************************
   UPDATE stats$user_log
      SET last_program =
             (SELECT program
                FROM v$session
               WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

   -- ***************************************************
   -- Update the last module accessed
   -- ***************************************************
   UPDATE stats$user_log
      SET last_module =
             (SELECT module
                FROM v$session
               WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = audsid)
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

   -- ***************************************************
   -- Update the logoff day
   -- ***************************************************
   UPDATE stats$user_log
      SET logoff_day = SYSDATE
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

   -- ***************************************************
   -- Update the logoff time
   -- ***************************************************
   UPDATE stats$user_log
      SET logoff_time = TO_CHAR (SYSDATE, 'hh24:mi:ss')
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;

   -- ***************************************************
   -- Compute the elapsed minutes
   -- ***************************************************
   UPDATE stats$user_log
      SET elapsed_minutes = ROUND ( (logoff_day - logon_day) * 1440)
    WHERE SYS_CONTEXT ('USERENV', 'SESSIONID') = session_id;
END;
/


--查看用户的登入登出信息
SQL> select * from sys.stats$user_log where rownum<3;

USER_ID    SESSION_ID HOST            LAST_PROGRAM     LAST_MODULE     LOGON_DAY LOGON_TIME LOGOFF_DA LOGOFF_TIM  ELP_MINS
---------- ---------- --------------- ---------------- ---------------- --------- ---------- --------- ---------- --------
GX_ADMIN    5409517   v2012DB01u      JDBC Thin Client JDBC Thin Client 24-OCT-13 12:20:30   24-OCT-13 16:20:30   240
GX_ADMIN    5409518   v2013DB01u      JDBC Thin Client JDBC Thin Client 24-OCT-13 12:22:23   24-OCT-13 16:22:30   240

--汇总用户登陆时间     
SQL> SELECT user_id, TRUNC (logon_day) logon_day, SUM (elapsed_minutes) total_time
  2  FROM sys.stats$user_log
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
  2  from sys.stats$user_log
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