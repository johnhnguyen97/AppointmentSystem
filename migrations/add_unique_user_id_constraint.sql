-- Add unique constraint to user_id in clients table
ALTER TABLE clients ADD CONSTRAINT unique_user_id UNIQUE (user_id);
