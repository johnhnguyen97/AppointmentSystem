-- Drop existing defaults and constraints
ALTER TABLE users 
    ALTER COLUMN updated_at DROP DEFAULT,
    ALTER COLUMN updated_at DROP NOT NULL;

ALTER TABLE appointments 
    ALTER COLUMN updated_at DROP DEFAULT,
    ALTER COLUMN updated_at DROP NOT NULL;

-- Update any NULL values
UPDATE users 
SET updated_at = created_at 
WHERE updated_at IS NULL;

UPDATE appointments 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Add back constraints with new defaults
ALTER TABLE users 
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET NOT NULL;

ALTER TABLE appointments 
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET NOT NULL;

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_users_timestamp ON users;
DROP TRIGGER IF EXISTS update_appointments_timestamp ON appointments;

-- Create triggers
CREATE TRIGGER update_users_timestamp
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_appointments_timestamp
    BEFORE INSERT OR UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
