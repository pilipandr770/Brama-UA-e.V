-- Add association_balance column to settings table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'brama' 
        AND table_name = 'settings' 
        AND column_name = 'association_balance'
    ) THEN
        ALTER TABLE brama.settings 
        ADD COLUMN association_balance NUMERIC(10, 2) DEFAULT 0.00;
        
        RAISE NOTICE 'Column association_balance added successfully';
    ELSE
        RAISE NOTICE 'Column association_balance already exists';
    END IF;
END $$;
