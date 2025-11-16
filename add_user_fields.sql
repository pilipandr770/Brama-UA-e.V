-- Додавання полів до таблиці brama.users
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS birth_date DATE;
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS specialty VARCHAR(128);
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS join_goal TEXT;
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS can_help TEXT;
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS want_to_do TEXT;
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS consent_given BOOLEAN DEFAULT FALSE;
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE brama.users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(255);
