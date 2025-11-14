@echo off
echo ========================================
echo   FaceStream - Starting Backend & Frontend
echo ========================================
echo.

echo [1/3] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m app.main"
timeout /t 3 /nobreak >nul

echo [2/3] Installing Frontend Dependencies...
cd frontend
if not exist node_modules (
    echo Installing npm packages...
    call npm install
) else (
    echo Dependencies already installed.
)

echo [3/3] Starting Frontend...
start "Frontend Dev Server" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul

