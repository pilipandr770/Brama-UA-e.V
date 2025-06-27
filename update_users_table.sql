-- Add profile_photo_url column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(300);
