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
