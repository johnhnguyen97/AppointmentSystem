# Update Bitwarden item with database connection details

# Read the JSON file
$jsonContent = Get-Content -Path "update_bitwarden_item.json" -Raw

# Convert to base64
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
$base64 = [System.Convert]::ToBase64String($bytes)

# Get session key
Write-Host "Enter your Bitwarden master password to unlock the vault:"
$sessionKey = bw unlock --raw

if (-not $sessionKey) {
    Write-Host "Failed to unlock Bitwarden. Update cannot continue." -ForegroundColor Red
    exit 1
}

# Set session environment variable
$env:BW_SESSION = $sessionKey

# Update the item
Write-Host "Updating Bitwarden item..."
bw edit item a790f790-dd4e-4478-be82-b29001633d79 $base64

# Clear session
$env:BW_SESSION = $null

Write-Host "Bitwarden item updated successfully!" -ForegroundColor Green
