<p align="center">
  <h1 align="center">AI Trading Analysis Bots</h1>
  <p align="center">
    <strong>AI-Powered Technical Analysis for Crypto & Forex Markets</strong>
  </p>
  <p align="center">
    Telegram bots that generate professional candlestick charts with technical indicators<br>
    and provide AI-powered trading insights using Google Gemini Vision
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Telegram-Bot%20API-blue.svg" alt="Telegram"></a>
  <a href="#"><img src="https://img.shields.io/badge/AI-Gemini%20Vision-orange.svg" alt="Gemini"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#technical-indicators">Indicators</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Overview

This project provides two specialized Telegram bots for real-time market analysis:

| Bot | Markets | Assets | Timeframes |
|-----|---------|--------|------------|
| **BTC Analyzer** | Cryptocurrency | 14 coins | 8 timeframes |
| **Forex Analyzer** | Forex & Commodities | 16 pairs | 7 timeframes |

Both bots leverage **Google Gemini Vision API** to analyze candlestick charts and provide natural language trading insights, pattern recognition, and actionable signals.

## Features

### Multi-Panel Professional Charts

Each analysis generates a comprehensive 4-panel chart:

```
┌─────────────────────────────────────────┐
│  Candlestick + EMA + Bollinger + Fib    │  Panel 1: Price Action
├─────────────────────────────────────────┤
│            Volume Bars                   │  Panel 2: Volume
├─────────────────────────────────────────┤
│     RSI (14) with 70/30 levels          │  Panel 3: RSI
├─────────────────────────────────────────┤
│   MACD + Signal + Histogram             │  Panel 4: MACD
└─────────────────────────────────────────┘
```

### Technical Indicators

| Indicator | Parameters | Description |
|-----------|------------|-------------|
| **EMA** | 20, 50 periods | Exponential Moving Averages for trend direction |
| **Bollinger Bands** | 20 periods, 2σ | Volatility bands with upper/middle/lower |
| **RSI** | 14 periods | Relative Strength Index with overbought (70) / oversold (30) |
| **MACD** | 12/26/9 | Moving Average Convergence Divergence with histogram |
| **Fibonacci** | Auto | Retracement levels: 23.6%, 38.2%, 50%, 61.8% |

### AI-Powered Analysis

The Gemini Vision API analyzes charts to provide:

- **Trading Signal**: BUY / SELL / HOLD with confidence level
- **Entry Point**: Suggested entry price
- **Take Profit**: TP1 and TP2 targets
- **Stop Loss**: Risk management level
- **Pattern Recognition**: Candlestick and chart patterns
- **Trend Analysis**: Current market direction
- **Support/Resistance**: Key price levels
- **Summary**: Actionable trading insights

### Supported Markets

<details>
<summary><strong>BTC Analyzer - 14 Cryptocurrencies</strong></summary>

| Symbol | Name | Symbol | Name |
|--------|------|--------|------|
| BTC | Bitcoin | LINK | Chainlink |
| ETH | Ethereum | DOT | Polkadot |
| SOL | Solana | ATOM | Cosmos |
| BNB | Binance Coin | UNI | Uniswap |
| XRP | Ripple | LTC | Litecoin |
| ADA | Cardano | AVAX | Avalanche |
| DOGE | Dogecoin | MATIC | Polygon |

**Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

</details>

<details>
<summary><strong>Forex Analyzer - 16 Pairs & Commodities</strong></summary>

**Commodities**
| Symbol | Name |
|--------|------|
| XAUUSD | Gold |
| XAGUSD | Silver |
| USOIL | Crude Oil |

**Major Pairs**
| Symbol | Pair |
|--------|------|
| EURUSD | Euro / US Dollar |
| GBPUSD | British Pound / US Dollar |
| USDJPY | US Dollar / Japanese Yen |
| USDCHF | US Dollar / Swiss Franc |
| AUDUSD | Australian Dollar / US Dollar |
| USDCAD | US Dollar / Canadian Dollar |
| NZDUSD | New Zealand Dollar / US Dollar |

**Cross Pairs**
| Symbol | Pair |
|--------|------|
| EURGBP | Euro / British Pound |
| EURJPY | Euro / Japanese Yen |
| GBPJPY | British Pound / Japanese Yen |
| AUDJPY | Australian Dollar / Japanese Yen |
| EURAUD | Euro / Australian Dollar |
| EURCHF | Euro / Swiss Franc |

**Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d

</details>

## Installation

### Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-trading-analysis-bots.git
cd ai-trading-analysis-bots

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run BTC Analyzer Bot
python src/btc_analyzer.py

# Run Forex Analyzer Bot (in separate terminal)
python src/xau_analyzer.py
```

### Using UV (Recommended)

```bash
# Install UV if not already installed
pip install uv

# Install dependencies
uv sync

# Run bots
uv run python src/btc_analyzer.py
uv run python src/xau_analyzer.py
```

### Deploy on Replit

[![Run on Replit](https://replit.com/badge/github/yourusername/ai-trading-analysis-bots)](https://replit.com/github/yourusername/ai-trading-analysis-bots)

1. Fork this repository on Replit
2. Add your API keys in the Secrets tab
3. Run the workflows

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | BTC Analyzer bot token from BotFather | Yes |
| `TELEGRAM_BOT_TOKEN_XAU` | Forex Analyzer bot token from BotFather | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

### Getting API Keys

<details>
<summary><strong>Telegram Bot Token</strong></summary>

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the token provided

</details>

<details>
<summary><strong>Google Gemini API Key</strong></summary>

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

</details>

## Usage

### Bot Commands

```
/start - Start the bot and show main menu
```

### How It Works

1. **Start** the bot with `/start` command
2. **Select** a cryptocurrency or forex pair
3. **Choose** your preferred timeframe
4. **Receive** a professional chart with AI analysis

### Analysis Output

The bot provides structured analysis including:

```
📊 ANALISIS TEKNIKAL [SYMBOL] - [TIMEFRAME]

📈 SINYAL: BUY/SELL/HOLD
   Alasan: [AI reasoning]

💰 ENTRY: $XX,XXX
📈 TAKE PROFIT 1: $XX,XXX
📈 TAKE PROFIT 2: $XX,XXX
🛑 STOP LOSS: $XX,XXX

🕯️ POLA: [Candlestick patterns]
📊 TREND: [Market trend]
📍 SUPPORT: $XX,XXX
📍 RESISTANCE: $XX,XXX

💡 KESIMPULAN: [Summary]
```

## Project Structure

```
ai-trading-analysis-bots/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── btc_analyzer.py       # Cryptocurrency analysis bot
│   └── xau_analyzer.py       # Forex & commodities bot
├── docs/                     # Documentation
├── assets/                   # Images and screenshots
├── examples/                 # Usage examples
├── tests/                    # Test suite
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── CHANGELOG.md             # Version history
├── CODE_OF_CONDUCT.md       # Community guidelines
├── CONTRIBUTING.md          # Contribution guide
├── LICENSE                  # MIT License
├── README.md                # This file
├── pyproject.toml           # Project configuration
└── requirements.txt         # Dependencies
```

## Data Sources

The bots use multiple data sources with automatic fallback:

| Priority | Source | Type | Coverage |
|----------|--------|------|----------|
| 1 | TradingView | Primary | All markets |
| 2 | Yahoo Finance | Fallback | Forex, Crypto |
| 3 | KuCoin API | Fallback | Crypto only |

This multi-source architecture ensures high availability and minimizes downtime.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a PR.

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Lint
ruff check src/
```

## Disclaimer

**This software is for educational and informational purposes only.**

- Not financial advice
- Do your own research before trading
- Past performance does not guarantee future results
- Trading cryptocurrencies and forex carries significant risk

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [mplfinance](https://github.com/matplotlib/mplfinance) - Financial charting library
- [Google Gemini](https://ai.google.dev/) - AI vision analysis
- [TradingView](https://tradingview.com/) - Market data

---

<p align="center">
  Made with ❤️ for traders
</p>

<p align="center">
  <a href="#ai-trading-analysis-bots">Back to top</a>
</p>
