#!/bin/bash

MT5_PATH="${MT5_PATH:-/app/mt5/terminal64.exe}"
MT5_DATA_PATH="${MT5_DATA_PATH:-/root/.wine/drive_c/Program Files/MetaTrader 5}"

echo "MT5 Launcher - Checking for MetaTrader 5 terminal..."

if [ ! -f "$MT5_PATH" ]; then
    POSSIBLE_PATHS=(
        "/app/mt5/terminal64.exe"
        "/app/mt5/terminal.exe"
        "/opt/mt5/terminal64.exe"
        "/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
        "/root/.wine/drive_c/Program Files (x86)/MetaTrader 5/terminal64.exe"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -f "$path" ]; then
            MT5_PATH="$path"
            echo "Found MT5 at: $MT5_PATH"
            break
        fi
    done
fi

if [ ! -f "$MT5_PATH" ]; then
    echo "WARNING: MetaTrader 5 terminal not found!"
    echo "To enable MT5 trading, you need to:"
    echo "1. Mount your MT5 installation to /app/mt5 volume"
    echo "2. Or install MT5 manually inside the container"
    echo ""
    echo "The bot will run in analysis-only mode without MT5."
    echo "Sleeping indefinitely to keep supervisor happy..."
    sleep infinity
    exit 0
fi

echo "Starting MetaTrader 5 terminal..."
echo "Path: $MT5_PATH"

export DISPLAY=:99
export WINEDEBUG=-all

if command -v wine &> /dev/null; then
    echo "Using Wine to launch MT5..."
    wine "$MT5_PATH" /portable &
    MT5_PID=$!
    echo "MT5 started with PID: $MT5_PID"
    
    sleep 10
    
    if kill -0 $MT5_PID 2>/dev/null; then
        echo "MT5 terminal is running"
        wait $MT5_PID
    else
        echo "MT5 terminal failed to start"
        exit 1
    fi
else
    echo "ERROR: Wine is not installed!"
    echo "Cannot run MT5 without Wine."
    sleep infinity
    exit 0
fi
