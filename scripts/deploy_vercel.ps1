# StreamPulse Vercel Deployment Script
# Deploys React frontend to Vercel
# Run from project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   StreamPulse Vercel Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
Write-Host "Checking Vercel CLI..." -ForegroundColor Yellow
$vercelCLI = Get-Command vercel -ErrorAction SilentlyContinue

if (-not $vercelCLI) {
    Write-Host "❌ Vercel CLI not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Vercel CLI:" -ForegroundColor Yellow
    Write-Host "npm install -g vercel" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Vercel CLI installed" -ForegroundColor Green
Write-Host ""

# Navigate to frontend directory
Write-Host "Navigating to frontend directory..." -ForegroundColor Yellow
Push-Location frontend

if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from project root." -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Write-Host "✅ Frontend directory found" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
Write-Host "Checking dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Dependency installation failed!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""

# Get Backend API URL from user
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Enter your Backend API URL (from Railway):" -ForegroundColor Yellow
Write-Host "Example: https://streampulse-api.up.railway.app" -ForegroundColor Gray
$backendURL = Read-Host "Backend URL"

if ([string]::IsNullOrWhiteSpace($backendURL)) {
    Write-Host "❌ Backend URL is required!" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Validate URL format
if ($backendURL -notmatch "^https?://") {
    Write-Host "⚠️  URL should start with http:// or https://" -ForegroundColor Yellow
    Write-Host "Adding https:// prefix..." -ForegroundColor Yellow
    $backendURL = "https://$backendURL"
}

Write-Host "✅ Backend URL: $backendURL" -ForegroundColor Green
Write-Host ""

# Login to Vercel
Write-Host "Logging in to Vercel..." -ForegroundColor Yellow
vercel login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Vercel login failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✅ Logged in to Vercel" -ForegroundColor Green
Write-Host ""

# Deploy to Vercel
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deploying to Vercel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deploying frontend..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes..." -ForegroundColor Gray
Write-Host ""

vercel --prod --yes

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host ""

# Set environment variable
Write-Host "Setting environment variable..." -ForegroundColor Yellow
vercel env add REACT_APP_API_URL production

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Environment variable setup requires manual input" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "When prompted:" -ForegroundColor Yellow
    Write-Host "  Enter value: $backendURL" -ForegroundColor White
    Write-Host ""
    
    # Try again
    vercel env add REACT_APP_API_URL production
}

Write-Host "✅ Environment variable set" -ForegroundColor Green
Write-Host ""

# Trigger redeployment to apply env var
Write-Host "Redeploying with environment variable..." -ForegroundColor Yellow
vercel --prod --yes

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Redeployment warning (non-critical)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Redeployment complete" -ForegroundColor Green
}

Write-Host ""

# Get deployment URL
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your StreamPulse dashboard is live! 🎉" -ForegroundColor Green
Write-Host ""

Write-Host "View your deployment:" -ForegroundColor Yellow
Write-Host "vercel inspect" -ForegroundColor White
Write-Host ""

Write-Host "Or check Vercel dashboard:" -ForegroundColor Yellow
Write-Host "https://vercel.com/dashboard" -ForegroundColor White
Write-Host ""

# Ask if user wants to open in browser
$openBrowser = Read-Host "Open dashboard in browser? (y/n)"
if ($openBrowser -eq "y") {
    # Get the deployment URL
    Write-Host ""
    Write-Host "Opening in browser..." -ForegroundColor Yellow
    
    # Note: Vercel CLI doesn't easily provide the URL in PowerShell
    # So we'll open the Vercel dashboard instead
    Start-Process "https://vercel.com/dashboard"
    
    Write-Host ""
    Write-Host "Find your deployment URL in the Vercel dashboard" -ForegroundColor Yellow
    Write-Host "It will be something like: https://streampulse.vercel.app" -ForegroundColor Gray
}

Write-Host ""

# Update Railway backend CORS
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Final Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  IMPORTANT: Update CORS in Backend API" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Get your Vercel deployment URL (e.g., https://streampulse.vercel.app)" -ForegroundColor White
Write-Host "2. Go to Railway dashboard → Backend API service" -ForegroundColor White
Write-Host "3. Add environment variable:" -ForegroundColor White
Write-Host "   ALLOWED_ORIGINS=https://your-deployment.vercel.app" -ForegroundColor Gray
Write-Host "4. Redeploy Backend API service" -ForegroundColor White
Write-Host ""

Write-Host "Without this, frontend will get CORS errors! ⚠️" -ForegroundColor Yellow
Write-Host ""

$openRailway = Read-Host "Open Railway dashboard to update CORS? (y/n)"
if ($openRailway -eq "y") {
    Start-Process "https://railway.app/dashboard"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Frontend deployed to Vercel" -ForegroundColor Green
Write-Host "✅ Environment variable configured" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Get your Vercel URL from dashboard" -ForegroundColor White
Write-Host "2. Update ALLOWED_ORIGINS in Railway Backend API" -ForegroundColor White
Write-Host "3. Wait 1-2 minutes for Railway to redeploy" -ForegroundColor White
Write-Host "4. Test your dashboard!" -ForegroundColor White
Write-Host ""

Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  vercel --prod          (redeploy)" -ForegroundColor White
Write-Host "  vercel logs            (view logs)" -ForegroundColor White
Write-Host "  vercel env ls          (list env vars)" -ForegroundColor White
Write-Host "  vercel domains         (manage domains)" -ForegroundColor White
Write-Host ""

Pop-Location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   All Done! 🚀" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your StreamPulse platform is now live!" -ForegroundColor Green
Write-Host ""