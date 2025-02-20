-- Create sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS user_sequential_id_seq;

-- Add sequential_id to users table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'sequential_id'
    ) THEN
        ALTER TABLE users ADD COLUMN sequential_id INTEGER DEFAULT nextval('user_sequential_id_seq');
    END IF;
END $$;

-- Create index on sequential_id
CREATE INDEX IF NOT EXISTS users_sequential_id_idx ON users(sequential_id);

-- Set sequence ownership
ALTER SEQUENCE user_sequential_id_seq OWNED BY users.sequential_id;

-- Update existing users with sequential IDs
DO $$
BEGIN
    -- Set sequential IDs for existing users if any don't have one
    WITH numbered_users AS (
        SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as seq_num
        FROM users 
        WHERE sequential_id IS NULL OR sequential_id = 0
    )
    UPDATE users u
    SET sequential_id = nextval('user_sequential_id_seq')
    FROM numbered_users n
    WHERE u.id = n.id;

    -- Make sequential_id NOT NULL after populating existing rows
    ALTER TABLE users ALTER COLUMN sequential_id SET NOT NULL;
    
    -- Add unique constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'users_sequential_id_key'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_sequential_id_key UNIQUE (sequential_id);
    END IF;
END $$;
