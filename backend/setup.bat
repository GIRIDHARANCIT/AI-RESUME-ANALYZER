@echo off
REM Quick setup script for ATS Analyzer Database
echo ========================================
echo ATS Analyzer - Database Setup
echo ========================================
echo.

REM Check if in backend directory
if not exist requirements.txt (
    echo [ERROR] Please run this script from the backend directory
    echo Usage: cd backend && setup.bat
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed!
echo.
echo [2/3] Database will auto-initialize on first run...
echo.
echo [3/3] Ready to start!
echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo Start the backend server:
echo   uvicorn main:app --reload
echo.
echo Or on Windows:
echo   python -m uvicorn main:app --reload
echo.
echo The database will be created automatically at:
echo   backend/storage/ats_analyzer.db
echo.
echo Frontend setup:
echo   cd ../frontend
echo   npm install
echo   npm run dev
echo.
echo ========================================
pause
