- 审计用户自行修改密码的行为

```

/*create table CPAUDIT(
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
recordtime date);
*/


CREATE OR REPLACE TRIGGER tt
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
                     -- 使用加密函数，或alter类型为user时便开始审计。
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

```







----

> 原文
>
> ```
> 
> -- 任何alter动作都会触发记录
> CREATE OR REPLACE TRIGGER tt
>   before alter ON DATABASE
> DECLARE
>   l_message varchar2(2000);
> BEGIN
>     if (ora_dict_obj_name like '%') then
>     select 'abc'      into l_message
>       from dual;  
>     -- write to alert log
>     sys.dbms_system.ksdwrt(2, l_message);
>   END IF;
> END;
> /
> 
> 
> 
> --任何alter动作都会触发记录，记录内容完整化
> CREATE OR REPLACE TRIGGER tt
>   before alter ON DATABASE
> DECLARE
>   l_message varchar2(2000);
> BEGIN
>   if (ora_dict_obj_name like '%') then
>     select 'MMM "' || sys_context('a.USERENV', 'a.AUTHENTICATED_IDENTITY') ||  '" schema' || ' using ' ||
>            sys_context('a.USERENV', 'a.AUTHENTICATION_TYPE') ||        ' authentication' || ' at ' ||
>            to_char(a.logon_time, 'dd-MON-yy hh24:mi:ss') || ' from ' ||            a.osuser || '@' || a.machine || ' [' ||
>            nvl(sys_context('a.USERENV', 'a.IP_ADDRESS'), 'Unknown IP') || ']' ||
>            ' via the "' || a.program || '" program.' || a.sql_id||' details: '||b.sql_fulltext
>       into l_message
>       from sys.v_$session a, sys.v_$sql b
>      where a.sid =
>            to_number(substr(dbms_session.unique_session_id, 1, 4), 'xxxx')
>        and a.serial# =
>            to_number(substr(dbms_session.unique_session_id, 5, 4), 'xxxx')
>        and a.sql_id=b.sql_id;
>     -- write to alert log
>     sys.dbms_system.ksdwrt(2, l_message);
>   END IF;
> END;
> /
> 
> 
> -- 任何密码动作都会触发记录
> CREATE OR REPLACE TRIGGER tt
>   before alter ON DATABASE
> DECLARE
>   l_message varchar2(2000);
> BEGIN
>     if (ora_des_encrypted_password is not null) then
>     select 'abc'      into l_message
>       from dual;  
>     -- write to alert log
>     sys.dbms_system.ksdwrt(2, l_message);
>   END IF;
> END;
> /
> 
> 
> --任何密码动作都会触发记录，记录内容完整化
> 
> CREATE OR REPLACE TRIGGER tt
>   before alter ON DATABASE
> DECLARE
>   l_message varchar2(2000);
>   n        NUMBER;
>   stmt     clob := NULL;
>   sql_text ora_name_list_t;
> BEGIN
>   n := ora_sql_txt(sql_text);
>   FOR i IN 1 .. n LOOP
>     stmt := stmt || sql_text(i);
>   END LOOP;
>   if (ora_dict_obj_name like '%') then
>     select sys_context('USERENV', 'AUTHENTICATED_IDENTITY') --oper 
>     || ' using ' ||
>            sys_context('USERENV', 'AUTHENTICATION_TYPE') --auth type
>     || ' at ' ||
>            to_char(logon_time, 'dd-MON-yy hh24:mi:ss') --command_time
>     || ' from ' ||
>            osuser --osuser 
>     || '@' || machine || ' [' || nvl(sys_context('USERENV', 'IP_ADDRESS'), 'Unknown IP') || ']' --opera_ip
>     || ' via the "' || 
>            program --program_name
>     || '" program.' ||
>            sys_context('userenv', 'terminal')  --terminal
>     || ',' || 
>            ora_sysevent --event
>     || ',' ||
>            ora_dict_obj_type --type
>     || ',' || 
>            ora_dict_obj_name --targetname
>     || ',' || 
>            user --oper
>     || ',' || 
>            stmt  --statement
>     || ',' || 
>            sysdate --record_time
>       into l_message
>       from sys.v_$session
>      where sid =
>            to_number(substr(dbms_session.unique_session_id, 1, 4), 'xxxx')
>        and serial# =
>            to_number(substr(dbms_session.unique_session_id, 5, 4), 'xxxx');
>     -- write to alert log
>     sys.dbms_system.ksdwrt(2, l_message);
>   END IF;
> END;
> /
> 
> 
> ora_des_encrypted_password
> ora_sql_txt(sql_text)
> 
> ```
>
> 