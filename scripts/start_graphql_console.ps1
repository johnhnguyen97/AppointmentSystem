# PowerShell script to start the GraphQL console

Write-Host "Appointment System - GraphQL Console" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if the server is running
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $serverRunning = $true
        Write-Host "Server is running!" -ForegroundColor Green
    }
}
catch {
    Write-Host "Server is not running! Starting the server..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\scripts\start_server.ps1"

    # Wait for the server to start
    Write-Host "Waiting for the server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Open the GraphQL console in the default browser
Write-Host "`nOpening GraphQL console in the default browser..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8000/graphql"

Write-Host "`nGraphQL console is now open in your browser!" -ForegroundColor Green
Write-Host "You can use the console to execute GraphQL queries and mutations." -ForegroundColor Green
Write-Host "Example query to get all clients:" -ForegroundColor Yellow
Write-Host @"
query {
  clients {
    id
    phone
    service
    status
    notes
    category
    loyalty_points
    total_spent
    visit_count
    last_visit
  }
}
"@ -ForegroundColor White
