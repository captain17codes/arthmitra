# ArthMitra - Local Docker Compose Deployment Script
# Automatically launches Docker Desktop if needed, builds and starts all containers, and verifies health.

Set-Location $PSScriptRoot

Write-Host "Working Directory: $PSScriptRoot" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       ArthMitra - Local Docker Compose Deployment        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Docker daemon responsiveness
Write-Host "[1/4] Checking Docker daemon status..." -ForegroundColor Yellow
$dockerReady = $false
try {
    $null = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
    }
} catch {
    $dockerReady = $false
}

if (-not $dockerReady) {
    Write-Host "Docker daemon is not running. Attempting to start Docker Desktop..." -ForegroundColor Yellow
    $dockerPath = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process -FilePath $dockerPath
        Write-Host "Docker Desktop launched. Waiting for the Linux engine to initialize..." -ForegroundColor Yellow
        
        $timeoutSeconds = 60
        $elapsed = 0
        while ($elapsed -lt $timeoutSeconds) {
            Start-Sleep -Seconds 3
            $elapsed += 3
            try {
                $null = docker ps 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $dockerReady = $true
                    break
                }
            } catch {}
            Write-Host "  ... waiting for Docker daemon ($elapsed/$timeoutSeconds s)" -ForegroundColor Gray
        }
    } else {
        Write-Host "Docker Desktop not found at default location ($dockerPath)." -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually from your Start Menu." -ForegroundColor Yellow
    }
}

if (-not $dockerReady) {
    Write-Host "Docker daemon is still not ready." -ForegroundColor Red
    Write-Host "Please open Docker Desktop from your Windows Start Menu, wait until the whale icon shows 'running', and re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker daemon is active and responsive!" -ForegroundColor Green

# 2. Build and start containers with docker compose
Write-Host ""
Write-Host "[2/4] Building and launching multi-container stack via docker-compose..." -ForegroundColor Yellow
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker compose failed to start containers. Check logs above." -ForegroundColor Red
    exit 1
}

# 3. Health check verification
Write-Host ""
Write-Host "[3/4] Verifying container health..." -ForegroundColor Yellow
$healthOk = $false
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        $resp = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($resp.status -eq "ok") {
            $healthOk = $true
            break
        }
    } catch {}
    Write-Host "  ... probing http://localhost:8000/health (attempt $i/15)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[4/4] Deployment Summary" -ForegroundColor Cyan
if ($healthOk) {
    Write-Host "SUCCESS: ArthMitra stack is UP and HEALTHY!" -ForegroundColor Green
} else {
    Write-Host "Containers started. Backend is completing initialization..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Access Services:" -ForegroundColor White
Write-Host "  PWA Frontend:     http://localhost:3000" -ForegroundColor Green
Write-Host "  FastAPI Backend:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Health Status:    http://localhost:8000/health" -ForegroundColor Green
Write-Host "  PostgreSQL 16:    localhost:5432" -ForegroundColor Gray
Write-Host "  Redis 7 Queue:    localhost:6379" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop the stack at any time: docker compose down" -ForegroundColor Gray
