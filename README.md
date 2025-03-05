# Appointment System

A comprehensive appointment management system with a Node.js backend API and Python data processing service.

## Features

### Core Features
- [ ] User authentication and authorization
- [x] Appointment scheduling and tracking
- [ ] Calendar view of appointments
- [ ] Email notifications
- [ ] User dashboard
- [ ] Admin panel

### Advanced Features
- [ ] Service history tracking
- [ ] Loyalty points system
- [ ] Client referral tracking
- [ ] Service package management

## Tech Stack

### Backend API (Node.js)
- Express.js
- MongoDB
- JWT Authentication
- Node.js v18+

### Data Processing Service (Python)
- Python 3.11+
- SQLAlchemy (Async)
- GraphQL with Strawberry
- PostgreSQL
- pytest for testing

## Project Structure
```
AppointmentSystem/
├── api/                   # Node.js API
│   ├── src/
│   │   ├── controllers/  # Request handlers
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   ├── utils/        # Helper functions
│   │   └── config/       # Configuration files
│   ├── docs/             # API documentation
│   └── tests/            # API test files
│
├── service/              # Python Service
│   ├── src/
│   │   ├── auth.py      # Authentication logic
│   │   ├── config.py    # Configuration settings
│   │   ├── database.py  # Database connection
│   │   ├── models.py    # SQLAlchemy models
│   │   └── schema.py    # GraphQL schema
│   └── tests/           # Python service tests
│
└── README.md            # Project documentation
```

## GraphQL API

The Appointment System includes a GraphQL API that provides a flexible and powerful way to interact with the system. The GraphQL API is built using Strawberry, a modern Python GraphQL library.

### GraphQL Console (GraphiQL)

The system includes GraphiQL, an in-browser IDE for exploring and testing the GraphQL API. To use the GraphQL console:

1. Start the GraphQL server and open the console:
```powershell
.\scripts\start_graphql_console.ps1
```

2. This will start the server and open the GraphQL console in your default browser at:
```
http://127.0.0.1:8000/graphql
```

3. Use the console to explore the API schema, write queries and mutations, and view the results.

For detailed information about using the GraphQL console, including authentication, example queries, and troubleshooting tips, see the [GraphQL Console Guide](docs/graphql_console_guide.md).

### Client Appointment Creation

The system now supports client-initiated appointment creation through the GraphQL API. This allows clients to schedule their own appointments without requiring staff intervention.

For detailed information about this feature, including API usage, business rules, and error handling, see the [Client Appointment Creation Guide](docs/client_appointment_creation.md).

To test the client appointment creation feature:

```powershell
.\scripts\test_client_appointment.ps1
```

This script will:
1. Check if the GraphQL server is running (and start it if needed)
2. Install any required Python packages
3. Run the test script that demonstrates client appointment creation
4. Display the results of the test

### GraphQL Server Management

The project includes several scripts for managing the GraphQL server:

- **`scripts/start_server.ps1`**: Starts the GraphQL server
- **`scripts/start_graphql_console.ps1`**: Starts the server (if needed) and opens the GraphQL console in your browser
- **`scripts/reset_graphql_server.ps1`**: Stops any running GraphQL server processes and starts a new one
- **`scripts/add_test_client.py`**: Adds a test client using the GraphQL API
- **`scripts/fix_service_types.py`**: Fixes service type enum values in the database
- **`scripts/test_client_appointment.ps1`**: Tests the client appointment creation feature

To reset the GraphQL server:
```powershell
.\scripts\reset_graphql_server.ps1
```

To add a test client:
```powershell
python .\scripts\add_test_client.py
```

If you encounter enum value errors, see the [Service Type Enum Fix](docs/service_type_enum_fix.md) documentation.

### Programmatic API Access

You can also interact with the GraphQL API programmatically using the provided Python script:

```powershell
python .\scripts\test_graphql_queries.py
```

This script demonstrates how to:
- Authenticate with the API
- Execute GraphQL queries and mutations
- Handle responses and errors

You can use this script as a starting point for integrating the GraphQL API into your own applications.

## Getting Started

### Prerequisites
- Node.js v18+
- Python 3.11+
- MongoDB
- PostgreSQL
- npm (Node.js package manager)
- pip (Python package manager)
- Bitwarden CLI (for credential management)
- DBeaver (for database management, optional)

### Installation

1. Clone the repository
```bash
git clone https://github.com/johnhnguyen97/AppointmentSystem.git
cd AppointmentSystem
```

2. Install Node.js API dependencies
```bash
cd api
npm install
```

3. Install Python service dependencies
```bash
cd ../service
pip install -r requirements.txt
pip install -r test-requirements.txt  # For development/testing
```

4. Set up environment variables and Bitwarden

Run the provided PowerShell script to set up your environment variables:
```powershell
# Run the environment setup script
./setup_env.ps1
```

This script will:
- Create a `.env` file based on the `.env.example` template
- Prompt you for your database password (securely)
- Optionally set up Bitwarden API credentials

Alternatively, you can manually create a `.env` file with the following variables:
```
# Database connection details
DB_HOST=your_db_host_here
DB_PORT=your_db_port_here
DB_NAME=your_db_name_here
DB_USER=your_db_username_here
DB_PASSWORD=your_db_password_here

# Bitwarden API credentials
BW_CLIENTID=your_client_id_here
BW_CLIENTSECRET=your_client_secret_here
```

For Bitwarden setup, run the provided PowerShell script:
```powershell
# Run the Bitwarden setup script
./scripts/setup_bitwarden.ps1
```

This script will:
- Check if Bitwarden CLI is installed
- Guide you through setting up Bitwarden API keys
- Create necessary vault items for the project

See [Bitwarden Integration](docs/bitwarden_integration.md) for detailed instructions on how Bitwarden is used for credential management.

5. Start the development servers
```bash
# Terminal 1 - Node.js API
cd api
npm run dev

# Terminal 2 - Python Service
cd service
python -m src.server
```

## Database Schemas

### MongoDB Collections (API)
- users: User authentication and profile data
- appointments: Appointment scheduling and details
- notifications: Email and system notifications
- settings: System configuration and preferences

### PostgreSQL Tables (Service)
- users: Extended user information
- clients: Client profiles and preferences
- appointments: Detailed appointment records
- service_packages: Package deals and tracking
- service_history: Historical service records

## Database Management

### Database Scripts
This project includes several PowerShell scripts for managing the database:

- **`scripts/setup_database.ps1`**: Main script that resets the database and verifies the schema
- **`scripts/reset_database.ps1`**: Drops all tables and recreates them using the initial schema
- **`scripts/verify_schema.ps1`**: Verifies that the GraphQL schema and database schema are in sync
- **`scripts/run_test_data.ps1`**: Populates the database with test data for development and testing
- **`scripts/generate_test_data.py`**: Generates SQL statements with nanoid values for testing

To reset the database and ensure everything is properly set up:
```powershell
.\scripts\setup_database.ps1
```

To populate the database with test data:
```powershell
.\scripts\run_test_data.ps1
```

For more information about these scripts, see the [Database Scripts README](scripts/README.md).

### Test Data and GraphQL Integration
This project includes comprehensive test data that can be loaded into the database for development and testing purposes. The test data includes:

- Users with different roles (admin, regular users)
- Clients in various categories (NEW, REGULAR, VIP, PREMIUM)
- Service history with satisfaction ratings
- Service packages with different parameters
- Appointments with various statuses

You can interact with this test data using both SQL and GraphQL:

- **SQL**: Use the `client_test_data_fixed4.sql` script to directly populate the database
- **GraphQL**: Use the examples in [Test Data GraphQL Documentation](docs/test_data_graphql.md) to query and mutate data

The GraphQL documentation includes examples for:
- Authentication and token management
- Querying users, clients, appointments, and service records
- Creating and updating records
- Common queries for business analytics

### DBeaver
This project uses DBeaver for database management and visualization. DBeaver is a free, open-source database tool that supports PostgreSQL and many other database systems.

To set up DBeaver for this project:
1. Install DBeaver using Scoop: `scoop install extras/dbeaver`
2. Run the automated setup script: `.\scripts\setup_dbeaver.ps1`
3. For detailed instructions, see the [DBeaver Setup Guide](docs/dbeaver_setup.md)

The setup script will:
- Automatically retrieve database credentials from Bitwarden or environment variables
- Generate connection profiles for Development, Testing, and Production environments
- Provide instructions for importing the profiles into DBeaver

DBeaver allows you to:
- Browse and edit database tables
- Execute SQL queries
- Create ER diagrams
- Export and import data
- Generate database documentation

## Testing

### Database Connection Test
To test the database connection:
```bash
python -m src.test.db_connection_test
```

This script will:
- Use the database credentials from your environment variables
- Connect to the PostgreSQL database
- Execute a simple query to verify the connection

If you haven't set the `DB_PASSWORD` environment variable, the script will prompt you to enter it.

### API Tests
```bash
cd api
npm test
```

### Service Tests
```bash
cd service
pytest
```

## Security and Credential Management

This project uses Bitwarden for secure credential management. This approach:

1. Keeps sensitive information out of the codebase
2. Centralizes credential management
3. Provides an audit trail for credential access
4. Makes it easier to update credentials without code changes

### Security Best Practices

- **NEVER commit API keys, passwords, or other credentials to the repository**
- Use `.env` files for local development and ensure they are in `.gitignore`
- Use environment variables in production environments
- Avoid hardcoding sensitive values in code, even in configuration files
- Use the provided setup scripts to configure your environment securely
- All password inputs in the system are hidden when typed for enhanced security
- Password input is securely masked with asterisks (*) for improved security (see [Password Security](docs/password_security.md))

### Cleaning Up Sensitive Information

If you accidentally commit sensitive information to the repository, use the provided cleanup script:

```powershell
./scripts/cleanup_secrets.ps1
```

This script will:
1. Create a backup of your current repository state
2. Remove the specified files from Git history
3. Guide you through the process of updating the remote repository

For more detailed information about security and credential management, see:
- [Security Guidelines](docs/security_guidelines.md)
- [Bitwarden Integration](docs/bitwarden_integration.md)
- [Password Security](docs/password_security.md)
- [GitHub's documentation on push protection](https://docs.github.com/code-security/secret-scanning/working-with-push-protection-from-the-command-line)

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## TODO
- [ ] Set up initial project structure
- [ ] Implement user authentication
- [x] Create appointment CRUD operations
- [x] Enable client-initiated appointment creation
- [ ] Add calendar view
- [ ] Implement email notifications
- [ ] Add admin functionality
- [ ] Write API documentation
- [ ] Add unit tests
- [ ] Set up CI/CD pipeline
- [ ] Implement service history tracking
- [ ] Add loyalty points system
- [ ] Create client referral system
- [x] Implement secure credential management with Bitwarden
- [x] Set up GraphQL console and documentation
- [x] Implement secure password input with masked characters
- [ ] Add GraphQL subscriptions for real-time updates
- [ ] Implement rate limiting for GraphQL queries
- [ ] Add query complexity analysis

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
