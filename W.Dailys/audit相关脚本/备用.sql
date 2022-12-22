/*
数据库用户登录审计。
version 1. 2022-12-21 by KK.

*/

create table db_user.T_IP_AUDIT(
    ipaddr          varchar2(18),   -- ip
    program_name    varchar2(200),  -- app name
    username        varchar2(100),  -- username
    lr_sj           date,           -- login time
    dlzt            varchar2(100)   -- login status
);

create or replace trigger "login_audit" after logon on database
declare
    v_program_name varchar2(200);
    v_username varchar2(100);
    v_ip varchar2(18);
    v_error varchar2(1000);
begin
    select username,program,sys_context('userenv','IP_ADDRESS')
    into v_username,v_program_name,v_ip
    from sys.v_$session where audsid=sys_context('userevn','SESSIONID');
    /**/
    if (upper(v_username)='DB_USER') then
        if (upper(v_program_name) in ('SQLPLUS.EXE','EXP.EXE','EXPDP.EXE')) then
            if (v_ip =('10.0.0.1')) then
                insert into db_user.T_IP_AUDIT(ipaddr,program_name,username,lr_sj,dlzt)
                    values (v_ip,v_username,v_program_name,sysdate,'登录失败！');
                commit;
                REISE_APPLICATION_ERROR(-29901,'不能使用sqlplus工具登录该用户！');
            end if;
        else
            if (v_ip !=('10.0.0.1')) then
                insert into db_user.T_IP_AUDIT(ipaddr,program_name,username,lr_sj,dlzt)
                    values (v_ip,v_username,v_program_name,sysdate,'登录失败！');
                commit;
                REISE_APPLICATION_ERROR(-29901,'不能使用sqlplus工具登录！'||v_ip);
            end if;
        end if;
    insert into db_user.T_IP_AUDIT(ipaddr,program_name,username,lr_sj,dlzt)
        values (v_ip,v_username,v_program_name,sysdate,'登录成功！');
    commit;
    end if;
    END LOGON_AUDIT;
      