# Multi-Coin & XAUUSD Technical Analysis Bot

## Overview
Bot Telegram untuk analisa teknikal cryptocurrency dan Gold (XAUUSD) menggunakan AI Gemini Vision. Terdiri dari 2 bot terpisah:
1. **Multi-Coin Bot** - Mendukung 14 cryptocurrency populer
2. **XAUUSD Bot** - Khusus untuk analisa Gold/Emas

## Recent Changes
- **Nov 2024**: Added XAUUSD (Gold) analyzer bot with API Ninjas integration
- **Nov 2024**: Upgraded to advanced version with multi-coin support
- Added support for 14 cryptocurrencies: BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC
- Enhanced interactive keyboard navigation
- Added `/coins` command to view all supported coins with live prices
- Added timeframe options: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

## Project Architecture

### Main Files
- `btc_analyzer.py` - Multi-coin crypto bot (BTC, ETH, SOL, etc.)
- `xau_analyzer.py` - XAUUSD/Gold specific bot
- `pyproject.toml` - Python dependencies
- `README.md` - Documentation

### Key Components

**Multi-Coin Bot (btc_analyzer.py):**
1. **Data Fetching**: Uses KuCoin API for real-time candlestick data
2. **Chart Generation**: Uses mplfinance with EMA20/EMA50 indicators
3. **AI Analysis**: Uses Google Gemini Vision API for technical analysis
4. **Telegram Bot**: Interactive keyboard-based navigation

**XAUUSD Bot (xau_analyzer.py):**
1. **Data Fetching**: Uses API Ninjas Gold Price Historical API
2. **Chart Generation**: Uses mplfinance with gold-themed styling
3. **AI Analysis**: Uses Google Gemini Vision API for technical analysis
4. **Telegram Bot**: Interactive keyboard-based navigation

### Supported Assets

**Cryptocurrencies:**
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC

**Commodities:**
XAUUSD (Gold)

### Timeframes
1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week

## Environment Variables Required

**For Multi-Coin Bot:**
- `TELEGRAM_BOT_TOKEN` - Telegram Bot API token from @BotFather
- `GEMINI_API_KEY` - Google Gemini API key for AI analysis

**For XAUUSD Bot:**
- `TELEGRAM_BOT_TOKEN_XAU` - Separate Telegram Bot token for XAUUSD bot (create new bot at @BotFather)
- `FINNHUB_API_KEY` - Finnhub API key for XAUUSD candlestick data (get free at https://finnhub.io/)

**Note:** Each Telegram bot needs its own unique token. The crypto bot uses `TELEGRAM_BOT_TOKEN` and the gold bot uses `TELEGRAM_BOT_TOKEN_XAU`.

## Running the Bots

**Multi-Coin Bot:**
```
python btc_analyzer.py
```

**XAUUSD Bot:**
```
python xau_analyzer.py
```

## User Preferences
- Language: Indonesian (Bahasa Indonesia)
- Output format: Structured technical analysis with trading signals
- Chart style: Candlestick with EMA indicators
