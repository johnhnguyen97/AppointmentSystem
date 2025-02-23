# Appointment System

A system for managing appointments and scheduling.

## Features
- [ ] User authentication and authorization
- [ ] Create, read, update, delete appointments
- [ ] Calendar view of appointments
- [ ] Email notifications
- [ ] User dashboard
- [ ] Admin panel

## Project Structure
```
AppointmentSystem/
├── src/                    # Source code
│   ├── controllers/        # Request handlers
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Helper functions
│   └── config/            # Configuration files
├── docs/                  # Documentation
├── tests/                 # Test files
└── README.md             # Project documentation
```

## Getting Started

### Prerequisites
- Node.js v18+
- MongoDB

### Installation
1. Clone the repository
```bash
git clone https://github.com/johnhnguyen97/AppointmentSystem.git
cd AppointmentSystem
```

2. Install dependencies
```bash
npm install
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server
```bash
npm run dev
```

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

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
