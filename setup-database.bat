@echo off
chcp 437 >nul
echo ================================================================================
echo            Career Planning Platform - Database Setup Script
echo ================================================================================
echo.

REM Check Python installation
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python environment OK

REM Get current directory
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set DATA_DIR=%SCRIPT_DIR%data

echo [INFO] Project directory: %SCRIPT_DIR%
echo [INFO] Backend directory: %BACKEND_DIR%
echo [INFO] Data directory: %DATA_DIR%

REM Create data directory if not exists
if not exist "%DATA_DIR%" (
    echo [INFO] Creating data directory...
    mkdir "%DATA_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to create data directory. Please check permissions.
        pause
        exit /b 1
    )
)

REM Check if database file exists
if exist "%DATA_DIR%\career_guidance.db" (
    echo [WARNING] Database file already exists.
    set /p choice="Do you want to recreate it? All data will be lost! (y/n): "
    if not "%choice%"=="y" (
        echo [INFO] Setup cancelled.
        pause
        exit /b 0
    )
    echo [INFO] Deleting old database...
    del "%DATA_DIR%\career_guidance.db" >nul 2>&1
)

REM Install dependencies
echo [INFO] Checking dependencies...
cd /d "%BACKEND_DIR%"
pip install -r requirements.txt -q >nul 2>&1

echo.
echo [INFO] Creating database tables...
echo.

REM Run database setup using the dedicated Python script
py "%BACKEND_DIR%\app\setup_database.py"

if errorlevel 1 (
    echo [ERROR] Failed to create database tables.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                         Database Setup Complete
echo ================================================================================
echo.
echo [INFO] Database location: %DATA_DIR%\career_guidance.db
echo.
echo [NEXT STEPS]:
echo   1. Start backend service: py -m uvicorn app.main:app --reload
echo   2. Initialize sample data: POST /api/init-data
echo   3. Access API docs: http://localhost:8000/docs
echo.
echo [HINT] If tables already exist, use the existing database.
echo ================================================================================
echo.

pause
