# Overview

This project is a dual Telegram bot system that provides AI-powered technical analysis for cryptocurrency and forex/commodity markets. The system uses Google Gemini Vision API to analyze candlestick charts with technical indicators, delivering insights directly to users through Telegram conversations.

**BTC Analyzer Bot** supports 14 major cryptocurrencies (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC) across 8 timeframes.

**Forex Analyzer Bot** covers 16 forex pairs and commodities including gold (XAUUSD), silver (XAGUSD), oil (USOIL), and major/cross currency pairs across 7 timeframes.

Both bots fetch real-time market data, generate visual charts with technical indicators (EMA20, EMA50), and leverage Gemini Vision to provide natural language technical analysis.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework & Communication
- **Telegram Bot API**: Core interaction layer using python-telegram-bot library
- **Async Architecture**: Built on asyncio for handling concurrent user requests
- **Callback-based Navigation**: InlineKeyboardButton/InlineKeyboardMarkup for interactive menus
- **Two Independent Bots**: Separate bot instances (btc_analyzer.py, xau_analyzer.py) running independently with different tokens

**Rationale**: Telegram provides reliable, user-friendly interface for real-time notifications. Separate bots allow independent scaling and specialized functionality for crypto vs forex markets.

## Data Fetching Strategy
- **Multi-source Approach**: Primary source is xnoxs_fetcher (TradingView wrapper), with fallback to yfinance and KuCoin API
- **Graceful Degradation**: ImportError handling allows bot to function with reduced data sources
- **Timeframe Mapping**: Unified timeframe interface (TV_INTERVAL_MAP) abstracts different API formats

**Rationale**: Multiple data sources ensure reliability. TradingView provides professional-grade data, while yfinance and KuCoin serve as fallbacks. This redundancy minimizes downtime when individual services fail.

**Alternatives Considered**: Single-source approach (rejected due to reliability concerns), paid data APIs (rejected due to cost).

**Pros**: High availability, no single point of failure, free data sources
**Cons**: Data inconsistency across sources, complex error handling

## Chart Generation
- **mplfinance Library**: Creates professional candlestick charts with customizable styling
- **Technical Indicators**:
  - EMA20 and EMA50 (price overlay)
  - Bollinger Bands (20-period, 2 std dev)
  - Fibonacci Retracement levels (23.6%, 38.2%, 50%, 61.8%)
  - RSI (14-period, separate panel with overbought/oversold lines)
  - MACD (12/26/9, separate panel with histogram)
- **Multi-panel Layout**: 4 panels - Price/Volume/RSI/MACD with ratio 6:2:2:2
- **In-memory Processing**: Charts generated as BytesIO objects, never saved to disk

**Rationale**: mplfinance provides finance-specific charting with minimal code. Multiple technical indicators give comprehensive market view. In-memory processing reduces storage requirements and improves security (no file remnants).

## AI Analysis Engine
- **Google Gemini Vision API**: Analyzes chart images to generate technical insights
- **Vision-based Approach**: Base64-encoded chart images sent directly to multimodal AI
- **Structured Prompts**: Analysis requests include timeframe context and specific instructions

**Rationale**: Vision API can "see" patterns humans recognize (support/resistance, chart patterns) that are difficult to encode algorithmically. Gemini provides cost-effective multimodal inference.

**Alternatives Considered**: Traditional TA libraries (rejected - less comprehensive than AI), GPT-4 Vision (rejected - higher cost), Custom ML models (rejected - resource intensive).

**Pros**: Natural language insights, pattern recognition beyond technical indicators, low implementation complexity
**Cons**: API costs, potential hallucinations, requires internet connectivity

## Configuration Management
- **Environment Variables**: Sensitive credentials stored in Replit Secrets
  - `TELEGRAM_BOT_TOKEN`: BTC bot authentication
  - `TELEGRAM_BOT_TOKEN_XAU`: Forex bot authentication
  - `GEMINI_API_KEY`: AI analysis authentication
- **No Database**: Stateless architecture, no user data persistence

**Rationale**: Environment variables prevent credential leakage in version control. Stateless design simplifies deployment and scaling.

## Logging & Error Handling
- **Python logging module**: Structured logging with configurable levels
- **Try-except blocks**: Graceful degradation when services unavailable
- **User-facing error messages**: Technical failures translated to actionable user guidance

**Rationale**: Comprehensive logging aids debugging in production. Graceful degradation ensures partial functionality during outages.

# External Dependencies

## APIs & Third-party Services

**Google Gemini API**
- Purpose: AI-powered chart image analysis
- Integration: REST API with base64 image payloads
- Authentication: API key via environment variable
- Cost Model: Pay-per-request (vision model pricing)

**Telegram Bot API**
- Purpose: User interface and message delivery
- Integration: python-telegram-bot library (async)
- Authentication: Bot tokens via environment variables
- Rate Limits: 30 messages/second per bot

**TradingView (via xnoxs_fetcher)**
- Purpose: Primary market data source
- Integration: Python wrapper library for TradingView websocket
- Authentication: None (public data)
- Data: OHLCV (Open, High, Low, Close, Volume) with multiple timeframes

**Yahoo Finance (yfinance)**
- Purpose: Fallback market data source
- Integration: yfinance Python library
- Authentication: None
- Limitations: Rate limiting, occasional data gaps

**KuCoin API**
- Purpose: Crypto-specific data fallback
- Integration: Direct REST API calls
- Authentication: None (public endpoints)
- Limitations: Crypto markets only

## Python Libraries

**Core Dependencies**
- `python-telegram-bot`: Async Telegram bot framework
- `mplfinance`: Financial charting library
- `pandas`: Data manipulation and time series handling
- `requests`: HTTP client for API calls
- `pytz`: Timezone conversions

**Optional Dependencies**
- `xnoxs_fetcher`: TradingView data wrapper (graceful degradation if unavailable)
- `yfinance`: Yahoo Finance wrapper (fallback data source)

## Deployment Environment

**Replit Platform**
- Purpose: Hosting and execution environment
- Features: Built-in secrets management, always-on deployments, workflow automation
- Constraints: Shared resources, potential cold starts

**Rationale**: Replit provides zero-configuration deployment with integrated secrets management, ideal for bot prototypes and small-scale production.