#!/bin/bash
# Discord AI Selfbot Startup Script

set -e

# Color codes for better logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

echo ""
echo -e "${BOLD}${MAGENTA}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${MAGENTA}║   Discord AI Selfbot - Startup Script    ║${NC}"
echo -e "${BOLD}${MAGENTA}╚════════════════════════════════════════════╝${NC}"
echo ""

log_step "Checking Python installation..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    log_info "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log_success "Python $PYTHON_VERSION found"

# Check if venv exists
log_step "Checking virtual environment..."
if [ ! -d "venv" ]; then
    log_info "Virtual environment not found, creating..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment found"
fi

# Activate venv
log_step "Activating virtual environment..."
source venv/bin/activate
log_success "Virtual environment activated"

# Detect OS and select appropriate requirements file
log_step "Detecting operating system..."
REQUIREMENTS_FILE="requirements.txt"
OS_TYPE=$(uname -s)

case "$OS_TYPE" in
    Linux*)     
        REQUIREMENTS_FILE="requirements.txt"
        log_info "Detected: Linux (using standard requirements)"
        ;;
    Darwin*)    
        REQUIREMENTS_FILE="requirements.txt"
        log_info "Detected: macOS (using standard requirements)"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        REQUIREMENTS_FILE="requirements-windows.txt"
        log_info "Detected: Windows (includes audioop-lts for Python 3.13+)"
        ;;
    *)
        log_warning "Unknown OS: $OS_TYPE, using default requirements.txt"
        ;;
esac

# Check if dependencies are installed
log_step "Checking dependencies..."
DEPS_HASH=$(md5sum "$REQUIREMENTS_FILE" 2>/dev/null || md5 "$REQUIREMENTS_FILE" | cut -d' ' -f1)
DEPS_FILE="venv/.installed_deps_${DEPS_HASH}"

if [ ! -f "$DEPS_FILE" ]; then
    log_info "Dependencies not up to date, installing from $REQUIREMENTS_FILE..."
    pip install -q -r "$REQUIREMENTS_FILE"
    if [ $? -eq 0 ]; then
        # Remove old dependency markers
        rm -f venv/.installed_deps_*
        touch "$DEPS_FILE"
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies"
        exit 1
    fi
else
    log_success "Dependencies are up to date (skipping installation)"
fi

# Check if .env exists
log_step "Checking configuration..."
if [ ! -f ".env" ]; then
    echo ""
    log_error ".env file not found!"
    echo ""
    log_info "Please create a .env file with your tokens:"
    echo "  1. Copy .env.example to .env"
    echo "     ${CYAN}\$ cp .env.example .env${NC}"
    echo ""
    echo "  2. Edit .env and add your tokens:"
    echo "     ${CYAN}\$ nano .env${NC}"
    echo ""
    log_info "See README.md for instructions on getting your tokens"
    exit 1
fi

log_success "Configuration file found"

# Start the selfbot
echo ""
echo -e "${BOLD}${MAGENTA}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${MAGENTA}║     Starting Discord AI Selfbot...       ║${NC}"
echo -e "${BOLD}${MAGENTA}╚════════════════════════════════════════════╝${NC}"
echo ""
log_info "Press ${BOLD}Ctrl+C${NC} to stop the selfbot"
echo ""

python3 discord_selfbot.py

# Capture exit code
EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -ne 0 ]; then
    log_error "Selfbot exited with error code $EXIT_CODE"
    exit $EXIT_CODE
else
    log_info "Selfbot shut down gracefully"
fi

