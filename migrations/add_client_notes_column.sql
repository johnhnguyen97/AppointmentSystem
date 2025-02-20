-- Add notes column to clients table
ALTER TABLE clients ADD COLUMN IF NOT EXISTS notes VARCHAR(500);
