-- Файл: sql/add_indexes.sql
-- SQLite синтаксис (CREATE INDEX IF NOT EXISTS)

-- Проекти: фільтри за блоком/статусом, сортування за датою
CREATE INDEX IF NOT EXISTS idx_projects_block_id ON projects(block_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

-- Галерея: фільтр по блоку
CREATE INDEX IF NOT EXISTS idx_gallery_images_block_id ON gallery_images(block_id);

-- Votes: пошук по юзеру/проекту
CREATE INDEX IF NOT EXISTS idx_votes_user_id ON votes(user_id);
CREATE INDEX IF NOT EXISTS idx_votes_project_id ON votes(project_id);

-- Users: пошук по email, role, is_member
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_member ON users(is_member);

-- Blocks: активність/тип
CREATE INDEX IF NOT EXISTS idx_blocks_type ON blocks(type);
CREATE INDEX IF NOT EXISTS idx_blocks_is_active ON blocks(is_active);