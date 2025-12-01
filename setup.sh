#!/bin/bash

echo "=============================================="
echo "  BTC & XAU Analyzer Bot - Termux Setup"
echo "  Script untuk Android (Termux)"
echo "=============================================="
echo ""

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fungsi untuk print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Cek apakah running di Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "Script ini hanya untuk Termux!"
    print_warning "Download Termux dari F-Droid: https://f-droid.org/packages/com.termux/"
    exit 1
fi

echo "Langkah 1: Update & Upgrade Termux packages..."
echo "----------------------------------------------"
pkg update -y && pkg upgrade -y
print_status "Termux packages updated"

echo ""
echo "Langkah 2: Install system dependencies..."
echo "----------------------------------------------"
pkg install -y python git clang build-essential cmake ninja patchelf binutils-is-llvm
pkg install -y libopenblas libandroid-execinfo freetype libpng pkg-config libjpeg-turbo zlib
print_status "System dependencies installed"

echo ""
echo "Langkah 3: Upgrade pip dan install build tools..."
echo "----------------------------------------------"
pip install --upgrade pip
pip install setuptools setuptools-scm cython wheel packaging
print_status "Build tools installed"

echo ""
echo "Langkah 4: Install numpy (mungkin butuh waktu lama)..."
echo "----------------------------------------------"
print_warning "Proses ini bisa memakan waktu 5-15 menit..."
MATHLIB=m pip install --no-build-isolation --no-cache-dir numpy
print_status "NumPy installed"

echo ""
echo "Langkah 5: Install pandas..."
echo "----------------------------------------------"
pip install pandas
print_status "Pandas installed"

echo ""
echo "Langkah 6: Install matplotlib dan mplfinance..."
echo "----------------------------------------------"
pip install matplotlib
pip install mplfinance
print_status "Matplotlib & mplfinance installed"

echo ""
echo "Langkah 7: Install Pillow (image processing)..."
echo "----------------------------------------------"
LDFLAGS="-L/data/data/com.termux/files/usr/lib" \
CFLAGS="-I/data/data/com.termux/files/usr/include/" \
pip install pillow
print_status "Pillow installed"

echo ""
echo "Langkah 8: Install yfinance dengan dependencies..."
echo "----------------------------------------------"
print_warning "yfinance membutuhkan beberapa dependencies tambahan..."
pip install --upgrade requests urllib3 certifi
pip install lxml html5lib beautifulsoup4
pip install yfinance==0.2.40
print_status "yfinance 0.2.40 installed (versi compatible Termux)"

echo ""
echo "Langkah 9: Install sisa packages..."
echo "----------------------------------------------"
pip install python-telegram-bot pytz nest-asyncio
print_status "All Python packages installed"

echo ""
echo "Langkah 10: Verifikasi instalasi yfinance..."
echo "----------------------------------------------"
python -c "import yfinance as yf; print('yfinance version:', yf.__version__)" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "yfinance berhasil diinstall dan dapat diimport"
else
    print_error "yfinance gagal diimport, coba langkah berikut:"
    echo "  1. pip install --upgrade pip setuptools wheel"
    echo "  2. pip uninstall yfinance -y"
    echo "  3. pip install yfinance --no-cache-dir"
fi

echo ""
echo "=============================================="
echo "  INSTALASI SELESAI!"
echo "=============================================="
echo ""
print_status "Semua dependencies berhasil diinstall"
echo ""
echo "Langkah selanjutnya:"
echo "1. Set environment variables:"
echo "   export TELEGRAM_BOT_TOKEN='your_btc_bot_token'"
echo "   export TELEGRAM_BOT_TOKEN_XAU='your_xau_bot_token'"
echo "   export GEMINI_API_KEY='your_gemini_api_key'"
echo ""
echo "2. Jalankan bot:"
echo "   - BTC Analyzer: python btc_analyzer.py"
echo "   - XAU Analyzer: python xau_analyzer.py"
echo ""
echo "3. Untuk menjalankan di background:"
echo "   nohup python btc_analyzer.py > btc_log.txt 2>&1 &"
echo "   nohup python xau_analyzer.py > xau_log.txt 2>&1 &"
echo ""
print_warning "Pastikan Termux tidak di-kill oleh Android!"
print_warning "Aktifkan 'Acquire Wakelock' di notifikasi Termux"
echo ""
