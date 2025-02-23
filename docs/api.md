# API Documentation

## Authentication

### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "role": "string"
  }
}
```

### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "name": "string"
}
```

## Appointments

### GET /api/appointments
Get all appointments for the logged-in user.

**Query Parameters:**
- start_date (optional): Filter appointments after this date
- end_date (optional): Filter appointments before this date
- status (optional): Filter by appointment status

### POST /api/appointments
Create a new appointment.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "start_time": "datetime",
  "end_time": "datetime",
  "attendees": ["string"],
  "location": "string"
}
```

### TODO Functions
- [ ] POST /api/appointments/{id}/cancel - Cancel an appointment
- [ ] PUT /api/appointments/{id} - Update appointment details
- [ ] GET /api/appointments/calendar - Get appointments in calendar format
- [ ] POST /api/appointments/{id}/remind - Send appointment reminder
- [ ] GET /api/appointments/statistics - Get appointment analytics
