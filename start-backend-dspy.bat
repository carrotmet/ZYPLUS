@echo off
chcp 65001 >nul
echo ================================================================================
echo            Career Planning Platform - Backend with DSPy Support
echo ================================================================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"

REM Remove trailing backslash if present
if "%BACKEND_DIR:~-1%"=="\" set "BACKEND_DIR=%BACKEND_DIR:~0,-1%"

set "PYTHON_PATH=%SCRIPT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python virtual environment not found at: %PYTHON_PATH%
    echo [HINT] Please run: python -m venv .venv
    echo [HINT] Then install dependencies: .venv\Scripts\pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo [INFO] Using virtual environment: %PYTHON_PATH%

REM Check API Key configuration
set "API_KEY_CONFIGURED=false"
if not "%LAZYLLM_KIMI_API_KEY%"=="" set "API_KEY_CONFIGURED=true"
if not "%LAZYLLM_DEEPSEEK_API_KEY%"=="" set "API_KEY_CONFIGURED=true"
if not "%LAZYLLM_OPENAI_API_KEY%"=="" set "API_KEY_CONFIGURED=true"

if "%API_KEY_CONFIGURED%"=="false" (
    echo [WARNING] No LLM API Key configured!
    echo [WARNING] The AI chat will use fallback responses (not intelligent)
    echo.
    echo [HINT] To enable AI features, set one of these environment variables:
    echo         LAZYLLM_KIMI_API_KEY     (Get from https://platform.moonshot.cn/)
    echo         LAZYLLM_DEEPSEEK_API_KEY (Get from https://platform.deepseek.com/)
    echo         LAZYLLM_OPENAI_API_KEY   (For OpenAI/GPT)
    echo.
    timeout /t 3 /nobreak >nul
) else (
    echo [INFO] LLM API Key configured
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
echo.
echo [HINT] Press Ctrl+C to stop service
echo ================================================================================
echo.

cd /d "%BACKEND_DIR%"
"%PYTHON_PATH%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
exit /b 0
