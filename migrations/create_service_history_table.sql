CREATE TABLE service_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) NOT NULL,
    service_type VARCHAR NOT NULL,
    provider_name VARCHAR NOT NULL,
    date_of_service TIMESTAMP WITH TIME ZONE NOT NULL,
    notes VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_service_history_client_id ON service_history(client_id);
CREATE INDEX idx_service_history_date ON service_history(date_of_service);
