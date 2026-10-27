# ArthMitra - Live Standalone Interactive Stack Launcher
# Initializes and seeds the SQLite demo database, starts the FastAPI backend (port 8000)
# and Vite PWA frontend (port 5173), and opens the application in your default browser.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       ArthMitra - Live Interactive Application           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Environment configuration
$dbPath = "$PSScriptRoot\backend\arthmitra.db"
$env:DATABASE_URL = "sqlite+aiosqlite:///$($dbPath.Replace('\', '/'))"
$env:DATABASE_URL_SYNC = "sqlite:///$($dbPath.Replace('\', '/'))"
$env:ENVIRONMENT = "development"
$env:DEBUG = "false"
$env:SECRET_KEY = "arthmitra-production-secret-key-32-chars-long"

Write-Host ""
Write-Host "[1/3] Initializing and seeding local database..." -ForegroundColor Yellow
& "C:\Users\gawan\anaconda3\python.exe" "$PSScriptRoot\backend\seed_demo.py"

# 3. Start Backend in Background Process
Write-Host ""
Write-Host "[2/3] Starting FastAPI backend on http://localhost:8000..." -ForegroundColor Yellow
$backendProc = Start-Process -FilePath "C:\Users\gawan\anaconda3\Scripts\uvicorn.exe" `
    -ArgumentList "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory "$PSScriptRoot\backend" `
    -PassThru

# Wait for backend health check
$backendReady = $false
for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($resp.status -eq "ok") {
            $backendReady = $true
            break
        }
    } catch {}
}

if ($backendReady) {
    Write-Host "Backend API is LIVE at http://localhost:8000!" -ForegroundColor Green
} else {
    Write-Host "Warning: Backend is still initializing..." -ForegroundColor Yellow
}

# 4. Start Frontend
Write-Host ""
Write-Host "[3/3] Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
$frontendProc = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "--prefix", "$PSScriptRoot\frontend", "run", "dev", "--", "--host" `
    -WorkingDirectory "$PSScriptRoot\frontend" `
    -PassThru

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ArthMitra is RUNNING & READY!                           " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "  PWA Interface:        http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Interactive API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Probe:         http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pre-seeded Demo Accounts:" -ForegroundColor White
Write-Host "  1. Field Agent (Bank Sakhi):   Phone: 9876543210  |  PIN: 1234" -ForegroundColor Yellow
Write-Host "  2. Field Agent (CSC VLE):      Phone: 9123456789  |  PIN: 5678" -ForegroundColor Yellow
Write-Host "  3. Supervisor (UMED District): Phone: 9999999999  |  PIN: 9999" -ForegroundColor Yellow
Write-Host "  4. Policy Administrator:       Phone: 9000000000  |  PIN: 1111" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening http://localhost:5173 in your default browser..." -ForegroundColor Gray
Start-Process "http://localhost:5173"
Write-Host "Press Ctrl+C in this console or close the window to stop services." -ForegroundColor Gray
