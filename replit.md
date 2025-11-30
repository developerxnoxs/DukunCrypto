# Multi-Coin Technical Analysis Bot

## Overview
Bot Telegram untuk analisa teknikal cryptocurrency menggunakan AI Gemini Vision. Versi advanced mendukung 14 cryptocurrency populer dengan multiple timeframe.

## Recent Changes
- **Nov 2024**: Upgraded to advanced version with multi-coin support
- Added support for 14 cryptocurrencies: BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC
- Enhanced interactive keyboard navigation
- Added `/coins` command to view all supported coins with live prices
- Added timeframe options: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

## Project Architecture

### Main Files
- `btc_analyzer.py` - Main bot script with all functionality
- `pyproject.toml` - Python dependencies
- `README.md` - Documentation

### Key Components
1. **Data Fetching**: Uses KuCoin API for real-time candlestick data
2. **Chart Generation**: Uses mplfinance with EMA20/EMA50 indicators
3. **AI Analysis**: Uses Google Gemini Vision API for technical analysis
4. **Telegram Bot**: Interactive keyboard-based navigation

### Supported Coins
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC

### Timeframes
1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week

## Environment Variables Required
- `TELEGRAM_BOT_TOKEN` - Telegram Bot API token from @BotFather
- `GEMINI_API_KEY` - Google Gemini API key for AI analysis

## Running the Bot
The bot runs via the "BTC Analyzer Bot" workflow which executes:
```
python btc_analyzer.py
```

## User Preferences
- Language: Indonesian (Bahasa Indonesia)
- Output format: Structured technical analysis with trading signals
- Chart style: Candlestick with EMA indicators
