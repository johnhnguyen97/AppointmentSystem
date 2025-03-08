# Appointment System

A robust, secure appointment scheduling system with GraphQL API, PostgreSQL database integration, and comprehensive security practices.

## Overview

This appointment system provides a scalable and secure platform for managing appointments, users, and client relationships. Built with modern Python frameworks, the system implements industry-standard security practices and follows a clean architecture approach.

## Project Structure

```
appointmentsystem/
├── .env                        # Environment variables (not committed to git)
├── .gitignore                  # Git ignore file
├── pyproject.toml              # Python project configuration
├── package.json                # Node.js package configuration
├── requirements.txt            # Python dependencies
├── test-requirements.txt       # Test-specific dependencies
├── pytest.ini                  # PyTest configuration
├── src/                        # Source code
│   ├── main/                   # Main application code
│   │   ├── __init__.py         # Package initialization
│   │   ├── auth.py             # Authentication logic
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database setup and configuration
│   │   ├── graphql_context.py  # GraphQL context
│   │   ├── graphql_schema.py   # GraphQL schema definitions
│   │   ├── models.py           # Data models
│   │   ├── schema.py           # Schema definitions
│   │   ├── server.py           # Server configuration
│   │   └── typing.py           # Type definitions
│   ├── test/                   # Test files
│   │   ├── test_bws_token.py   # Bitwarden token authentication test
│   │   ├── test_db_connection.py # Database connection using Bitwarden secret
│   │   ├── simple_db_test.py   # Simple database connectivity test
│   │   ├── direct_db_test.py   # Direct database interaction tests
│   │   ├── test_appointments.py # Appointment functionality tests
│   │   └── test_models.py      # Data model validation tests
│   └── utils/                  # Utility functions
│       └── db_connection.py    # Database connection utilities
├── scripts/                    # Automation scripts
│   └── generate_schemas.py     # Schema generation script
├── tools/                      # Tools and executables
│   └── bws.exe                 # Bitwarden Secrets Manager CLI
└── certs/                      # Certificates for secure connections
```

## Security Practices

### Secrets Management with Bitwarden

The project uses Bitwarden Secrets Manager CLI (`bws.exe`) for secure management of sensitive information, particularly database credentials:

- **Zero secrets in code**: No hardcoded credentials or connection strings in the codebase
- **Centralized management**: All secrets stored and managed through Bitwarden's secure platform
- **Access control**: Fine-grained permissions for team access to secrets
- **Audit trail**: Complete history of secret access and modifications
- **Rotation support**: Easy credential rotation without code changes

#### Using bws.exe for Database Connectivity

The Bitwarden CLI tool is integrated into our database connection process:

```python
# From src/test/test_db_connection.py
async def get_db_url_from_bws():
    """
    Get database connection URL from Bitwarden Secrets Manager
    """
    # Load environment variables for the access token
    load_dotenv()

    access_token = os.environ.get("BWS_ACCESS_TOKEN")
    if not access_token:
        print("BWS_ACCESS_TOKEN not found in .env file")
        return None

    # Run the Bitwarden CLI command to get the database secret
    cmd = ['./tools/bws.exe', 'secret', 'get',
           '8fc2205d-8981-45d4-9f64-b29a00047d75',  # Secret ID for DB connection
           '--access-token', access_token]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse the connection string from the output
    secret_data = json.loads(result.stdout)
    return secret_data.get("value")  # Return the connection string
```

This approach provides several advantages:
- **Secure automation**: Scripts can access secrets without hardcoding
- **CI/CD integration**: Testing environments can securely access credentials
- **Centralized rotation**: Update credentials in one place
- **Access auditing**: Track who accessed database credentials and when

### Additional Security Measures

- **Environment isolation**: `.env` file for local development (excluded from version control)
- **TLS/SSL**: Secure database connections with certificate verification
- **Input validation**: Comprehensive validation on all inputs
- **Authentication**: Secure token-based authentication
- **Authorization**: Role-based access control
- **Data protection**: Encrypted sensitive data at rest and in transit

## Testing Strategy

The project employs a comprehensive testing strategy with a strong focus on secure credential management:

- **Secret-based Tests**: Tests that verify Bitwarden Secrets Manager integration
- **Database Connection Tests**: Verify secure database connections using retrieved credentials
- **Model Tests**: Ensure data models enforce proper validation rules
- **GraphQL Tests**: Verify API functionality and security
- **Integration Tests**: Validate end-to-end flows and component interactions

### Bitwarden-integrated Tests

Our testing suite includes specialized tests for Bitwarden Secrets Manager integration:

- **test_bws_token.py**: Verifies Bitwarden CLI access token authentication
- **test_db_connection.py**: Retrieves database credentials from Bitwarden and tests connectivity
- **direct_db_test.py**: Tests database interactions using credentials from Bitwarden

### Running Tests

```powershell
# Run Bitwarden token authentication test
python -m src.test.test_bws_token

# Run Bitwarden database connection test
python -m src.test.test_db_connection

# Run all tests
python -m pytest

# Run specific test category
python -m pytest src/test/test_appointments.py

# Run tests with coverage
python -m pytest --cov=src
```

## Scripts and Automation

The project leverages automation with secure secret management to streamline development and operations:

### Schema Generation

Schemas are automatically generated from models to maintain consistency:

```powershell
# Generate GraphQL and database schemas
python -m scripts.generate_schemas
```

### Automated Testing and CI/CD

Our automation pipeline securely integrates with Bitwarden Secrets Manager:

- **Continuous Integration**: All tests run on commit using secrets from Bitwarden
- **Environment Setup**: CI environments configured with BWS_ACCESS_TOKEN
- **Database Credentials**: Test databases accessed using Bitwarden-stored credentials
- **No hardcoded secrets**: CI scripts fetch credentials at runtime

### Secure Database Migrations

Database migrations run securely with proper access controls:

```powershell
# Database migration example
$env:BWS_ACCESS_TOKEN = "your_access_token"
$DB_CONNECTION = & "./tools/bws.exe" get secret db-connection --output-value
python -m scripts.run_migrations "$DB_CONNECTION"
```

### Secret Rotation Automation

Credentials are rotated on schedule without downtime:

- **Automated rotation**: Scheduled tasks update secrets in Bitwarden
- **Version control**: Multiple secret versions maintained during transition
- **Validation**: Automated tests verify new credentials before full cutover
- **Rollback capability**: Previous versions retained until successful transition

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

3. Set up Bitwarden Secrets Manager:
   - Install Bitwarden CLI tool (already included as `tools/bws.exe`)
   - Configure access token:
     ```powershell
     $env:BWS_ACCESS_TOKEN = "your_access_token"
     ```
   - Verify connection:
     ```powershell
     python -m src.test.test_bws_token
     ```

4. Set up the database:
   - Obtain connection credentials from Bitwarden
   - Test connection:
     ```powershell
     python -m src.test.test_db_connection
     ```

5. Start the development server:
   ```powershell
   python -m src.main.server
   ```

## Development Guidelines

### Secure Development Workflow

For secure development practices with proper secrets management:

1. **Never hardcode secrets**: All sensitive data must be retrieved from Bitwarden
   ```python
   # INCORRECT - DO NOT DO THIS
   db_password = "MyP@ssw0rd123"

   # CORRECT - Always use the secrets manager
   db_password = get_secret_from_bws("db-password-id")
   ```

2. **Use the utility functions**: Always use the provided db_connection.py utilities
   ```python
   # Proper database connection
   from src.utils.db_connection import get_database_url, get_ssl_context

   async def your_function():
       db_url = get_database_url()  # Gets URL from Bitwarden
       ssl_context = get_ssl_context()
       conn = await asyncpg.connect(db_url, ssl=ssl_context)
   ```

3. **Test with Bitwarden integration**: Ensure tests run with proper secrets retrieval
   ```python
   # Testing pattern for database functions
   async def test_db_feature():
       # Uses Bitwarden to get test database credentials
       conn = await get_test_db_connection()
       # Run test against the database
   ```

### Additional Guidelines

- **Type hints**: Use Python type hints throughout the codebase
- **Documentation**: Document all functions, classes, and modules
- **Validation**: Validate all inputs, especially those from external sources
- **Error handling**: Implement comprehensive error handling
- **Code reviews**: All changes must go through code review with security focus

## Contributing

1. Create a feature branch from `main`
2. Implement changes with appropriate tests
3. Ensure all tests pass
4. Submit a pull request for review
5. Address feedback and maintain code quality standards

## License

[Specify your license here]
