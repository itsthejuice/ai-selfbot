@echo off
REM Discord AI Selfbot Startup Script for Windows
setlocal EnableDelayedExpansion

REM ANSI color codes (requires Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "BOLD=[1m"
set "RESET=[0m"

echo.
echo %MAGENTA%%BOLD%================================================%RESET%
echo %MAGENTA%%BOLD%    Discord AI Selfbot - Startup Script         %RESET%
echo %MAGENTA%%BOLD%================================================%RESET%
echo.

echo %CYAN%[STEP]%RESET% Checking Python installation...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Python is not installed or not in PATH
    echo %GREEN%[INFO]%RESET% Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[SUCCESS]%RESET% Python %PYTHON_VERSION% found

echo.
echo %CYAN%[STEP]%RESET% Checking virtual environment...

REM Check if venv exists
if not exist "venv\" (
    echo %GREEN%[INFO]%RESET% Virtual environment not found, creating...
    python -m venv venv
    if errorlevel 1 (
        echo %RED%[ERROR]%RESET% Failed to create virtual environment
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%RESET% Virtual environment created
) else (
    echo %GREEN%[SUCCESS]%RESET% Virtual environment found
)

echo.
echo %CYAN%[STEP]%RESET% Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Failed to activate virtual environment
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%RESET% Virtual environment activated

echo.
echo %CYAN%[STEP]%RESET% Installing/checking dependencies...
echo %GREEN%[INFO]%RESET% Using requirements-windows.txt (includes audioop-lts for Python 3.13+)

pip install -q -r requirements-windows.txt
if errorlevel 1 (
    echo.
    echo %RED%[ERROR]%RESET% Failed to install dependencies!
    echo %GREEN%[INFO]%RESET% If you're using Python 3.13+, audioop-lts should install automatically
    echo %GREEN%[INFO]%RESET% If you're using Python ^<3.13, you may need to update Python
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%RESET% Dependencies installed successfully

echo.
echo %CYAN%[STEP]%RESET% Checking configuration...

REM Check if .env exists
if not exist ".env" (
    echo.
    echo %RED%[ERROR]%RESET% .env file not found!
    echo.
    echo %GREEN%[INFO]%RESET% Please create a .env file with your tokens:
    echo   1. Copy .env.example to .env
    echo.
    echo   2. Edit .env and add your tokens:
    echo      DISCORD_TOKEN=your_discord_token
    echo      BINX_TOKEN=your_binx_token
    echo.
    echo %GREEN%[INFO]%RESET% See README.md for instructions on getting your tokens
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%RESET% Configuration file found

REM Start the selfbot
echo.
echo %MAGENTA%%BOLD%================================================%RESET%
echo %MAGENTA%%BOLD%     Starting Discord AI Selfbot...             %RESET%
echo %MAGENTA%%BOLD%================================================%RESET%
echo.
echo %GREEN%[INFO]%RESET% Press %BOLD%Ctrl+C%RESET% to stop the selfbot
echo.

python discord_selfbot.py

REM Keep window open if there's an error
set EXIT_CODE=%errorlevel%
echo.
if %EXIT_CODE% neq 0 (
    echo %RED%[ERROR]%RESET% Selfbot exited with error code %EXIT_CODE%
    pause
    exit /b %EXIT_CODE%
) else (
    echo %GREEN%[INFO]%RESET% Selfbot shut down gracefully
)
