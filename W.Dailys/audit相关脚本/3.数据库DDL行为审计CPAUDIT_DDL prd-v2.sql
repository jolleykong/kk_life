/*
数据库DDL行为审计。
version 1. 2022-12-22 by KK.
version 2. 2022-12-23 by KK. 增加SID列；触发器增加对module：MMON_SLAVE，MMON_SLAVE行为的排除。

*/
create table sys.CPAUDIT_DDL(
        session_id  NUMBER (20),  
        sid         NUMBER (20),  
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
    if (   SYS_CONTEXT('USERENV', 'module')  not in ('MMON_SLAVE','MMON_SLAVE')) then

        n := ora_sql_txt(sql_text);
        FOR i IN 1 .. n LOOP
            v_stmt := stmt || sql_text(i);
        END LOOP; 
/*
    v_oper      := SYS_CONTEXT('USERENV', 'AUTHENTICATED_IDENTITY');
    v_auth_type := SYS_CONTEXT('USERENV', 'AUTHENTICATION_TYPE');
    v_terminal  := SYS_CONTEXT('userenv', 'terminal');
    v_sid       := SYS_CONTEXT('USERENV', 'SESSIONID');
    v_host      := SYS_CONTEXT('USERENV', 'HOST');
    v_ip        := SYS_CONTEXT('userenv', 'IP_ADDRESS');
    v_osuser    := SYS_CONTEXT('USERENV', 'OS_USER'); 
    v_module    := SYS_CONTEXT('USERENV', 'module');
*/
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
                    sid,
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
            SYS_CONTEXT('USERENV', 'SID'),
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
    end if;
   EXCEPTION
   WHEN OTHERS THEN
   NULL;
END;
/