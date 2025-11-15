@echo off
REM Railway CLI script to create admin user
REM Run this after: railway login && railway link

echo ============================================================
echo   Creating Admin User via Railway CLI
echo ============================================================
echo.

echo Step 1: Checking Railway CLI...
railway --version
if %errorlevel% neq 0 (
    echo ERROR: Railway CLI not found!
    echo Please install Railway CLI first: npm install -g @railway/cli
    pause
    exit /b 1
)
echo.

echo Step 2: Checking if logged in...
railway whoami
if %errorlevel% neq 0 (
    echo ERROR: Not logged in to Railway!
    echo Please run: railway login
    pause
    exit /b 1
)
echo.

echo Step 3: Creating admin user...
railway run python create_admin_simple.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS: Admin user created!
    echo ============================================================
    echo.
    echo Username: admin
    echo Password: admin123
    echo.
    echo You can now login at your frontend!
) else (
    echo.
    echo ============================================================
    echo   ERROR: Failed to create admin user
    echo ============================================================
    echo.
    echo Check the error messages above for details.
)

pause

