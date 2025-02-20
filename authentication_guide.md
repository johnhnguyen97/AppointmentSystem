# Authentication Guide

## Step 1: Create a User
```graphql
mutation CreateUser {
  createUser(input: {
    username: "testuser"
    email: "test@example.com"
    password: "Password123!"
    first_name: "Test"
    last_name: "User"
  }) {
    id
    sequential_id
    username
  }
}
```

## Step 2: Login to Get Token
```graphql
mutation Login {
  login(input: {
    username: "testuser"
    password: "Password123!"
  }) {
    token
    user {
      sequential_id
      username
    }
  }
}
```

## Step 3: Add Token to HTTP Headers
1. In the GraphQL playground, click on "HTTP HEADERS" at the bottom
2. Add this JSON (replace token with the one you got from login):
```json
{
  "Authorization": "Bearer your-token-here"
}
```

## Step 4: Now You Can Create Client
```graphql
mutation CreateClient {
  createClient(input: {
    phone: "123-456-7890"
    service: "Hair Cut"
    notes: "New client"
  }) {
    id
    service
    user {
      sequential_id
      username
    }
  }
}
```

## Important Notes
- The token must be prefixed with "Bearer "
- Headers must be valid JSON format
- Token expires after 30 minutes (you'll need to login again)
- Keep the HTTP HEADERS panel open while making authenticated requests
