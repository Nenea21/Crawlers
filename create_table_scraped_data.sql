-- PROCEDURE: public.create_mouse_data_table()

-- DROP PROCEDURE IF EXISTS public.create_mouse_data_table();

CREATE OR REPLACE PROCEDURE public.create_mouse_data_table(OUT created_table_name TEXT)
LANGUAGE plpgsql
AS $BODY$
DECLARE
    base_table_name TEXT := 'mouse_data_' || to_char(CURRENT_DATE, 'YYYYMMDD');
    final_table_name TEXT := base_table_name;
    suffix INT := 1;
    create_sql TEXT;
BEGIN
    WHILE EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = final_table_name
    ) LOOP
        final_table_name := base_table_name || '_' || suffix::TEXT;
        suffix := suffix + 1;
    END LOOP;
    
    create_sql := format('
        CREATE TABLE %I (
            id SERIAL PRIMARY KEY,
            name TEXT,
			brand TEXT,
            url TEXT,
            price REAL,  -- Changed to REAL (float) for proper float handling
            tip TEXT,
            interfata_mouse TEXT,
            interfata_receiver TEXT,
            tehnologie TEXT,
            culoare TEXT,
            event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );', final_table_name);
    EXECUTE create_sql;
    created_table_name := final_table_name;
END;
$BODY$;
