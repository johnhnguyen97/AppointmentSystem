# Bitwarden Integration for Credential Management

This document explains how Bitwarden is used for credential management in the Appointment System project.

## Overview

Instead of hardcoding sensitive values in the codebase, we use Bitwarden CLI to securely retrieve credentials and configuration values. This approach:

1. Enhances security by removing sensitive data from the codebase
2. Centralizes credential management
3. Makes it easier to update configuration values without code changes
4. Provides an audit trail for credential access

## Setup Requirements

To use the Bitwarden integration, you need:

1. Bitwarden CLI installed (`bw` command available in PATH)
2. Bitwarden account with API key access
3. Environment variables set:
   - `BW_CLIENTID`: Your Bitwarden API client ID
   - `BW_CLIENTSECRET`: Your Bitwarden API client secret

### Automated Setup

For convenience, we provide a PowerShell script that automates the setup process:

```powershell
./scripts/setup_bitwarden.ps1
```

This script will:
1. Check if Bitwarden CLI is installed
2. Guide you through setting up Bitwarden API keys as environment variables
3. Log in to your Bitwarden account
4. Create the necessary vault items with default values
5. Log out from Bitwarden

Running this script is the recommended way to set up Bitwarden for the project.

## Bitwarden Vault Structure

The system expects the following items in your Bitwarden vault:

### 1. Nail Appointment Database

Item name: `Nail Appointment Database`

This item should contain:
- Username and password in the standard login fields
- Custom fields:
  - `host`: Database hostname
  - `port`: Database port
  - `database`: Database name

### 2. Appointment System Configuration

Item name: `Appointment System Configuration`

This item should contain configuration values in the Notes section as a JSON object:

```json
{
  "business_hours": {
    "start": 9,
    "end": 19
  },
  "appointment": {
    "min_notice_hours": 2,
    "min_duration": 15,
    "max_duration": 480
  },
  "service_package": {
    "min_duration_days": 30,
    "max_sessions": 52,
    "discount_percentage": 20.0
  },
  "client_categories": {
    "premium_spend": 1000.0,
    "premium_visits": 20,
    "vip_spend": 500.0,
    "vip_visits": 10,
    "regular_visits": 3
  },
  "service_types": {
    "durations": {
      "Hair Cut": 30,
      "Manicure": 45,
      "Pedicure": 60,
      "Facial": 60,
      "Massage": 60,
      "Hair Color": 120,
      "Hair Style": 45,
      "Makeup": 60,
      "Waxing": 30,
      "Other": 30
    },
    "costs": {
      "Hair Cut": 30.0,
      "Manicure": 25.0,
      "Pedicure": 35.0,
      "Facial": 65.0,
      "Massage": 75.0,
      "Hair Color": 100.0,
      "Hair Style": 45.0,
      "Makeup": 55.0,
      "Waxing": 30.0,
      "Other": 40.0
    },
    "loyalty_points": {
      "Hair Cut": 10,
      "Manicure": 8,
      "Pedicure": 12,
      "Facial": 15,
      "Massage": 20,
      "Hair Color": 25,
      "Hair Style": 12,
      "Makeup": 15,
      "Waxing": 10,
      "Other": 10
    }
  }
}
```

## How It Works

1. The `src/utils/bitwarden.py` module provides utility functions to interact with Bitwarden CLI:
   - `get_bitwarden_credentials()`: Generic function to retrieve credentials from any Bitwarden item
   - `get_service_config()`: Retrieves configuration for a specific service
   - `get_database_credentials()`: Specifically retrieves database credentials

2. The `src/main/config.py` module:
   - Imports the Bitwarden utility functions
   - Attempts to load configuration values from Bitwarden during initialization
   - Falls back to default values if Bitwarden is not available or values are missing

3. The application code uses the `settings` object from `config.py` instead of hardcoded values

## Testing Bitwarden Integration

### Python Database Connection Test

You can test the database connection using the `src/test/db_connection_test.py` script, which:
1. Retrieves database credentials from Bitwarden
2. Constructs a database URL
3. Tests the connection to the database

Run the test with:

```bash
python -m src.test.db_connection_test
```

### PowerShell Integration Test

For a more comprehensive test of the Bitwarden integration, use the provided PowerShell script:

```powershell
./scripts/test_bitwarden_integration.ps1
```

This script will:
1. Check if Bitwarden CLI is installed
2. Log in to your Bitwarden account
3. Verify that the required vault items exist and have the correct structure
4. Validate that all required configuration sections are present
5. Display a summary of the retrieved credentials and configuration values

This test is useful for verifying that your Bitwarden setup is correctly configured for the Appointment System.

## Fallback Mechanism

If Bitwarden credentials cannot be retrieved (e.g., CLI not installed, API key not available), the system will:
1. Log a warning
2. Fall back to environment variables for critical settings like database connection
3. Use default values for non-critical settings

## Adding New Configuration Values

To add new configuration values:

1. Add the value to the Bitwarden `Appointment System Configuration` item in the appropriate section
2. Add a corresponding field in the `Settings` class in `src/main/config.py` with a default value
3. Update the `_load_from_bitwarden()` method to load the new value from Bitwarden

## Security Considerations

### Preventing Credential Leaks

- **NEVER commit API keys, passwords, or other credentials to the repository**
  - Use `.env` files for local development and ensure they are in `.gitignore`
  - Use environment variables in production environments
  - If you accidentally commit sensitive information, use the `scripts/cleanup_secrets.ps1` script to remove it from Git history

- **Avoid hardcoding sensitive values in code**
  - Even in configuration files, use environment variables or secure credential stores
  - Use placeholder values in example files (like `.env.example`)

- **Use the provided setup scripts**
  - The `setup_env.ps1` script helps create a secure `.env` file
  - The `scripts/setup_bitwarden.ps1` script configures Bitwarden integration safely

### Credential Management Best Practices

- Regularly rotate your Bitwarden API keys and database credentials
- Use the principle of least privilege when setting up API access
- Consider using a dedicated service account for API access in production
- Implement proper access controls for your Bitwarden vault
- Audit credential access regularly

### GitHub Push Protection

GitHub's push protection feature helps prevent accidental commits of secrets. If you encounter push protection errors:

1. Remove the sensitive information from your current files
2. Clean your Git history using the provided `scripts/cleanup_secrets.ps1` script
3. Force push to update the remote repository
4. If needed, use GitHub's UI to acknowledge any false positives

For more information, see [GitHub's documentation on push protection](https://docs.github.com/code-security/secret-scanning/working-with-push-protection-from-the-command-line).
