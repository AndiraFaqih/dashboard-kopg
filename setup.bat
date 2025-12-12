@echo off
REM Dashboard Keuangan - Quick Setup Script for Windows
REM Run this script untuk quick setup semua dependencies

echo.
echo ============================================================
echo   Dashboard Keuangan Perbankan - kwd-dashboard Setup
echo ============================================================
echo.

REM Check Python
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Please install Python 3.8 or higher
    echo     Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [+] %PYTHON_VERSION% found
echo.

REM Check Node.js
echo [*] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [!] Node.js not found. Please install Node.js 16 or higher
    echo     Download from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [+] Node.js %NODE_VERSION% found
echo.

REM Install Python dependencies
echo [*] Installing Python dependencies...
python -m pip install --upgrade pip
pip install flask pandas openpyxl
echo [+] Python dependencies installed
echo.

REM Install Node dependencies
echo [*] Installing Node.js dependencies...
cd kwd-dashboard
call npm install
cd ..
echo [+] Node.js dependencies installed
echo.

REM Check data file
echo [*] Checking data file...
if exist "data\KINERJA PERBANKAN.xlsx" (
    echo [+] Data file found: data\KINERJA PERBANKAN.xlsx
) else (
    echo [!] Data file not found at: data\KINERJA PERBANKAN.xlsx
    echo     Please make sure the Excel file is placed in the data\ folder
)
echo.

echo ============================================================
echo   ✨ Setup Complete!
echo ============================================================
echo.
echo To start development:
echo.
echo Terminal 1 (Frontend - Vite):
echo   cd kwd-dashboard
echo   npm run dev
echo   Open: http://localhost:5173
echo.
echo Terminal 2 (Backend - Flask):
echo   python server.py
echo   Open: http://localhost:5000/keuangan
echo.
echo API Documentation:
echo   GET /api/data - Returns dashboard data
echo.
echo ============================================================
echo.
pause
