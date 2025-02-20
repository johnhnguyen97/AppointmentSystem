-- Ensure all required columns exist in clients table
ALTER TABLE clients 
    ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY,
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NOT NULL,
    ADD COLUMN IF NOT EXISTS service VARCHAR(100) NOT NULL,
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'active',
    ADD COLUMN IF NOT EXISTS notes VARCHAR(500),
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) NOT NULL;

-- Add unique constraint for user_id if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'clients_user_id_key'
    ) THEN
        ALTER TABLE clients ADD CONSTRAINT clients_user_id_key UNIQUE (user_id);
    END IF;
END $$;
