#!/bin/bash

echo "=============================================="
echo "  Fix yfinance untuk Termux"
echo "=============================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo "Langkah 1: Uninstall curl-cffi (tidak support Termux)..."
pip uninstall curl-cffi -y 2>/dev/null
print_status "curl-cffi removed (akan fallback ke requests)"

echo ""
echo "Langkah 2: Uninstall yfinance yang bermasalah..."
pip uninstall yfinance -y 2>/dev/null
pip uninstall pandas -y 2>/dev/null
print_status "Uninstalled old packages"

echo ""
echo "Langkah 2: Clear pip cache..."
pip cache purge 2>/dev/null
print_status "Cache cleared"

echo ""
echo "Langkah 3: Update pip dan setuptools..."
pip install --upgrade pip setuptools wheel
print_status "pip upgraded"

echo ""
echo "Langkah 4: Install dependencies yfinance satu per satu..."
echo "----------------------------------------------"

echo "Installing requests..."
pip install requests --no-cache-dir
print_status "requests installed"

echo "Installing lxml..."
pkg install libxml2 libxslt -y 2>/dev/null
pip install lxml --no-cache-dir
print_status "lxml installed"

echo "Installing beautifulsoup4..."
pip install beautifulsoup4 html5lib --no-cache-dir
print_status "beautifulsoup4 installed"

echo "Installing pandas (ini bisa lama)..."
pip install pandas --no-build-isolation --no-cache-dir
print_status "pandas installed"

echo ""
echo "Langkah 5: Install yfinance versi 0.2.40 (tanpa curl-cffi)..."
pip install yfinance==0.2.40 --no-cache-dir
print_status "yfinance 0.2.40 installed (compatible dengan Termux)"

echo ""
echo "Langkah 7: Verifikasi..."
echo "----------------------------------------------"
python -c "
try:
    import yfinance as yf
    print('yfinance version:', yf.__version__)
    
    # Test download data
    print('Testing download AAPL...')
    data = yf.download('AAPL', period='1d', progress=False)
    if not data.empty:
        print('Test berhasil! yfinance berfungsi dengan baik.')
    else:
        print('Warning: Data kosong, tapi import berhasil.')
except Exception as e:
    print(f'Error: {e}')
    print('')
    print('Coba solusi alternatif:')
    print('1. Restart Termux sepenuhnya')
    print('2. Jalankan: pkg install python-numpy')
    print('3. Jalankan script ini lagi')
"

echo ""
echo "=============================================="
echo "Jika masih error, coba:"
echo "1. Restart Termux (tutup dan buka lagi)"
echo "2. Jalankan: termux-change-repo (pilih mirror lain)"
echo "3. Jalankan script ini lagi"
echo "=============================================="
