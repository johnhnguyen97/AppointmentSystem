# Update Bitwarden item fields with database connection details

# Get session key
Write-Host "Enter your Bitwarden master password to unlock the vault:"
$sessionKey = bw unlock --raw

if (-not $sessionKey) {
    Write-Host "Failed to unlock Bitwarden. Update cannot continue." -ForegroundColor Red
    exit 1
}

# Set session environment variable
$env:BW_SESSION = $sessionKey

# Item ID
$itemId = "a790f790-dd4e-4478-be82-b29001633d79"

# Update username
Write-Host "Updating username..."
bw edit item-field $itemId username avnadmin

# Update password
Write-Host "Updating password..."
bw edit item-field $itemId password "AVNS_IouBYATtqgwj42TCq5l"

# Update custom fields
Write-Host "Updating host field..."
bw edit item-field $itemId "host" "nail-appointment-db-appointmentsystem.e.aivencloud.com" --field-type "text"

Write-Host "Updating port field..."
bw edit item-field $itemId "port" "23309" --field-type "text"

Write-Host "Updating database field..."
bw edit item-field $itemId "database" "defaultdb" --field-type "text"

# Update URI
Write-Host "Updating URI..."
bw edit item-uri $itemId 0 "postgres://avnadmin:AVNS_IouBYATtqgwj42TCq5l@nail-appointment-db-appointmentsystem.e.aivencloud.com:23309/defaultdb?sslmode=require"

# Clear session
$env:BW_SESSION = $null

Write-Host "Bitwarden item fields updated successfully!" -ForegroundColor Green
