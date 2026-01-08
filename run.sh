#!/bin/bash

# YouTube Clipboard Downloader - Startup Script
# This script installs dependencies and runs the application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎬 YouTube Clipboard Downloader"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Sanal ortam oluşturuluyor..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import PyQt5" 2>/dev/null; then
    echo "📥 Bağımlılıklar yükleniyor..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Run the application
echo "🚀 Uygulama başlatılıyor..."
python main.py
