# Appointment System

A robust appointment management system built with FastAPI, SQLAlchemy, and Pydantic.

## Features

- User Management
  - User creation and authentication
  - JWT-based authentication
  - Password hashing and validation
  - User profile updates

- Appointment Management
  - Create, read, update, and delete appointments
  - Multiple attendee support
  - Duration and time slot validation
  - Appointment status tracking (scheduled, confirmed, cancelled, completed)
  - Automatic future date validation for appointments

## Technical Details

### Database Models

- **User Model**
  - UUID-based identification
  - Username and email (unique constraints)
  - Secure password storage
  - Account status tracking
  - Timestamps for creation and updates

- **Appointment Model**
  - UUID-based identification
  - Title and description
  - Start time and duration validation
  - Many-to-many relationship with users (creator and attendees)
  - Status tracking with enum values
  - Automatic timestamps

### Data Validation

- Pydantic v2 schemas for request/response validation
- Custom validators for:
  - Future date appointments
  - Duration constraints (15 minutes to 8 hours)
  - Required attendees
  - Title length requirements

### Testing

Comprehensive test suite covering:
- User operations
- Appointment creation and updates
- Attendee management
- Cascade deletion behavior
- Database constraints

## Environment Configuration

Required environment variables:
```
DATABASE_URL=your_database_url
TEST_DATABASE_URL=your_test_database_url
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Development

1. Set up your virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your .env file with the required configuration

4. Run tests:
```bash
python -m pytest
