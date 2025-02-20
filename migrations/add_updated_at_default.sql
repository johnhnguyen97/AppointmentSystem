-- Set default value for updated_at column
ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT now();
