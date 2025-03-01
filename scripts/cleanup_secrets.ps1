# Cleanup script to remove sensitive information from Git history
# This script helps remove secrets from the Git history to address GitHub push protection issues

Write-Host "Cleaning up sensitive information from Git history..." -ForegroundColor Cyan

# Function to check if Git is installed
function Test-GitInstalled {
    try {
        $null = git --version
        return $true
    }
    catch {
        return $false
    }
}

# Check if Git is installed
if (-not (Test-GitInstalled)) {
    Write-Host "Git is not installed or not in PATH. Please install Git and try again." -ForegroundColor Red
    exit 1
}

# Check if we're in a Git repository
if (-not (Test-Path ".git")) {
    Write-Host "This doesn't appear to be a Git repository. Please run this script from the root of your Git repository." -ForegroundColor Red
    exit 1
}

# Warn the user about the implications
Write-Host "`n⚠️  WARNING: This script will rewrite Git history!" -ForegroundColor Yellow
Write-Host "This is a destructive operation that will change commit hashes." -ForegroundColor Yellow
Write-Host "If you've already pushed this repository, you'll need to force push after running this script." -ForegroundColor Yellow
Write-Host "Anyone else working on this repository will need to re-clone or reset their local copy." -ForegroundColor Yellow
Write-Host "`nAre you sure you want to continue? (y/n)" -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne "y") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit
}

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "`nCurrent branch: $currentBranch" -ForegroundColor Cyan

# Create a backup branch
$backupBranch = "backup-before-cleanup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "Creating backup branch: $backupBranch" -ForegroundColor Cyan
git branch $backupBranch

# Identify files with sensitive information
Write-Host "`nIdentifying files with sensitive information..." -ForegroundColor Cyan

$filesToClean = @(
    ".env",
    "src/utils/bitwarden.py",
    "update_bitwarden.ps1",
    "update_bitwarden_fields.ps1",
    "update_bitwarden_item.json"
)

# Show files that will be cleaned
Write-Host "`nThe following files will be cleaned:" -ForegroundColor Cyan
foreach ($file in $filesToClean) {
    Write-Host "  - $file" -ForegroundColor White
}

Write-Host "`nDo you want to add more files to clean? (y/n)" -ForegroundColor Yellow
$addMore = Read-Host

if ($addMore -eq "y") {
    do {
        Write-Host "Enter the path of the file to clean (relative to repository root):" -ForegroundColor Cyan
        $additionalFile = Read-Host
        if ($additionalFile -and -not $filesToClean.Contains($additionalFile)) {
            $filesToClean += $additionalFile
        }
        Write-Host "Add another file? (y/n)" -ForegroundColor Yellow
        $addAnother = Read-Host
    } while ($addAnother -eq "y")
}

# Prepare BFG command if available, otherwise use git-filter-repo
$useBFG = $false
try {
    $null = java -jar bfg.jar --version
    $useBFG = $true
    Write-Host "`nBFG Repo-Cleaner found. Will use BFG for cleaning." -ForegroundColor Green
}
catch {
    Write-Host "`nBFG Repo-Cleaner not found. Will use git filter-repo instead." -ForegroundColor Yellow
    
    # Check if git-filter-repo is available
    try {
        $null = git filter-repo --version
        Write-Host "git-filter-repo found." -ForegroundColor Green
    }
    catch {
        Write-Host "git-filter-repo not found. Please install it with:" -ForegroundColor Red
        Write-Host "pip install git-filter-repo" -ForegroundColor Cyan
        Write-Host "`nAlternatively, you can download BFG Repo-Cleaner from:" -ForegroundColor Yellow
        Write-Host "https://rtyley.github.io/bfg-repo-cleaner/" -ForegroundColor Cyan
        exit 1
    }
}

# Confirm before proceeding
Write-Host "`nReady to clean the repository. This will rewrite Git history." -ForegroundColor Yellow
Write-Host "Are you sure you want to proceed? (y/n)" -ForegroundColor Yellow
$finalConfirm = Read-Host

if ($finalConfirm -ne "y") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit
}

# Clean the repository
Write-Host "`nCleaning repository..." -ForegroundColor Cyan

if ($useBFG) {
    # Using BFG Repo-Cleaner
    # First, we need to create a mirror of the repository
    Write-Host "Creating a mirror of the repository..." -ForegroundColor Cyan
    git clone --mirror . ../repo-mirror
    
    # Change to the mirror directory
    Set-Location ../repo-mirror
    
    # Run BFG to clean each file
    foreach ($file in $filesToClean) {
        Write-Host "Cleaning $file with BFG..." -ForegroundColor Cyan
        java -jar ../bfg.jar --delete-files $file
    }
    
    # Clean up the repository
    Write-Host "Running git reflog expire and git gc..." -ForegroundColor Cyan
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    
    # Return to the original repository
    Set-Location ..
    
    # Update the original repository from the mirror
    Write-Host "Updating original repository from mirror..." -ForegroundColor Cyan
    git remote add mirror ../repo-mirror
    git fetch mirror --all
    git reset --hard mirror/$currentBranch
    git remote remove mirror
    
    # Clean up
    Write-Host "Cleaning up..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force ../repo-mirror
}
else {
    # Using git filter-repo
    foreach ($file in $filesToClean) {
        Write-Host "Cleaning $file with git filter-repo..." -ForegroundColor Cyan
        git filter-repo --path $file --invert-paths
    }
}

# Final steps
Write-Host "`nRepository cleaned successfully!" -ForegroundColor Green
Write-Host "A backup of your original repository state was saved in the branch: $backupBranch" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Verify that the sensitive information has been removed" -ForegroundColor White
Write-Host "2. Force push to update the remote repository:" -ForegroundColor White
Write-Host "   git push -f origin $currentBranch" -ForegroundColor Cyan
Write-Host "3. If you're still having issues with GitHub push protection, you may need to:" -ForegroundColor White
Write-Host "   - Use the GitHub UI to acknowledge the secrets" -ForegroundColor White
Write-Host "   - Contact GitHub support if the secrets are no longer present but still being detected" -ForegroundColor White

Write-Host "`nIMPORTANT: Make sure your .gitignore file includes all files with sensitive information" -ForegroundColor Yellow
Write-Host "and that you're not committing any new secrets." -ForegroundColor Yellow
