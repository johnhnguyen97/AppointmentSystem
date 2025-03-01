# Cleanup script to remove files with sensitive information

Write-Host "Removing files with sensitive information..." -ForegroundColor Cyan

# List of files to remove
$filesToRemove = @(
    "update_bitwarden_item.json",
    "update_bitwarden.ps1",
    "update_bitwarden_fields.ps1"
)

# Remove each file
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "Removed $file" -ForegroundColor Green
    } else {
        Write-Host "$file not found, skipping" -ForegroundColor Yellow
    }
}

Write-Host "Cleanup completed!" -ForegroundColor Green
