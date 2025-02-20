-- First, create a backup of the service column
ALTER TABLE clients ADD COLUMN service_temp varchar;
UPDATE clients SET service_temp = service::text;

-- Drop the service column and recreate it as varchar
ALTER TABLE clients DROP COLUMN service;
ALTER TABLE clients ADD COLUMN service varchar NOT NULL;

-- Restore the data
UPDATE clients SET service = service_temp;

-- Drop the temporary column
ALTER TABLE clients DROP COLUMN service_temp;

-- Drop the enum type
DROP TYPE IF EXISTS service_type;
