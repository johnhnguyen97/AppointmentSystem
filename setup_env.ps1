# Setup environment variables for the Appointment System

Write-Host "Setting up environment variables for the Appointment System..." -ForegroundColor Cyan

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host ".env file already exists. Do you want to overwrite it? (y/n)" -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "y") {
        Write-Host "Setup cancelled. Existing .env file will not be modified." -ForegroundColor Yellow
        exit
    }
}

# Copy .env.example to .env if it exists
if (Test-Path ".env.example") {
    Copy-Item ".env.example" -Destination ".env" -Force
    Write-Host "Copied .env.example to .env" -ForegroundColor Green
} else {
    # Create .env file from scratch
    @"
# Database connection details
DB_HOST=nail-appointment-db-appointmentsystem.e.aivencloud.com
DB_PORT=23309
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=

# Bitwarden API credentials
BW_CLIENTID=
BW_CLIENTSECRET=
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Created new .env file" -ForegroundColor Green
}

# Prompt for database password
Write-Host "`nEnter your database password:" -ForegroundColor Cyan
$dbPassword = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
$dbPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

# Update .env file with database password
$envContent = Get-Content ".env" -Raw
$envContent = $envContent -replace "DB_PASSWORD=.*", "DB_PASSWORD=$dbPasswordPlain"
$envContent | Out-File -FilePath ".env" -Encoding utf8

# Prompt for Bitwarden API credentials
Write-Host "`nDo you want to set up Bitwarden API credentials? (y/n)" -ForegroundColor Cyan
$setupBitwarden = Read-Host
if ($setupBitwarden -eq "y") {
    Write-Host "`nEnter your Bitwarden Client ID:" -ForegroundColor Cyan
    $bwClientId = Read-Host
    
    Write-Host "Enter your Bitwarden Client Secret:" -ForegroundColor Cyan
    $bwClientSecret = Read-Host -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($bwClientSecret)
    $bwClientSecretPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    
    # Update .env file with Bitwarden API credentials
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "BW_CLIENTID=.*", "BW_CLIENTID=$bwClientId"
    $envContent = $envContent -replace "BW_CLIENTSECRET=.*", "BW_CLIENTSECRET=$bwClientSecretPlain"
    $envContent | Out-File -FilePath ".env" -Encoding utf8
}

Write-Host "`nEnvironment variables setup completed!" -ForegroundColor Green
Write-Host "You can now run the database connection test with:" -ForegroundColor Green
Write-Host "python -m src.test.db_connection_test" -ForegroundColor Cyan
