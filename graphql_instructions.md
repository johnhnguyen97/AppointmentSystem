# Creating a Client with GraphQL

## Key Features
- Clients have auto-incrementing IDs (no need to manage UUIDs)
- One-to-one relationship with users (each user can have only one client profile)
- Status defaults to "active" (no need to specify)
- Client is automatically associated with the authenticated user

## Authentication Flow

1. First create a user account (if you don't have one):
```graphql
mutation CreateUser {
  createUser(input: {
    username: "testuser",
    email: "test@example.com",
    password: "test123",
    first_name: "Test",
    last_name: "User"
  }) {
    id
    username
  }
}
```

2. Login to get an authentication token:
```graphql
mutation Login {
  login(input: {
    username: "testuser",
    password: "test123"
  }) {
    token
    user {
      id
      username
    }
  }
}
```

3. In the GraphQL playground, click on "HTTP HEADERS" at the bottom and add your token:
```json
{
  "Authorization": "Bearer your-token-here"
}
```

## Creating a Client Profile

Once authenticated, create your client profile with this mutation:
```graphql
mutation CreateClient {
  createClient(input: {
    phone: "123-456-7890"
    service: "Hair Cut"
    notes: "New client"  # Optional field
    # status defaults to "active" if not provided
  }) {
    id
    phone
    service
    status
    notes
    user {
      id
      username
      email
    }
  }
}
```

Notes:
- The client will automatically be associated with your authenticated user account
- Each user can only have one client profile
- The ID will be auto-generated sequentially (1, 2, 3, etc.)
- You can view your client profile through the authenticated user's data

## GraphQL Playground
Access the GraphQL playground at: http://127.0.0.1:8000/graphql
