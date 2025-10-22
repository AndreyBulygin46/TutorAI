-- Инициализация базы данных AI Tutor
-- Этот файл выполняется при первом запуске PostgreSQL контейнера

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание схемы (если нужно)
-- CREATE SCHEMA IF NOT EXISTS aitutor;

-- Установка прав доступа
GRANT ALL PRIVILEGES ON DATABASE ai_tutor TO aitutor;
