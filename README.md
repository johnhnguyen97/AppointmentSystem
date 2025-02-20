# Appointment System

A GraphQL-based appointment scheduling system that manages users, clients, and appointments.

## Data Models

### User
- Base user model with authentication capabilities
- Has one-to-one relationship with Client profile
- Can create and attend appointments

### Client
- Represents a client profile associated with a user
- Contains service-specific information
- One-to-one relationship with User

### Appointment
- Manages scheduling information
- Has a creator (User) and multiple attendees (Users)
- Includes validation for time and duration

## GraphQL Schema

### Automated User-Client Creation

Two options are provided for creating users and clients with automatic UUID handling:

1. **GraphQL Queries** (auto_uuid_queries.graphql):
   - Sequential mutations that use UUIDs from previous responses
   - Single operation that creates both user and client
   - Verification queries to check the created records
   - Works with GraphQL clients that support automatic variable passing

2. **Python Script** (create_user_client.py):
   - Automated user and client creation
   - Handles UUID passing programmatically
   - Includes verification step
   - Requirements: `gql`, `aiohttp`

To use the Python script:
```bash
pip install gql aiohttp
python create_user_client.py
```

### Queries

#### Client Queries
```graphql
# Get all clients
query GetClients {
  clients {
    id
    phone
    service
    status
    notes
    user {
      id
      username
      email
      firstName
      lastName
    }
  }
}

# Get client by ID
query GetClient($id: Int!) {
  client(id: $id)
}

# Get clients by service
query GetClientsByService($service: String!) {
  clients(service: $service)
}
```

#### User Queries
```graphql
# Get user by ID (authenticated users can only view their own profile)
query GetUser($id: UUID!) {
  user(id: $id)
}
```

#### Appointment Queries
```graphql
# Get all appointments (for authenticated user)
query GetAppointments {
  appointments
}

# Get specific appointment
query GetAppointment($id: UUID!) {
  appointment(id: $id)
}
```

### Mutations

#### Client Mutations
```graphql
# Create new client profile
mutation CreateClient($userId: UUID!) {
  createClient(
    input: {
      userId: $userId
      phone: String!
      service: String!
      status: String!
      notes: String
    }
  )
}

# Update existing client
mutation UpdateClient($id: Int!) {
  updateClient(
    id: $id
    input: {
      phone: String
      service: String
      status: String
      notes: String
    }
  )
}
```

#### Appointment Mutations
```graphql
# Create new appointment
mutation CreateAppointment(
  $title: String!
  $description: String
  $startTime: DateTime!
  $durationMinutes: Int!
  $attendeeIds: [UUID!]!
) {
  createAppointment(
    title: $title
    description: $description
    startTime: $startTime
    durationMinutes: $durationMinutes
    attendeeIds: $attendeeIds
  )
}

# Update appointment
mutation UpdateAppointment(
  $id: UUID!
  $title: String
  $description: String
  $startTime: DateTime
  $durationMinutes: Int
  $status: AppointmentStatus
) {
  updateAppointment(
    id: $id
    title: $title
    description: $description
    startTime: $startTime
    durationMinutes: $durationMinutes
    status: $status
  )
}

# Delete appointment
mutation DeleteAppointment($id: UUID!) {
  deleteAppointment(id: $id)
}

# Update appointment attendance
mutation UpdateAppointmentAttendance($id: UUID!, $attendeeIds: [UUID!]!) {
  updateAppointmentAttendance(id: $id, attendeeIds: $attendeeIds)
}

# Update appointment status
mutation UpdateAppointmentStatus($id: UUID!, $status: AppointmentStatus!) {
  updateAppointmentStatus(id: $id, status: $status)
}
```

## Authentication

The system uses JWT-based authentication. To access protected endpoints:

1. Login using the login mutation to get a token
2. Include the token in the Authorization header for subsequent requests

```graphql
mutation Login($username: String!, $password: String!) {
  login(input: { username: $username, password: $password }) {
    token
    user {
      id
      username
      email
    }
  }
}
```

## Validation Rules

### Appointments
- Start time cannot be in the past
- Duration must be between 15 minutes and 8 hours
- Only creators can cancel appointments
- Only attendees can decline appointments

### Clients
- Must be associated with a valid user
- Phone number and service are required
- Status must be provided

## TODO

- [ ] Add email notifications for appointment changes
- [ ] Implement recurring appointments
- [ ] Add calendar integration
- [ ] Add service duration presets
- [ ] Implement waitlist functionality
- [ ] Add client notes history
- [ ] Add appointment reminders
- [ ] Implement service categories
- [ ] Add availability management
- [ ] Implement client preferences
