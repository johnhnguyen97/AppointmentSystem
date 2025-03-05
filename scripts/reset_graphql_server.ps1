# PowerShell script to reset and restart the GraphQL server

# Import common functions
. "$PSScriptRoot\common_functions.ps1"

function Stop-GraphQLServer {
    param (
        [switch]$Force
    )

    Write-Host "Stopping GraphQL server..." -ForegroundColor Yellow

    # Find all GraphQL server processes
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_server.ps1*" }

    if ($processes.Count -eq 0) {
        Write-Host "No GraphQL server processes found." -ForegroundColor Green
        return
    }

    Write-Host "Found $($processes.Count) GraphQL server processes." -ForegroundColor Yellow

    foreach ($process in $processes) {
        if ($Force) {
            # Force kill the process
            $process | Stop-Process -Force
            Write-Host "Forcefully stopped process $($process.Id)" -ForegroundColor Red
        } else {
            # Try to gracefully stop the process
            $process | Stop-Process
            Write-Host "Gracefully stopped process $($process.Id)" -ForegroundColor Yellow
        }
    }

    # Wait for processes to stop
    Start-Sleep -Seconds 2

    # Check if processes are still running
    $remainingProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_server.ps1*" }

    if ($remainingProcesses.Count -gt 0) {
        Write-Host "Some processes are still running. Use -Force to forcefully stop them." -ForegroundColor Red
        return $false
    }

    Write-Host "All GraphQL server processes stopped." -ForegroundColor Green
    return $true
}

function Start-GraphQLServer {
    Write-Host "Starting GraphQL server..." -ForegroundColor Yellow

    # Start the server in a new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\scripts\start_server.ps1"

    # Wait for the server to start
    Write-Host "Waiting for the server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check if the server is running
    $serverRunning = $false
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverRunning = $true
            Write-Host "GraphQL server started successfully!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Failed to start GraphQL server." -ForegroundColor Red
        return $false
    }

    return $serverRunning
}

# Main script
Write-Host "Appointment System - GraphQL Server Reset" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if the server is running
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $serverRunning = $true
        Write-Host "GraphQL server is currently running." -ForegroundColor Green
    }
} catch {
    Write-Host "GraphQL server is not running." -ForegroundColor Yellow
}

# If the server is running, stop it
if ($serverRunning) {
    $stopped = Stop-GraphQLServer
    if (-not $stopped) {
        $forcefullyStop = Read-Host "Do you want to forcefully stop the server? (y/n)"
        if ($forcefullyStop -eq "y") {
            Stop-GraphQLServer -Force
        } else {
            Write-Host "Server reset aborted." -ForegroundColor Red
            exit 1
        }
    }
}

# Start the server
$started = Start-GraphQLServer
if (-not $started) {
    Write-Host "Failed to restart the GraphQL server." -ForegroundColor Red
    exit 1
}

# Open the GraphQL console
$openConsole = Read-Host "Do you want to open the GraphQL console in your browser? (y/n)"
if ($openConsole -eq "y") {
    Write-Host "Opening GraphQL console..." -ForegroundColor Cyan
    Start-Process "http://127.0.0.1:8000/graphql"
}

Write-Host "`nGraphQL server has been reset and restarted successfully!" -ForegroundColor Green
Write-Host "You can access the GraphQL console at: http://127.0.0.1:8000/graphql" -ForegroundColor Cyan
Write-Host "You can add a test client using: python .\scripts\add_test_client.py" -ForegroundColor Cyan
