-- This SQL script handles migration fixes for the existing votes table
-- and creates the new meeting_votes table

-- Make sure we're not affecting existing votes table
CREATE TABLE IF NOT EXISTS meeting_votes (
    id SERIAL PRIMARY KEY,
    agenda_item_id INTEGER REFERENCES agenda_items(id),
    user_id INTEGER REFERENCES users(id),
    vote VARCHAR(10),
    comment TEXT,
    voted_at TIMESTAMP DEFAULT NOW()
);

-- Create the VoteType enum if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'votetype') THEN
        CREATE TYPE votetype AS ENUM ('yes', 'no', 'abstain');
    END IF;
END $$;

-- Create the MeetingStatus enum if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'meetingstatus') THEN
        CREATE TYPE meetingstatus AS ENUM ('planned', 'active', 'completed', 'cancelled');
    END IF;
END $$;

-- Create the UserRole enum if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('member', 'admin', 'founder');
    END IF;
END $$;

-- Add role column to users if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role') THEN
        ALTER TABLE users ADD COLUMN role userrole DEFAULT 'member';
    END IF;
END $$;

-- Update existing admins to also be founders
UPDATE users SET role = 'founder' WHERE is_admin = true;
