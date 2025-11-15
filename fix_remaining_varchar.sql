-- Fix remaining VARCHAR column in projects table
-- Run this in Render Shell: psql $DATABASE_URL

ALTER TABLE brama.projects ALTER COLUMN total_budget TYPE TEXT;

-- Verify all columns are now TEXT or proper types:
\d brama.projects
