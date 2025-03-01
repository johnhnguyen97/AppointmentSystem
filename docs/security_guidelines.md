# Security Guidelines for Appointment System

This document provides guidelines for handling sensitive information in the Appointment System project, with a focus on preventing credential leaks and maintaining a secure codebase.

## Handling Sensitive Information

### What is Considered Sensitive Information?

- API keys and secrets
- Database credentials (usernames, passwords, connection strings)
- Authentication tokens
- Private encryption keys
- Personal data (PII)
- Environment-specific configuration that contains any of the above

### Never Commit Sensitive Information

The most important rule: **NEVER commit sensitive information to the Git repository**. This includes:

- Actual credentials in `.env` files
- Hardcoded credentials in source code
- Configuration files with real credentials
- Log files that might contain sensitive data
- Backup files of databases or configuration

## Using Environment Variables

### Local Development

For local development, use `.env` files to store environment-specific configuration:

1. Copy `.env.example` to `.env` using the provided setup script:
   ```powershell
   ./setup_env.ps1
   ```

2. Add your actual credentials to the `.env` file
3. Ensure `.env` is listed in `.gitignore` (it should be by default)
4. NEVER commit your `.env` file to the repository

### Production Environments

For production environments:

1. Use environment variables set at the system or container level
2. Consider using a secure secrets management service (like AWS Secrets Manager, HashiCorp Vault, etc.)
3. Rotate credentials regularly
4. Use the principle of least privilege for service accounts

## Using Bitwarden for Credential Management

This project uses Bitwarden as a secure credential store. See [Bitwarden Integration](bitwarden_integration.md) for detailed instructions.

Key benefits:
- Centralized credential management
- Secure storage with encryption
- Audit trail for credential access
- Easy credential rotation without code changes

## Cleanup Scripts

### If You Accidentally Commit Sensitive Information

If you accidentally commit sensitive information to the repository, use the provided cleanup scripts:

#### 1. Clean Git History

Use the `cleanup_secrets.ps1` script to remove sensitive files from Git history:

```powershell
./scripts/cleanup_secrets.ps1
```

This script will:
- Create a backup of your current repository state
- Remove specified files from Git history
- Guide you through updating the remote repository

#### 2. Sanitize Environment Files

Use the `sanitize_env.ps1` script to create safe versions of your environment files:

```powershell
./scripts/sanitize_env.ps1
```

This script will:
- Create a sanitized version of your `.env` file with placeholders
- Save it as `.env.example` (safe to commit)
- Check if `.env` is properly included in `.gitignore`

### GitHub Push Protection

GitHub's push protection feature helps prevent accidental commits of secrets. If you encounter push protection errors:

1. Remove the sensitive information from your current files
2. Clean your Git history using the provided `scripts/cleanup_secrets.ps1` script
3. Force push to update the remote repository
4. If needed, use GitHub's UI to acknowledge any false positives

For more information, see [GitHub's documentation on push protection](https://docs.github.com/code-security/secret-scanning/working-with-push-protection-from-the-command-line).

## Best Practices for Secure Development

### Code Reviews

- Always review code for hardcoded credentials before merging
- Use automated tools to scan for secrets in pull requests
- Implement a "no secrets" policy for all code reviews

### Secure Coding

- Use environment variables or secure credential stores instead of hardcoding
- Implement proper input validation to prevent injection attacks
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Use HTTPS for all external communications
- Validate and sanitize all user inputs

### Dependency Management

- Regularly update dependencies to patch security vulnerabilities
- Use tools like Dependabot to automate dependency updates
- Scan dependencies for known vulnerabilities

## Reporting Security Issues

If you discover a security vulnerability in this project:

1. **DO NOT** disclose it publicly in issues, discussions, or pull requests
2. Contact the project maintainers directly via email
3. Provide detailed information about the vulnerability and how to reproduce it
4. Allow time for the issue to be addressed before public disclosure

## Additional Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Bitwarden Security](https://bitwarden.com/help/security/)
