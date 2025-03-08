# Appointment System

A robust appointment scheduling system with database integration.

## Project Structure

```
appointmentsystem/
├── .env                  # Environment variables (not committed to git)
├── src/                  # Source code
│   ├── main/             # Main application code
│   │   ├── migrations/   # Database migrations
│   │   └── services/     # Business logic services
│   ├── test/             # Test files
│   └── utils/            # Utility functions
├── tools/                # Tools and executables
│   └── bws.exe           # Bitwarden Secrets Manager CLI
└── certs/                # Certificates for secure connections
```

## Setup

1. Clone the repository
2. Create a `.env` file in the root directory with the following variables:

```
# Bitwarden Secrets Manager Access Token
BWS_ACCESS_TOKEN=your_access_token

# Database Connection String
DATABASE_URL=your_database_connection_string
```

3. Install dependencies:

```
pip install -r requirements.txt
```

## Database Configuration

The application uses PostgreSQL for data storage. Database credentials are stored securely using the Bitwarden Secrets Manager or environment variables.

To test the database connection:

```
python -m src.test.simple_db_test
```

## Security

- Sensitive credentials are stored in the `.env` file, which is excluded from version control in `.gitignore`
- Database connections use SSL for secure communication
- Bitwarden Secrets Manager is used for accessing secrets securely

## Development

When developing:

1. Always use the environment variables from `.env` for credentials
2. Do not hardcode sensitive information in source code
3. Use the utility functions in `src/utils/db_connection.py` for database connections
