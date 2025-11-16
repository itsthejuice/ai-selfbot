#!/bin/bash
# Discord AI Selfbot Startup Script

set -e

echo "🤖 Discord AI Selfbot - Startup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
DEPS_HASH=$(md5sum requirements.txt | cut -d' ' -f1)
DEPS_FILE="venv/.installed_deps_${DEPS_HASH}"

if [ ! -f "$DEPS_FILE" ]; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
    # Remove old dependency markers
    rm -f venv/.installed_deps_*
    touch "$DEPS_FILE"
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed (skipping)"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found!"
    echo ""
    echo "Please create a .env file with your tokens:"
    echo "1. Copy .env.example to .env"
    echo "   $ cp .env.example .env"
    echo ""
    echo "2. Edit .env and add your tokens"
    echo "   $ nano .env"
    echo ""
    echo "See README.md for instructions on getting your tokens."
    exit 1
fi

# Start the selfbot
echo ""
echo "🚀 Starting Discord AI Selfbot..."
echo "Press Ctrl+C to stop"
echo ""

python3 discord_selfbot.py

