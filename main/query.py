get_tables ={
    'sql':'SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables ORDER BY TABLE_SCHEMA',
    'MySQL':"SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA ={}",
    'postgres':"SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA NOT IN('information_schema', 'pg_catalog') ORDER BY TABLE_SCHEMA"
}