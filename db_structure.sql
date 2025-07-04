
-- Показати всі схеми в базі даних
SELECT schema_name FROM information_schema.schemata;

-- Показати всі таблиці з їх схемами
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;

-- Показати інформацію про стовпці для всіх таблиць
SELECT 
    t.table_schema,
    t.table_name, 
    c.column_name, 
    c.data_type,
    c.is_nullable
FROM 
    information_schema.tables t
    JOIN information_schema.columns c 
        ON t.table_name = c.table_name 
        AND t.table_schema = c.table_schema
WHERE 
    t.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 
    t.table_schema, t.table_name, c.ordinal_position;

-- Показати первинні ключі
SELECT
    tc.table_schema, 
    tc.table_name, 
    kc.column_name
FROM 
    information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kc
        ON tc.constraint_name = kc.constraint_name
WHERE 
    tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 
    tc.table_schema, tc.table_name;

-- Показати зовнішні ключі
SELECT
    tc.table_schema, 
    tc.table_name, 
    kc.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM 
    information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kc
        ON tc.constraint_name = kc.constraint_name
    JOIN information_schema.constraint_column_usage ccu
        ON tc.constraint_name = ccu.constraint_name
WHERE 
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 
    tc.table_schema, tc.table_name;

