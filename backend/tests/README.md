# Test Directory Structure

This directory contains categorized tests for the Appointment System backend.

## Directory Structure

```
tests/
├── database/               # Database-related tests
│   ├── test_db_connection.py  # Database connection tests
│   ├── test_models.py         # Database model tests
│   └── test_migration.py      # Migration tests
├── auth/                   # Authentication related tests
│   ├── test_auth.py          # Authentication tests
│   └── test_permissions.py   # Permission tests
├── api/                    # API endpoint tests
│   ├── test_appointment_api.py
│   ├── test_user_api.py
│   └── test_service_api.py
├── unit/                   # Unit tests
│   ├── test_utils.py
│   └── test_validators.py
└── integration/            # Integration tests
    └── test_workflow.py
```

## Running Tests

### Run all tests
```
python run_tests.py
```

### Run tests from a specific category
```
python run_tests.py -c database
```

### Run tests with a specific marker
```
python run_tests.py -m database
```

### Run tests that match a keyword
```
python run_tests.py -k connection
```

### Generate coverage report
```
python run_tests.py --coverage
```
