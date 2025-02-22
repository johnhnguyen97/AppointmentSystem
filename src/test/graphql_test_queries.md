# GraphQL Test Queries for Appointment System

## 1. Create User
```graphql
mutation CreateUser {
  createUser(input: {
    username: "test.user"
    email: "test.user@example.com"
    password: "TestPass123!"
    firstName: "Test"
    lastName: "User"
  }) {
    id
    username
    email
    firstName
    lastName
    createdAt
  }
}
```

## 2. Create Client
```graphql
mutation CreateClient($userId: UUID!) {
  createClient(input: {
    userId: $userId
    phone: "(555) 123-4567"
    service: HAIRCUT
    status: "active"
    notes: "Test client notes"
  }) {
    id
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

# Variables:
{
  "userId": "paste-user-id-here"
}
```

## 3. Create Appointment
```graphql
mutation CreateAppointment($input: AppointmentCreateInput!) {
  createAppointment(input: $input) {
    id
    title
    description
    startTime
    durationMinutes
    status
    creator {
      id
      username
    }
    attendees {
      id
      username
    }
  }
}

# Variables:
{
  "input": {
    "title": "Test Haircut",
    "description": "Regular haircut appointment",
    "startTime": "2025-02-21T15:00:00Z",
    "durationMinutes": 30,
    "attendeeIds": ["paste-attendee-id-here"]
  }
}
```

## 4. Test Service Type Validation
```graphql
mutation CreateClientInvalidService {
  createClient(input: {
    userId: "paste-user-id-here"
    phone: "(555) 123-4567"
    service: INVALID_TYPE  # Should fail
    status: "active"
  }) {
    id
    service
  }
}
```

## 5. Test Multiple Attendees
```graphql
mutation CreateGroupAppointment($input: AppointmentCreateInput!) {
  createAppointment(input: $input) {
    id
    title
    attendees {
      id
      username
    }
  }
}

# Variables:
{
  "input": {
    "title": "Group Session",
    "description": "Multiple attendee test",
    "startTime": "2025-02-21T16:00:00Z",
    "durationMinutes": 60,
    "attendeeIds": [
      "paste-attendee1-id-here",
      "paste-attendee2-id-here"
    ]
  }
}
```

## 6. Update Appointment Status
```graphql
mutation UpdateAppointmentStatus($id: UUID!, $status: AppointmentStatus!) {
  updateAppointment(id: $id, input: {
    status: $status
  }) {
    id
    status
    updatedAt
  }
}

# Variables:
{
  "id": "paste-appointment-id-here",
  "status": "CONFIRMED"  # SCHEDULED, CONFIRMED, CANCELLED, COMPLETED
}
```

## 7. Update Client Notes
```graphql
mutation UpdateClientNotes($id: Int!, $notes: String!) {
  updateClient(id: $id, input: {
    notes: $notes
  }) {
    id
    notes
  }
}

# Variables:
{
  "id": 1,
  "notes": "Updated client preferences - prefers afternoon appointments"
}
```

## 8. Query Client with Service History
```graphql
query GetClientWithHistory($id: Int!) {
  client(id: $id) {
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

# Variables:
{
  "id": 1
}
```

## Test Flow Example

1. Create user and save the returned ID
2. Create client using the user ID
3. Create an appointment with the client as attendee
4. Update appointment status to CONFIRMED
5. Add notes to client profile
6. Query client to verify all data

## Testing Error Cases

1. Invalid Service Type:
```graphql
mutation TestInvalidService {
  createClient(input: {
    userId: "paste-user-id-here"
    phone: "(555) 123-4567"
    service: "INVALID"
    status: "active"
  }) {
    id
  }
}
```

2. Past Date Appointment:
```graphql
mutation TestPastDate {
  createAppointment(input: {
    title: "Past Appointment",
    startTime: "2024-01-01T10:00:00Z",
    durationMinutes: 30,
    attendeeIds: ["paste-attendee-id-here"]
  }) {
    id
  }
}
```

3. Invalid Status Transition:
```graphql
mutation TestInvalidTransition {
  updateAppointment(id: "paste-appointment-id-here", input: {
    status: COMPLETED
  }) {
    id
    status
  }
}
```

## Headers for Authentication
```json
{
  "Authorization": "Bearer your-auth-token-here"
}
```

Remember to:
1. Replace placeholder UUIDs with actual IDs
2. Use valid authentication tokens
3. Ensure dates are in the future
4. Test both success and error cases
5. Verify returned data matches expectations
