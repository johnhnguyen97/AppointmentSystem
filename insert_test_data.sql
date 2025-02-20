-- Drop and recreate enum types
DROP TYPE IF EXISTS service_type CASCADE;
DROP TYPE IF EXISTS client_status CASCADE;

CREATE TYPE service_type AS ENUM ('Haircut', 'Color', 'Style', 'Treatment', 'Nails');
CREATE TYPE client_status AS ENUM ('active', 'inactive', 'pending');

INSERT INTO clients (
    id, 
    name,
    email,
    phone,
    service,
    status,
    created_at,
    updated_at
)
VALUES 
    (1, 'John Doe', 'john@example.com', '(555) 123-4567', 
     'Haircut'::service_type, 'active'::client_status, 
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 'Jane Smith', 'jane@example.com', '(555) 987-6543', 
     'Color'::service_type, 'pending'::client_status, 
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
