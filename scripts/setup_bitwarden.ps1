# Setup Bitwarden for Appointment System
# This script helps set up Bitwarden for credential management in the Appointment System project

# Import common functions
. "$PSScriptRoot\common_functions.ps1"

# Create or update Bitwarden items
function Set-BitwardenItems {
    param (
        [string]$sessionKey
    )
    
    if (-not $sessionKey) {
        Write-Host "No session key provided. Cannot create Bitwarden items." -ForegroundColor Red
        return
    }
    
    # Set session environment variable
    $env:BW_SESSION = $sessionKey
    
    # Check if items already exist
    Write-Host "`nChecking for existing Bitwarden items..." -ForegroundColor Cyan
    
    # Database item
    $dbItemExists = $false
    try {
        $dbItem = bw get item "Nail Appointment Database" --session $sessionKey | ConvertFrom-Json
        if ($dbItem) {
            $dbItemExists = $true
            Write-Host "Database item already exists." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Database item does not exist. Will create it." -ForegroundColor Cyan
    }
    
    # Config item
    $configItemExists = $false
    try {
        $configItem = bw get item "Appointment System Configuration" --session $sessionKey | ConvertFrom-Json
        if ($configItem) {
            $configItemExists = $true
            Write-Host "Configuration item already exists." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Configuration item does not exist. Will create it." -ForegroundColor Cyan
    }
    
    # Create database item if it doesn't exist
    if (-not $dbItemExists) {
        Write-Host "`nCreating database item..." -ForegroundColor Cyan
        
        # Get database credentials from user
        $dbHost = Read-Host "Enter database host (default: localhost)"
        if (-not $dbHost) { $dbHost = "localhost" }
        
        $dbPort = Read-Host "Enter database port (default: 5432)"
        if (-not $dbPort) { $dbPort = "5432" }
        
        $dbName = Read-Host "Enter database name (default: appointment_system)"
        if (-not $dbName) { $dbName = "appointment_system" }
        
        $dbUser = Read-Host "Enter database username"
        $dbPassword = Read-Host "Enter database password" -AsSecureString
        $dbPasswordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
        )
        
        # Create item JSON
        $dbItemJson = @{
            name = "Nail Appointment Database"
            login = @{
                username = $dbUser
                password = $dbPasswordText
            }
            fields = @(
                @{
                    name = "host"
                    value = $dbHost
                    type = 0  # Text type
                },
                @{
                    name = "port"
                    value = $dbPort
                    type = 0
                },
                @{
                    name = "database"
                    value = $dbName
                    type = 0
                }
            )
            notes = "Database credentials for Appointment System"
        } | ConvertTo-Json -Depth 10
        
        # Create item in vault
        try {
            $encodedJson = [System.Text.Encoding]::UTF8.GetBytes($dbItemJson)
            $base64Json = [System.Convert]::ToBase64String($encodedJson)
            bw create item --session $sessionKey --raw $base64Json | Out-Null
            Write-Host "Database item created successfully." -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to create database item: $_" -ForegroundColor Red
        }
    }
    
    # Create configuration item if it doesn't exist
    if (-not $configItemExists) {
        Write-Host "`nCreating configuration item..." -ForegroundColor Cyan
        
        # Default configuration JSON
        $configJson = @{
            name = "Appointment System Configuration"
            notes = @"
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
"@
        } | ConvertTo-Json -Depth 10
        
        # Create item in vault
        try {
            $encodedJson = [System.Text.Encoding]::UTF8.GetBytes($configJson)
            $base64Json = [System.Convert]::ToBase64String($encodedJson)
            bw create item --session $sessionKey --raw $base64Json | Out-Null
            Write-Host "Configuration item created successfully." -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to create configuration item: $_" -ForegroundColor Red
        }
    }
    
    # Clear session
    $env:BW_SESSION = $null
}


# Main script
Write-Host "Appointment System - Bitwarden Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if Bitwarden CLI is installed
if (-not (Test-BWInstalled)) {
    exit 1
}

# Setup API key
Set-BitwardenApiKey

# Login to Bitwarden
$sessionKey = Login-Bitwarden
if (-not $sessionKey) {
    Write-Host "Failed to login to Bitwarden. Setup cannot continue." -ForegroundColor Red
    exit 1
}

# Create or update Bitwarden items
Set-BitwardenItems -sessionKey $sessionKey

# Logout
Write-Host "`nLogging out from Bitwarden..." -ForegroundColor Cyan
bw logout

Write-Host "`nBitwarden setup completed!" -ForegroundColor Green
Write-Host "You can now use Bitwarden for credential management in the Appointment System." -ForegroundColor Green
