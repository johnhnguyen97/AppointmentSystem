# Client Self-Service Flow

## 1. Client Sign Up Process

### Step 1: Create New User Account
```graphql
mutation ClientSignUp {
  createUser(input: {
    username: "alice.client"
    email: "alice.client@example.com"
    password: "ClientPass123!"
    firstName: "Alice"
    lastName: "Johnson"
  }) {
    id
    username
    email
    createdAt
  }
}
```

When executed, you'll get a response like:
```json
{
  "data": {
    "createUser": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "alice.client",
      "email": "alice.client@example.com",
      "createdAt": "2025-02-20T21:49:50Z"
    }
  }
}
```

### Step 2: Log In and Get Authentication Token
```graphql
mutation ClientLogin {
  login(input: {
    username: "alice.client"
    password: "ClientPass123!"
  }) {
    token
    user {
      id
      username
    }
  }
}
```

Response:
```json
{
  "data": {
    "login": {
      "token": "eyJhbGciOiJS...",
      "user": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "alice.client"
      }
    }
  }
}
```

### Step 3: Create Client Profile
```graphql
mutation CreateClientProfile {
  createClient(input: {
    userId: "123e4567-e89b-12d3-a456-426614174000"  # Use ID from Step 1
    phone: "(555) 234-5678"
    service: HAIRCUT
    status: "active"
    notes: "First time client, prefers afternoon appointments"
  }) {
    id
    service
    status
    user {
      username
      email
    }
  }
}
```

Headers to include:
```json
{
  "Authorization": "Bearer eyJhbGciOiJS..."  # Token from Step 2
}
```

## 2. Booking an Appointment

### Step 1: View Available Service Types
```graphql
query GetServiceTypes {
  serviceTypes {
    id
    name
    description
    duration
  }
}
```

### Step 2: Book Appointment
```graphql
mutation BookAppointment {
  createAppointment(input: {
    title: "Haircut Appointment"
    description: "First haircut appointment"
    startTime: "2025-02-22T14:00:00Z"  # Future date
    durationMinutes: 30
    attendeeIds: ["123e4567-e89b-12d3-a456-426614174000"]  # Client's user ID
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

### Step 3: View Booked Appointment
```graphql
query ViewMyAppointments {
  myAppointments {
    id
    title
    startTime
    status
    service
    provider {
      username
      firstName
      lastName
    }
  }
}
```

## 3. Managing Appointments

### Update Appointment (e.g., Cancel)
```graphql
mutation CancelAppointment {
  updateAppointment(id: "appointment-id-here", input: {
    status: CANCELLED
  }) {
    id
    status
    updatedAt
  }
}
```

### View Appointment History
```graphql
query ViewAppointmentHistory {
  myAppointments(status: COMPLETED) {
    id
    title
    startTime
    service
    provider {
      firstName
      lastName
    }
    notes
  }
}
```

## Example Complete Flow

1. First, run the ClientSignUp mutation and save the returned user ID
2. Run the ClientLogin mutation and save the token
3. Add the token to your headers for all subsequent requests
4. Create the client profile with CreateClientProfile
5. View available services with GetServiceTypes
6. Book an appointment with BookAppointment
7. View the booked appointment with ViewMyAppointments

## Error Cases to Test

### 1. Booking Outside Business Hours
```graphql
mutation TestAfterHours {
  createAppointment(input: {
    title: "After Hours Appointment"
    startTime: "2025-02-22T23:00:00Z"  # 11 PM
    durationMinutes: 30
    attendeeIds: ["user-id-here"]
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
      "message": "Appointments must be within business hours (9 AM - 7 PM)",
      "extensions": {
        "code": "VALIDATION_ERROR"
      }
    }
  ]
}
```

### 2. Double Booking
```graphql
mutation TestDoubleBooking {
  createAppointment(input: {
    title: "Overlapping Appointment"
    startTime: "2025-02-22T14:00:00Z"  # Same time as existing appointment
    durationMinutes: 30
    attendeeIds: ["user-id-here"]
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
      "message": "This time slot is already booked",
      "extensions": {
        "code": "VALIDATION_ERROR"
      }
    }
  ]
}
```

## Tips for Testing
1. Save returned IDs and tokens in a notepad as you test
2. Replace placeholder dates with actual future dates
3. Test error cases to ensure proper validation
4. Verify all appointments appear in appointment history
5. Test cancellation and rebooking flows
6. Check that notifications/emails are received (if implemented)
