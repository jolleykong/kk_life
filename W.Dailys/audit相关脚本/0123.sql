create tablespace tbs_aud datafile size 1M autoextend on maxsize 30G;
/*
CREATE OR REPLACE TRIGGER sys.logon_denied_write_alertlog
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



create table sys.CPAUDIT(
oper varchar2(1000), 
auth_type varchar2(1000), 
command_time timestamp, 
osinfo varchar2(3000), 
program_name varchar2(1000), 
terminal varchar2(1000), 
event_name varchar2(200),
event_type varchar2(200), 
targetname varchar2(500), 
username varchar2(500), 
stmt varchar2(4000), 
recordtime date)
tablespace tbs_aud
nologging;


CREATE OR REPLACE TRIGGER sys.CPAUDIT
  before alter ON DATABASE
DECLARE
  PRAGMA AUTONOMOUS_TRANSACTION;
  l_message      varchar2(2000);
  n              NUMBER;
  stmt           clob := NULL;
  sql_text       ora_name_list_t;
  v_oper         varchar2(1000);
  v_auth_type    varchar2(1000);
  v_command_time timestamp;
  v_osuser       varchar2(3000);
  v_program_name varchar2(1000);
  v_terminal     varchar2(1000);
  v_stmt         varchar2(4000);

BEGIN
  n := ora_sql_txt(sql_text);
  FOR i IN 1 .. n LOOP
    v_stmt := stmt || sql_text(i);
  END LOOP;
  v_oper      := sys_context('USERENV', 'AUTHENTICATED_IDENTITY');
  v_auth_type := sys_context('USERENV', 'AUTHENTICATION_TYPE');
  v_terminal  := sys_context('userenv', 'terminal');
  if (ora_des_encrypted_password is not null ) or (ora_dict_obj_type = 'USER') then
    select logon_time,
           osuser || '@' || machine || ' [' ||
           nvl(sys_context('USERENV', 'IP_ADDRESS'), 'Unknown IP') || ']',
           program
      into v_command_time, v_osuser, v_program_name
      from sys.v_$session
     where sid =
           to_number(substr(dbms_session.unique_session_id, 1, 4), 'xxxx')
       and serial# =
           to_number(substr(dbms_session.unique_session_id, 5, 4), 'xxxx');
    insert into sys.CPAUDIT
      (oper,
       auth_type,
       command_time,
       osinfo,
       program_name,
       terminal,
       event_name,
       event_type,
       targetname,
       username,
       stmt,
       recordtime)
    values
      (v_oper,
       v_auth_type,
       v_command_time,
       v_osuser,
       v_program_name,
       v_terminal,
       ora_sysevent,
       ora_dict_obj_type,
       ora_dict_obj_name,
       user,
       v_stmt,
       sysdate);
    commit;
  END IF;
END;
/


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

CREATE OR REPLACE TRIGGER sys.tt_logon
   AFTER LOGON
   ON DATABASE
BEGIN
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
END;
/

CREATE OR REPLACE TRIGGER sys.tt_logoff
   BEFORE LOGOFF
   ON DATABASE
BEGIN
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
END;
/

create table sys.CPAUDIT_DDL(
        session_id  NUMBER (20),  
        oper        varchar2(1000), 
        auth_type   varchar2(1000), 
        command_time timestamp, 
        osinfo      varchar2(3000), 
        host        VARCHAR2 (200), 
        ipaddr      VARCHAR2 (50), 
        os_user     VARCHAR2 (50), 
        module      VARCHAR2 (200), 
        program_name varchar2(1000), 
        terminal    varchar2(1000), 
        event_name  varchar2(200),
        event_type  varchar2(200), 
        targetname  varchar2(500), 
        username    varchar2(500), 
        stmt        varchar2(4000), 
        recordtime  date
    ) tablespace tbs_aud
    nologging;



CREATE OR REPLACE TRIGGER sys.tt_ddl
AFTER DDL ON DATABASE
DECLARE
    PRAGMA AUTONOMOUS_TRANSACTION;
    n              NUMBER;
    stmt           clob := NULL;
    sql_text       ora_name_list_t;
    v_command_time timestamp;
    v_info       varchar2(3000);
    v_program_name varchar2(1000);
    v_stmt         varchar2(4000);

    BEGIN
    n := ora_sql_txt(sql_text);

    FOR i IN 1 .. n LOOP
        v_stmt := stmt || sql_text(i);
    END LOOP; 
-- DDL预计审计记录
        select 
            logon_time,
            osuser || '@' || machine || ' [' ||
            nvl(SYS_CONTEXT('USERENV', 'IP_ADDRESS'), 'Unknown IP') || ']',
            program
        into 
            v_command_time, 
            v_info, 
            v_program_name
        from sys.v_$session
        where sid =
            to_number(substr(dbms_session.unique_session_id, 1, 4), 'xxxx')
        and serial# =
            to_number(substr(dbms_session.unique_session_id, 5, 4), 'xxxx');
        insert into sys.CPAUDIT_DDL
        (
                    session_id,
                    oper,
                    auth_type,
                    command_time,
                    osinfo,
                    host,
                    ipaddr,
                    os_user,
                    module,
                    program_name,
                    terminal,
                    event_name,
                    event_type,
                    targetname,
                    username,
                    stmt,
                    recordtime
        )
        values
        (
            SYS_CONTEXT('USERENV', 'SESSIONID'),
            SYS_CONTEXT('USERENV', 'AUTHENTICATED_IDENTITY'),
            SYS_CONTEXT('USERENV', 'AUTHENTICATION_TYPE'),
            v_command_time,
            v_info,
            SYS_CONTEXT('USERENV', 'HOST'),
            SYS_CONTEXT('userenv', 'IP_ADDRESS'),
            SYS_CONTEXT('USERENV', 'OS_USER'), 
            SYS_CONTEXT('USERENV', 'module'),
            v_program_name,
            SYS_CONTEXT('userenv', 'terminal'),
            ora_sysevent,
            ora_dict_obj_type,
            ora_dict_obj_name,
            user,
            v_stmt,
            sysdate
        );
        commit;
    END;
    /

*/

-- rollback：
-- drop TRIGGER sys.tt_ddl;
-- drop TRIGGER sys.tt_logoff;
-- drop TRIGGER sys.tt_logon;
-- drop TRIGGER sys.CPAUDIT;
-- drop TRIGGER sys.logon_denied_write_alertlog;