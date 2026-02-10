@echo off
chcp 65001 >nul
echo ================================================================================
echo            Career Planning Platform - Backend Service Startup Script
echo ================================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"

REM Remove trailing backslash if present
if "%BACKEND_DIR:~-1%"=="\" set "BACKEND_DIR=%BACKEND_DIR:~0,-1%"

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

echo [INFO] Backend directory: %BACKEND_DIR%

if not exist "%BACKEND_DIR%\requirements.txt" (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Create directories if needed
if not exist "%SCRIPT_DIR%data" (
    echo [INFO] Creating data directory...
    mkdir "%SCRIPT_DIR%data" >nul 2>&1
)

if not exist "%SCRIPT_DIR%logs" (
    echo [INFO] Creating logs directory...
    mkdir "%SCRIPT_DIR%logs" >nul 2>&1
)

echo.
echo ================================================================================
echo                          Starting Backend Service
echo ================================================================================
echo.
echo [INFO] Server: http://localhost:8000
echo [INFO] API Docs: http://localhost:8000/docs
echo [INFO] OpenAPI: http://localhost:8000/openapi.json
echo.
echo [HINT] Press Ctrl+C to stop service
echo ================================================================================
echo.

cd /d "%BACKEND_DIR%"
"%PYTHON_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
exit /b 0
