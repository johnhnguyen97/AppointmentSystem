# AI Reference Instructions

Always refer to the file located at /doc/ai_custom_instructions.md for the latest updates regarding Git-related actions across different projects, repositories, and computers. Ensure you are using the most recent version of the file when performing any Git-related tasks, including branch creation, merging, and syncing.

# Table of **Contents**
- [AI Reference Instructions](#ai-reference-instructions)
- [Table of **Contents**](#table-of-contents)
- [Python](#python)
  - [Project Overview](#project-overview)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
  - [GraphQL](#graphql)
    - [Structure](#structure)
    - [Environment Configuration](#environment-configuration)
  - [Utils](#utils)
    - [Database Utils](#database-utils)
  - [Tools](#tools)
    - [BWS Executable](#bws-executable)
    - [Troubleshooting BWS](#troubleshooting-bws)
  - [Testing](#testing)
    - [Dependencies](#dependencies)
    - [Running Tests](#running-tests)
- [Angular](#angular)
  - [Project Overview](#project-overview-1)
    - [Authentication System Implementation Plan](#authentication-system-implementation-plan)
    - [Key Features](#key-features)
  - [Prerequisites](#prerequisites-1)
    - [Installing nvm for Windows](#installing-nvm-for-windows)
    - [Setting up Node.js with nvm](#setting-up-nodejs-with-nvm)
  - [Initial Setup](#initial-setup-1)
  - [SASS (Indented) Configuration](#sass-indented-configuration)
    - [Structure](#structure-1)
    - [Configuration in angular.json](#configuration-in-angularjson)
    - [SASS Best Practices](#sass-best-practices)
  - [TypeScript Guidelines](#typescript-guidelines)
    - [Structure](#structure-2)
    - [Best Practices](#best-practices)
  - [Testing](#testing-1)
    - [Unit Tests](#unit-tests)
    - [E2E Tests](#e2e-tests)
- [Git Guidelines](#git-guidelines)
  - [Branch Management](#branch-management)
    - [Branch Naming Conventions](#branch-naming-conventions)
    - [Creating New Branches](#creating-new-branches)
    - [Branch Synchronization](#branch-synchronization)
  - [Commits](#commits)
    - [Message Format](#message-format)
    - [Best Practices](#best-practices-1)
  - [Push and Merge](#push-and-merge)
    - [Push Guidelines](#push-guidelines)
    - [Merge Process](#merge-process)
    - [General Rules](#general-rules)

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

# Angular

## Project Overview

### Authentication System Implementation Plan
1. **Backend API Setup**
   - Create fake backend API for initial development
   - Plan for future migration to GraphQL API
   - Implement JWT-based authentication

2. **Frontend Implementation Steps**
   - Create Angular Environment File
   - Create User Model
   - Update TS Config File
   - Create Account Service
   - Import ReactiveFormsModule and HttpClientModule into App Module
   - Add Form Logic to Login Component
   - Add Form HTML to Login Component Template
   - Add Logout and Show/Hide Nav to App Component
   - Create Route Guard
   - Create JWT Interceptor
   - Create Error Interceptor
   - Add HTTP Interceptors to App Module

The project structure follows Angular Style Guide best practices with feature-based organization and lazy loading. Common code is prefixed with underscore (_) for easy differentiation.

```
src/
├── app/
│   ├── _components/       # Shared components
│   │   ├── alert.component.html
│   │   ├── alert.component.ts
│   │   └── index.ts      # Barrel file for easier imports
│   ├── _helpers/         # Auth guards, interceptors
│   │   ├── auth.guard.ts
│   │   ├── error.interceptor.ts
│   │   ├── jwt.interceptor.ts
│   │   └── index.ts
│   ├── _models/          # Shared interfaces/types
│   │   ├── alert.ts
│   │   ├── user.ts
│   │   └── index.ts
│   ├── _services/        # Shared services
│   │   ├── account.service.ts
│   │   ├── alert.service.ts
│   │   └── index.ts
│   ├── login/           # Authentication feature module
│   │   ├── components/
│   │   │   ├── login-form/
│   │   │   │   ├── login-form.component.html
│   │   │   │   ├── login-form.component.sass
│   │   │   │   └── login-form.component.ts
│   │   │   └── forgot-password/
│   │   │       ├── forgot-password.component.html
│   │   │       ├── forgot-password.component.sass
│   │   │       └── forgot-password.component.ts
│   │   ├── services/
│   │   │   ├── auth.service.ts
│   │   │   └── token.service.ts
│   │   ├── models/
│   │   │   ├── user-credentials.interface.ts
│   │   │   └── auth-response.interface.ts
│   │   ├── guards/
│   │   │   └── auth.guard.ts
│   │   ├── login-routing.module.ts
│   │   ├── login.module.ts
│   │   └── index.ts
│   ├── account/          # Account management feature module
│   │   ├── account-routing.module.ts
│   │   ├── account.module.ts
│   │   ├── components/
│   │   │   ├── profile/
│   │   │   │   ├── profile.component.html
│   │   │   │   ├── profile.component.sass
│   │   │   │   └── profile.component.ts
│   │   │   └── register/
│   │   │       ├── register.component.html
│   │   │       ├── register.component.sass
│   │   │       └── register.component.ts
│   │   └── index.ts
│   ├── home/            # Home feature module
│   │   ├── home.component.html
│   │   ├── home.component.ts
│   │   └── index.ts
│   ├── users/           # Users feature module
│   │   ├── add-edit.component.html
│   │   ├── add-edit.component.ts
│   │   ├── layout.component.html
│   │   ├── layout.component.ts
│   │   ├── list.component.html
│   │   ├── list.component.ts
│   │   ├── users-routing.module.ts
│   │   ├── users.module.ts
│   │   └── index.ts
│   ├── app-routing.module.ts
│   ├── app.component.html
│   ├── app.component.ts
│   └── app.module.ts
├── environments/
│   ├── environment.prod.ts
│   └── environment.ts
├── assets/              # Static assets
├── styles/             # Global styles
├── index.html
├── main.ts
├── polyfills.ts
└── styles.sass
```

### Key Features
1. **Feature Modules**: Each feature (account, home, users) is organized into self-contained modules with their own routing and components.
2. **Barrel Files**: `index.ts` files group exported modules for cleaner imports (e.g., `import { AccountService } from '@app/_services'`).
3. **TypeScript Path Aliases**: Configured in tsconfig.json:
   ```json
   {
     "compilerOptions": {
       "paths": {
         "@app/*": ["src/app/*"],
         "@environments/*": ["src/environments/*"]
       }
     }
   }
   ```
4. **Common Code Organization**: Shared code prefixed with underscore (_) for easy identification:
   - _components: Reusable UI components
   - _helpers: Guards, interceptors
   - _models: Interfaces and types
   - _services: Shared services
5. **Lazy Loading**: Feature modules are lazy loaded through the app routing module for better performance.

## Prerequisites
- nvm (Node Version Manager) for Windows
- VS Code Extensions:
  - Angular Language Service
  - Angular Snippets
  - SASS Formatter

### Installing nvm for Windows
1. Install using winget:
   ```bash
   winget install -e --id CoreyButler.NVMforWindows
   ```
2. Restart your terminal after installation
3. Verify installation:
   ```bash
   nvm version
   ```

### Setting up Node.js with nvm
```bash
# Install LTS version of Node.js
nvm install lts

# Use the installed version
nvm use lts

# Verify installation
node --version
npm --version
```

## Initial Setup
```bash
# Create new nvm environment for your project
nvm install lts
nvm use lts

# Install Angular CLI globally in this environment
npm install -g @angular/cli

# Create new project
ng new project-name --style=sass --routing=true

# Install dependencies
npm install

# Start development server (either method works)
ng serve
# OR using npx if ng command is not found
npx --yes @angular/cli serve
```

## SASS (Indented) Configuration
### Structure
```
src/
└── styles/
    ├── _variables.sass    # Global variables
    ├── _mixins.sass      # Reusable mixins
    ├── _functions.sass   # Custom functions
    └── styles.sass       # Main styles file
```

### Configuration in angular.json
```json
{
  "projects": {
    "your-project": {
      "architect": {
        "build": {
          "options": {
            "styles": [
              "src/styles/styles.sass"
            ],
            "stylePreprocessorOptions": {
              "includePaths": [
                "src/styles"
              ]
            }
          }
        }
      }
    }
  }
}
```

### SASS Best Practices
1. Use indented syntax (.sass) not SCSS
2. Follow BEM naming convention
3. Structure example:
```sass
// Component structure
.component-name
  &__element
    property: value

    &--modifier
      property: value
```

## TypeScript Guidelines
### Structure
```
src/app/
├── models/
│   └── interfaces/        # TypeScript interfaces
└── types/                # Custom types
```

### Best Practices
1. Use strict mode in tsconfig.json:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

2. Type definitions:
```typescript
// Use interfaces for objects
interface User {
  id: number
  name: string
  email?: string  // Optional property
}

// Use type for unions/intersections
type Status = 'active' | 'inactive'
```

3. Generics example:
```typescript
interface ApiResponse<T> {
  data: T
  status: number
}
```

## Testing
### Unit Tests
```bash
# Run all tests
ng test

# Run with coverage
ng test --code-coverage

# Run specific test file
ng test --include src/app/component-name
```

### E2E Tests
```bash
# Run all e2e tests
ng e2e

# Run specific e2e test
ng e2e --specs=src/e2e/feature-name.e2e-spec.ts
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
