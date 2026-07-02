-- =====================================================================
--  Миграция 0005: новый тип места «Рынки».
--
--  Добавляет значение в справочник point_type («Тип места» в UI, группа
--  «Другое» — выводится автоматически, т.к. не входит в BUILDING_TYPE_NAMES).
--
--  Неразрушающая и идемпотентная: ON CONFLICT DO NOTHING, повторный
--  запуск ничего не меняет. Флаги has_fixed_coordinates / has_address = TRUE
--  (рынок — адресуемое место с фиксированной координатой, как «Учреждение/
--  предприятие»).
--
--  Применить к запущенной БД (из папки code):
--    docker compose exec -T db psql -U root -d db < ./database-core/migrations/0005_point_type_markets.sql
-- =====================================================================

BEGIN;

-- Сначала выравниваем последовательность id по максимальному значению:
-- seed вставляет id явно и не двигает sequence, поэтому авто-id мог бы
-- столкнуться с уже занятыми (напр. id 1). После setval nextval даст max+1.
SELECT setval(
    pg_get_serial_sequence('point_type', 'point_type_id'),
    (SELECT MAX(point_type_id) FROM point_type)
);

-- id не указываем — берётся из последовательности (max+1). Повторный запуск
-- отсекается по UNIQUE(name).
INSERT INTO point_type(name, has_fixed_coordinates, has_address)
VALUES ('Рынки', TRUE, TRUE)
ON CONFLICT (name) DO NOTHING;

COMMIT;
