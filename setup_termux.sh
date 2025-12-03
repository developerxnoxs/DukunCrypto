#!/bin/bash

echo "=========================================="
echo "  Bot Analisa Teknikal - Setup Termux"
echo "=========================================="
echo ""
echo "Script ini khusus untuk instalasi di Termux (Android)"
echo ""

if [ ! -d "/data/data/com.termux" ]; then
    echo "⚠️  Peringatan: Sepertinya ini bukan lingkungan Termux."
    echo "   Script ini dioptimalkan untuk Termux."
    read -p "Lanjutkan? (y/n): " choice
    if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
        echo "Dibatalkan."
        exit 1
    fi
fi

echo "1️⃣ Memperbarui paket Termux..."
pkg update -y && pkg upgrade -y

echo ""
echo "2️⃣ Menginstal dependensi sistem yang diperlukan..."
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
echo "5️⃣ Menginstal contourpy (memerlukan --no-build-isolation)..."
pip install --no-build-isolation contourpy

echo ""
echo "6️⃣ Menginstal matplotlib dari pkg Termux..."
pkg install -y matplotlib

echo ""
echo "7️⃣ Menginstal dependensi bot..."
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
echo "8️⃣ Menyiapkan file konfigurasi..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 File .env dibuat dari template."
else
    echo "📝 File .env sudah ada."
fi

echo ""
echo "=========================================="
echo "  ✅ Setup Termux Selesai!"
echo "=========================================="
echo ""
echo "Langkah selanjutnya:"
echo ""
echo "1. Edit file .env dengan API key Anda:"
echo "   nano .env"
echo ""
echo "2. Masukkan nilai berikut:"
echo "   TELEGRAM_BOT_TOKEN=token_dari_botfather"
echo "   GEMINI_API_KEY=api_key_dari_google"
echo ""
echo "3. Jalankan bot:"
echo "   python main.py"
echo ""
