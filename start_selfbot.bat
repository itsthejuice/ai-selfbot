@echo off
REM Discord AI Selfbot Startup Script for Windows

echo.
echo ========================================
echo Discord AI Selfbot - Startup
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv\" (
    echo [Setup] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [Success] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [Info] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if dependencies need to be installed
set DEPS_FILE=venv\.deps_installed
set FORCE_INSTALL=0

if not exist "%DEPS_FILE%" set FORCE_INSTALL=1

REM Check if requirements.txt is newer than marker file
if exist "%DEPS_FILE%" (
    for %%i in (requirements.txt) do set REQ_TIME=%%~ti
    for %%i in (%DEPS_FILE%) do set MARKER_TIME=%%~ti
    REM Note: This is a simple check, not perfect but good enough
)

if %FORCE_INSTALL% equ 1 (
    echo [Setup] Installing dependencies...
    echo This may take a minute on first run...
    echo.
    pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies
        echo Try running: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo. > "%DEPS_FILE%"
    echo [Success] Dependencies installed
    echo.
) else (
    echo [Info] Dependencies already installed (skipping)
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ================================================
    echo [WARNING] .env file not found!
    echo ================================================
    echo.
    echo Please create a .env file with your tokens:
    echo.
    echo 1. Copy .env.example to .env
    echo    copy .env.example .env
    echo.
    echo 2. Edit .env and add your tokens
    echo    notepad .env
    echo.
    echo See README.md for instructions on getting your tokens.
    echo.
    pause
    exit /b 1
)

REM Start the selfbot
echo ================================================
echo Starting Discord AI Selfbot...
echo Press Ctrl+C to stop
echo ================================================
echo.

python discord_selfbot.py

REM If we get here, the script ended
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Selfbot exited with error code %errorlevel%
    pause
)

