@echo off
REM Discord AI Selfbot Startup Script for Windows

echo.
echo Discord AI Selfbot - Startup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing/updating dependencies...
pip install -q -r requirements-windows.txt
if errorlevel 1 (
    echo.
    echo Error installing dependencies!
    echo If you're using Python 3.13+, audioop-lts will be installed automatically.
    echo If you're using Python ^<3.13, you may need to update Python.
    pause
    exit /b 1
)
echo Dependencies installed successfully

REM Check if .env exists
if not exist ".env" (
    echo.
    echo Warning: .env file not found!
    echo.
    echo Please create a .env file with your tokens:
    echo 1. Copy .env.example to .env
    echo.
    echo 2. Edit .env and add your tokens:
    echo    DISCORD_TOKEN=your_discord_token
    echo    BINX_TOKEN=your_binx_token
    echo.
    echo See README.md for instructions on getting your tokens.
    pause
    exit /b 1
)

REM Start the selfbot
echo.
echo Starting Discord AI Selfbot...
echo Press Ctrl+C to stop
echo.

python discord_selfbot.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo [ERROR] Selfbot exited with error code %errorlevel%
    pause
)
