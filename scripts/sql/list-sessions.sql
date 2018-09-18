select  sa.datid
       ,sa.datname
       ,sa.pid
       ,sa.usesysid
       ,sa.usename
       ,substring(sa.query from 1 for 50) current_query
       ,sa.state
       ,sa.wait_event_type
       ,sa.wait_event
       ,age(clock_timestamp(),sa.xact_start) age_xact_start
       ,age(clock_timestamp(),sa.query_start) age_query_start
       ,age(clock_timestamp(),sa.backend_start) age_backend_start
       ,sa.client_addr
       ,sa.client_port
  from  pg_stat_activity sa
 order by  sa.backend_start DESC
          ,sa.xact_start DESC
,sa.query_start DESC ;
