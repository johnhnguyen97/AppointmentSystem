# Appointment System

## Git Setup Instructions

1. Initialize Git repository:
```bash
git init
```

2. Add remote repository:
```bash
git remote add origin https://github.com/johnhnguyen97/AppointmentSystem.git
```

3. Configure Git credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

4. Initial commit and push:
```bash
git add .
git commit -m "Initial commit"
git push -f origin main
```

Note: We use `-f` flag for the first push to override the unrelated histories error.

## Project Structure

- `src/main/`: Core application code
  - `models.py`: Database models
  - `schema.py`: GraphQL schema definitions
  - `graphql_schema.py`: GraphQL resolvers
  - `server.py`: FastAPI server setup
  
- `migrations/`: Database migrations
- `src/test/`: Test files
