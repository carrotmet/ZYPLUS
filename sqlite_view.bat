@echo off
chcp 65001 >nul
echo ================================================================================
echo                    SQLite Database Viewer
echo ================================================================================
echo.

set DB_PATH=data\career_guidance.db

if not exist "%DB_PATH%" (
    echo [ERROR] Database not found: %DB_PATH%
    pause
    exit /b 1
)

echo Database: %DB_PATH%
echo.
echo Available commands:
echo   .tables              - List all tables
echo   .schema TABLE        - Show table schema
echo   SELECT * FROM TABLE; - Query table data
echo   .quit                - Exit
echo.

sqlite3 "%DB_PATH%"
