-- Remove existing constraints and defaults
ALTER TABLE users 
    ALTER COLUMN updated_at DROP DEFAULT,
    ALTER COLUMN updated_at DROP NOT NULL;

-- Update any existing NULL values with created_at
UPDATE users 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Add back NOT NULL constraint without default
ALTER TABLE users 
    ALTER COLUMN updated_at SET NOT NULL;

-- Add a trigger to prevent NULL values
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.updated_at IS NULL THEN
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ensure_user_timestamp ON users;
CREATE TRIGGER ensure_user_timestamp
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
