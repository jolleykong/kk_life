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
