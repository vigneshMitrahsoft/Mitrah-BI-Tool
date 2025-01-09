string_query = {
	'sql':"SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables ORDER BY TABLE_SCHEMA,TABLE_NAME",
	'MySQL':"SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA ={}",
	'postgres':"SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA NOT IN('information_schema', 'pg_catalog') ORDER BY TABLE_SCHEMA,TABLE_NAME"
}

incremental_load = {
    'select_table_records':"select * from {}"
}

get_primary_key = {
    'PostgreSQL':"SELECT kcu.COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND tc.TABLE_SCHEMA = '{}' AND tc.TABLE_NAME = '{}' ",
    'MySQL':"SELECT K.COLUMN_NAME FROM  INFORMATION_SCHEMA.TABLE_CONSTRAINTS T JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K ON K.CONSTRAINT_NAME=T.CONSTRAINT_NAME  WHERE K.TABLE_SCHEMA='{}' AND K.TABLE_NAME='{}'  AND T.CONSTRAINT_TYPE='PRIMARY KEY' LIMIT 1",
    'SQL Server':"SELECT col.COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS t JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS col ON t.CONSTRAINT_NAME = col.CONSTRAINT_NAME WHERE t.TABLE_SCHEMA = '{}' And t.TABLE_NAME = '{}' AND t.CONSTRAINT_TYPE = 'PRIMARY KEY';"
}

get_column_with_dtype ={
    'PostgreSQL':"select COLUMN_NAME,DATA_TYPE from INFORMATION_SCHEMA.columns where TABLE_NAME='{}'",
    'SQL Server':"select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'",
    'MySQL':"select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'",
}