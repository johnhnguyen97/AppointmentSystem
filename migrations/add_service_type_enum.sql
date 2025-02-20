-- Create service type enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_type') THEN
        CREATE TYPE service_type AS ENUM (
            'Hair Cut',
            'Manicure',
            'Pedicure',
            'Facial',
            'Massage',
            'Hair Color',
            'Hair Style',
            'Makeup',
            'Waxing',
            'Other'
        );
    END IF;
END $$;

-- Modify clients table to use service_type
ALTER TABLE clients 
    ALTER COLUMN service TYPE service_type 
    USING service::service_type;
