@echo off
chcp 65001 >nul
echo ================================================================================
echo            Career Planning Platform - Frontend Service Startup Script
echo ================================================================================
echo.

set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check for virtual environment first
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    set "PYTHON_CMD=%VENV_PYTHON%"
    echo [INFO] Using virtual environment Python
) else (
    REM Check Python installation (try py first, then python)
    py --version >nul 2>&1
    if errorlevel 1 (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Python not found. Please install Python 3.9+
            echo [HINT] Or create virtual environment: python -m venv .venv
            echo Download: https://www.python.org/downloads/
            pause
            exit /b 1
        ) else (
            set PYTHON_CMD=python
        )
    ) else (
        set PYTHON_CMD=py
    )
    echo [INFO] Using system Python: %PYTHON_CMD%
)

echo [INFO] Project directory: %SCRIPT_DIR%

if not exist "%SCRIPT_DIR%index.html" (
    echo [ERROR] index.html not found
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                          Starting Frontend Service
echo ================================================================================
echo.
echo [INFO] Server: http://localhost:8001
echo [INFO] Home: http://localhost:8001/index.html
echo [INFO] Major Detail: http://localhost:8001/major-detail.html
echo [INFO] Add Info: http://localhost:8001/add-info.html
echo [INFO] Experience: http://localhost:8001/experience-sharing.html
echo.
echo [HINT] 1. Make sure backend service is running (http://localhost:8000)
echo [HINT] 2. Press Ctrl+C to stop service
echo ================================================================================
echo.

cd /d "%SCRIPT_DIR%"
"%PYTHON_CMD%" -m http.server 8001

pause
exit /b 0
