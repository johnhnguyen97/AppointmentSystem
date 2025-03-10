# AI Reference Instructions

Always refer to the file located at /doc/ai_custom_instructions.md for the latest updates regarding Git-related actions across different projects, repositories, and computers. Ensure you are using the most recent version of the file when performing any Git-related tasks, including branch creation, merging, and syncing.

# Table of Contents
- [Python Project Structure](#python-project-structure)
  - [GraphQL](#graphql)
  - [Utils](#utils)
  - [Tools](#tools)
  - [Testing](#testing)
- [Git Guidelines](#git-guidelines)
  - [Branch Management](#branch-management)
  - [Commits](#commits)
  - [Push and Merge](#push-and-merge)

# Python 

## Project Overview
```
appointmentsystem/
├── docs/               # Documentation
├── src/               # Source code
│   ├── main/         # Main application code
│   ├── test/         # Test files
│   └── utils/        # Utility functions
├── tools/            # Contains bws.exe
├── .env              # Environment configuration
├── requirements.txt  # Project dependencies
└── test-requirements.txt  # Test dependencies
```

## Prerequisites
- Python 3.12.x
- pip (Python package installer)
- Virtual environment tool (venv)

## Initial Setup
```bash
git clone [repository-url]
cd appointmentsystem
python -m venv venv

# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
pip install -r test-requirements.txt
```

## GraphQL
### Structure
- `src/main/graphql_context.py`: GraphQL context configuration
- `src/main/graphql_schema.py`: Schema definitions
- `src/main/schema.py`: Main schema implementation

### Environment Configuration
Create `.env` file in project root:
```dotenv
BWS_ACCESS_TOKEN=[your-bws-access-token]
PROJECT_ID=[your-project-id]
```

## Utils
### Database Utils
- Location: `src/utils/db_connection.py`
- Purpose: Handle database connection management
- Usage: Import for database operations

## Tools
### BWS Executable
- Download: https://github.com/bitwarden/sdk-sm/releases/download/bws-v1.0.0/bws-x86_64-pc-windows-msvc-1.0.0.zip
- Place in: `tools/bws.exe`
- Purpose: Bitwarden Secrets Manager integration

### Troubleshooting BWS
- Verify BWS_ACCESS_TOKEN in .env
- Ensure bws.exe is correctly placed in tools directory
- Confirm using correct BWS executable version
- Check network connectivity

## Testing
### Dependencies
```
pytest==8.0.0
pytest-asyncio==0.23.5
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-env==1.1.3
pytest-timeout==2.2.0
pytest-xdist==3.5.0
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest src/test/test_bws.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

# Git Guidelines

## Branch Management

### Branch Naming Conventions
- Feature branches: `feature/<descriptive-name>`
- Bug fix branches: `bugfix/<issue-description>`
- Hotfix branches: `hotfix/<issue-description>`
- Release branches: `release/<version>`

### Creating New Branches
```bash
git checkout main
git pull
git checkout -b <branch-name>
```

### Branch Synchronization
```bash
git checkout <your-branch>
git fetch origin
git merge origin/main
```

## Commits

### Message Format
Format: `<type>: <description>`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style updates
- refactor: Code refactoring
- test: Test updates
- chore: Build process or auxiliary tool changes

Examples:
- `feat: Add user authentication system`
- `fix: Resolve database connection timeout`
- `docs: Update API documentation`

### Best Practices
1. Make atomic commits (one logical change per commit)
2. Write clear, descriptive commit messages
3. Separate subject from body with a blank line
4. Use imperative mood in commit messages
5. Reference issue numbers when applicable

## Push and Merge

### Push Guidelines
1. Before pushing:
   ```bash
   git pull --rebase origin <your-branch>
   ```
2. Run tests if applicable
3. Push to remote:
   ```bash
   git push origin <your-branch>
   ```

### Merge Process
1. Ensure branch is up-to-date with main
2. Verify all tests pass
3. Resolve any conflicts
4. Use merge commit or rebase based on project preference
5. Delete branch after successful merge

### General Rules
1. Never force push to main
2. Keep commits clean and well-organized
3. Document significant changes
4. Back up work regularly
