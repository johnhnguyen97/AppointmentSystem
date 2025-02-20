-- Update users table timestamp columns to use consistent defaults
ALTER TABLE users 
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET NOT NULL;

-- Update any existing NULL values
UPDATE users 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;
