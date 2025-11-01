# StreamPulse Railway Deployment Script
# Deploys all backend services to Railway
# Run from project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   StreamPulse Railway Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
Write-Host "Checking Railway CLI..." -ForegroundColor Yellow
$railwayCLI = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayCLI) {
    Write-Host "❌ Railway CLI not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Railway CLI:" -ForegroundColor Yellow
    Write-Host "npm install -g @railway/cli" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Railway CLI installed" -ForegroundColor Green
Write-Host ""

# Login to Railway
Write-Host "Logging in to Railway..." -ForegroundColor Yellow
railway login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Railway login failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in to Railway" -ForegroundColor Green
Write-Host ""

# Ask user if they want to create new project or use existing
Write-Host "Do you want to:" -ForegroundColor Yellow
Write-Host "1. Create new Railway project" -ForegroundColor White
Write-Host "2. Use existing Railway project" -ForegroundColor White
$projectChoice = Read-Host "Enter choice (1 or 2)"

if ($projectChoice -eq "1") {
    Write-Host ""
    Write-Host "Creating new Railway project..." -ForegroundColor Yellow
    railway init
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Project creation failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Project created" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Linking to existing project..." -ForegroundColor Yellow
    railway link
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Project linking failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Project linked" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deploying Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to deploy a service
function Deploy-Service {
    param (
        [string]$ServiceName,
        [string]$ServicePath
    )
    
    Write-Host "Deploying $ServiceName..." -ForegroundColor Yellow
    Write-Host "Path: $ServicePath" -ForegroundColor Gray
    
    Push-Location $ServicePath
    
    railway up
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ $ServiceName deployment failed!" -ForegroundColor Red
        Pop-Location
        return $false
    }
    
    Write-Host "✅ $ServiceName deployed successfully" -ForegroundColor Green
    Write-Host ""
    
    Pop-Location
    return $true
}

# Deploy Event Generator
$success = Deploy-Service -ServiceName "Event Generator" -ServicePath "event-generator"
if (-not $success) { exit 1 }

# Deploy Flink Processor
$success = Deploy-Service -ServiceName "Flink Processor" -ServicePath "flink-processor"
if (-not $success) { exit 1 }

# Deploy Backend API
$success = Deploy-Service -ServiceName "Backend API" -ServicePath "backend"
if (-not $success) { exit 1 }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setting Environment Variables" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  IMPORTANT: Set environment variables in Railway dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "For Event Generator:" -ForegroundColor Cyan
Write-Host "  - KAFKA_BOOTSTRAP_SERVERS" -ForegroundColor White
Write-Host "  - KAFKA_USERNAME" -ForegroundColor White
Write-Host "  - KAFKA_PASSWORD" -ForegroundColor White
Write-Host "  - KAFKA_TOPIC=content-downloads" -ForegroundColor White
Write-Host ""

Write-Host "For Flink Processor:" -ForegroundColor Cyan
Write-Host "  - KAFKA_BOOTSTRAP_SERVERS" -ForegroundColor White
Write-Host "  - KAFKA_USERNAME" -ForegroundColor White
Write-Host "  - KAFKA_PASSWORD" -ForegroundColor White
Write-Host "  - PG_HOST" -ForegroundColor White
Write-Host "  - PG_DATABASE" -ForegroundColor White
Write-Host "  - PG_USER" -ForegroundColor White
Write-Host "  - PG_PASSWORD" -ForegroundColor White
Write-Host ""

Write-Host "For Backend API:" -ForegroundColor Cyan
Write-Host "  - PG_HOST" -ForegroundColor White
Write-Host "  - PG_DATABASE" -ForegroundColor White
Write-Host "  - PG_USER" -ForegroundColor White
Write-Host "  - PG_PASSWORD" -ForegroundColor White
Write-Host "  - ALLOWED_ORIGINS=https://your-frontend.vercel.app" -ForegroundColor White
Write-Host ""

Write-Host "Set variables at: https://railway.app/dashboard" -ForegroundColor Yellow
Write-Host ""

# Open Railway dashboard
$openDashboard = Read-Host "Open Railway dashboard in browser? (y/n)"
if ($openDashboard -eq "y") {
    Start-Process "https://railway.app/dashboard"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ All services deployed to Railway!" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Railway dashboard" -ForegroundColor White
Write-Host "2. Wait for services to restart (2-3 minutes)" -ForegroundColor White
Write-Host "3. Check logs to verify services are running" -ForegroundColor White
Write-Host "4. Get Backend API URL from Railway dashboard" -ForegroundColor White
Write-Host "5. Deploy frontend to Vercel (run deploy_vercel.ps1)" -ForegroundColor White
Write-Host ""

Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "railway logs" -ForegroundColor White
Write-Host ""

Write-Host "View service URLs:" -ForegroundColor Yellow
Write-Host "railway status" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Complete! 🚀" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan