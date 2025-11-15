# PowerShell script to create admin user via Railway CLI
# Prerequisites: railway login && railway link (run these first!)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Creating Admin User via Railway CLI" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
Write-Host "Step 1: Checking Railway CLI..." -ForegroundColor Yellow
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Railway CLI not found!" -ForegroundColor Red
    Write-Host "Please install Railway CLI first: npm install -g @railway/cli" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Railway CLI found: $railwayVersion" -ForegroundColor Green
Write-Host ""

# Check if logged in
Write-Host "Step 2: Checking Railway authentication..." -ForegroundColor Yellow
$whoami = railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not logged in to Railway!" -ForegroundColor Red
    Write-Host "Please run: railway login" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Logged in as: $whoami" -ForegroundColor Green
Write-Host ""

# Check if project is linked
Write-Host "Step 3: Checking Railway project link..." -ForegroundColor Yellow
$status = railway status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Project might not be linked" -ForegroundColor Yellow
    Write-Host "If this fails, run: railway link" -ForegroundColor Yellow
}
Write-Host ""

# Create admin user
Write-Host "Step 4: Creating admin user..." -ForegroundColor Yellow
Write-Host "Running: railway run python create_admin_simple.py" -ForegroundColor Cyan
Write-Host ""

railway run python create_admin_simple.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  ✅ SUCCESS: Admin user created!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Username: admin" -ForegroundColor Cyan
    Write-Host "Password: admin123" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now login at your frontend!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verify admin exists:" -ForegroundColor Yellow
    Write-Host "https://testrtcc-production.up.railway.app/debug/users" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "  ❌ ERROR: Failed to create admin user" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're logged in: railway login" -ForegroundColor White
    Write-Host "2. Make sure project is linked: railway link" -ForegroundColor White
    Write-Host "3. Check DATABASE_URL is set in Railway" -ForegroundColor White
    Write-Host "4. Check backend logs in Railway Dashboard" -ForegroundColor White
    exit 1
}

