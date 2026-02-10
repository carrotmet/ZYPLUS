@echo off
chcp 65001 >nul
echo ================================================================================
echo                Career Planning Platform - Dev Environment Launcher
echo ================================================================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend

REM Check for virtual environment
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" (
    set PYTHON_CMD=%VENV_PYTHON%
    echo [INFO] Using virtual environment Python
) else (
    py --version >nul 2>&1
    if errorlevel 1 (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Python not found. Please install Python 3.9+
            pause
            exit /b 1
        ) else (
            set PYTHON_CMD=python
        )
    ) else (
        set PYTHON_CMD=py
    )
    echo [INFO] Using system Python
)

echo [INFO] Project directory: %SCRIPT_DIR%

if not exist "%BACKEND_DIR%\requirements.txt" (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%index.html" (
    echo [ERROR] index.html not found
    pause
    exit /b 1
)

REM Create directories if needed
if not exist "%SCRIPT_DIR%data" mkdir "%SCRIPT_DIR%data" >nul 2>&1
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs" >nul 2>&1

REM Check dependencies
echo [INFO] Checking backend dependencies...

"%PYTHON_CMD%" -c "import uvicorn" >nul 2>&1

if errorlevel 1 (
    echo [INFO] Installing dependencies first time...
    "%PYTHON_CMD%" -m pip install -r "%BACKEND_DIR%\requirements.txt" -q
    echo [INFO] Dependencies installed
) else (
    echo [INFO] Dependencies already installed
)

echo [INFO] Database will be initialized automatically

echo.
set API_KEY_OK=0
if not "%LAZYLLM_KIMI_API_KEY%"=="" set API_KEY_OK=1
if not "%LAZYLLM_DEEPSEEK_API_KEY%"=="" set API_KEY_OK=1
if not "%LAZYLLM_OPENAI_API_KEY%"=="" set API_KEY_OK=1

if "%API_KEY_OK%"=="0" (
    echo [WARNING] No LLM API Key configured - AI will use fallback
    timeout /t 2 /nobreak >nul
) else (
    echo [INFO] LLM API Key configured
)

echo.
echo ================================================================================
echo                          Select Startup Mode
echo ================================================================================
echo.
echo   [1] Start Full Dev Environment (Backend + Frontend)
echo   [2] Start Backend Only
echo   [3] Start Frontend Only
echo   [4] Run API Tests
echo   [0] Exit
echo.
echo ================================================================================

set /p choice=Enter option [0-4]:

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_FRONTEND
if "%choice%"=="4" goto RUN_TEST
if "%choice%"=="0" exit /b 0

echo [ERROR] Invalid option
pause
exit /b 1

:START_ALL
echo.
echo [INFO] Starting full dev environment...
echo [INFO] Starting Backend...
start "Career Platform - Backend" cmd /k "cd /d "%BACKEND_DIR%" && "%PYTHON_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul
echo [INFO] Starting Frontend...
start "Career Platform - Frontend" cmd /k "cd /d "%SCRIPT_DIR%" && "%PYTHON_CMD%" -m http.server 8001"
echo.
echo ================================================================================
echo                         Dev Environment Ready
echo ================================================================================
echo.
echo   Frontend: http://localhost:8001
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
exit /b 0

:START_BACKEND
echo.
echo [INFO] Starting backend...
echo [INFO] Server: http://localhost:8000
cd /d "%BACKEND_DIR%"
"%PYTHON_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
exit /b 0

:START_FRONTEND
echo.
echo [INFO] Starting frontend...
echo [INFO] Server: http://localhost:8001
cd /d "%SCRIPT_DIR%"
"%PYTHON_CMD%" -m http.server 8001
pause
exit /b 0

:RUN_TEST
echo.
echo [INFO] Running API tests...
timeout /t 2 /nobreak >nul
cd /d "%SCRIPT_DIR%"
"%PYTHON_CMD%" temp/test-api.py
pause
exit /b 0
