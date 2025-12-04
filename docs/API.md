# API Documentation

This document describes the internal APIs and data flow of the AI Trading Analysis Bots.

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Telegram   │────▶│   Bot Core   │────▶│  Data Layer  │
│   User       │◀────│              │◀────│              │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Gemini    │
                     │   Vision AI  │
                     └──────────────┘
```

## Data Sources

### TradingView (Primary)

```python
from xnoxs_fetcher import Interval, TradingView

tv = TradingView()
data = tv.get_hist(
    symbol="BINANCE:BTCUSDT",
    exchange="",
    interval=Interval.in_1_hour,
    n_bars=100
)
```

**Returns**: DataFrame with columns `[time, open, high, low, close, volume]`

### Yahoo Finance (Fallback)

```python
import yfinance as yf

ticker = yf.Ticker("BTC-USD")
data = ticker.history(period="5d", interval="1h")
```

**Returns**: DataFrame with columns `[Open, High, Low, Close, Volume]`

### KuCoin API (Crypto Fallback)

```python
import requests

url = "https://api.kucoin.com/api/v1/market/candles"
params = {
    "symbol": "BTC-USDT",
    "type": "1hour",
    "startAt": start_timestamp,
    "endAt": end_timestamp
}
response = requests.get(url, params=params)
```

**Returns**: List of `[timestamp, open, close, high, low, volume, turnover]`

## Technical Indicators

### EMA Calculation

```python
def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
    return data['close'].ewm(span=period, adjust=False).mean()
```

### RSI Calculation

```python
def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
```

### MACD Calculation

```python
def calculate_macd(data: pd.DataFrame) -> tuple:
    ema12 = data['close'].ewm(span=12, adjust=False).mean()
    ema26 = data['close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram
```

### Bollinger Bands Calculation

```python
def calculate_bollinger(data: pd.DataFrame, period: int = 20, std: int = 2):
    sma = data['close'].rolling(window=period).mean()
    std_dev = data['close'].rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower
```

### Fibonacci Levels

```python
def calculate_fibonacci(data: pd.DataFrame) -> dict:
    high = data['high'].max()
    low = data['low'].min()
    diff = high - low
    
    return {
        '0%': high,
        '23.6%': high - (0.236 * diff),
        '38.2%': high - (0.382 * diff),
        '50%': high - (0.5 * diff),
        '61.8%': high - (0.618 * diff),
        '100%': low
    }
```

## Chart Generation

### Panel Configuration

```python
import mplfinance as mpf

# Create chart with 4 panels
fig, axes = mpf.plot(
    data,
    type='candle',
    style=custom_style,
    addplot=additional_plots,
    volume=True,
    panel_ratios=(6, 2, 2, 2),  # Price:Volume:RSI:MACD
    returnfig=True
)
```

### Additional Plots Structure

```python
additional_plots = [
    # EMA on main panel
    mpf.make_addplot(ema20, color='blue', panel=0),
    mpf.make_addplot(ema50, color='orange', panel=0),
    
    # Bollinger Bands on main panel
    mpf.make_addplot(bb_upper, color='purple', linestyle='--', panel=0),
    mpf.make_addplot(bb_lower, color='purple', linestyle='--', panel=0),
    
    # RSI on panel 2
    mpf.make_addplot(rsi, color='purple', panel=2, ylabel='RSI'),
    
    # MACD on panel 3
    mpf.make_addplot(macd_line, color='blue', panel=3),
    mpf.make_addplot(signal_line, color='red', panel=3),
    mpf.make_addplot(histogram, type='bar', panel=3),
]
```

## Gemini Vision API

### Request Format

```python
import requests
import base64

def analyze_chart(image_bytes: bytes, prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": base64.b64encode(image_bytes).decode()
                    }
                }
            ]
        }]
    }
    
    response = requests.post(
        f"{url}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload
    )
    
    return response.json()['candidates'][0]['content']['parts'][0]['text']
```

### Prompt Structure (Timeframe-Aware)

Bot menggunakan prompt yang disesuaikan berdasarkan timeframe untuk menghasilkan analisa yang lebih akurat.

**Konfigurasi Timeframe:**

| Timeframe | Tipe Trading | Target Profit | Stop Loss | Hold Time |
|-----------|--------------|---------------|-----------|-----------|
| 1min | Scalping | 0.1% - 0.3% | 0.05% - 0.15% | 1-15 menit |
| 5min | Scalping | 0.2% - 0.5% | 0.1% - 0.25% | 5-30 menit |
| 15min | Intraday | 0.3% - 0.8% | 0.15% - 0.4% | 15 menit - 2 jam |
| 30min | Intraday | 0.5% - 1.2% | 0.25% - 0.6% | 30 menit - 4 jam |
| 1hour | Swing Trading | 1% - 2.5% | 0.5% - 1.2% | 2-24 jam |
| 4hour | Swing Trading | 2% - 5% | 1% - 2.5% | 1-7 hari |
| 1day | Position Trading | 3% - 10% | 1.5% - 5% | 3-30 hari |
| 1week | Position/Investment | 5% - 20% | 3% - 10% | 2-12 minggu |

**Output Format:**

```
PREDIKSI ARAH: [NAIK/TURUN/SIDEWAYS] - [Keyakinan: Tinggi/Sedang/Rendah]
SINYAL: [BELI/JUAL/TAHAN] - [Alasan]
HARGA SAAT INI: [Harga terakhir]
HARGA MASUK: [Entry optimal]
TARGET PROFIT 1: [TP1 sesuai timeframe]
TARGET PROFIT 2: [TP2 lebih ambisius]
STOP LOSS: [SL berdasarkan support/resistance]
RASIO RR: [Risk:Reward ratio]
WAKTU HOLD: [Estimasi durasi]
POLA: [Pola candlestick]
TREN: [Naik Kuat/Naik Lemah/Turun Kuat/Turun Lemah/Sideways]
RSI: [Nilai dan kondisi]
MACD: [Kondisi MACD]
BOLLINGER: [Posisi terhadap band]
FIBONACCI: [Level terdekat]
SUPPORT: [S1 dan S2]
RESISTANCE: [R1 dan R2]
KONFIRMASI: [X dari 5 indikator]
KESIMPULAN: [Ringkasan 2-3 kalimat]
```

## Telegram Bot Handlers

### Command Handler

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_main_menu()
    await update.message.reply_text(
        "Welcome! Select an asset to analyze:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

### Callback Handler

```python
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith("coin_"):
        # Handle coin selection
        symbol = data.replace("coin_", "")
        await show_timeframe_menu(query, symbol)
    
    elif data.startswith("tf_"):
        # Handle timeframe selection
        params = data.split("_")
        symbol, timeframe = params[1], params[2]
        await generate_analysis(query, symbol, timeframe)
```

## Error Handling

### Graceful Degradation

```python
async def fetch_data(symbol: str, timeframe: str) -> pd.DataFrame:
    # Try TradingView first
    try:
        data = fetch_from_tradingview(symbol, timeframe)
        if data is not None and not data.empty:
            return data
    except Exception as e:
        logger.warning(f"TradingView failed: {e}")
    
    # Fallback to Yahoo Finance
    try:
        data = fetch_from_yfinance(symbol, timeframe)
        if data is not None and not data.empty:
            return data
    except Exception as e:
        logger.warning(f"Yahoo Finance failed: {e}")
    
    # Final fallback to KuCoin (crypto only)
    if is_crypto(symbol):
        try:
            data = fetch_from_kucoin(symbol, timeframe)
            if data is not None and not data.empty:
                return data
        except Exception as e:
            logger.warning(f"KuCoin failed: {e}")
    
    raise DataFetchError(f"All data sources failed for {symbol}")
```

## Rate Limiting

### Telegram API Limits

- **Messages per second**: 30 per bot
- **Messages per chat per minute**: 20

### Gemini API Limits

- Check [Google AI pricing](https://ai.google.dev/pricing) for current limits
- Implement exponential backoff for rate limit errors

## Environment Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | string | Yes | BTC bot token |
| `TELEGRAM_BOT_TOKEN_XAU` | string | Yes | Forex bot token |
| `GEMINI_API_KEY` | string | Yes | Google Gemini API key |
