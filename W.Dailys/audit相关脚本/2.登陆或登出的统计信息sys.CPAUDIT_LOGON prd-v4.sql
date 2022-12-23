/*
数据库用户登录审计。
version 1. 2022-12-22 by KK.
version 2. 2022-12-22 by KK. exclude: ZABBIX2019
!version 3. 2022-12-23 by KK. 新增列记录SID，触发器中加入了对SID的关联条件，避免单行查询返回多个记录的问题。 存在问题， 不要使用。
version 4. 2022-12-23 by KK. 触发器回归v2，增加异常处理。
*/


--创建表用于存储登陆或登出的统计信息
--drop table sys.CPAUDIT_LOGON;
CREATE TABLE sys.CPAUDIT_LOGON
(
   user_id           VARCHAR2 (100),
   session_id        NUMBER (20),
   sid               NUMBER (20),
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
                  SYS_CONTEXT('USERENV', 'SID'),
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
   EXCEPTION
   WHEN OTHERS THEN
   NULL;
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
   EXCEPTION
   WHEN OTHERS THEN
   NULL;
END;
/
