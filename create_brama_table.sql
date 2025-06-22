-- SQL запрос для создания таблицы Brama
CREATE TABLE IF NOT EXISTS brama (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Добавим несколько тестовых записей
INSERT INTO brama (title, description) VALUES 
    ('Brama UA', 'Головная страница проекта'),
    ('О проекте', 'Информация о проекте Brama');
