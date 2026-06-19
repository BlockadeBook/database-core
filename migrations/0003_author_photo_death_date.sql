-- =====================================================================
--  Миграция 0003: фотография и дата смерти у автора.
--
--  Добавляет два необязательных поля в таблицу author:
--    • death_date — дата смерти (часто неизвестна, поэтому NULL);
--    • photo      — фотография автора как data URL (base64), TEXT.
--
--  Оба поля выводятся только на персональной странице автора
--  (/authors/:id) и в фильтрах не участвуют.
--
--  Применить к запущенной БД (из папки code):
--    docker compose exec -T db psql -U root -d db < ./database-core/migrations/0003_author_photo_death_date.sql
--  На чистой базе колонки создаются из моделей (create_all) — миграция
--  не нужна.
-- =====================================================================

ALTER TABLE author
    ADD COLUMN IF NOT EXISTS death_date date,
    ADD COLUMN IF NOT EXISTS photo      text;
