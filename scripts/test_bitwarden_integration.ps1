# Test Bitwarden Integration for Appointment System
# This script tests that Bitwarden integration is working correctly

# Import common functions
. "$PSScriptRoot\common_functions.ps1"

# Test database credentials
function Test-DatabaseCredentials {
    param (
        [string]$sessionKey
    )
    
    Write-Host "`nTesting database credentials..." -ForegroundColor Cyan
    
    if (-not $sessionKey) {
        Write-Host "No session key provided. Cannot test database credentials." -ForegroundColor Red
        return $false
    }
    
    # Set session environment variable
    $env:BW_SESSION = $sessionKey
    
    try {
        # Get the database item
        $dbItem = bw get item "Nail Appointment Database" --session $sessionKey | ConvertFrom-Json
        
        if (-not $dbItem) {
            Write-Host "Database item not found in Bitwarden vault." -ForegroundColor Red
            Write-Host "Please run ./scripts/setup_bitwarden.ps1 to set up the required items." -ForegroundColor Yellow
            return $false
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
        
        # Construct connection string
        $connectionString = "Host=$dbHost;Port=$port;Database=$database;Username=$username;Password=$password"
        
        Write-Host "Successfully retrieved database credentials:" -ForegroundColor Green
        Write-Host "  Host: $dbHost" -ForegroundColor Green
        Write-Host "  Port: $port" -ForegroundColor Green
        Write-Host "  Database: $database" -ForegroundColor Green
        Write-Host "  Username: $username" -ForegroundColor Green
        Write-Host "  Password: ********" -ForegroundColor Green
        
        return $true
    }
    catch {
        Write-Host "Failed to retrieve database credentials: $_" -ForegroundColor Red
        return $false
    }
    finally {
        # Clear session
        $env:BW_SESSION = $null
    }
}

# Test configuration values
function Test-ConfigurationValues {
    param (
        [string]$sessionKey
    )
    
    Write-Host "`nTesting configuration values..." -ForegroundColor Cyan
    
    if (-not $sessionKey) {
        Write-Host "No session key provided. Cannot test configuration values." -ForegroundColor Red
        return $false
    }
    
    # Set session environment variable
    $env:BW_SESSION = $sessionKey
    
    try {
        # Get the configuration item
        $configItem = bw get item "Appointment System Configuration" --session $sessionKey | ConvertFrom-Json
        
        if (-not $configItem) {
            Write-Host "Configuration item not found in Bitwarden vault." -ForegroundColor Red
            Write-Host "Please run ./scripts/setup_bitwarden.ps1 to set up the required items." -ForegroundColor Yellow
            return $false
        }
        
        # Extract configuration from notes
        $notes = $configItem.notes
        
        if (-not $notes) {
            Write-Host "Configuration notes not found in Bitwarden item." -ForegroundColor Red
            return $false
        }
        
        try {
            # Parse JSON
            $config = $notes | ConvertFrom-Json
            
            # Check required sections
            $requiredSections = @("business_hours", "appointment", "service_package", "client_categories", "service_types")
            $missingSection = $false
            
            foreach ($section in $requiredSections) {
                if (-not $config.$section) {
                    Write-Host "Missing required section: $section" -ForegroundColor Red
                    $missingSection = $true
                }
            }
            
            if ($missingSection) {
                Write-Host "Configuration is incomplete. Please run ./scripts/setup_bitwarden.ps1 to set up the required items." -ForegroundColor Yellow
                return $false
            }
            
            Write-Host "Successfully retrieved configuration values:" -ForegroundColor Green
            Write-Host "  Business hours: $($config.business_hours.start) AM to $($config.business_hours.end - 12) PM" -ForegroundColor Green
            Write-Host "  Appointment min notice: $($config.appointment.min_notice_hours) hours" -ForegroundColor Green
            Write-Host "  Service package discount: $($config.service_package.discount_percentage)%" -ForegroundColor Green
            Write-Host "  Number of service types: $($config.service_types.durations.PSObject.Properties.Count)" -ForegroundColor Green
            
            return $true
        }
        catch {
            Write-Host "Failed to parse configuration JSON: $_" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Failed to retrieve configuration values: $_" -ForegroundColor Red
        return $false
    }
    finally {
        # Clear session
        $env:BW_SESSION = $null
    }
}

# Main script
Write-Host "Appointment System - Bitwarden Integration Test" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Bitwarden CLI is installed
if (-not (Test-BWInstalled)) {
    exit 1
}

# Login to Bitwarden
$sessionKey = Login-Bitwarden
if (-not $sessionKey) {
    Write-Host "Failed to login to Bitwarden. Test cannot continue." -ForegroundColor Red
    exit 1
}

# Test database credentials
$dbSuccess = Test-DatabaseCredentials -sessionKey $sessionKey
if (-not $dbSuccess) {
    Write-Host "Database credentials test failed." -ForegroundColor Red
}

# Test configuration values
$configSuccess = Test-ConfigurationValues -sessionKey $sessionKey
if (-not $configSuccess) {
    Write-Host "Configuration values test failed." -ForegroundColor Red
}

# Logout
Write-Host "`nLogging out from Bitwarden..." -ForegroundColor Cyan
bw logout

# Final result
if ($dbSuccess -and $configSuccess) {
    Write-Host "`nBitwarden integration test PASSED!" -ForegroundColor Green
    Write-Host "Your Bitwarden setup is correctly configured for the Appointment System." -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`nBitwarden integration test FAILED!" -ForegroundColor Red
    Write-Host "Please fix the issues above and run the test again." -ForegroundColor Red
    exit 1
}
