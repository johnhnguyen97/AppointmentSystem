# Creating a Client with Auto User Association

1. First, create a new user (skip if you already have one):
```graphql
mutation CreateUser {
  createUser(input: {
    username: "your_username",
    email: "your@email.com",
    password: "your_password",
    first_name: "Your",
    last_name: "Name"
  }) {
    id
    username
    email
  }
}
```

2. Login to get your authentication token:
```graphql
mutation Login {
  login(input: {
    username: "your_username",
    password: "your_password"
  }) {
    token
    user {
      id
      username
    }
  }
}
```

3. In the GraphQL playground, add your token in HTTP HEADERS:
```json
{
  "Authorization": "Bearer your_token_here"
}
```

4. Create a client (automatically associated with your user):
```graphql
mutation CreateClient {
  createClient(input: {
    phone: "123-456-7890"
    service: "Hair Cut"
    notes: "New client"  # Optional
    # status defaults to "active" if not provided
  }) {
    id  # This will be an auto-incrementing number
    phone
    service
    status
    notes
    user {
      id
      username
    }
  }
}
```

Notes:
- Each user can only have one client profile
- Client IDs are auto-incrementing numbers (1, 2, 3, etc.)
- The client is automatically associated with your authenticated user account
- The status field defaults to "active" if not provided
