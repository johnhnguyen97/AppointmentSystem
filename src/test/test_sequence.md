# Step-by-Step GraphQL Testing Sequence

## 1. First Test: Create User and Client

### Step 1.1: Create User
```graphql
mutation {
  createUser(input: {
    username: "john.stylist"
    email: "john.stylist@example.com"
    password: "StylePass123!"
    firstName: "John"
    lastName: "Stylist"
  }) {
    id
    username
    email
  }
}
```

Expected Response:
```json
{
  "data": {
    "createUser": {
      "id": "<user-id>",  # Save this ID
      "username": "john.stylist",
      "email": "john.stylist@example.com"
    }
  }
}
```

### Step 1.2: Login
```graphql
mutation {
  login(input: {
    username: "john.stylist"
    password: "StylePass123!"
  }) {
    token
    user {
      id
      username
    }
  }
}
```

Expected Response:
```json
{
  "data": {
    "login": {
      "token": "<auth-token>",  # Save this token for headers
      "user": {
        "id": "<user-id>",
        "username": "john.stylist"
      }
    }
  }
}
```

### Step 1.3: Create Client
```graphql
mutation {
  createClient(input: {
    userId: "<paste-user-id-from-step-1.1>"
    phone: "(555) 987-6543"
    service: HAIRCUT
    status: "active"
    notes: "New client - prefers morning appointments"
  }) {
    id
    phone
    service
    user {
      username
    }
  }
}
```

Headers:
```json
{
  "Authorization": "Bearer <paste-token-from-step-1.2>"
}
```

## 2. Second Test: Appointment Creation and Management

### Step 2.1: Create Appointment
```graphql
mutation {
  createAppointment(input: {
    title: "Haircut Appointment"
    description: "Regular trim"
    startTime: "2025-02-22T10:00:00Z"
    durationMinutes: 30
    attendeeIds: ["<paste-user-id-from-step-1.1>"]
  }) {
    id
    title
    startTime
    status
    creator {
      username
    }
    attendees {
      username
    }
  }
}
```

### Step 2.2: Update Appointment Status
```graphql
mutation {
  updateAppointment(id: "<paste-appointment-id-from-2.1>", input: {
    status: CONFIRMED
  }) {
    id
    status
    updatedAt
  }
}
```

## 3. Test Error Cases

### Step 3.1: Try Invalid Service Type
```graphql
mutation {
  createClient(input: {
    userId: "<paste-user-id-from-step-1.1>"
    phone: "(555) 123-4567"
    service: INVALID_SERVICE  # Should fail
    status: "active"
  }) {
    id
  }
}
```

Expected Error:
```json
{
  "errors": [
    {
      "message": "Invalid service type",
      "extensions": {
        "code": "VALIDATION_ERROR"
      }
    }
  ]
}
```

### Step 3.2: Try Past Date Appointment
```graphql
mutation {
  createAppointment(input: {
    title: "Past Appointment"
    startTime: "2024-01-01T10:00:00Z"  # Past date
    durationMinutes: 30
    attendeeIds: ["<paste-user-id-from-step-1.1>"]
  }) {
    id
  }
}
```

Expected Error:
```json
{
  "errors": [
    {
      "message": "Appointment start time cannot be in the past",
      "extensions": {
        "code": "VALIDATION_ERROR"
      }
    }
  ]
}
```

## 4. Query Tests

### Step 4.1: Get Client with Appointments
```graphql
query {
  client(id: "<paste-client-id-from-step-1.3>") {
    id
    service
    notes
    user {
      username
    }
    appointments {
      id
      title
      startTime
      status
    }
  }
}
```

## Notes
- Replace placeholders (text in <>) with actual values from previous responses
- Keep track of IDs returned from creation mutations
- All mutations except login require the Authorization header
- Test both success and error cases to ensure proper validation
- Verify response data matches expected formats
- Check error messages are helpful and accurate
