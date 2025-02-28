# Common PowerShell functions for Appointment System scripts

# Check if Bitwarden CLI is installed
function Test-BWInstalled {
    try {
        $bwVersion = bw --version
        Write-Host "Bitwarden CLI version $bwVersion is installed." -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Bitwarden CLI is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Bitwarden CLI from https://bitwarden.com/help/cli/" -ForegroundColor Yellow
        return $false
    }
}

# Login to Bitwarden
function Login-Bitwarden {
    Write-Host "`nLogging in to Bitwarden..." -ForegroundColor Cyan
    
    # Check if API key is available
    $clientId = $env:BW_CLIENTID
    $clientSecret = $env:BW_CLIENTSECRET
    
    if ($clientId -and $clientSecret) {
        Write-Host "Using API key from environment variables..." -ForegroundColor Cyan
        try {
            $sessionKey = bw login --apikey --raw
            if ($sessionKey) {
                Write-Host "Successfully logged in with API key." -ForegroundColor Green
                return $sessionKey
            }
        }
        catch {
            Write-Host "Failed to login with API key: $_" -ForegroundColor Red
        }
    }
    
    # If API key login failed or not available, try interactive login
    Write-Host "Please login to your Bitwarden account:" -ForegroundColor Cyan
    try {
        $sessionKey = bw login --raw
        if ($sessionKey) {
            Write-Host "Successfully logged in." -ForegroundColor Green
            return $sessionKey
        }
    }
    catch {
        Write-Host "Failed to login: $_" -ForegroundColor Red
        return $null
    }
}

# Setup API key for environment
function Set-BitwardenApiKey {
    Write-Host "`nSetting up Bitwarden API key..." -ForegroundColor Cyan
    
    # Check if API key is already set
    if ($env:BW_CLIENTID -and $env:BW_CLIENTSECRET) {
        Write-Host "Bitwarden API key is already set in environment variables." -ForegroundColor Yellow
        $reset = Read-Host "Do you want to reset it? (y/n)"
        if ($reset -ne "y") {
            return
        }
    }
    
    # Guide user to create API key
    Write-Host "To use Bitwarden CLI with API key, you need to create an API key in your Bitwarden account." -ForegroundColor Cyan
    Write-Host "1. Go to https://vault.bitwarden.com/#/settings/account/security/keys" -ForegroundColor Cyan
    Write-Host "2. Click 'View API Key'" -ForegroundColor Cyan
    Write-Host "3. Copy the Client ID and Client Secret" -ForegroundColor Cyan
    
    $clientId = Read-Host "Enter your Bitwarden Client ID"
    $clientSecret = Read-Host "Enter your Bitwarden Client Secret"
    
    if ($clientId -and $clientSecret) {
        # Set environment variables for current session
        $env:BW_CLIENTID = $clientId
        $env:BW_CLIENTSECRET = $clientSecret
        
        # Add to user environment variables
        [System.Environment]::SetEnvironmentVariable("BW_CLIENTID", $clientId, "User")
        [System.Environment]::SetEnvironmentVariable("BW_CLIENTSECRET", $clientSecret, "User")
        
        Write-Host "Bitwarden API key has been set in environment variables." -ForegroundColor Green
        Write-Host "You can now use Bitwarden CLI with API key authentication." -ForegroundColor Green
    }
    else {
        Write-Host "API key setup was cancelled or incomplete." -ForegroundColor Yellow
    }
}

# Get database credentials from Bitwarden
function Get-DatabaseCredentials {
    param (
        [string]$sessionKey
    )
    
    if (-not $sessionKey) {
        Write-Host "No session key provided. Cannot get database credentials." -ForegroundColor Red
        return $null
    }
    
    # Set session environment variable
    $env:BW_SESSION = $sessionKey
    
    try {
        # Get the database item
        $dbItem = bw get item "Nail Appointment Database" --session $sessionKey | ConvertFrom-Json
        
        if (-not $dbItem) {
            Write-Host "Database item not found in Bitwarden vault." -ForegroundColor Red
            return $null
        }
        
        # Extract credentials
        $username = $dbItem.login.username
        $password = $dbItem.login.password
        
        # Extract custom fields
        $dbHost = "localhost"
        $port = "5432"
        $database = "appointment_system"
        
        foreach ($field in $dbItem.fields) {
            if ($field.name -eq "host") {
                $dbHost = $field.value
            }
            elseif ($field.name -eq "port") {
                $port = $field.value
            }
            elseif ($field.name -eq "database") {
                $database = $field.value
            }
        }
        
        # Create credentials object
        $credentials = @{
            Username = $username
            Password = $password
            Host = $dbHost
            Port = $port
            Database = $database
            ConnectionString = "Host=$dbHost;Port=$port;Database=$database;Username=$username;Password=$password"
        }
        
        return $credentials
    }
    catch {
        Write-Host "Failed to retrieve database credentials: $_" -ForegroundColor Red
        return $null
    }
    finally {
        # Clear session
        $env:BW_SESSION = $null
    }
}

# Get configuration values from Bitwarden
function Get-AppConfiguration {
    param (
        [string]$sessionKey
    )
    
    if (-not $sessionKey) {
        Write-Host "No session key provided. Cannot get configuration values." -ForegroundColor Red
        return $null
    }
    
    # Set session environment variable
    $env:BW_SESSION = $sessionKey
    
    try {
        # Get the configuration item
        $configItem = bw get item "Appointment System Configuration" --session $sessionKey | ConvertFrom-Json
        
        if (-not $configItem) {
            Write-Host "Configuration item not found in Bitwarden vault." -ForegroundColor Red
            return $null
        }
        
        # Extract configuration from notes
        $notes = $configItem.notes
        
        if (-not $notes) {
            Write-Host "Configuration notes not found in Bitwarden item." -ForegroundColor Red
            return $null
        }
        
        try {
            # Parse JSON
            $config = $notes | ConvertFrom-Json
            return $config
        }
        catch {
            Write-Host "Failed to parse configuration JSON: $_" -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-Host "Failed to retrieve configuration values: $_" -ForegroundColor Red
        return $null
    }
    finally {
        # Clear session
        $env:BW_SESSION = $null
    }
}

# Export functions
Export-ModuleMember -Function Test-BWInstalled, Login-Bitwarden, Set-BitwardenApiKey, Get-DatabaseCredentials, Get-AppConfiguration
