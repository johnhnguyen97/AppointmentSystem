# Appointment System

A comprehensive appointment management system with a Node.js backend API and Python data processing service.

## Features

### Core Features
- [ ] User authentication and authorization
- [ ] Appointment scheduling and tracking
- [ ] Calendar view of appointments
- [ ] Email notifications
- [ ] User dashboard
- [ ] Admin panel

### Advanced Features
- [ ] Service history tracking
- [ ] Loyalty points system
- [ ] Client referral tracking
- [ ] Service package management

## Tech Stack

### Backend API (Node.js)
- Express.js
- MongoDB
- JWT Authentication
- Node.js v18+

### Data Processing Service (Python)
- Python 3.11+
- SQLAlchemy (Async)
- GraphQL
- PostgreSQL
- pytest for testing

## Project Structure
```
AppointmentSystem/
├── api/                   # Node.js API
│   ├── src/
│   │   ├── controllers/  # Request handlers
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   ├── utils/        # Helper functions
│   │   └── config/       # Configuration files
│   ├── docs/             # API documentation
│   └── tests/            # API test files
│
├── service/              # Python Service
│   ├── src/
│   │   ├── auth.py      # Authentication logic
│   │   ├── config.py    # Configuration settings
│   │   ├── database.py  # Database connection
│   │   ├── models.py    # SQLAlchemy models
│   │   └── schema.py    # GraphQL schema
│   └── tests/           # Python service tests
│
└── README.md            # Project documentation
```

## Getting Started

### Prerequisites
- Node.js v18+
- Python 3.11+
- MongoDB
- PostgreSQL
- npm (Node.js package manager)
- pip (Python package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/johnhnguyen97/AppointmentSystem.git
cd AppointmentSystem
```

2. Install Node.js API dependencies
```bash
cd api
npm install
```

3. Install Python service dependencies
```bash
cd ../service
pip install -r requirements.txt
pip install -r test-requirements.txt  # For development/testing
```

4. Set up environment variables
```bash
# In api directory
cp .env.example .env
# Edit .env with Node.js API configuration

# In service directory
cp .env.example .env
# Edit .env with Python service configuration
```

5. Start the development servers
```bash
# Terminal 1 - Node.js API
cd api
npm run dev

# Terminal 2 - Python Service
cd service
python -m src.server
```

## Database Schemas

### MongoDB Collections (API)
- users: User authentication and profile data
- appointments: Appointment scheduling and details
- notifications: Email and system notifications
- settings: System configuration and preferences

### PostgreSQL Tables (Service)
- users: Extended user information
- clients: Client profiles and preferences
- appointments: Detailed appointment records
- service_packages: Package deals and tracking
- service_history: Historical service records

## Testing

### API Tests
```bash
cd api
npm test
```

### Service Tests
```bash
cd service
pytest
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## TODO
- [ ] Set up initial project structure
- [ ] Implement user authentication
- [ ] Create appointment CRUD operations
- [ ] Add calendar view
- [ ] Implement email notifications
- [ ] Add admin functionality
- [ ] Write API documentation
- [ ] Add unit tests
- [ ] Set up CI/CD pipeline
- [ ] Implement service history tracking
- [ ] Add loyalty points system
- [ ] Create client referral system

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
