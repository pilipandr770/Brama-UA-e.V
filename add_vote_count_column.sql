-- Add vote_count column to projects table
-- Execute this in Render Shell psql

ALTER TABLE brama.projects ADD COLUMN IF NOT EXISTS vote_count INTEGER DEFAULT 0;

-- Update existing projects to have vote_count = 0
UPDATE brama.projects SET vote_count = 0 WHERE vote_count IS NULL;

-- Verify the column was added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'brama' 
  AND table_name = 'projects' 
  AND column_name = 'vote_count';
