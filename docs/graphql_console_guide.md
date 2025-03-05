# GraphQL Console Guide

This guide explains how to use the GraphQL console for the Appointment System.

## Getting Started

### Starting the GraphQL Server

To start the GraphQL server, run:

```powershell
.\scripts\start_server.ps1
```

This will start the server at http://127.0.0.1:8000 with the GraphQL endpoint at http://127.0.0.1:8000/graphql.

### Opening the GraphQL Console

To open the GraphQL console in your browser, run:

```powershell
.\scripts\start_graphql_console.ps1
```

This script will:
1. Check if the server is running and start it if needed
2. Open the GraphQL console in your default browser

### Resetting the GraphQL Server

If you need to reset the GraphQL server, run:

```powershell
.\scripts\reset_graphql_server.ps1
```

This script will:
1. Stop any running GraphQL server processes
2. Start a new GraphQL server
3. Optionally open the GraphQL console in your browser

## Using the GraphQL Console

The GraphQL console provides a user interface for executing GraphQL queries and mutations.

### Authentication

Most operations require authentication. To authenticate, use the login mutation:

```graphql
mutation {
  login(input: {username: "admin", password: "password"}) {
    token
    user {
      id
      username
      first_name
      last_name
      is_admin
    }
  }
}
```

Copy the token from the response and click on the "HTTP HEADERS" tab at the bottom of the console. Add the following header:

```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

Replace `YOUR_TOKEN_HERE` with the token you received from the login mutation.

### Example Queries

#### Get All Clients

```graphql
query {
  clients {
    id
    phone
    service
    status
    notes
    category
    loyalty_points
    total_spent
    visit_count
    last_visit
  }
}
```

#### Get Available Service Types

```graphql
query {
  __type(name: "ServiceType") {
    enumValues {
      name
    }
  }
}
```

### Example Mutations

#### Add a New Client

```graphql
mutation {
  addClient(input: {
    phone: "(555) 123-4567",
    service: "HAIRCUT",
    status: "ACTIVE",
    notes: "New client",
    category: "NEW"
  }) {
    id
    phone
    service
    status
    notes
    category
    loyalty_points
    total_spent
    visit_count
    last_visit
  }
}
```

## Using the Python Scripts

### Adding a Test Client

To add a test client using a Python script, run:

```powershell
python .\scripts\add_test_client.py
```

This script will:
1. Check if the server is running
2. Get available service types
3. Login as the admin user
4. Add a new client with default values

You can customize the client by providing command-line arguments:

```powershell
python .\scripts\add_test_client.py --phone "(555) 987-6543" --service "MANICURE" --notes "VIP client" --category "VIP"
```

Run `python .\scripts\add_test_client.py --help` for more information on available options.

## Troubleshooting

### Enum Value Errors

If you encounter errors like "Enum 'ServiceType' cannot represent value: 'Makeup'", it means there's a mismatch between the enum values in the code and the database. To fix this, run:

```powershell
python .\scripts\fix_service_types.py
```

For more information, see [Service Type Enum Fix](service_type_enum_fix.md).

### Server Not Starting

If the server fails to start, check:
1. The database connection (make sure the database is running)
2. The environment variables (make sure the .env file exists and has the correct values)
3. The Bitwarden vault (make sure it's unlocked and has the correct credentials)

### Authentication Issues

If you're getting authentication errors:
1. Make sure you're using the correct username and password
2. Make sure you've added the Authorization header with the token
3. Check if the token has expired (tokens expire after 24 hours)
