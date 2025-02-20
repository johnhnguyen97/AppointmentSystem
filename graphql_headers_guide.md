# Setting Up Headers in GraphQL Playground

## 1. First, run the login mutation:
```graphql
mutation Login {
  login(input: {
    username: "testuser"
    password: "Password123!"
  }) {
    token    # Copy this token
    user {
      sequential_id
      username
    }
  }
}
```a# 1. Create a user
mutation {
  createUser(input: {
    username: "john"
    email: "john@example.com"
    password: "Password123!"
    first_name: "John"
    last_name: "Doe"
  }) {
    sequential_id
    username
    client_profile {
      id
      service  # Will show as "Hair Cut", "Manicure", etc.
    }
  }
}

# 2. Login to get token
mutation {
  login(input: {
    username: "john"
    password: "Password123!"
  }) {
    token
    user {
      sequential_id
      username
      client_profile {
        id
        service
        phone
      }
    }
  }
}

# 3. Add this to HTTP HEADERS at bottom:
{
  "Authorization": "Bearer your-token-here"
}

# 4. Create client (use enum values without quotes)
mutation {
  createClient(input: {
    phone: "123-456-7890"
    service: HAIRCUT  # Use HAIRCUT, not "Hair Cut"
    notes: "New client"
  }) {
    id
    service  # Will show as "Hair Cut"
    phone
    notes
    user {
      sequential_id
      username
      client_profile {
        service
        phone
      }
    }
  }
}

# 5. View your profile with client info
query {
  user(sequential_id: 1) {
    username
    client_profile {
      service  # Will show as "Hair Cut"
      phone
      notes
    }
  }
}

# Service types - Use the enum value (left) to get the display value (right):
# HAIRCUT   -> "Hair Cut"
# MANICURE  -> "Manicure"
# PEDICURE  -> "Pedicure"
# FACIAL    -> "Facial"
# MASSAGE   -> "Massage"
# HAIRCOLOR -> "Hair Color"
# HAIRSTYLE -> "Hair Style"
# MAKEUP    -> "Makeup"
# WAXING    -> "Waxing"
# OTHER     -> "Other"


## 2. In the GraphQL Playground:
1. Look at the bottom of the screen
2. Click on "HTTP HEADERS"
3. A panel will open up
4. Copy and paste this exactly (replace YOUR_TOKEN with the token from login):
```json
{
  "Authorization": "Bearer YOUR_TOKEN"
}
```

Example with a real token:
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
}
```

## Common Mistakes to Avoid:
❌ Don't forget the quotes around "Authorization"
❌ Don't forget the space after "Bearer"
❌ Don't include any comments in the JSON
❌ Don't add a comma after the last line

## Correct Format:
```json
{
  "Authorization": "Bearer eyJhbG...token...here"
}
```

## Testing Authentication
After adding headers, try this query:
```graphql
query TestAuth {
  user(sequential_id: 1) {
    username
    sequential_id
  }
}
```

If it works, you're authenticated! Now you can create clients and make other authenticated requests.
