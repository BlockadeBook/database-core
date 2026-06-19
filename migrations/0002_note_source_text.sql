-- =====================================================================
--  Снимаем ограничение длины у note.source.
--
--  Раньше колонка была VARCHAR(63) и обрезала длинные библиографические
--  ссылки при сохранении (ошибка StringDataRightTruncation). Делаем её TEXT —
--  как citation и diary.source. Данные не теряются.
--
--  Применить к запущенной БД (из папки code):
--    docker compose exec -T db psql -U root -d db < ./database-core/migrations/0002_note_source_text.sql
-- =====================================================================

ALTER TABLE note ALTER COLUMN source TYPE TEXT;
