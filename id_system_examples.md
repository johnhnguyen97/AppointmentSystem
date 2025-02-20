# Dual ID System Explanation

The system now uses two types of IDs for users:

1. UUID (id)
   - Used internally by the system
   - Guaranteed to be globally unique
   - Example: "123e4567-e89b-12d3-a456-426614174000"
   - Perfect for system operations and relationships

2. Sequential ID (sequential_id)
   - Auto-incrementing numbers (1, 2, 3, etc.)
   - Human-readable and user-friendly
   - Easy to reference in conversations
   - Perfect for user interfaces and communication

## Example Usage

1. Create a user (returns both IDs):
```graphql
mutation CreateUser {
  createUser(input: {
    username: "johndoe",
    email: "john@example.com",
    password: "Password123!",
    first_name: "John",
    last_name: "Doe"
  }) {
    id              # UUID like "123e4567-e89b-12d3-a456-426614174000"
    sequential_id   # Simple number like 1
    username
  }
}
```

2. Query user by sequential ID (user-friendly):
```graphql
query {
  user(sequential_id: 1) {
    sequential_id
    username
    email
  }
}
```

3. Query user by UUID (system operations):
```graphql
query {
  user(id: "123e4567-e89b-12d3-a456-426614174000") {
    sequential_id
    username
    email
  }
}
```

## Benefits
1. Easy reference: "I'm user #42" instead of a long UUID
2. Maintained security with UUIDs for system operations
3. User-friendly IDs for customer service and communication
4. Both IDs are indexed for fast queries
5. Perfect balance of human usability and system integrity

## Example Use Cases
1. Customer Service: "What's your user number?" -> "I'm user #42"
2. System Logs: Uses UUID for accurate tracking
3. URLs: Can use either format
   - User-friendly: /users/42
   - System: /users/123e4567-e89b-12d3-a456-426614174000
4. Database Relations: Always use UUID internally
