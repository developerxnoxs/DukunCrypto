#!/usr/bin/env python3
"""
Bot Analisa Teknikal Trading - Crypto & Forex
Tool CLI untuk analisa teknikal menggunakan Telegram Bot dan Gemini AI Vision
Mendukung: Cryptocurrency (14 koin) dan Forex/Komoditas (16 pasangan)
"""

import logging
import base64
import json
import re
import os
import sys
import requests
import mplfinance as mpf
import pandas as pd
from datetime import datetime, timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pytz import timezone as tz
import asyncio
from dotenv import load_dotenv

load_dotenv()


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'


class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"{Colors.DIM}%(message)s{Colors.RESET}",
        logging.INFO: f"{Colors.CYAN}%(message)s{Colors.RESET}",
        logging.WARNING: f"{Colors.YELLOW}%(message)s{Colors.RESET}",
        logging.ERROR: f"{Colors.RED}{Colors.BOLD}%(message)s{Colors.RESET}",
        logging.CRITICAL: f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}%(message)s{Colors.RESET}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, "%(message)s")
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class QuietFilter(logging.Filter):
    def filter(self, record):
        noisy_messages = [
            'HTTP Request',
            'httpx',
            'httpcore',
            'urllib3',
            'Retrying',
            'Starting new HTTP',
        ]
        return not any(msg in record.getMessage() for msg in noisy_messages)


logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('yfinance').setLevel(logging.WARNING)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
console_handler.addFilter(QuietFilter())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(console_handler)
logger.propagate = False


def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {Colors.YELLOW}📊 BOT ANALISA TEKNIKAL TRADING{Colors.CYAN}                        ║
║   {Colors.WHITE}Crypto & Forex Analysis with AI{Colors.CYAN}                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def log_success(message):
    print(f"{Colors.GREEN}  ✓ {message}{Colors.RESET}")


def log_warning(message):
    print(f"{Colors.YELLOW}  ⚠ {message}{Colors.RESET}")


def log_error(message):
    print(f"{Colors.RED}  ✗ {message}{Colors.RESET}")


def log_info(message):
    print(f"{Colors.CYAN}  ℹ {message}{Colors.RESET}")


def log_data(message):
    print(f"{Colors.MAGENTA}  📡 {message}{Colors.RESET}")


def log_analysis(message):
    print(f"{Colors.BLUE}  🤖 {message}{Colors.RESET}")


try:
    from xnoxs_fetcher import XnoxsFetcher, TimeFrame
    fetcher = XnoxsFetcher()
    TV_AVAILABLE = True
    TV_INTERVAL_MAP = {
        "1min": TimeFrame.MINUTE_1,
        "5min": TimeFrame.MINUTE_5,
        "15min": TimeFrame.MINUTE_15,
        "30min": TimeFrame.MINUTE_30,
        "1hour": TimeFrame.HOUR_1,
        "4hour": TimeFrame.HOUR_4,
        "1day": TimeFrame.DAILY,
        "1week": TimeFrame.WEEKLY,
    }
except ImportError:
    TV_AVAILABLE = False
    fetcher = None
    TV_INTERVAL_MAP = {
        "1min": None,
        "5min": None,
        "15min": None,
        "30min": None,
        "1hour": None,
        "4hour": None,
        "1day": None,
        "1week": None,
    }

try:
    import yfinance as yf
except ImportError:
    yf = None

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SUPPORTED_COINS = {
    "BTC": {"name": "Bitcoin", "emoji": "₿", "color": "#F7931A", "yf_symbol": "BTC-USD", "tv_symbol": "BTCUSDT"},
    "ETH": {"name": "Ethereum", "emoji": "Ξ", "color": "#627EEA", "yf_symbol": "ETH-USD", "tv_symbol": "ETHUSDT"},
    "SOL": {"name": "Solana", "emoji": "◎", "color": "#00FFA3", "yf_symbol": "SOL-USD", "tv_symbol": "SOLUSDT"},
    "BNB": {"name": "BNB", "emoji": "🔶", "color": "#F3BA2F", "yf_symbol": "BNB-USD", "tv_symbol": "BNBUSDT"},
    "XRP": {"name": "Ripple", "emoji": "✕", "color": "#23292F", "yf_symbol": "XRP-USD", "tv_symbol": "XRPUSDT"},
    "ADA": {"name": "Cardano", "emoji": "₳", "color": "#0033AD", "yf_symbol": "ADA-USD", "tv_symbol": "ADAUSDT"},
    "DOGE": {"name": "Dogecoin", "emoji": "🐕", "color": "#C2A633", "yf_symbol": "DOGE-USD", "tv_symbol": "DOGEUSDT"},
    "AVAX": {"name": "Avalanche", "emoji": "🔺", "color": "#E84142", "yf_symbol": "AVAX-USD", "tv_symbol": "AVAXUSDT"},
    "MATIC": {"name": "Polygon", "emoji": "⬡", "color": "#8247E5", "yf_symbol": "MATIC-USD", "tv_symbol": "MATICUSDT"},
    "LINK": {"name": "Chainlink", "emoji": "⬡", "color": "#2A5ADA", "yf_symbol": "LINK-USD", "tv_symbol": "LINKUSDT"},
    "DOT": {"name": "Polkadot", "emoji": "●", "color": "#E6007A", "yf_symbol": "DOT-USD", "tv_symbol": "DOTUSDT"},
    "ATOM": {"name": "Cosmos", "emoji": "⚛", "color": "#2E3148", "yf_symbol": "ATOM-USD", "tv_symbol": "ATOMUSDT"},
    "UNI": {"name": "Uniswap", "emoji": "🦄", "color": "#FF007A", "yf_symbol": "UNI-USD", "tv_symbol": "UNIUSDT"},
    "LTC": {"name": "Litecoin", "emoji": "Ł", "color": "#345D9D", "yf_symbol": "LTC-USD", "tv_symbol": "LTCUSDT"},
}

FOREX_PAIRS = {
    "XAUUSD": {"name": "Emas", "emoji": "🥇", "yf_symbol": "GC=F", "category": "commodity"},
    "XAGUSD": {"name": "Perak", "emoji": "🥈", "yf_symbol": "SI=F", "category": "commodity"},
    "EURUSD": {"name": "EUR/USD", "emoji": "💶", "yf_symbol": "EURUSD=X", "category": "major"},
    "GBPUSD": {"name": "GBP/USD", "emoji": "💷", "yf_symbol": "GBPUSD=X", "category": "major"},
    "USDJPY": {"name": "USD/JPY", "emoji": "💴", "yf_symbol": "USDJPY=X", "category": "major"},
    "USDCHF": {"name": "USD/CHF", "emoji": "🇨🇭", "yf_symbol": "USDCHF=X", "category": "major"},
    "AUDUSD": {"name": "AUD/USD", "emoji": "🇦🇺", "yf_symbol": "AUDUSD=X", "category": "major"},
    "USDCAD": {"name": "USD/CAD", "emoji": "🇨🇦", "yf_symbol": "USDCAD=X", "category": "major"},
    "NZDUSD": {"name": "NZD/USD", "emoji": "🇳🇿", "yf_symbol": "NZDUSD=X", "category": "major"},
    "EURGBP": {"name": "EUR/GBP", "emoji": "🇪🇺", "yf_symbol": "EURGBP=X", "category": "cross"},
    "EURJPY": {"name": "EUR/JPY", "emoji": "🇪🇺", "yf_symbol": "EURJPY=X", "category": "cross"},
    "GBPJPY": {"name": "GBP/JPY", "emoji": "🇬🇧", "yf_symbol": "GBPJPY=X", "category": "cross"},
    "AUDJPY": {"name": "AUD/JPY", "emoji": "🇦🇺", "yf_symbol": "AUDJPY=X", "category": "cross"},
    "EURAUD": {"name": "EUR/AUD", "emoji": "🇪🇺", "yf_symbol": "EURAUD=X", "category": "cross"},
    "EURCHF": {"name": "EUR/CHF", "emoji": "🇪🇺", "yf_symbol": "EURCHF=X", "category": "cross"},
    "USOIL": {"name": "Minyak Mentah", "emoji": "🛢️", "yf_symbol": "CL=F", "category": "commodity"},
}

INTERVAL_MAP = {
    "1min": "1m", "5min": "5m", "15min": "15m",
    "30min": "30m", "1hour": "1h", "4hour": "4h",
    "1day": "1d", "1week": "1wk"
}

KUCOIN_INTERVAL_MAP = {
    "1min": 60, "3min": 180, "5min": 300, "15min": 900,
    "30min": 1800, "1hour": 3600, "2hour": 7200,
    "4hour": 14400, "6hour": 21600, "8hour": 28800,
    "12hour": 43200, "1day": 86400, "1week": 604800
}


def fetch_crypto_from_tradingview(symbol="BTC", interval="1hour", n_bars=200):
    """Mengambil data candlestick Crypto dari TradingView"""
    
    if not TV_AVAILABLE:
        return None
    
    if interval not in TV_INTERVAL_MAP:
        return None
    
    if symbol not in SUPPORTED_COINS:
        return None
    
    tv_interval = TV_INTERVAL_MAP[interval]
    tv_symbol = SUPPORTED_COINS[symbol].get("tv_symbol", f"{symbol}USDT")
    
    exchanges = ['BINANCE', 'BYBIT', 'COINBASE', 'KRAKEN', 'BITSTAMP']
    
    for exchange in exchanges:
        try:
            df = fetcher.get_historical_data(
                symbol=tv_symbol,
                exchange=exchange,
                timeframe=tv_interval,
                bars=n_bars
            )
            
            if df is not None and not df.empty:
                df = df.dropna()
                if df.empty:
                    continue
                
                candles = []
                for timestamp, row in df.iterrows():
                    candles.append([
                        int(timestamp.timestamp()),
                        float(row["open"]),
                        float(row["close"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["volume"]) if "volume" in row else 0
                    ])
                
                log_data(f"{symbol} ({interval}): {len(candles)} candle dari TradingView")
                return candles
                
        except Exception:
            continue
    
    return None


def fetch_crypto_from_yfinance(symbol="BTC", interval="1hour"):
    """Mengambil data candlestick Crypto dari Yahoo Finance (cadangan)"""
    
    if not yf:
        return None
    
    if interval not in INTERVAL_MAP:
        return None
    
    if symbol not in SUPPORTED_COINS:
        return None

    try:
        yf_symbol = SUPPORTED_COINS[symbol]["yf_symbol"]
        yf_interval = INTERVAL_MAP[interval]
        ticker = yf.Ticker(yf_symbol)
        
        if interval in ["1min", "5min", "15min", "30min"]:
            period = "3d"
        else:
            period = "1y"
        
        df = ticker.history(period=period, interval=yf_interval)
        
        if df.empty:
            return None
        
        df = df.dropna()
        if df.empty:
            return None
        
        candles = []
        for timestamp, row in df.iterrows():
            volume = float(row["Volume"]) if "Volume" in row and pd.notna(row["Volume"]) else 0
            candles.append([
                int(timestamp.timestamp()),
                float(row["Open"]),
                float(row["Close"]),
                float(row["High"]),
                float(row["Low"]),
                volume
            ])
        
        log_data(f"{symbol} ({interval}): {len(candles)} candle dari Yahoo Finance")
        return candles[-200:] if len(candles) > 200 else candles
        
    except Exception:
        return None


def fetch_crypto_kucoin(symbol="BTC", interval="15min", candle_limit=200):
    """Mengambil data candlestick dari KuCoin API (cadangan)"""
    pair = f"{symbol}-USDT"
    
    if interval not in KUCOIN_INTERVAL_MAP:
        return None
    
    end_at = int(datetime.now(timezone.utc).timestamp())
    start_at = end_at - KUCOIN_INTERVAL_MAP[interval] * candle_limit

    try:
        response = requests.get(
            "https://api.kucoin.com/api/v1/market/candles",
            params={
                "symbol": pair,
                "type": interval,
                "startAt": start_at,
                "endAt": end_at
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "200000":
            return None
        
        candles = data.get("data", [])
        if not candles:
            return None
            
        sorted_candles = sorted(candles, key=lambda x: int(x[0]))
        log_data(f"{symbol} ({interval}): {len(sorted_candles)} candle dari KuCoin")
        return sorted_candles
        
    except Exception:
        return None


def fetch_crypto_data(symbol="BTC", interval="1hour"):
    """Mengambil data candlestick Crypto - prioritas TradingView, cadangan Yahoo Finance, lalu KuCoin"""
    
    if symbol not in SUPPORTED_COINS:
        return None
    
    data = fetch_crypto_from_tradingview(symbol, interval)
    if data and len(data) >= 20:
        return data
    
    data = fetch_crypto_from_yfinance(symbol, interval)
    if data and len(data) >= 20:
        return data
    
    data = fetch_crypto_kucoin(symbol, interval)
    if data and len(data) >= 20:
        return data
    
    log_error(f"Gagal mengambil data {symbol}")
    return None


def fetch_forex_from_tradingview(symbol="XAUUSD", interval="1hour", n_bars=200):
    """Mengambil data candlestick Forex dari TradingView"""
    
    if not TV_AVAILABLE:
        return None
    
    if interval not in TV_INTERVAL_MAP or interval == "1week":
        return None
    
    if symbol not in FOREX_PAIRS:
        return None
    
    tv_interval = TV_INTERVAL_MAP[interval]
    
    exchanges = ['OANDA', 'FXCM', 'FX_IDC', 'FOREXCOM', 'CAPITALCOM']
    
    for exchange in exchanges:
        try:
            df = fetcher.get_historical_data(
                symbol=symbol,
                exchange=exchange,
                timeframe=tv_interval,
                bars=n_bars
            )
            
            if df is not None and not df.empty:
                df = df.dropna()
                if df.empty:
                    continue
                
                candles = []
                for timestamp, row in df.iterrows():
                    candles.append([
                        int(timestamp.timestamp()),
                        float(row["open"]),
                        float(row["close"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["volume"]) if "volume" in row else 0
                    ])
                
                log_data(f"{symbol} ({interval}): {len(candles)} candle dari TradingView")
                return candles
                
        except Exception:
            continue
    
    return None


def fetch_forex_from_yfinance(symbol="XAUUSD", interval="1hour"):
    """Mengambil data candlestick Forex dari Yahoo Finance (cadangan)"""
    
    if not yf:
        return None
    
    forex_interval_map = {k: v for k, v in INTERVAL_MAP.items() if k != "1week"}
    
    if interval not in forex_interval_map:
        return None
    
    if symbol not in FOREX_PAIRS:
        return None

    try:
        yf_symbol = FOREX_PAIRS[symbol]["yf_symbol"]
        yf_interval = forex_interval_map[interval]
        ticker = yf.Ticker(yf_symbol)
        
        if interval in ["1min", "5min", "15min", "30min"]:
            period = "3d"
        else:
            period = "1y"
        
        df = ticker.history(period=period, interval=yf_interval)
        
        if df.empty:
            return None
        
        df = df.dropna()
        if df.empty:
            return None
        
        candles = []
        for timestamp, row in df.iterrows():
            volume = float(row["Volume"]) if "Volume" in row and pd.notna(row["Volume"]) else 0
            candles.append([
                int(timestamp.timestamp()),
                float(row["Open"]),
                float(row["Close"]),
                float(row["High"]),
                float(row["Low"]),
                volume
            ])
        
        log_data(f"{symbol} ({interval}): {len(candles)} candle dari Yahoo Finance")
        return candles[-200:] if len(candles) > 200 else candles
        
    except Exception:
        return None


def fetch_forex_data(symbol="XAUUSD", interval="1hour"):
    """Mengambil data candlestick Forex - prioritas TradingView, cadangan Yahoo Finance"""
    
    forex_interval_map = {k: v for k, v in INTERVAL_MAP.items() if k != "1week"}
    
    if interval not in forex_interval_map:
        return None
    
    if symbol not in FOREX_PAIRS:
        return None
    
    data = fetch_forex_from_tradingview(symbol, interval)
    if data and len(data) >= 20:
        return data
    
    data = fetch_forex_from_yfinance(symbol, interval)
    if data and len(data) >= 20:
        return data
    
    log_error(f"Gagal mengambil data {symbol}")
    return None


def get_crypto_price(symbol="BTC"):
    """Mengambil harga crypto terkini"""
    
    if symbol not in SUPPORTED_COINS:
        return None
    
    if TV_AVAILABLE:
        try:
            tv_symbol = SUPPORTED_COINS[symbol].get("tv_symbol", f"{symbol}USDT")
            df = fetcher.get_historical_data(
                symbol=tv_symbol,
                exchange='BINANCE',
                timeframe=TimeFrame.MINUTE_1,
                bars=1
            )
            if df is not None and not df.empty:
                return float(df.iloc[-1]["close"])
        except Exception:
            pass
    
    if yf:
        try:
            yf_symbol = SUPPORTED_COINS[symbol]["yf_symbol"]
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data.iloc[-1]["Close"])
        except Exception:
            pass
    
    pair = f"{symbol}-USDT"
    try:
        response = requests.get(
            f"https://api.kucoin.com/api/v1/market/orderbook/level1",
            params={"symbol": pair},
            timeout=10
        )
        data = response.json()
        if data.get("code") == "200000" and data.get("data"):
            return float(data["data"].get("price", 0))
    except Exception:
        pass
    
    return None


def get_forex_price(symbol="XAUUSD"):
    """Mengambil harga forex/komoditas terkini"""
    
    if symbol not in FOREX_PAIRS:
        return None
    
    if TV_AVAILABLE:
        try:
            df = fetcher.get_historical_data(
                symbol=symbol,
                exchange='OANDA',
                timeframe=TimeFrame.MINUTE_1,
                bars=1
            )
            if df is not None and not df.empty:
                return float(df.iloc[-1]["close"])
        except Exception:
            pass
    
    if yf:
        try:
            yf_symbol = FOREX_PAIRS[symbol]["yf_symbol"]
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data.iloc[-1]["Close"])
        except Exception:
            pass
    
    return None


def calculate_rsi(series, period=14):
    """Menghitung RSI (Relative Strength Index)"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series, fast=12, slow=26, signal=9):
    """Menghitung MACD (Moving Average Convergence Divergence)"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Menghitung Bollinger Bands"""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def calculate_fibonacci_levels(df):
    """Menghitung level Fibonacci retracement"""
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low
    
    levels = {
        '0.0%': high,
        '23.6%': high - (diff * 0.236),
        '38.2%': high - (diff * 0.382),
        '50.0%': high - (diff * 0.5),
        '61.8%': high - (diff * 0.618),
        '78.6%': high - (diff * 0.786),
        '100.0%': low
    }
    return levels


def generate_chart(data, filename="chart.png", symbol="BTC", tf="15min", market_type="crypto"):
    """Generate chart candlestick dengan RSI, MACD, Bollinger Bands, dan Fibonacci"""
    if not data:
        return None
    
    try:
        ohlc = []
        for item in data:
            ts = datetime.fromtimestamp(int(item[0]), tz=tz("Asia/Jakarta"))
            ohlc.append([
                ts,
                float(item[1]),
                float(item[3]),
                float(item[4]),
                float(item[2]),
                float(item[5])
            ])
        
        df = pd.DataFrame(ohlc, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df.set_index("Date", inplace=True)

        mc = mpf.make_marketcolors(
            up='#00AA00', down='#FF0000',
            wick={'up': '#00AA00', 'down': '#FF0000'},
            volume={'up': '#00AA00', 'down': '#FF0000'}
        )
        style = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle=':',
            gridcolor='#cccccc',
            facecolor='#f5f5f5',
            edgecolor='#666666'
        )

        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
        
        rsi = calculate_rsi(df['Close'])
        rsi_overbought = pd.Series([70] * len(df), index=df.index)
        rsi_oversold = pd.Series([30] * len(df), index=df.index)
        
        macd_line, signal_line, macd_histogram = calculate_macd(df['Close'])
        
        fib_levels = calculate_fibonacci_levels(df)
        fib_236 = pd.Series([fib_levels['23.6%']] * len(df), index=df.index)
        fib_382 = pd.Series([fib_levels['38.2%']] * len(df), index=df.index)
        fib_500 = pd.Series([fib_levels['50.0%']] * len(df), index=df.index)
        fib_618 = pd.Series([fib_levels['61.8%']] * len(df), index=df.index)
        
        macd_colors = ['#00AA00' if val >= 0 else '#FF0000' for val in macd_histogram]
        
        addplots = [
            mpf.make_addplot(ema20, color='blue', width=1.2),
            mpf.make_addplot(ema50, color='orange', width=1.2),
            
            mpf.make_addplot(bb_upper, color='purple', width=0.8, linestyle='--'),
            mpf.make_addplot(bb_middle, color='purple', width=0.5, linestyle=':'),
            mpf.make_addplot(bb_lower, color='purple', width=0.8, linestyle='--'),
            
            mpf.make_addplot(fib_236, color='#FFD700', width=0.5, linestyle='-.'),
            mpf.make_addplot(fib_382, color='#FFA500', width=0.5, linestyle='-.'),
            mpf.make_addplot(fib_500, color='#FF6347', width=0.7, linestyle='-.'),
            mpf.make_addplot(fib_618, color='#FF4500', width=0.5, linestyle='-.'),
            
            mpf.make_addplot(rsi, panel=2, color='#9C27B0', width=1.2, ylabel='RSI'),
            mpf.make_addplot(rsi_overbought, panel=2, color='red', width=0.5, linestyle='--'),
            mpf.make_addplot(rsi_oversold, panel=2, color='green', width=0.5, linestyle='--'),
            
            mpf.make_addplot(macd_line, panel=3, color='blue', width=1, ylabel='MACD'),
            mpf.make_addplot(signal_line, panel=3, color='red', width=1),
            mpf.make_addplot(macd_histogram, panel=3, type='bar', color=macd_colors, width=0.7),
        ]

        if market_type == "crypto":
            title = f"\n{symbol}/USDT ({tf}) - Analisa Teknikal"
            ylabel = "Harga (USDT)"
        else:
            pair_info = FOREX_PAIRS.get(symbol, {"name": symbol})
            title = f"\n{symbol} - {pair_info['name']} ({tf}) - Analisa Teknikal"
            ylabel = "Harga"

        mpf.plot(
            df, type='candle', volume=True, style=style,
            title=title,
            ylabel=ylabel,
            ylabel_lower="Volume",
            savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
            figratio=(16, 12),
            figscale=1.5,
            tight_layout=True,
            addplot=addplots,
            warn_too_much_data=500,
            panel_ratios=(6, 2, 2, 2)
        )
        
        log_success(f"Chart {symbol} ({tf}) dibuat")
        return filename
        
    except Exception:
        return None


def get_timeframe_context(interval):
    """Mendapatkan konteks berdasarkan timeframe untuk analisa yang lebih akurat"""
    timeframe_configs = {
        "1min": {
            "name": "1 Menit",
            "type": "Scalping",
            "tp_range": "0.1% - 0.3%",
            "sl_range": "0.05% - 0.15%",
            "hold_time": "1-15 menit",
            "volatility": "sangat tinggi",
            "reliability": "rendah (noise tinggi)",
            "rr_ratio": "1:1 hingga 1:2"
        },
        "5min": {
            "name": "5 Menit",
            "type": "Scalping",
            "tp_range": "0.2% - 0.5%",
            "sl_range": "0.1% - 0.25%",
            "hold_time": "5-30 menit",
            "volatility": "tinggi",
            "reliability": "rendah-sedang",
            "rr_ratio": "1:1.5 hingga 1:2"
        },
        "15min": {
            "name": "15 Menit",
            "type": "Intraday",
            "tp_range": "0.3% - 0.8%",
            "sl_range": "0.15% - 0.4%",
            "hold_time": "15 menit - 2 jam",
            "volatility": "sedang-tinggi",
            "reliability": "sedang",
            "rr_ratio": "1:1.5 hingga 1:2.5"
        },
        "30min": {
            "name": "30 Menit",
            "type": "Intraday",
            "tp_range": "0.5% - 1.2%",
            "sl_range": "0.25% - 0.6%",
            "hold_time": "30 menit - 4 jam",
            "volatility": "sedang",
            "reliability": "sedang-baik",
            "rr_ratio": "1:2 hingga 1:3"
        },
        "1hour": {
            "name": "1 Jam",
            "type": "Swing Trading",
            "tp_range": "1% - 2.5%",
            "sl_range": "0.5% - 1.2%",
            "hold_time": "2-24 jam",
            "volatility": "sedang",
            "reliability": "baik",
            "rr_ratio": "1:2 hingga 1:3"
        },
        "4hour": {
            "name": "4 Jam",
            "type": "Swing Trading",
            "tp_range": "2% - 5%",
            "sl_range": "1% - 2.5%",
            "hold_time": "1-7 hari",
            "volatility": "sedang-rendah",
            "reliability": "baik-sangat baik",
            "rr_ratio": "1:2 hingga 1:4"
        },
        "1day": {
            "name": "Harian",
            "type": "Position Trading",
            "tp_range": "3% - 10%",
            "sl_range": "1.5% - 5%",
            "hold_time": "3-30 hari",
            "volatility": "rendah",
            "reliability": "sangat baik",
            "rr_ratio": "1:2 hingga 1:5"
        },
        "1week": {
            "name": "Mingguan",
            "type": "Position/Investment",
            "tp_range": "5% - 20%",
            "sl_range": "3% - 10%",
            "hold_time": "2-12 minggu",
            "volatility": "sangat rendah",
            "reliability": "sangat baik (tren utama)",
            "rr_ratio": "1:2 hingga 1:5"
        }
    }
    return timeframe_configs.get(interval, timeframe_configs["1hour"])


def analyze_with_gemini(image_path, symbol, market_type="crypto", interval="1hour"):
    """Analisa chart menggunakan Gemini Vision API dengan konteks timeframe"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY tidak ditemukan. Silakan set environment variable terlebih dahulu."
    
    if interval not in INTERVAL_MAP:
        logger.warning(f"Interval tidak valid: {interval}, menggunakan default 1hour")
        interval = "1hour"
    
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return f"File tidak ditemukan: {image_path}"
    except Exception as e:
        return f"Error membaca file: {e}"

    if market_type == "crypto":
        coin_info = SUPPORTED_COINS.get(symbol, {"name": symbol})
        asset_name = f"{symbol}/USDT ({coin_info.get('name', symbol)})"
    else:
        pair_info = FOREX_PAIRS.get(symbol, {"name": symbol})
        asset_name = f"{symbol} ({pair_info.get('name', symbol)})"

    tf_context = get_timeframe_context(interval)

    prompt = f"""Kamu adalah analis teknikal profesional. Analisa chart candlestick {asset_name} pada timeframe {tf_context['name']} ini.

KONTEKS TIMEFRAME {tf_context['name'].upper()}:
- Tipe Trading: {tf_context['type']}
- Target Profit Wajar: {tf_context['tp_range']} dari harga entry
- Stop Loss Wajar: {tf_context['sl_range']} dari harga entry
- Estimasi Waktu Hold: {tf_context['hold_time']}
- Volatilitas: {tf_context['volatility']}
- Keandalan Sinyal: {tf_context['reliability']}
- Rasio Risk:Reward yang Diharapkan: {tf_context['rr_ratio']}

INDIKATOR PADA CHART:
- EMA 20 (biru) dan EMA 50 (orange) - untuk identifikasi tren
- Bollinger Bands (ungu, garis putus-putus) - untuk volatilitas dan level overbought/oversold
- Fibonacci Retracement (garis kuning-orange) - untuk level support/resistance
- RSI (panel bawah pertama) - dengan level 70 (overbought) dan 30 (oversold)
- MACD (panel bawah kedua) - dengan histogram hijau (bullish) dan merah (bearish)

ATURAN ANALISA:
1. Sesuaikan jarak TP dan SL dengan karakteristik timeframe {tf_context['name']}
2. Prediksi arah harga HARUS konsisten dengan semua indikator
3. Jika indikator saling bertentangan, rekomendasikan TAHAN
4. Gunakan level Fibonacci dan Bollinger Band untuk menentukan target yang realistis
5. Pastikan rasio Risk:Reward minimal 1:1.5 untuk sinyal BELI/JUAL

Berikan analisa dalam format berikut (Bahasa Indonesia):

PREDIKSI ARAH: [NAIK/TURUN/SIDEWAYS] - [Persentase keyakinan: Tinggi/Sedang/Rendah]
SINYAL: [BELI/JUAL/TAHAN] - [Alasan berdasarkan minimal 2 indikator]
HARGA SAAT INI: [Harga terakhir yang terlihat di chart]
HARGA MASUK: [Harga entry optimal]
TARGET PROFIT 1: [Target pertama - jarak wajar untuk timeframe {tf_context['name']}]
TARGET PROFIT 2: [Target kedua - lebih ambisius tapi realistis]
STOP LOSS: [Harga SL berdasarkan support/resistance terdekat]
RASIO RR: [Risk:Reward ratio, misal 1:2]
WAKTU HOLD: [Estimasi waktu berdasarkan timeframe]
POLA: [Pola candlestick yang terlihat]
TREN: [Tren saat ini berdasarkan EMA: Naik Kuat/Naik Lemah/Turun Kuat/Turun Lemah/Sideways]
RSI: [Nilai dan kondisi: Overbought(>70)/Netral(30-70)/Oversold(<30)]
MACD: [Bullish Crossover/Bearish Crossover/Momentum Positif/Momentum Negatif/Netral]
BOLLINGER: [Di atas Upper Band/Di Middle Band/Di bawah Lower Band/Squeeze]
FIBONACCI: [Level Fib terdekat dan signifikansinya]
SUPPORT: [Level support 1 dan 2]
RESISTANCE: [Level resistance 1 dan 2]
KONFIRMASI: [Berapa indikator yang mendukung sinyal: X dari 5]
KESIMPULAN: [Ringkasan 2-3 kalimat yang menjelaskan mengapa prediksi ini masuk akal untuk timeframe {tf_context['name']}]

PENTING: Berikan angka SPESIFIK dan REALISTIS berdasarkan chart. Target profit harus dalam range {tf_context['tp_range']} sesuai timeframe {tf_context['name']}."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.8,
            "maxOutputTokens": 1024
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        log_analysis(f"Menganalisa {symbol} dengan AI...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    if text:
                        log_success(f"Analisa {symbol} selesai")
                        return text
            
            return "Format respons Gemini tidak sesuai. Coba lagi."
            
        elif response.status_code == 400:
            error_detail = response.json()
            return f"Error: Request tidak valid - {error_detail.get('error', {}).get('message', 'Tidak diketahui')}"
            
        elif response.status_code == 403:
            return "Error: API key tidak valid atau tidak memiliki akses"
            
        elif response.status_code == 429:
            return "Error: Batas permintaan tercapai. Tunggu beberapa saat dan coba lagi."
            
        else:
            return f"Error dari Gemini API (status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return "Timeout saat menghubungi Gemini API. Coba lagi."
    except requests.exceptions.RequestException as e:
        return f"Error koneksi: {e}"
    except Exception as e:
        return f"Error: {e}"


def format_analysis_reply(text):
    """Format hasil analisa menjadi lebih mudah dibaca"""
    if not text or text.startswith("Error") or text.startswith("Timeout"):
        return text
    
    text_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text_clean = re.sub(r'\*([^*]+)\*', r'\1', text_clean)
    text_clean = re.sub(r'`([^`]+)`', r'\1', text_clean)
    text_clean = re.sub(r'^\s*[-•]\s*', '', text_clean, flags=re.MULTILINE)
    
    section_keywords = [
        {'keywords': ['prediksi arah', 'prediksi'], 'emoji': '🔮', 'group': 'prediction'},
        {'keywords': ['sinyal', 'signal'], 'emoji': '📊', 'group': 'signal'},
        {'keywords': ['harga saat ini', 'harga sekarang', 'current price'], 'emoji': '💵', 'group': 'trading'},
        {'keywords': ['harga masuk', 'entry', 'masuk'], 'emoji': '🎯', 'group': 'trading'},
        {'keywords': ['target profit 1', 'tp1', 'tp 1'], 'emoji': '💰', 'group': 'trading'},
        {'keywords': ['target profit 2', 'tp2', 'tp 2'], 'emoji': '💎', 'group': 'trading'},
        {'keywords': ['target profit', 'take profit', 'target'], 'emoji': '💰', 'group': 'trading'},
        {'keywords': ['stop loss', 'stoploss', 'sl'], 'emoji': '🛑', 'group': 'trading'},
        {'keywords': ['rasio rr', 'rasio risk', 'risk reward', 'rr ratio'], 'emoji': '⚖️', 'group': 'trading'},
        {'keywords': ['waktu hold', 'holding time', 'durasi'], 'emoji': '⏱️', 'group': 'trading'},
        {'keywords': ['pola', 'pattern', 'candlestick'], 'emoji': '🕯️', 'group': 'analysis'},
        {'keywords': ['tren', 'trend'], 'emoji': '📈', 'group': 'analysis'},
        {'keywords': ['rsi'], 'emoji': '📉', 'group': 'indicators'},
        {'keywords': ['macd'], 'emoji': '📊', 'group': 'indicators'},
        {'keywords': ['bollinger', 'bb'], 'emoji': '〰️', 'group': 'indicators'},
        {'keywords': ['fibonacci', 'fib'], 'emoji': '🔢', 'group': 'indicators'},
        {'keywords': ['support', 's1', 's2'], 'emoji': '🔻', 'group': 'levels'},
        {'keywords': ['resistance', 'r1', 'r2'], 'emoji': '🔺', 'group': 'levels'},
        {'keywords': ['konfirmasi', 'confirmation'], 'emoji': '✅', 'group': 'confirmation'},
        {'keywords': ['kesimpulan', 'conclusion', 'ringkasan'], 'emoji': '🧠', 'group': 'conclusion'},
    ]
    
    sections = {
        'prediction': [],
        'signal': [],
        'trading': [],
        'analysis': [],
        'indicators': [],
        'levels': [],
        'confirmation': [],
        'conclusion': [],
        'other': []
    }
    
    lines = text_clean.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()
            value = parts[1].strip() if len(parts) > 1 else ''
            
            if not value:
                continue
            
            matched = False
            for config in section_keywords:
                for keyword in config['keywords']:
                    if keyword in key:
                        sections[config['group']].append(f"{config['emoji']} *{parts[0].strip().upper()}:*\n{value}")
                        matched = True
                        break
                if matched:
                    break
            
            if not matched and value and len(value) > 3:
                sections['other'].append(f"• {parts[0].strip()}: {value}")
    
    result_parts = []
    if sections['prediction']:
        result_parts.append('─── Prediksi Harga ───')
        result_parts.append('\n\n'.join(sections['prediction']))
    if sections['signal']:
        if result_parts:
            result_parts.append('')
        result_parts.append('\n\n'.join(sections['signal']))
    if sections['trading']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Setup Trading ───')
        result_parts.append('\n\n'.join(sections['trading']))
    if sections['levels']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Support & Resistance ───')
        result_parts.append('\n\n'.join(sections['levels']))
    if sections['analysis']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Analisa Teknikal ───')
        result_parts.append('\n\n'.join(sections['analysis']))
    if sections['indicators']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Indikator ───')
        result_parts.append('\n\n'.join(sections['indicators']))
    if sections['confirmation']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Konfirmasi Sinyal ───')
        result_parts.append('\n\n'.join(sections['confirmation']))
    if sections['conclusion']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Kesimpulan ───')
        result_parts.append('\n\n'.join(sections['conclusion']))
    
    return '\n'.join(result_parts) if result_parts else text


def get_main_menu_keyboard():
    """Generate keyboard untuk menu utama"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Cryptocurrency", callback_data='market_crypto')],
        [InlineKeyboardButton("💱 Forex & Komoditas", callback_data='market_forex')],
    ])


def get_crypto_keyboard():
    """Generate keyboard untuk pilihan cryptocurrency"""
    buttons = []
    row = []
    for symbol, info in SUPPORTED_COINS.items():
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'crypto_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='back_to_main')])
    return InlineKeyboardMarkup(buttons)


def get_forex_keyboard():
    """Generate keyboard untuk pilihan forex"""
    commodities = [s for s, info in FOREX_PAIRS.items() if info["category"] == "commodity"]
    majors = [s for s, info in FOREX_PAIRS.items() if info["category"] == "major"]
    crosses = [s for s, info in FOREX_PAIRS.items() if info["category"] == "cross"]
    
    buttons = []
    
    buttons.append([InlineKeyboardButton("─── Komoditas ───", callback_data='ignore')])
    row = []
    for symbol in commodities:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'forex_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("─── Pasangan Utama ───", callback_data='ignore')])
    row = []
    for symbol in majors:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'forex_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("─── Pasangan Silang ───", callback_data='ignore')])
    row = []
    for symbol in crosses:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'forex_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='back_to_main')])
    return InlineKeyboardMarkup(buttons)


def get_timeframe_keyboard(symbol, market_type):
    """Generate keyboard untuk pilihan timeframe"""
    if market_type == "crypto":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1m", callback_data=f'tf_crypto_{symbol}_1min'),
                InlineKeyboardButton("5m", callback_data=f'tf_crypto_{symbol}_5min'),
                InlineKeyboardButton("15m", callback_data=f'tf_crypto_{symbol}_15min'),
                InlineKeyboardButton("30m", callback_data=f'tf_crypto_{symbol}_30min'),
            ],
            [
                InlineKeyboardButton("1j", callback_data=f'tf_crypto_{symbol}_1hour'),
                InlineKeyboardButton("4j", callback_data=f'tf_crypto_{symbol}_4hour'),
                InlineKeyboardButton("1h", callback_data=f'tf_crypto_{symbol}_1day'),
                InlineKeyboardButton("1mg", callback_data=f'tf_crypto_{symbol}_1week'),
            ],
            [
                InlineKeyboardButton("⬅️ Kembali ke Daftar Koin", callback_data='market_crypto'),
            ],
        ])
    else:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1m", callback_data=f'tf_forex_{symbol}_1min'),
                InlineKeyboardButton("5m", callback_data=f'tf_forex_{symbol}_5min'),
                InlineKeyboardButton("15m", callback_data=f'tf_forex_{symbol}_15min'),
                InlineKeyboardButton("30m", callback_data=f'tf_forex_{symbol}_30min'),
            ],
            [
                InlineKeyboardButton("1j", callback_data=f'tf_forex_{symbol}_1hour'),
                InlineKeyboardButton("4j", callback_data=f'tf_forex_{symbol}_4hour'),
                InlineKeyboardButton("1h", callback_data=f'tf_forex_{symbol}_1day'),
            ],
            [
                InlineKeyboardButton("⬅️ Kembali ke Daftar Pair", callback_data='market_forex'),
            ],
        ])


def get_after_analysis_keyboard(symbol, market_type):
    """Generate keyboard setelah analisa"""
    if market_type == "crypto":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔄 Analisa {symbol} Lagi", callback_data=f'crypto_{symbol}')],
            [InlineKeyboardButton("💰 Pilih Koin Lain", callback_data='market_crypto')],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_main')],
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔄 Analisa {symbol} Lagi", callback_data=f'forex_{symbol}')],
            [InlineKeyboardButton("💱 Pilih Pair Lain", callback_data='market_forex')],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_main')],
        ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    welcome_text = """📊 *Bot Analisa Teknikal Trading*
━━━━━━━━━━━━━━━━━━━━

Selamat datang! Bot ini menyediakan analisa teknikal menggunakan AI untuk:

💰 *Cryptocurrency* - 14 koin populer
   BTC, ETH, SOL, BNB, XRP, dan lainnya

💱 *Forex & Komoditas* - 16 pasangan
   Emas, Perak, EUR/USD, GBP/USD, dan lainnya

*Fitur:*
• Chart candlestick real-time
• Indikator: EMA, RSI, MACD, Bollinger Bands
• Fibonacci Retracement
• Analisa AI dengan Gemini Vision
• Sinyal BELI/JUAL/TAHAN

━━━━━━━━━━━━━━━━━━━━
*Pilih pasar untuk memulai:*"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )


async def handle_market_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback pilihan pasar"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'market_crypto':
        await query.edit_message_text(
            "💰 *Pilih Cryptocurrency untuk Analisa:*",
            reply_markup=get_crypto_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == 'market_forex':
        await query.edit_message_text(
            "💱 *Pilih Pair Forex/Komoditas untuk Analisa:*",
            reply_markup=get_forex_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == 'back_to_main':
        welcome_text = """📊 *Bot Analisa Teknikal Trading*
━━━━━━━━━━━━━━━━━━━━

*Pilih pasar untuk memulai:*"""
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == 'ignore':
        return


async def handle_crypto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback pilihan crypto"""
    query = update.callback_query
    await query.answer()
    
    symbol = query.data.replace('crypto_', '')
    
    if symbol not in SUPPORTED_COINS:
        return
    
    info = SUPPORTED_COINS[symbol]
    context.user_data['selected_symbol'] = symbol
    context.user_data['market_type'] = 'crypto'
    
    current_price = get_crypto_price(symbol)
    price_text = f"💵 Harga saat ini: ${current_price:,.2f}" if current_price else ""
    
    await query.edit_message_text(
        f"{info['emoji']} *{symbol} - {info['name']}*\n{price_text}\n\n*Pilih timeframe:*",
        reply_markup=get_timeframe_keyboard(symbol, 'crypto'),
        parse_mode='Markdown'
    )


async def handle_forex_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback pilihan forex"""
    query = update.callback_query
    await query.answer()
    
    symbol = query.data.replace('forex_', '')
    
    if symbol not in FOREX_PAIRS:
        return
    
    info = FOREX_PAIRS[symbol]
    context.user_data['selected_symbol'] = symbol
    context.user_data['market_type'] = 'forex'
    
    current_price = get_forex_price(symbol)
    if current_price:
        if info["category"] == "commodity":
            price_text = f"💵 Harga saat ini: ${current_price:,.2f}"
        else:
            price_text = f"💵 Harga saat ini: {current_price:.5f}"
    else:
        price_text = ""
    
    await query.edit_message_text(
        f"{info['emoji']} *{symbol} - {info['name']}*\n{price_text}\n\n*Pilih timeframe:*",
        reply_markup=get_timeframe_keyboard(symbol, 'forex'),
        parse_mode='Markdown'
    )


async def handle_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback pilihan timeframe"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.replace('tf_', '').split('_')
    if len(parts) < 3:
        return
    
    market_type = parts[0]
    symbol = parts[1]
    interval = parts[2]
    
    if market_type == "crypto":
        if symbol not in SUPPORTED_COINS or interval not in INTERVAL_MAP:
            return
        info = SUPPORTED_COINS[symbol]
    else:
        if symbol not in FOREX_PAIRS or interval not in INTERVAL_MAP:
            return
        if interval == "1week":
            await query.edit_message_text(
                "❌ Timeframe mingguan tidak tersedia untuk Forex.\n\n*Pilih timeframe lain:*",
                reply_markup=get_timeframe_keyboard(symbol, 'forex'),
                parse_mode='Markdown'
            )
            return
        info = FOREX_PAIRS[symbol]
    
    chat_id = query.message.chat_id
    current_message_id = query.message.message_id
    
    for key in ['last_chart_message_id', 'last_analysis_message_id', 'last_button_message_id']:
        if key in context.user_data:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data[key])
            except:
                pass
            context.user_data.pop(key, None)
    
    status_message = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ Mengambil data {info['emoji']} {symbol} ({interval})..."
    )
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
    except:
        pass
    
    if market_type == "crypto":
        data = fetch_crypto_data(symbol, interval)
    else:
        data = fetch_forex_data(symbol, interval)
    
    if not data:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Gagal mengambil data {symbol}. Coba lagi nanti.\n\n{info['emoji']} Pilih timeframe lain:",
            reply_markup=get_timeframe_keyboard(symbol, market_type)
        )
        return
    
    if len(data) < 20:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Data terlalu sedikit ({len(data)} candle). Coba timeframe lain.",
            reply_markup=get_timeframe_keyboard(symbol, market_type)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"📊 Membuat chart {info['emoji']} {symbol} ({interval})..."
    )
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_chart(data, filename, symbol, interval, market_type)
    
    if not chart_path:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Gagal membuat chart.\n\n{info['emoji']} Pilih timeframe:",
            reply_markup=get_timeframe_keyboard(symbol, market_type)
        )
        return
    
    try:
        with open(chart_path, "rb") as photo:
            if market_type == "crypto":
                caption = f"{info['emoji']} {symbol}/USDT ({interval})"
            else:
                caption = f"{info['emoji']} {symbol} - {info['name']} ({interval})"
            
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
            context.user_data['last_chart_message_id'] = photo_message.message_id
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal mengirim chart.",
            reply_markup=get_timeframe_keyboard(symbol, market_type)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"🤖 Menganalisa chart {symbol} dengan AI..."
    )
    
    analysis = analyze_with_gemini(chart_path, symbol, market_type, interval)
    formatted = format_analysis_reply(analysis)
    
    if market_type == "crypto":
        result_text = f"""{info['emoji']} *Hasil Analisa {symbol}/USDT ({interval})*
━━━━━━━━━━━━━━━━━━━━

{formatted}

━━━━━━━━━━━━━━━━━━━━
⚠️ _Peringatan: Ini bukan saran keuangan._"""
    else:
        result_text = f"""{info['emoji']} *Hasil Analisa {symbol} ({interval})*
━━━━━━━━━━━━━━━━━━━━

{formatted}

━━━━━━━━━━━━━━━━━━━━
⚠️ _Peringatan: Ini bukan saran keuangan._"""
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=result_text,
            parse_mode='Markdown'
        )
        context.user_data['last_analysis_message_id'] = status_message.message_id
    except:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=result_text.replace('*', '').replace('_', '')
        )
    
    try:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="📊 *Lanjutkan analisa:*",
            parse_mode='Markdown',
            reply_markup=get_after_analysis_keyboard(symbol, market_type)
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    except:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="📊 Lanjutkan analisa:",
            reply_markup=get_after_analysis_keyboard(symbol, market_type)
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /analyze [symbol] [timeframe]"""
    args = context.args
    
    if len(args) < 2:
        crypto_list = ", ".join(SUPPORTED_COINS.keys())
        forex_list = ", ".join(FOREX_PAIRS.keys())
        await update.message.reply_text(
            f"📊 *Cara Penggunaan:*\n"
            f"/analyze <simbol> <timeframe>\n\n"
            f"*Contoh:*\n"
            f"/analyze BTC 15min\n"
            f"/analyze XAUUSD 1hour\n\n"
            f"*Cryptocurrency:*\n{crypto_list}\n\n"
            f"*Forex & Komoditas:*\n{forex_list}\n\n"
            f"*Timeframe:*\n1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week",
            parse_mode='Markdown'
        )
        return
    
    symbol = args[0].upper()
    interval = args[1].lower()
    
    if symbol in SUPPORTED_COINS:
        market_type = "crypto"
        info = SUPPORTED_COINS[symbol]
    elif symbol in FOREX_PAIRS:
        market_type = "forex"
        info = FOREX_PAIRS[symbol]
        if interval == "1week":
            await update.message.reply_text("❌ Timeframe mingguan tidak tersedia untuk Forex.")
            return
    else:
        await update.message.reply_text(
            f"❌ Simbol tidak valid: {symbol}\n"
            f"Gunakan /analyze untuk melihat daftar simbol."
        )
        return
    
    if interval not in INTERVAL_MAP:
        await update.message.reply_text(
            f"❌ Timeframe tidak valid: {interval}\n"
            f"Gunakan: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week"
        )
        return
    
    await update.message.reply_text(f"⏳ Mengambil data {info['emoji']} {symbol} ({interval})...")
    
    if market_type == "crypto":
        data = fetch_crypto_data(symbol, interval)
    else:
        data = fetch_forex_data(symbol, interval)
    
    if not data or len(data) < 20:
        await update.message.reply_text("❌ Gagal mengambil data atau data terlalu sedikit.")
        return
    
    await update.message.reply_text("📊 Membuat chart...")
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_chart(data, filename, symbol, interval, market_type)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        if market_type == "crypto":
            caption = f"{info['emoji']} {symbol}/USDT ({interval})\n⏳ Menganalisa..."
        else:
            caption = f"{info['emoji']} {symbol} ({interval})\n⏳ Menganalisa..."
        await update.message.reply_photo(photo=photo, caption=caption)
    
    analysis = analyze_with_gemini(chart_path, symbol, market_type, interval)
    formatted = format_analysis_reply(analysis)
    
    await update.message.reply_text(
        f"{info['emoji']} Hasil Analisa {symbol} ({interval}):\n\n{formatted}\n\n"
        "⚠️ Peringatan: Ini bukan saran keuangan.",
        reply_markup=get_after_analysis_keyboard(symbol, market_type)
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /price [symbol]"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "📊 *Cara Penggunaan:*\n"
            "/price <simbol>\n\n"
            "*Contoh:*\n"
            "/price BTC\n"
            "/price XAUUSD",
            parse_mode='Markdown'
        )
        return
    
    symbol = args[0].upper()
    
    if symbol in SUPPORTED_COINS:
        info = SUPPORTED_COINS[symbol]
        price = get_crypto_price(symbol)
        if price:
            await update.message.reply_text(
                f"{info['emoji']} *Harga {symbol} ({info['name']}) Saat Ini*\n\n"
                f"💵 *${price:,.2f}*",
                parse_mode='Markdown',
                reply_markup=get_timeframe_keyboard(symbol, 'crypto')
            )
        else:
            await update.message.reply_text(f"❌ Gagal mengambil harga {symbol}. Coba lagi nanti.")
    elif symbol in FOREX_PAIRS:
        info = FOREX_PAIRS[symbol]
        price = get_forex_price(symbol)
        if price:
            if info["category"] == "commodity":
                price_str = f"${price:,.2f}"
            else:
                price_str = f"{price:.5f}"
            await update.message.reply_text(
                f"{info['emoji']} *Harga {symbol} ({info['name']}) Saat Ini*\n\n"
                f"💵 *{price_str}*",
                parse_mode='Markdown',
                reply_markup=get_timeframe_keyboard(symbol, 'forex')
            )
        else:
            await update.message.reply_text(f"❌ Gagal mengambil harga {symbol}. Coba lagi nanti.")
    else:
        await update.message.reply_text(f"❌ Simbol tidak valid: {symbol}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    crypto_list = ", ".join(SUPPORTED_COINS.keys())
    forex_list = ", ".join(FOREX_PAIRS.keys())
    
    help_text = f"""📖 *Panduan Penggunaan Bot*

*Perintah:*
/start - Mulai bot dan pilih pasar
/analyze <simbol> <tf> - Analisa langsung
/price <simbol> - Lihat harga terkini
/help - Tampilkan bantuan ini

*Contoh:*
/analyze BTC 15min
/analyze XAUUSD 4hour
/price ETH

*Cryptocurrency ({len(SUPPORTED_COINS)}):*
{crypto_list}

*Forex & Komoditas ({len(FOREX_PAIRS)}):*
{forex_list}

*Timeframe:*
1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week

*Fitur:*
• Chart candlestick dengan EMA20 & EMA50
• Bollinger Bands & Fibonacci
• Indikator RSI dan MACD
• Analisa AI menggunakan Gemini Vision
• Sinyal BELI/JUAL/TAHAN
• Harga masuk, Target Profit, Stop Loss

*Sumber Data:*
• TradingView - Data candlestick historical
• Yahoo Finance - Sumber data cadangan
• KuCoin - Sumber data cadangan crypto
• Google Gemini Vision - Analisa AI

⚠️ *Peringatan:* Bot ini hanya untuk edukasi. Bukan saran keuangan."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Exception saat menangani update: {context.error}")
    
    if "Conflict" in str(context.error):
        logger.warning("Konflik bot terdeteksi - mungkin ada instance lain yang berjalan")


def main():
    """Fungsi utama untuk menjalankan bot"""
    print_banner()
    
    print(f"{Colors.WHITE}{Colors.BOLD}  Memeriksa konfigurasi...{Colors.RESET}")
    print()
    
    if not TELEGRAM_BOT_TOKEN:
        log_error("TELEGRAM_BOT_TOKEN tidak ditemukan!")
        log_info("Set di Replit Secrets: TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    else:
        log_success("Telegram Bot Token terkonfigurasi")
    
    if not GEMINI_API_KEY:
        log_warning("GEMINI_API_KEY tidak ditemukan - Analisa AI tidak aktif")
    else:
        log_success("Gemini API Key terkonfigurasi")
    
    print()
    print(f"{Colors.WHITE}{Colors.BOLD}  Status Sistem:{Colors.RESET}")
    print()
    
    if TV_AVAILABLE:
        log_success(f"TradingView: Aktif")
    else:
        log_warning(f"TradingView: Tidak tersedia (fallback ke Yahoo/KuCoin)")
    
    if yf:
        log_success(f"Yahoo Finance: Aktif")
    else:
        log_warning(f"Yahoo Finance: Tidak tersedia")
    
    log_info(f"Cryptocurrency: {len(SUPPORTED_COINS)} koin didukung")
    log_info(f"Forex & Komoditas: {len(FOREX_PAIRS)} pasangan didukung")
    
    print()
    print(f"{Colors.WHITE}{Colors.BOLD}  Memulai bot...{Colors.RESET}")
    print()
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    
    app.add_handler(CallbackQueryHandler(handle_market_callback, pattern=r'^(market_|back_to_main|ignore)'))
    app.add_handler(CallbackQueryHandler(handle_crypto_callback, pattern=r'^crypto_'))
    app.add_handler(CallbackQueryHandler(handle_forex_callback, pattern=r'^forex_'))
    app.add_handler(CallbackQueryHandler(handle_timeframe_callback, pattern=r'^tf_'))
    
    app.add_error_handler(error_handler)
    
    log_success("Bot siap menerima pesan!")
    print()
    print(f"{Colors.GREEN}{Colors.BOLD}  ══════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.GREEN}  Bot berjalan... Tekan Ctrl+C untuk berhenti{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  ══════════════════════════════════════════{Colors.RESET}")
    print()
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
