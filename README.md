# Appointment System

A comprehensive appointment management system built with Python, SQLAlchemy, and GraphQL.

## Features

- User and client management
- Appointment scheduling and tracking
- Service history tracking
- Loyalty points system
- Client referral tracking
- Service package management

## Tech Stack

- Python
- SQLAlchemy (Async)
- GraphQL
- PostgreSQL
- pytest for testing

## Prerequisites

- Python 3.11+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/johnhnguyen97/AppointmentSystem.git
cd AppointmentSystem
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r test-requirements.txt  # For development/testing
```

3. Set up environment variables:
```bash
# Main database connection
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/appointmentdb

# Test database connection (for running tests)
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/testdb
```

## Project Structure

```
src/
├── main/
│   ├── auth.py           # Authentication logic
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection and models
│   ├── graphql_schema.py # GraphQL schema definitions
│   ├── models.py         # SQLAlchemy models
│   ├── schema.py         # Pydantic schemas
│   ├── server.py         # Main server implementation
│   └── typing.py         # Type definitions
└── test/
    ├── conftest.py       # Test configurations and fixtures
    ├── test_appointments.py
    ├── test_basic_models.py
    ├── test_client_appointments.py
    ├── test_database_connection.py
    ├── test_model_validation.py
    └── test_relationships.py
```

## Testing

Run the test suite:
```bash
pytest
```

Note: Make sure to set the `TEST_DATABASE_URL` environment variable before running tests.

## Database Schema

### Tables
- users: User account information
- clients: Client profiles and preferences
- appointments: Appointment scheduling and details
- appointment_attendees: Many-to-many relationship for appointments
- service_packages: Package deals and session tracking
- service_history: Historical record of services provided

### Enums
- appointmentstatus: SCHEDULED, CONFIRMED, CANCELLED, COMPLETED, DECLINED
- servicetype: HAIRCUT, MANICURE, PEDICURE, FACIAL, MASSAGE, etc.

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## TODO

See [TODO.md](TODO.md) for planned features and improvements.
