# AI Reference Instructions

For this project, any AI assistant (like Cline) must:

Always refer to the file located at C:/Users/jnguyen/Documents/Work/Projects/appointmentsystem/docs/ai_custom_instructions.md for the latest updates regarding Git-related actions. Ensure you are using the most recent version of the file when performing any actions related to Git, branch creation, merging, or syncing tasks.

Recent changes include:
1. Git workflow guidelines and best practices
2. Project setup and configuration procedures
3. Consolidated setup documentation
4. Machine-specific configuration requirements

# Git Workflow Instructions

## Branch Management

### Branch Naming Conventions
- Feature branches: `feature/<descriptive-name>`
- Bug fix branches: `bugfix/<issue-description>`
- Hotfix branches: `hotfix/<issue-description>`
- Release branches: `release/<version>`

### Creating New Branches
1. Always create new branches from up-to-date `main`:
```bash
git checkout main
git pull
git checkout -b <branch-name>
```

### Working with Branches
1. Keep branches focused on a single feature/fix
2. Regularly sync with main to avoid divergence:
```bash
git checkout <your-branch>
git fetch origin
git merge origin/main
```

## Commit Guidelines

### Commit Message Format
Format: `<type>: <description>`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style updates
- refactor: Code refactoring
- test: Test updates
- chore: Build process or auxiliary tool changes

Example commit messages:
- `feat: Add user authentication system`
- `fix: Resolve database connection timeout`
- `docs: Update API documentation`

### Commit Best Practices
1. Make atomic commits (one logical change per commit)
2. Write clear, descriptive commit messages
3. Separate subject from body with a blank line
4. Use imperative mood in commit messages
5. Reference issue numbers when applicable

## Push Guidelines
1. Before pushing:
   ```bash
   git pull --rebase origin <your-branch>
   ```
2. Run tests if applicable
3. Push to remote:
   ```bash
   git push origin <your-branch>
   ```

## Code Review Process
1. Keep changes focused and manageable
2. Respond to review comments promptly
3. Address all feedback before merging

## Merging Guidelines
1. Ensure branch is up-to-date with main
2. Verify all tests pass
3. Resolve any conflicts
4. Use merge commit or rebase based on project preference
5. Delete branch after successful merge

## General Rules
1. Never force push to main
2. Keep commits clean and well-organized
3. Document significant changes
4. Back up work regularly

# Project Setup and Configuration

## Prerequisites
- Python 3.12.x
- pip (Python package installer)
- Virtual environment tool (venv)

## Initial Setup Steps

1. **Clone and Basic Setup**
   ```bash
   git clone [repository-url]
   cd appointmentsystem
   ```

2. **BWS Executable Setup**
   - Download: https://github.com/bitwarden/sdk-sm/releases/download/bws-v1.0.0/bws-x86_64-pc-windows-msvc-1.0.0.zip
   - Extract to the `tools` directory in your project
   - Verify `tools/bws.exe` exists and has correct permissions
   > **Important**: Do not use the standard BWS installation. This project specifically requires the executable from the above link.

3. **Virtual Environment Setup**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Dependencies Installation**
   ```bash
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

## Environment Configuration

1. **Create .env file** in project root:
   ```dotenv
   BWS_ACCESS_TOKEN=[your-bws-access-token]
   PROJECT_ID=[your-project-id]
   ```
   - Keep tokens secure and never commit to version control
   - Required for BWS service authentication and project identification

2. **Machine-Specific Setup**
   - These steps must be performed on each new machine
   - Cline does not sync settings between devices
   - Create fresh virtual environment per machine
   - Verify all dependencies are installed correctly

## Testing

### Test Dependencies
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

## Project Structure
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

## Troubleshooting

### BWS Connection Issues
- Verify BWS_ACCESS_TOKEN in .env
- Ensure bws.exe is correctly placed in tools directory
- Confirm using correct BWS executable version
- Check network connectivity

### Environment Issues
- Double-check .env values
- Ensure virtual environment is active
- Verify Python version matches requirements
- Check for package version conflicts

### Best Practices
1. **Version Control**
   - Don't commit .env files
   - Keep BWS executable in tools directory
   - Document machine-specific configurations

2. **Security**
   - Keep access tokens secure
   - Don't share credentials between environments
   - Regularly rotate tokens if needed

3. **Maintenance**
   - Update documentation for changes
   - Track different machine setups
   - Document special configurations
