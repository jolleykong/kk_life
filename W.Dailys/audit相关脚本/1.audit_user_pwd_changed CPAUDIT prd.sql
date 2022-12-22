-- create tablespace tbs_aud datafile size 1M autoextend on maxsize 30G;
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


drop TRIGGER sys.CPAUDIT;
CREATE OR REPLACE TRIGGER CPAUDIT
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
   -- 使用加密函数，或alter类型为user时便开始审计。
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

