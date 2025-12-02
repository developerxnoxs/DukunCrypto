# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-02

### Added

- **BTC Analyzer Bot** with support for 14 major cryptocurrencies
  - BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC
  - 8 timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

- **Forex Analyzer Bot** with support for 16 forex pairs and commodities
  - Commodities: XAUUSD (Gold), XAGUSD (Silver), USOIL
  - Major Pairs: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
  - Cross Pairs: EURGBP, EURJPY, GBPJPY, AUDJPY, EURAUD, EURCHF
  - 7 timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d

- **Technical Indicators**
  - EMA20 and EMA50 (Exponential Moving Averages)
  - Bollinger Bands (20-period, 2 standard deviations)
  - RSI - Relative Strength Index (14-period)
  - MACD - Moving Average Convergence Divergence (12/26/9)
  - Fibonacci Retracement levels (23.6%, 38.2%, 50%, 61.8%)

- **Multi-panel Professional Charts**
  - Panel 1: Candlestick with EMA, Bollinger Bands, Fibonacci levels
  - Panel 2: Volume bars
  - Panel 3: RSI with overbought/oversold lines
  - Panel 4: MACD with signal line and histogram

- **AI-Powered Analysis** using Google Gemini Vision API
  - Pattern recognition and trend analysis
  - Support/resistance level identification
  - Trading signals with entry, take profit, and stop loss levels
  - Market sentiment analysis

- **Multi-Source Data Fetching**
  - Primary: TradingView via xnoxs_fetcher
  - Fallback: Yahoo Finance via yfinance
  - Crypto Fallback: KuCoin API

- **Project Infrastructure**
  - MIT License
  - Contributing guidelines
  - Code of Conduct
  - Comprehensive documentation

### Technical Details

- Async architecture using `python-telegram-bot`
- In-memory chart generation (no disk I/O)
- Graceful degradation when data sources unavailable
- Structured logging for debugging

## [Unreleased]

### Planned Features

- Additional technical indicators (Stochastic, ATR, Williams %R)
- Multi-language support
- Custom alert system
- Portfolio tracking
- Historical analysis comparison
- Backtesting capabilities

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-12-02 | Initial release with full indicator suite |

