select                         
       sat.relname
      ,sat.n_dead_tup
      ,sat.n_live_tup  
      ,to_char(sat.last_autovacuum, 'YYYY-MM-DD HH24:MI:SS') last_autovacuum
      ,sat.autovacuum_count
      ,to_char(sat.last_vacuum, 'YYYY-MM-DD HH24:MI:SS') last_vacuum
      ,sat.vacuum_count
      ,sat.seq_scan
      ,sat.idx_scan
  from pg_stat_all_tables sat
 where sat.n_dead_tup != 0
order by sat.n_dead_tup desc;
