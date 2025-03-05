-- SQL script to fix the service and status column types in the clients table

-- Begin transaction
BEGIN;

-- Create a temporary column to store the service values
ALTER TABLE clients ADD COLUMN service_temp TEXT;

-- Copy the current service values to the temporary column
UPDATE clients SET service_temp = service::TEXT;

-- Drop the service column
ALTER TABLE clients ALTER COLUMN service DROP NOT NULL;
ALTER TABLE clients DROP COLUMN service;

-- Create a new service column of type TEXT with a default value
ALTER TABLE clients ADD COLUMN service TEXT NOT NULL DEFAULT 'HAIRCUT';

-- Copy the values back from the temporary column
UPDATE clients SET service = service_temp;

-- Drop the temporary column
ALTER TABLE clients DROP COLUMN service_temp;

-- Now fix the status column and category column
ALTER TABLE clients ADD COLUMN status_temp TEXT;
UPDATE clients SET status_temp = status::TEXT;
ALTER TABLE clients ALTER COLUMN status DROP NOT NULL;
ALTER TABLE clients DROP COLUMN status;
ALTER TABLE clients ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE';
UPDATE clients SET status = status_temp;
ALTER TABLE clients DROP COLUMN status_temp;

-- Fix the category column
ALTER TABLE clients ADD COLUMN category_temp TEXT;
UPDATE clients SET category_temp = category::TEXT;
ALTER TABLE clients ALTER COLUMN category DROP NOT NULL;
ALTER TABLE clients DROP COLUMN category;
ALTER TABLE clients ADD COLUMN category TEXT NOT NULL DEFAULT 'NEW';
UPDATE clients SET category = category_temp;
ALTER TABLE clients DROP COLUMN category_temp;

-- Do the same for other tables that use the service_type column
-- service_history table
ALTER TABLE service_history ADD COLUMN service_type_temp TEXT;
UPDATE service_history SET service_type_temp = service_type::TEXT;
ALTER TABLE service_history ALTER COLUMN service_type DROP NOT NULL;
ALTER TABLE service_history DROP COLUMN service_type;
ALTER TABLE service_history ADD COLUMN service_type TEXT NOT NULL DEFAULT 'HAIRCUT';
UPDATE service_history SET service_type = service_type_temp;
ALTER TABLE service_history DROP COLUMN service_type_temp;

-- service_packages table
ALTER TABLE service_packages ADD COLUMN service_type_temp TEXT;
UPDATE service_packages SET service_type_temp = service_type::TEXT;
ALTER TABLE service_packages ALTER COLUMN service_type DROP NOT NULL;
ALTER TABLE service_packages DROP COLUMN service_type;
ALTER TABLE service_packages ADD COLUMN service_type TEXT NOT NULL DEFAULT 'HAIRCUT';
UPDATE service_packages SET service_type = service_type_temp;
ALTER TABLE service_packages DROP COLUMN service_type_temp;

-- Fix the status column in appointments table
ALTER TABLE appointments ADD COLUMN status_temp TEXT;
UPDATE appointments SET status_temp = status::TEXT;
ALTER TABLE appointments ALTER COLUMN status DROP NOT NULL;
ALTER TABLE appointments DROP COLUMN status;
ALTER TABLE appointments ADD COLUMN status TEXT NOT NULL DEFAULT 'SCHEDULED';
UPDATE appointments SET status = status_temp;
ALTER TABLE appointments DROP COLUMN status_temp;

-- Fix the service_type column in appointments table
ALTER TABLE appointments ADD COLUMN service_type_temp TEXT;
UPDATE appointments SET service_type_temp = service_type::TEXT;
ALTER TABLE appointments ALTER COLUMN service_type DROP NOT NULL;
ALTER TABLE appointments DROP COLUMN service_type;
ALTER TABLE appointments ADD COLUMN service_type TEXT NOT NULL DEFAULT 'HAIRCUT';
UPDATE appointments SET service_type = service_type_temp;
ALTER TABLE appointments DROP COLUMN service_type_temp;

-- Commit transaction
COMMIT;
