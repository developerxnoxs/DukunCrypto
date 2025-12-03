#!/usr/bin/env python3
"""
Bot Analisa Teknikal Trading - Setup Script (Cross-Platform)
Script ini mendeteksi lingkungan dan menjalankan instalasi yang sesuai.
"""

import os
import sys
import subprocess
import platform

def print_header():
    print("=" * 50)
    print("  Bot Analisa Teknikal Trading - Setup")
    print("=" * 50)
    print()

def detect_environment():
    if os.environ.get('REPL_ID'):
        return 'replit'
    elif os.path.exists('/data/data/com.termux'):
        return 'termux'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Darwin':
        return 'macos'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        return 'unknown'

def run_command(cmd, shell=True):
    print(f"Menjalankan: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def setup_termux():
    print("📱 Mengatur lingkungan Termux...")
    print()
    
    os.environ['CFLAGS'] = '-Wno-implicit-function-declaration'
    os.environ['MATHLIB'] = 'm'
    
    commands = [
        "pkg update -y && pkg upgrade -y",
        "pkg install -y python python-pip git",
        "pkg install -y ninja automake cmake binutils patchelf",
        "pip install --upgrade pip",
        "pip install meson",
        "pip install meson-python",
        "pip install pybind11",
        "pip install --no-build-isolation contourpy",
        "pkg install -y matplotlib",
    ]
    
    for cmd in commands:
        print()
        if not run_command(cmd):
            print(f"⚠️ Peringatan: Gagal menjalankan: {cmd}")
    
    install_requirements()

def setup_linux():
    print("🐧 Mengatur lingkungan Linux...")
    print()
    run_command("pip install --upgrade pip")
    install_requirements()

def setup_macos():
    print("🍎 Mengatur lingkungan macOS...")
    print()
    run_command("pip3 install --upgrade pip")
    install_requirements_pip3()

def setup_windows():
    print("🪟 Mengatur lingkungan Windows...")
    print()
    run_command("python -m pip install --upgrade pip")
    run_command("python -m pip install -r requirements.txt")

def setup_replit():
    print("💻 Mengatur lingkungan Replit...")
    print()
    print("Dependensi dikelola oleh Replit.")
    print("Pastikan Anda sudah mengatur secrets:")
    print("  - TELEGRAM_BOT_TOKEN")
    print("  - GEMINI_API_KEY")

def install_requirements():
    packages = [
        "python-telegram-bot>=21.0",
        "mplfinance>=0.12.10b0",
        "pandas>=2.2.0",
        "requests>=2.31.0",
        "pytz>=2024.1",
        "pillow>=10.0.0",
        "xnoxs-fetcher>=4.0.0",
        "yfinance>=0.2.40",
        "websocket-client>=1.7.0",
        "nest-asyncio>=1.6.0",
        "python-dotenv",
    ]
    
    print()
    print("Menginstal dependensi proyek...")
    for pkg in packages:
        run_command(f"pip install {pkg}")

def install_requirements_pip3():
    run_command("pip3 install -r requirements.txt")

def setup_env_file():
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print()
            print("📝 Membuat file .env dari template...")
            with open('.env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("⚠️  Silakan edit file .env dan masukkan API key Anda!")
    else:
        print()
        print("📝 File .env sudah ada.")

def main():
    print_header()
    
    env = detect_environment()
    print(f"Lingkungan terdeteksi: {env}")
    print()
    
    if env == 'termux':
        setup_termux()
        setup_env_file()
    elif env == 'linux':
        setup_linux()
        setup_env_file()
    elif env == 'macos':
        setup_macos()
        setup_env_file()
    elif env == 'windows':
        setup_windows()
        setup_env_file()
    elif env == 'replit':
        setup_replit()
    else:
        print("⚠️ Lingkungan tidak dikenal. Mencoba instalasi standar...")
        install_requirements()
        setup_env_file()
    
    print()
    print("=" * 50)
    print("  Setup Selesai!")
    print("=" * 50)
    print()
    print("Langkah selanjutnya:")
    print("1. Edit file .env dengan API key Anda")
    print("2. Jalankan bot: python main.py")
    print()

if __name__ == "__main__":
    main()
