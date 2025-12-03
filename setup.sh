#!/bin/bash

echo "=========================================="
echo "  Bot Analisa Teknikal Trading - Setup"
echo "=========================================="
echo ""

detect_environment() {
    if [ -n "$REPL_ID" ]; then
        echo "replit"
    elif [ -d "/data/data/com.termux" ]; then
        echo "termux"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

ENV=$(detect_environment)
echo "Lingkungan terdeteksi: $ENV"
echo ""

setup_termux() {
    echo "📱 Mengatur lingkungan Termux..."
    echo ""
    
    echo "1️⃣ Memperbarui paket Termux..."
    pkg update -y && pkg upgrade -y
    
    echo ""
    echo "2️⃣ Menginstal dependensi sistem..."
    pkg install -y python python-pip git
    pkg install -y ninja automake cmake binutils patchelf
    
    echo ""
    echo "3️⃣ Mengatur variabel environment untuk kompilasi..."
    export CFLAGS="-Wno-implicit-function-declaration"
    export MATHLIB="m"
    
    echo ""
    echo "4️⃣ Menginstal dependensi build Python..."
    pip install --upgrade pip
    pip install meson
    pip install meson-python
    pip install pybind11
    
    echo ""
    echo "5️⃣ Menginstal contourpy (tanpa build isolation)..."
    pip install --no-build-isolation contourpy
    
    echo ""
    echo "6️⃣ Menginstal matplotlib dari pkg..."
    pkg install -y matplotlib
    
    echo ""
    echo "7️⃣ Menginstal dependensi proyek..."
    pip install python-telegram-bot>=21.0
    pip install mplfinance>=0.12.10b0
    pip install pandas>=2.2.0
    pip install requests>=2.31.0
    pip install pytz>=2024.1
    pip install pillow>=10.0.0
    pip install xnoxs-fetcher>=4.0.0
    pip install yfinance>=0.2.40
    pip install websocket-client>=1.7.0
    pip install nest-asyncio>=1.6.0
    pip install python-dotenv
    
    echo ""
    echo "✅ Setup Termux selesai!"
}

setup_linux() {
    echo "🐧 Mengatur lingkungan Linux..."
    echo ""
    
    echo "1️⃣ Memperbarui pip..."
    pip install --upgrade pip
    
    echo ""
    echo "2️⃣ Menginstal dependensi proyek..."
    pip install -r requirements.txt
    
    echo ""
    echo "✅ Setup Linux selesai!"
}

setup_macos() {
    echo "🍎 Mengatur lingkungan macOS..."
    echo ""
    
    echo "1️⃣ Memperbarui pip..."
    pip3 install --upgrade pip
    
    echo ""
    echo "2️⃣ Menginstal dependensi proyek..."
    pip3 install -r requirements.txt
    
    echo ""
    echo "✅ Setup macOS selesai!"
}

setup_windows() {
    echo "🪟 Mengatur lingkungan Windows..."
    echo ""
    
    echo "1️⃣ Memperbarui pip..."
    python -m pip install --upgrade pip
    
    echo ""
    echo "2️⃣ Menginstal dependensi proyek..."
    python -m pip install -r requirements.txt
    
    echo ""
    echo "✅ Setup Windows selesai!"
}

setup_replit() {
    echo "💻 Mengatur lingkungan Replit..."
    echo ""
    
    echo "Dependensi sudah dikelola oleh Replit."
    echo "Pastikan Anda sudah mengatur secrets:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - GEMINI_API_KEY"
    
    echo ""
    echo "✅ Setup Replit selesai!"
}

setup_env_file() {
    if [ ! -f ".env" ]; then
        echo ""
        echo "📝 Membuat file .env dari template..."
        cp .env.example .env
        echo "⚠️  Silakan edit file .env dan masukkan API key Anda!"
    else
        echo ""
        echo "📝 File .env sudah ada."
    fi
}

case $ENV in
    "termux")
        setup_termux
        setup_env_file
        ;;
    "linux")
        setup_linux
        setup_env_file
        ;;
    "macos")
        setup_macos
        setup_env_file
        ;;
    "windows")
        setup_windows
        setup_env_file
        ;;
    "replit")
        setup_replit
        ;;
    *)
        echo "⚠️ Lingkungan tidak dikenal. Mencoba instalasi standar..."
        pip install -r requirements.txt
        setup_env_file
        ;;
esac

echo ""
echo "=========================================="
echo "  Setup Selesai!"
echo "=========================================="
echo ""
echo "Langkah selanjutnya:"
echo "1. Edit file .env dengan API key Anda"
echo "2. Jalankan bot: python main.py"
echo ""
