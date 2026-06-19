-- =====================================================================
--  Починка счётчиков (sequences) после загрузки тестовых данных.
--
--  Тестовые данные вставляются с ЯВНЫМИ id (INSERT ... (id, ...)), а
--  TRUNCATE ... RESTART IDENTITY сбрасывает счётчики на 1. В результате
--  следующая обычная вставка (новый автор/место/свидетельство) пытается
--  занять уже существующий id → нарушение первичного ключа → 400/500.
--
--  Этот скрипт выставляет каждый счётчик на MAX(id)+1. Безопасно запускать
--  на работающей базе сколько угодно раз (данные не меняются).
--
--  Применить к запущенной БД:
--    docker compose exec -T db psql -U root -d db < ./database-core/test_data/fix_sequences.sql
-- =====================================================================

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT s.relname  AS seq_name,
               t.relname  AS tbl_name,
               a.attname  AS col_name
        FROM pg_class s
        JOIN pg_depend d  ON d.objid = s.oid AND d.deptype = 'a'
        JOIN pg_class t   ON t.oid = d.refobjid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
        WHERE s.relkind = 'S'
    LOOP
        EXECUTE format(
            'SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I), 0) + 1, false)',
            r.seq_name, r.col_name, r.tbl_name
        );
    END LOOP;
END $$;
