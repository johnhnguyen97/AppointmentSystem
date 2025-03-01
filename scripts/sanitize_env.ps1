# Sanitize .env file to remove sensitive information
# This script creates a sanitized version of your .env file with placeholders instead of actual credentials

Write-Host "Sanitizing .env file..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Please run setup_env.ps1 first." -ForegroundColor Red
    exit 1
}

# Create sanitized version of .env file
Write-Host "Creating sanitized version of .env file..." -ForegroundColor Cyan

# Read the current .env file
$envContent = Get-Content ".env" -Raw

# Replace sensitive values with placeholders
$sanitizedContent = $envContent -replace "(DB_PASSWORD=).*", '$1your_db_password_here'
$sanitizedContent = $sanitizedContent -replace "(BW_CLIENTID=).*", '$1your_client_id_here'
$sanitizedContent = $sanitizedContent -replace "(BW_CLIENTSECRET=).*", '$1your_client_secret_here'

# Check if .env.example exists
if (Test-Path ".env.example") {
    Write-Host ".env.example already exists. Do you want to overwrite it? (y/n)" -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "y") {
        # Create a different file if not overwriting
        $sanitizedContent | Out-File -FilePath ".env.sanitized" -Encoding utf8
        Write-Host "Sanitized .env file saved as .env.sanitized" -ForegroundColor Green
        exit
    }
}

# Save sanitized content to .env.example
$sanitizedContent | Out-File -FilePath ".env.example" -Encoding utf8
Write-Host "Sanitized .env file saved as .env.example" -ForegroundColor Green

Write-Host "`nIMPORTANT: The .env.example file is safe to commit to the repository." -ForegroundColor Yellow
Write-Host "It contains placeholders instead of actual credentials." -ForegroundColor Yellow
Write-Host "Make sure your actual .env file is in .gitignore and never committed." -ForegroundColor Yellow

# Check if .env is in .gitignore
$gitignoreExists = Test-Path ".gitignore"
if ($gitignoreExists) {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -notmatch "\.env") {
        Write-Host "`nWARNING: .env is not in your .gitignore file!" -ForegroundColor Red
        Write-Host "Add the following line to your .gitignore file:" -ForegroundColor Yellow
        Write-Host ".env" -ForegroundColor Cyan
    } else {
        Write-Host "`n.env is properly included in .gitignore. Good!" -ForegroundColor Green
    }
}
