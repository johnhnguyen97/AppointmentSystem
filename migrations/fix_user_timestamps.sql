-- Drop the existing default and update trigger
ALTER TABLE users 
    ALTER COLUMN updated_at DROP DEFAULT,
    ALTER COLUMN updated_at DROP NOT NULL;

-- Update any existing NULL values
UPDATE users 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Add back the constraints with the correct default
ALTER TABLE users 
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET NOT NULL;
