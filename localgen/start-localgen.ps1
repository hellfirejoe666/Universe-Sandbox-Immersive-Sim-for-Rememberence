# LocalGen Startup Script
# Starts LocalGen server in background for hybrid router

Write-Host "Starting LocalGen Server..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$workspace = "D:\Ollama\OpenClaw\workspace"
$localgenDir = Join-Path $workspace "localgen"
$serverScript = Join-Path $localgenDir "server.py"

# Check if server is already running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ LocalGen already running on http://localhost:5000" -ForegroundColor Green
    Write-Host ""
    $response.Content | ConvertFrom-Json | Format-List
    exit 0
} catch {
    # Server not running, start it
}

# Start LocalGen server
Write-Host "Starting LocalGen server..." -ForegroundColor Yellow
Start-Process python -ArgumentList $serverScript -WorkingDirectory $workspace -WindowStyle Hidden

# Wait for server to start
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verify it started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ LocalGen started successfully!" -ForegroundColor Green
    Write-Host ""
    $response.Content | ConvertFrom-Json | Format-List
    Write-Host ""
    Write-Host "Server will continue running in background." -ForegroundColor Cyan
    Write-Host "To stop: Find and kill the python process running server.py" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Failed to start LocalGen server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
