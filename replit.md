# AI Trading Analysis Bots

## Overview

This project is a dual Telegram bot system that provides AI-powered technical analysis for cryptocurrency and forex/commodity markets. The system uses Google Gemini Vision API to analyze candlestick charts with technical indicators, delivering insights directly to users through Telegram conversations.

**BTC Analyzer Bot** supports 14 major cryptocurrencies (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC) across 8 timeframes.

**Forex Analyzer Bot** covers 16 forex pairs and commodities including gold (XAUUSD), silver (XAGUSD), oil (USOIL), and major/cross currency pairs across 7 timeframes.

Both bots fetch real-time market data, generate visual charts with technical indicators, and leverage Gemini Vision to provide natural language technical analysis.

## User Preferences

- Preferred communication style: Simple, everyday language
- Language: Indonesian (Bahasa Indonesia) for bot responses

## Project Structure

```
ai-trading-analysis-bots/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── btc_analyzer.py       # Cryptocurrency analysis bot
│   └── xau_analyzer.py       # Forex & commodities bot
├── docs/
│   ├── API.md                # API documentation
│   └── TECHNICAL_INDICATORS.md
├── assets/                   # Images and screenshots
├── examples/                 # Usage examples
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── CHANGELOG.md             # Version history
├── CODE_OF_CONDUCT.md       # Community guidelines
├── CONTRIBUTING.md          # Contribution guide
├── LICENSE                  # MIT License
├── README.md                # Main documentation
├── main.py                  # Entry point
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── replit.md                # This file
```

## Technical Indicators

- **EMA20 and EMA50**: Exponential Moving Averages (price overlay)
- **Bollinger Bands**: 20-period, 2 standard deviations
- **Fibonacci Retracement**: Auto-calculated levels (23.6%, 38.2%, 50%, 61.8%)
- **RSI**: 14-period with overbought (70) / oversold (30) lines
- **MACD**: 12/26/9 with signal line and histogram

## Chart Layout

4-panel professional layout with ratio 6:2:2:2:
1. Candlestick + EMA + Bollinger + Fibonacci
2. Volume bars
3. RSI indicator
4. MACD indicator

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | BTC Analyzer bot token |
| `TELEGRAM_BOT_TOKEN_XAU` | Forex Analyzer bot token |
| `GEMINI_API_KEY` | Google Gemini API key |

## Workflows

| Name | Command | Description |
|------|---------|-------------|
| BTC Analyzer Bot | `uv run python src/btc_analyzer.py` | Crypto analysis |
| Forex Analyzer Bot | `uv run python src/xau_analyzer.py` | Forex analysis |

## Data Sources

1. **TradingView** (primary) - via xnoxs_fetcher
2. **Yahoo Finance** (fallback) - via yfinance
3. **KuCoin API** (crypto fallback) - direct REST

## Recent Changes

- 2024-12-02: Added RSI, MACD, Bollinger Bands, Fibonacci indicators
- 2024-12-02: Reorganized project structure for GitHub
- 2024-12-02: Added comprehensive documentation
- 2024-12-02: Created LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md
