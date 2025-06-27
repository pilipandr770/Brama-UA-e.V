-- Скрипт для добавления полей image_data и image_mimetype в таблицу blocks
ALTER TABLE blocks ADD COLUMN image_data BYTEA;
ALTER TABLE blocks ADD COLUMN image_mimetype VARCHAR(128);
