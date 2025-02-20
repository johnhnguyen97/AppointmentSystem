-- Drop and recreate the client_status type if needed
DROP TYPE IF EXISTS client_status CASCADE;
CREATE TYPE client_status AS ENUM ('active', 'inactive', 'pending');

-- Drop and recreate the service_type if needed
DROP TYPE IF EXISTS service_type CASCADE;
CREATE TYPE service_type AS ENUM ('haircut', 'color', 'nails', 'style', 'treatment');

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    enabled BOOLEAN DEFAULT true
);

-- Create clients table if it doesn't exist
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    phone VARCHAR(20),
    service service_type,
    status client_status,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Insert test users and their client profiles
WITH inserted_users AS (
    INSERT INTO users (id, username, email, password, first_name, last_name)
    VALUES 
        ('123e4567-e89b-12d3-a456-426614174000', 'johndoe', 'john@example.com', 'hashed_password', 'John', 'Doe'),
        ('987fcdeb-51a2-43f7-9abc-def012345678', 'janesmith', 'jane@example.com', 'hashed_password', 'Jane', 'Smith')
    RETURNING id
)
INSERT INTO clients (user_id, phone, service, status, notes) 
SELECT 
    id,
    CASE WHEN username = 'johndoe' THEN '(555) 123-4567' ELSE '(555) 987-6543' END,
    CASE WHEN username = 'johndoe' THEN 'haircut' ELSE 'color' END,
    CASE WHEN username = 'johndoe' THEN 'active' ELSE 'pending' END,
    CASE WHEN username = 'johndoe' THEN 'Regular client' ELSE 'New client consultation needed' END
FROM users
WHERE username IN ('johndoe', 'janesmith');
