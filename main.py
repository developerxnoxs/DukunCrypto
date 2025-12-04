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


def calculate_atr(df, period=14):
    """Menghitung ATR (Average True Range) - untuk volatilitas dan penentuan SL/TP"""
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def calculate_stochastic_rsi(series, rsi_period=14, stoch_period=14, smooth_k=3, smooth_d=3):
    """Menghitung Stochastic RSI - lebih sensitif dari RSI biasa"""
    rsi = calculate_rsi(series, rsi_period)
    
    rsi_min = rsi.rolling(window=stoch_period).min()
    rsi_max = rsi.rolling(window=stoch_period).max()
    
    stoch_rsi = ((rsi - rsi_min) / (rsi_max - rsi_min)) * 100
    stoch_rsi = stoch_rsi.fillna(50)
    
    stoch_k = stoch_rsi.rolling(window=smooth_k).mean()
    stoch_d = stoch_k.rolling(window=smooth_d).mean()
    
    return stoch_k, stoch_d


def calculate_adx(df, period=14):
    """Menghitung ADX (Average Directional Index) - mengukur kekuatan tren"""
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return adx, plus_di, minus_di


def calculate_vwap(df):
    """Menghitung VWAP (Volume Weighted Average Price)"""
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
    return vwap


def calculate_ema(series, period):
    """Menghitung EMA dengan period tertentu"""
    return series.ewm(span=period, adjust=False).mean()


def detect_rsi_divergence(df, rsi, lookback=10):
    """Mendeteksi RSI divergence (bullish/bearish)"""
    close = df['Close']
    divergence = []
    
    for i in range(lookback, len(df)):
        price_window = close.iloc[i-lookback:i+1]
        rsi_window = rsi.iloc[i-lookback:i+1]
        
        price_min_idx = price_window.idxmin()
        price_max_idx = price_window.idxmax()
        
        current_price = close.iloc[i]
        current_rsi = rsi.iloc[i]
        
        if current_price <= price_window.min() * 1.01:
            rsi_at_prev_low = rsi.loc[price_min_idx] if price_min_idx in rsi.index else current_rsi
            if current_rsi > rsi_at_prev_low:
                divergence.append("bullish")
                continue
        
        if current_price >= price_window.max() * 0.99:
            rsi_at_prev_high = rsi.loc[price_max_idx] if price_max_idx in rsi.index else current_rsi
            if current_rsi < rsi_at_prev_high:
                divergence.append("bearish")
                continue
        
        divergence.append("none")
    
    result = ['none'] * lookback + divergence
    return result[-1] if result else "none"


def detect_macd_divergence(df, macd_line, lookback=10):
    """Mendeteksi MACD divergence (bullish/bearish)"""
    close = df['Close']
    
    for i in range(lookback, len(df)):
        price_window = close.iloc[i-lookback:i+1]
        macd_window = macd_line.iloc[i-lookback:i+1]
        
        current_price = close.iloc[i]
        current_macd = macd_line.iloc[i]
        
        if current_price <= price_window.min() * 1.01:
            prev_macd_at_low = macd_window.min()
            if current_macd > prev_macd_at_low:
                return "bullish"
        
        if current_price >= price_window.max() * 0.99:
            prev_macd_at_high = macd_window.max()
            if current_macd < prev_macd_at_high:
                return "bearish"
    
    return "none"


def calculate_confluence_score(df, market_type="crypto"):
    """Menghitung skor konfluensi dari berbagai indikator untuk sinyal trading"""
    close = df['Close']
    current_price = close.iloc[-1]
    
    ema20 = calculate_ema(close, 20)
    ema50 = calculate_ema(close, 50)
    ema200 = calculate_ema(close, 200)
    
    rsi = calculate_rsi(close, 14)
    current_rsi = rsi.iloc[-1]
    
    macd_line, signal_line, histogram = calculate_macd(close)
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    current_hist = histogram.iloc[-1]
    prev_hist = histogram.iloc[-2] if len(histogram) > 1 else 0
    
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    
    stoch_k, stoch_d = calculate_stochastic_rsi(close)
    current_stoch_k = stoch_k.iloc[-1]
    current_stoch_d = stoch_d.iloc[-1]
    
    adx, plus_di, minus_di = calculate_adx(df)
    current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 20
    current_plus_di = plus_di.iloc[-1] if not pd.isna(plus_di.iloc[-1]) else 25
    current_minus_di = minus_di.iloc[-1] if not pd.isna(minus_di.iloc[-1]) else 25
    
    atr = calculate_atr(df)
    current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
    
    rsi_divergence = detect_rsi_divergence(df, rsi)
    macd_divergence = detect_macd_divergence(df, macd_line)
    
    bullish_signals = 0
    bearish_signals = 0
    neutral_signals = 0
    total_weight = 0
    
    signal_details = {
        "bullish": [],
        "bearish": [],
        "neutral": []
    }
    
    weight = 2
    total_weight += weight
    if current_price > ema20.iloc[-1] and current_price > ema50.iloc[-1]:
        bullish_signals += weight
        signal_details["bullish"].append("Harga di atas EMA20 & EMA50")
    elif current_price < ema20.iloc[-1] and current_price < ema50.iloc[-1]:
        bearish_signals += weight
        signal_details["bearish"].append("Harga di bawah EMA20 & EMA50")
    else:
        neutral_signals += weight
        signal_details["neutral"].append("Harga di antara EMA20 & EMA50")
    
    if len(ema200) > 0 and not pd.isna(ema200.iloc[-1]):
        weight = 1.5
        total_weight += weight
        if current_price > ema200.iloc[-1]:
            bullish_signals += weight
            signal_details["bullish"].append("Harga di atas EMA200 (tren jangka panjang bullish)")
        else:
            bearish_signals += weight
            signal_details["bearish"].append("Harga di bawah EMA200 (tren jangka panjang bearish)")
    
    weight = 1.5
    total_weight += weight
    if ema20.iloc[-1] > ema50.iloc[-1]:
        if ema20.iloc[-2] <= ema50.iloc[-2]:
            bullish_signals += weight * 1.5
            signal_details["bullish"].append("Golden Cross EMA20/EMA50 (sinyal kuat)")
        else:
            bullish_signals += weight
            signal_details["bullish"].append("EMA20 di atas EMA50")
    else:
        if ema20.iloc[-2] >= ema50.iloc[-2]:
            bearish_signals += weight * 1.5
            signal_details["bearish"].append("Death Cross EMA20/EMA50 (sinyal kuat)")
        else:
            bearish_signals += weight
            signal_details["bearish"].append("EMA20 di bawah EMA50")
    
    weight = 2
    total_weight += weight
    if current_rsi < 30:
        bullish_signals += weight
        signal_details["bullish"].append(f"RSI oversold ({current_rsi:.1f})")
    elif current_rsi > 70:
        bearish_signals += weight
        signal_details["bearish"].append(f"RSI overbought ({current_rsi:.1f})")
    elif current_rsi > 50:
        bullish_signals += weight * 0.5
        signal_details["bullish"].append(f"RSI bullish zone ({current_rsi:.1f})")
    else:
        bearish_signals += weight * 0.5
        signal_details["bearish"].append(f"RSI bearish zone ({current_rsi:.1f})")
    
    weight = 2
    total_weight += weight
    if current_macd > current_signal:
        if macd_line.iloc[-2] <= signal_line.iloc[-2]:
            bullish_signals += weight * 1.5
            signal_details["bullish"].append("MACD Bullish Crossover (sinyal beli)")
        else:
            bullish_signals += weight
            signal_details["bullish"].append("MACD di atas Signal Line")
    else:
        if macd_line.iloc[-2] >= signal_line.iloc[-2]:
            bearish_signals += weight * 1.5
            signal_details["bearish"].append("MACD Bearish Crossover (sinyal jual)")
        else:
            bearish_signals += weight
            signal_details["bearish"].append("MACD di bawah Signal Line")
    
    weight = 1
    total_weight += weight
    if current_hist > 0 and current_hist > prev_hist:
        bullish_signals += weight
        signal_details["bullish"].append("MACD histogram meningkat (momentum bullish)")
    elif current_hist < 0 and current_hist < prev_hist:
        bearish_signals += weight
        signal_details["bearish"].append("MACD histogram menurun (momentum bearish)")
    else:
        neutral_signals += weight
        signal_details["neutral"].append("MACD histogram netral")
    
    weight = 1.5
    total_weight += weight
    if current_price <= bb_lower.iloc[-1]:
        bullish_signals += weight
        signal_details["bullish"].append("Harga di bawah Lower Bollinger Band (oversold)")
    elif current_price >= bb_upper.iloc[-1]:
        bearish_signals += weight
        signal_details["bearish"].append("Harga di atas Upper Bollinger Band (overbought)")
    else:
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        if bb_position < 0.3:
            bullish_signals += weight * 0.5
            signal_details["bullish"].append("Harga mendekati Lower BB")
        elif bb_position > 0.7:
            bearish_signals += weight * 0.5
            signal_details["bearish"].append("Harga mendekati Upper BB")
        else:
            neutral_signals += weight
            signal_details["neutral"].append("Harga di tengah Bollinger Bands")
    
    weight = 1.5
    total_weight += weight
    if current_stoch_k < 20:
        bullish_signals += weight
        signal_details["bullish"].append(f"Stochastic RSI oversold ({current_stoch_k:.1f})")
    elif current_stoch_k > 80:
        bearish_signals += weight
        signal_details["bearish"].append(f"Stochastic RSI overbought ({current_stoch_k:.1f})")
    elif current_stoch_k > current_stoch_d:
        bullish_signals += weight * 0.5
        signal_details["bullish"].append("Stochastic RSI bullish")
    else:
        bearish_signals += weight * 0.5
        signal_details["bearish"].append("Stochastic RSI bearish")
    
    weight = 1.5
    total_weight += weight
    if current_adx > 25:
        if current_plus_di > current_minus_di:
            bullish_signals += weight
            signal_details["bullish"].append(f"ADX kuat ({current_adx:.1f}) dengan +DI dominan")
        else:
            bearish_signals += weight
            signal_details["bearish"].append(f"ADX kuat ({current_adx:.1f}) dengan -DI dominan")
    else:
        neutral_signals += weight
        signal_details["neutral"].append(f"ADX lemah ({current_adx:.1f}) - tren tidak jelas")
    
    weight = 2
    if rsi_divergence == "bullish":
        bullish_signals += weight
        signal_details["bullish"].append("RSI Bullish Divergence terdeteksi (sinyal reversal)")
    elif rsi_divergence == "bearish":
        bearish_signals += weight
        signal_details["bearish"].append("RSI Bearish Divergence terdeteksi (sinyal reversal)")
    
    if macd_divergence == "bullish":
        bullish_signals += weight
        signal_details["bullish"].append("MACD Bullish Divergence terdeteksi")
    elif macd_divergence == "bearish":
        bearish_signals += weight
        signal_details["bearish"].append("MACD Bearish Divergence terdeteksi")
    
    total_signals = bullish_signals + bearish_signals + neutral_signals
    
    if total_signals > 0:
        bullish_pct = (bullish_signals / total_signals) * 100
        bearish_pct = (bearish_signals / total_signals) * 100
    else:
        bullish_pct = 50
        bearish_pct = 50
    
    if bullish_signals > bearish_signals * 1.3:
        if bullish_pct >= 70:
            signal = "STRONG_BUY"
            confidence = "TINGGI"
        else:
            signal = "BUY"
            confidence = "SEDANG"
    elif bearish_signals > bullish_signals * 1.3:
        if bearish_pct >= 70:
            signal = "STRONG_SELL"
            confidence = "TINGGI"
        else:
            signal = "SELL"
            confidence = "SEDANG"
    else:
        signal = "HOLD"
        confidence = "RENDAH"
    
    trend_strength = "TIDAK JELAS"
    if current_adx > 40:
        trend_strength = "SANGAT KUAT"
    elif current_adx > 25:
        trend_strength = "KUAT"
    elif current_adx > 20:
        trend_strength = "SEDANG"
    else:
        trend_strength = "LEMAH"
    
    if current_price > ema20.iloc[-1] > ema50.iloc[-1]:
        trend_direction = "UPTREND"
    elif current_price < ema20.iloc[-1] < ema50.iloc[-1]:
        trend_direction = "DOWNTREND"
    else:
        trend_direction = "SIDEWAYS"
    
    atr_pct = (current_atr / current_price) * 100 if current_price > 0 else 0
    
    return {
        "signal": signal,
        "confidence": confidence,
        "bullish_score": bullish_signals,
        "bearish_score": bearish_signals,
        "neutral_score": neutral_signals,
        "bullish_pct": bullish_pct,
        "bearish_pct": bearish_pct,
        "trend_direction": trend_direction,
        "trend_strength": trend_strength,
        "adx": current_adx,
        "rsi": current_rsi,
        "stoch_rsi": current_stoch_k,
        "atr": current_atr,
        "atr_pct": atr_pct,
        "rsi_divergence": rsi_divergence,
        "macd_divergence": macd_divergence,
        "signal_details": signal_details,
        "ema20": ema20.iloc[-1],
        "ema50": ema50.iloc[-1],
        "ema200": ema200.iloc[-1] if len(ema200) > 0 and not pd.isna(ema200.iloc[-1]) else None,
        "bb_upper": bb_upper.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "bb_middle": bb_middle.iloc[-1],
        "macd": current_macd,
        "macd_signal": current_signal,
        "macd_hist": current_hist
    }


def generate_chart(data, filename="chart.png", symbol="BTC", tf="15min", market_type="crypto"):
    """Generate chart candlestick dengan RSI, MACD, Bollinger Bands, Fibonacci, Stochastic RSI, dan EMA200"""
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
        ema200 = df['Close'].ewm(span=200, adjust=False).mean()
        
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
        
        rsi = calculate_rsi(df['Close'])
        rsi_overbought = pd.Series([70] * len(df), index=df.index)
        rsi_oversold = pd.Series([30] * len(df), index=df.index)
        rsi_middle = pd.Series([50] * len(df), index=df.index)
        
        stoch_k, stoch_d = calculate_stochastic_rsi(df['Close'])
        stoch_overbought = pd.Series([80] * len(df), index=df.index)
        stoch_oversold = pd.Series([20] * len(df), index=df.index)
        
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
            mpf.make_addplot(ema200, color='red', width=1.5, linestyle='-'),
            
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
            mpf.make_addplot(rsi_middle, panel=2, color='gray', width=0.3, linestyle=':'),
            
            mpf.make_addplot(stoch_k, panel=3, color='#2196F3', width=1.2, ylabel='Stoch RSI'),
            mpf.make_addplot(stoch_d, panel=3, color='#FF9800', width=1),
            mpf.make_addplot(stoch_overbought, panel=3, color='red', width=0.5, linestyle='--'),
            mpf.make_addplot(stoch_oversold, panel=3, color='green', width=0.5, linestyle='--'),
            
            mpf.make_addplot(macd_line, panel=4, color='blue', width=1, ylabel='MACD'),
            mpf.make_addplot(signal_line, panel=4, color='red', width=1),
            mpf.make_addplot(macd_histogram, panel=4, type='bar', color=macd_colors, width=0.7),
        ]

        if market_type == "crypto":
            ylabel = "Harga (USDT)"
        else:
            ylabel = "Harga"

        mpf.plot(
            df, type='candle', volume=True, style=style,
            ylabel=ylabel,
            ylabel_lower="Volume",
            savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
            figratio=(16, 14),
            figscale=1.5,
            tight_layout=True,
            addplot=addplots,
            warn_too_much_data=500,
            panel_ratios=(6, 2, 1.5, 1.5, 1.5)
        )
        
        log_success(f"Chart {symbol} ({tf}) dibuat")
        return filename
        
    except Exception:
        return None


def generate_chart_with_confluence(data, filename="chart.png", symbol="BTC", tf="15min", market_type="crypto"):
    """Generate chart dan hitung confluence score"""
    if not data:
        return None, None
    
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
        
        confluence = calculate_confluence_score(df, market_type)
        
        chart_path = generate_chart(data, filename, symbol, tf, market_type)
        
        return chart_path, confluence
        
    except Exception:
        return None, None


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
            "rr_ratio": "1:1 hingga 1:2",
            "next_candle": "1 menit ke depan",
            "prediction_horizon": "1-5 menit"
        },
        "5min": {
            "name": "5 Menit",
            "type": "Scalping",
            "tp_range": "0.2% - 0.5%",
            "sl_range": "0.1% - 0.25%",
            "hold_time": "5-30 menit",
            "volatility": "tinggi",
            "reliability": "rendah-sedang",
            "rr_ratio": "1:1.5 hingga 1:2",
            "next_candle": "5 menit ke depan",
            "prediction_horizon": "5-15 menit"
        },
        "15min": {
            "name": "15 Menit",
            "type": "Intraday",
            "tp_range": "0.3% - 0.8%",
            "sl_range": "0.15% - 0.4%",
            "hold_time": "15 menit - 2 jam",
            "volatility": "sedang-tinggi",
            "reliability": "sedang",
            "rr_ratio": "1:1.5 hingga 1:2.5",
            "next_candle": "15 menit ke depan",
            "prediction_horizon": "15-45 menit"
        },
        "30min": {
            "name": "30 Menit",
            "type": "Intraday",
            "tp_range": "0.5% - 1.2%",
            "sl_range": "0.25% - 0.6%",
            "hold_time": "30 menit - 4 jam",
            "volatility": "sedang",
            "reliability": "sedang-baik",
            "rr_ratio": "1:2 hingga 1:3",
            "next_candle": "30 menit ke depan",
            "prediction_horizon": "30-90 menit"
        },
        "1hour": {
            "name": "1 Jam",
            "type": "Swing Trading",
            "tp_range": "1% - 2.5%",
            "sl_range": "0.5% - 1.2%",
            "hold_time": "2-24 jam",
            "volatility": "sedang",
            "reliability": "baik",
            "rr_ratio": "1:2 hingga 1:3",
            "next_candle": "1 jam ke depan",
            "prediction_horizon": "1-4 jam"
        },
        "4hour": {
            "name": "4 Jam",
            "type": "Swing Trading",
            "tp_range": "2% - 5%",
            "sl_range": "1% - 2.5%",
            "hold_time": "1-7 hari",
            "volatility": "sedang-rendah",
            "reliability": "baik-sangat baik",
            "rr_ratio": "1:2 hingga 1:4",
            "next_candle": "4 jam ke depan",
            "prediction_horizon": "4-12 jam"
        },
        "1day": {
            "name": "Harian",
            "type": "Position Trading",
            "tp_range": "3% - 10%",
            "sl_range": "1.5% - 5%",
            "hold_time": "3-30 hari",
            "volatility": "rendah",
            "reliability": "sangat baik",
            "rr_ratio": "1:2 hingga 1:5",
            "next_candle": "1 hari ke depan",
            "prediction_horizon": "1-3 hari"
        },
        "1week": {
            "name": "Mingguan",
            "type": "Position/Investment",
            "tp_range": "5% - 20%",
            "sl_range": "3% - 10%",
            "hold_time": "2-12 minggu",
            "volatility": "sangat rendah",
            "reliability": "sangat baik (tren utama)",
            "rr_ratio": "1:2 hingga 1:5",
            "next_candle": "1 minggu ke depan",
            "prediction_horizon": "1-4 minggu"
        }
    }
    return timeframe_configs.get(interval, timeframe_configs["1hour"])


def analyze_with_gemini(image_path, symbol, market_type="crypto", interval="1hour", confluence=None):
    """Analisa chart menggunakan Gemini Vision API dengan konteks timeframe dan confluence score"""
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
    
    confluence_context = ""
    if confluence:
        bullish_details = "\n  - ".join(confluence['signal_details']['bullish'][:5]) if confluence['signal_details']['bullish'] else "Tidak ada"
        bearish_details = "\n  - ".join(confluence['signal_details']['bearish'][:5]) if confluence['signal_details']['bearish'] else "Tidak ada"
        
        ema200_str = f"{confluence['ema200']:.4f}" if confluence['ema200'] else "N/A"
        adx_status = "(Tren Kuat)" if confluence['adx'] > 25 else "(Tren Lemah)"
        rsi_status = "(Overbought - Potensi Turun)" if confluence['rsi'] > 70 else "(Oversold - Potensi Naik)" if confluence['rsi'] < 30 else "(Netral)"
        stoch_status = "(Overbought)" if confluence['stoch_rsi'] > 80 else "(Oversold)" if confluence['stoch_rsi'] < 20 else "(Netral)"
        rsi_div_status = "(Sinyal Reversal Kuat!)" if confluence['rsi_divergence'] != 'none' else ""
        macd_div_status = "(Sinyal Reversal Kuat!)" if confluence['macd_divergence'] != 'none' else ""
        
        confluence_context = f"""
DATA ANALISA KUANTITATIF (SUDAH DIHITUNG):
- Sinyal Sistem: {confluence['signal']} (Keyakinan: {confluence['confidence']})
- Skor Bullish: {confluence['bullish_pct']:.1f}% | Skor Bearish: {confluence['bearish_pct']:.1f}%
- Arah Tren: {confluence['trend_direction']} | Kekuatan Tren: {confluence['trend_strength']}
- ADX (Kekuatan Tren): {confluence['adx']:.1f} {adx_status}
- RSI: {confluence['rsi']:.1f} {rsi_status}
- Stochastic RSI: {confluence['stoch_rsi']:.1f} {stoch_status}
- ATR (Volatilitas): {confluence['atr']:.4f} ({confluence['atr_pct']:.2f}% dari harga)
- RSI Divergence: {confluence['rsi_divergence'].upper()} {rsi_div_status}
- MACD Divergence: {confluence['macd_divergence'].upper()} {macd_div_status}
- EMA20: {confluence['ema20']:.4f} | EMA50: {confluence['ema50']:.4f} | EMA200: {ema200_str}
- Bollinger Upper: {confluence['bb_upper']:.4f} | Middle: {confluence['bb_middle']:.4f} | Lower: {confluence['bb_lower']:.4f}
- MACD: {confluence['macd']:.6f} | Signal: {confluence['macd_signal']:.6f} | Histogram: {confluence['macd_hist']:.6f}

SINYAL BULLISH TERDETEKSI:
  - {bullish_details}

SINYAL BEARISH TERDETEKSI:
  - {bearish_details}
"""

    prompt = f"""Kamu adalah analis teknikal profesional dengan pengalaman 15+ tahun. Analisa chart candlestick {asset_name} pada timeframe {tf_context['name']} dengan SANGAT TELITI.

KONTEKS TIMEFRAME {tf_context['name'].upper()}:
- Tipe Trading: {tf_context['type']}
- Target Profit Wajar: {tf_context['tp_range']} dari harga entry
- Stop Loss Wajar: {tf_context['sl_range']} dari harga entry (Gunakan 1.5-2x ATR untuk presisi)
- Estimasi Waktu Hold: {tf_context['hold_time']}
- Volatilitas: {tf_context['volatility']}
- Keandalan Sinyal: {tf_context['reliability']}
- Rasio Risk:Reward Minimal: {tf_context['rr_ratio']}
- Horizon Prediksi: {tf_context['next_candle']} ({tf_context['prediction_horizon']})
{confluence_context}
INDIKATOR PADA CHART (5 Panel):
1. Panel Utama - Price Action:
   - EMA 20 (biru) - tren jangka pendek
   - EMA 50 (orange) - tren jangka menengah  
   - EMA 200 (merah tebal) - tren jangka panjang PENTING
   - Bollinger Bands (ungu putus-putus) - volatilitas dan overbought/oversold
   - Fibonacci Retracement (kuning-orange) - level support/resistance kunci

2. Panel RSI (14):
   - Level 70 = Overbought (potensi koreksi turun)
   - Level 30 = Oversold (potensi bounce naik)
   - Level 50 = Garis tengah (konfirmasi tren)

3. Panel Stochastic RSI:
   - Garis K (biru) dan D (orange)
   - Level 80 = Overbought ekstrem
   - Level 20 = Oversold ekstrem
   - Cross bullish/bearish = sinyal entry

4. Panel MACD:
   - MACD line (biru) vs Signal line (merah)
   - Histogram hijau = momentum bullish
   - Histogram merah = momentum bearish
   - Crossover = sinyal penting

METODOLOGI ANALISA MULTI-KONFLUENSI:
1. TREN PRIMER: Tentukan arah tren dari EMA20/50/200 dan posisi harga relatif
2. MOMENTUM: Konfirmasi dengan RSI, Stochastic RSI, dan MACD
3. DIVERGENCE: Perhatikan RSI/MACD divergence untuk sinyal reversal
4. VOLATILITAS: Gunakan Bollinger Bands dan ATR untuk placement SL/TP
5. SUPPORT/RESISTANCE: Kombinasikan Fibonacci dengan high/low sebelumnya
6. KONFIRMASI: Minimal 3 dari 5 indikator harus setuju untuk sinyal kuat

ATURAN KETAT:
- Jika ADX < 20: Pasar ranging, JANGAN trade melawan batas range
- Jika RSI > 70 DAN Stoch RSI > 80: SANGAT OVERBOUGHT, risiko koreksi tinggi
- Jika RSI < 30 DAN Stoch RSI < 20: SANGAT OVERSOLD, potensi bounce
- Jika ada Divergence: Prioritaskan sinyal divergence di atas indikator lain
- Jika harga di bawah EMA200: Tren primer bearish, hati-hati long
- Jika harga di atas EMA200: Tren primer bullish, hati-hati short
- Pastikan RR minimal 1:2 untuk setiap trade

Berikan analisa dalam format LENGKAP berikut (Bahasa Indonesia):

PREDIKSI {tf_context['next_candle'].upper()}: [NAIK/TURUN/SIDEWAYS] - Keyakinan [Tinggi/Sedang/Rendah] - [Alasan spesifik berdasarkan 2-3 indikator utama]

PERKIRAAN PERGERAKAN: Dalam {tf_context['prediction_horizon']}, harga diperkirakan [naik/turun/sideways] dari [harga saat ini] menuju [target spesifik] dengan probabilitas [persentase berdasarkan konfluensi]

SINYAL: [STRONG BUY/BUY/HOLD/SELL/STRONG SELL] - [Penjelasan mengapa, sebutkan minimal 3 indikator pendukung]

KEKUATAN SINYAL: [X dari 8 indikator mendukung] - [daftar indikator yang setuju]

HARGA SAAT INI: [Harga terakhir dari chart - HARUS AKURAT]
HARGA MASUK IDEAL: [Harga entry optimal - bisa sama dengan harga saat ini atau tunggu pullback]

TARGET PROFIT 1: [TP1 dengan persentase dari entry - target konservatif]
TARGET PROFIT 2: [TP2 dengan persentase dari entry - target moderat]  
TARGET PROFIT 3: [TP3 dengan persentase dari entry - target ambisius jika tren kuat]

STOP LOSS: [Harga SL berdasarkan ATR dan support/resistance - WAJIB dengan jarak yang jelas]
RASIO RR: [Risk:Reward ratio yang tepat, minimal 1:2]
POTENSI PROFIT: [Persentase potensi profit jika TP1 tercapai]
POTENSI LOSS: [Persentase potensi loss jika SL terkena]

WAKTU HOLD: {tf_context['hold_time']}

ANALISA TEKNIKAL DETAIL:
POLA CANDLESTICK: [Pola yang teridentifikasi dan implikasinya]
TREN EMA: [Posisi EMA20 vs EMA50 vs EMA200 dan maknanya]
KONDISI RSI: [Nilai RSI, kondisi, dan apakah ada divergence]
KONDISI STOCH RSI: [Nilai K/D, cross, dan kondisi overbought/oversold]
KONDISI MACD: [Posisi MACD vs Signal, histogram, dan momentum]
POSISI BOLLINGER: [Dimana harga relatif terhadap BB dan apakah ada squeeze]
LEVEL FIBONACCI: [Level Fib aktif saat ini dan target berikutnya]

SUPPORT KUNCI:
- S1: [Level support pertama - terdekat]
- S2: [Level support kedua]
- S3: [Level support kuat jika breakdown]

RESISTANCE KUNCI:
- R1: [Level resistance pertama - terdekat]
- R2: [Level resistance kedua]
- R3: [Level resistance kuat jika breakout]

PERINGATAN RISIKO: [Sebutkan skenario yang bisa membatalkan analisa ini]

KESIMPULAN: Dalam {tf_context['next_candle']}, harga {asset_name} diprediksi [NAIK/TURUN/SIDEWAYS] dengan keyakinan [tinggi/sedang/rendah] karena [alasan utama 2-3 kalimat yang jelas dan spesifik berdasarkan konfluensi indikator].

CATATAN: Berikan angka SPESIFIK dan PRESISI berdasarkan chart. JANGAN menebak - baca nilai dari chart dengan teliti. Target dan SL harus REALISTIS sesuai timeframe {tf_context['name']}."""

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
            "temperature": 0.2,
            "topP": 0.85,
            "maxOutputTokens": 2048
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        log_analysis(f"Menganalisa {symbol} dengan AI (Enhanced)...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    if text:
                        log_success(f"Analisa {symbol} selesai (Enhanced)")
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


def extract_signal_from_analysis(text):
    """Mengekstrak sinyal trading dari hasil analisa Gemini"""
    if not text or text.startswith("Error") or text.startswith("Timeout"):
        return None, None
    
    text_upper = text.upper()
    
    signal_patterns = [
        (r'SINYAL[:\s]*\[?(STRONG[\s_]?BUY)\]?', 'STRONG_BUY'),
        (r'SINYAL[:\s]*\[?(STRONG[\s_]?SELL)\]?', 'STRONG_SELL'),
        (r'SINYAL[:\s]*\[?(BUY)\]?', 'BUY'),
        (r'SINYAL[:\s]*\[?(SELL)\]?', 'SELL'),
        (r'SINYAL[:\s]*\[?(HOLD)\]?', 'HOLD'),
        (r'SIGNAL[:\s]*\[?(STRONG[\s_]?BUY)\]?', 'STRONG_BUY'),
        (r'SIGNAL[:\s]*\[?(STRONG[\s_]?SELL)\]?', 'STRONG_SELL'),
        (r'SIGNAL[:\s]*\[?(BUY)\]?', 'BUY'),
        (r'SIGNAL[:\s]*\[?(SELL)\]?', 'SELL'),
        (r'SIGNAL[:\s]*\[?(HOLD)\]?', 'HOLD'),
    ]
    
    for pattern, signal in signal_patterns:
        match = re.search(pattern, text_upper)
        if match:
            signal_emoji = {
                "STRONG_BUY": "🟢🟢", 
                "BUY": "🟢", 
                "HOLD": "🟡", 
                "SELL": "🔴", 
                "STRONG_SELL": "🔴🔴"
            }.get(signal, "⚪")
            
            signal_display = signal.replace("_", " ")
            return signal, f"{signal_emoji} Sinyal AI: {signal_display}"
    
    return None, None


def format_analysis_reply(text):
    """Format hasil analisa menjadi lebih mudah dibaca dengan kode blok"""
    if not text or text.startswith("Error") or text.startswith("Timeout"):
        return text
    
    text_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text_clean = re.sub(r'\*([^*]+)\*', r'\1', text_clean)
    text_clean = re.sub(r'`([^`]+)`', r'\1', text_clean)
    text_clean = re.sub(r'^\s*[-•]\s*', '', text_clean, flags=re.MULTILINE)
    
    section_config = {
        'signal': {'title': '📊 SINYAL', 'keywords': ['sinyal', 'signal', 'kekuatan sinyal']},
        'prediction': {'title': '🔮 PREDIKSI', 'keywords': ['prediksi', 'perkiraan', 'arah']},
        'entry': {'title': '🎯 ENTRY', 'keywords': ['harga masuk', 'entry', 'masuk ideal']},
        'tp': {'title': '💰 TARGET PROFIT', 'keywords': ['target profit', 'tp1', 'tp2', 'tp3', 'tp 1', 'tp 2', 'tp 3', 'take profit']},
        'sl': {'title': '🛑 STOP LOSS', 'keywords': ['stop loss', 'stoploss', 'sl']},
        'rr': {'title': '⚖️ RISK/REWARD', 'keywords': ['rasio rr', 'risk reward', 'rr ratio', 'rasio risk']},
        'support': {'title': '🔻 SUPPORT', 'keywords': ['support', 's1', 's2', 's3']},
        'resistance': {'title': '🔺 RESISTANCE', 'keywords': ['resistance', 'r1', 'r2', 'r3']},
        'trend': {'title': '📈 TREN', 'keywords': ['tren', 'trend']},
        'rsi': {'title': '📉 RSI', 'keywords': ['rsi', 'kondisi rsi']},
        'macd': {'title': '📊 MACD', 'keywords': ['macd', 'kondisi macd']},
        'stoch': {'title': '📊 STOCHASTIC', 'keywords': ['stoch', 'stochastic']},
        'bb': {'title': '〰️ BOLLINGER', 'keywords': ['bollinger', 'bb', 'posisi bollinger']},
        'fib': {'title': '🔢 FIBONACCI', 'keywords': ['fibonacci', 'fib', 'level fib']},
        'pattern': {'title': '🕯️ POLA', 'keywords': ['pola', 'pattern', 'candlestick']},
        'warning': {'title': '⚠️ PERINGATAN', 'keywords': ['peringatan', 'risiko', 'warning']},
        'conclusion': {'title': '🧠 KESIMPULAN', 'keywords': ['kesimpulan', 'conclusion', 'ringkasan']},
    }
    
    sections = {k: [] for k in section_config}
    sections['other'] = []
    
    lines = text_clean.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()
            value = parts[1].strip() if len(parts) > 1 else ''
            
            if not value:
                continue
            
            matched = False
            for section_key, config in section_config.items():
                for keyword in config['keywords']:
                    if keyword in key:
                        sections[section_key].append(value)
                        matched = True
                        break
                if matched:
                    break
            
            if not matched and value and len(value) > 3:
                sections['other'].append(f"{parts[0].strip()}: {value}")
    
    result_lines = []
    
    if sections['signal']:
        result_lines.append(f"📊 *SINYAL:* `{sections['signal'][0]}`")
    
    if sections['prediction']:
        result_lines.append(f"🔮 *PREDIKSI:* `{sections['prediction'][0]}`")
    
    if sections['entry'] or sections['tp'] or sections['sl']:
        result_lines.append("")
        result_lines.append("```")
        result_lines.append("╔══════ SETUP TRADING ══════╗")
        if sections['entry']:
            result_lines.append(f"  Entry    : {sections['entry'][0]}")
        for i, tp in enumerate(sections['tp'], 1):
            result_lines.append(f"  TP{i}      : {tp}")
        if sections['sl']:
            result_lines.append(f"  SL       : {sections['sl'][0]}")
        if sections['rr']:
            result_lines.append(f"  R:R      : {sections['rr'][0]}")
        result_lines.append("╚═══════════════════════════╝")
        result_lines.append("```")
    
    if sections['support'] or sections['resistance']:
        result_lines.append("")
        result_lines.append("```")
        result_lines.append("╔══ SUPPORT & RESISTANCE ═══╗")
        for i, s in enumerate(sections['support'], 1):
            result_lines.append(f"  S{i}       : {s}")
        for i, r in enumerate(sections['resistance'], 1):
            result_lines.append(f"  R{i}       : {r}")
        result_lines.append("╚═══════════════════════════╝")
        result_lines.append("```")
    
    indicator_lines = []
    if sections['trend']:
        indicator_lines.append(f"📈 Tren: `{sections['trend'][0]}`")
    if sections['rsi']:
        indicator_lines.append(f"📉 RSI: `{sections['rsi'][0]}`")
    if sections['macd']:
        indicator_lines.append(f"📊 MACD: `{sections['macd'][0]}`")
    if sections['stoch']:
        indicator_lines.append(f"📊 Stoch: `{sections['stoch'][0]}`")
    if sections['bb']:
        indicator_lines.append(f"〰️ BB: `{sections['bb'][0]}`")
    if sections['pattern']:
        indicator_lines.append(f"🕯️ Pola: `{sections['pattern'][0]}`")
    
    if indicator_lines:
        result_lines.append("")
        result_lines.extend(indicator_lines)
    
    if sections['warning']:
        result_lines.append("")
        result_lines.append(f"⚠️ *Peringatan:* _{sections['warning'][0]}_")
    
    if sections['conclusion']:
        result_lines.append("")
        result_lines.append(f"🧠 *Kesimpulan:* {sections['conclusion'][0]}")
    
    return '\n'.join(result_lines) if result_lines else text


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
    if not update.message:
        return
    
    welcome_text = """📊 *Bot Analisa Teknikal Pro*
━━━━━━━━━━━━━━━━━━━━

Selamat datang! Bot ini menyediakan analisa teknikal PROFESSIONAL menggunakan AI untuk:

💰 *Cryptocurrency* - 14 koin populer
   BTC, ETH, SOL, BNB, XRP, dan lainnya

💱 *Forex & Komoditas* - 16 pasangan
   Emas (XAUUSD), Perak, EUR/USD, GBP/USD, dll

*Fitur Analisa Pro:*
• 8+ Indikator Teknikal (EMA, RSI, MACD, BB, Stoch RSI)
• Sistem Konfluensi Multi-Indikator
• Deteksi Divergence RSI & MACD
• ADX (Kekuatan Tren) & ATR (Volatilitas)
• Fibonacci Retracement
• Analisa AI Gemini Vision Enhanced
• Sinyal STRONG BUY/BUY/HOLD/SELL/STRONG SELL
• 3 Level Target Profit + Stop Loss Optimal

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
    if not query or not query.data:
        return
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
    if not query or not query.data:
        return
    await query.answer()
    
    symbol = query.data.replace('crypto_', '')
    
    if symbol not in SUPPORTED_COINS:
        return
    
    info = SUPPORTED_COINS[symbol]
    if context.user_data is not None:
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
    if not query or not query.data:
        return
    await query.answer()
    
    symbol = query.data.replace('forex_', '')
    
    if symbol not in FOREX_PAIRS:
        return
    
    info = FOREX_PAIRS[symbol]
    if context.user_data is not None:
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
    if not query or not query.data or not query.message:
        return
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
    
    chat_id = query.message.chat.id
    current_message_id = query.message.message_id
    
    user_data = context.user_data or {}
    for key in ['last_chart_message_id', 'last_analysis_message_id', 'last_button_message_id']:
        if key in user_data:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=user_data[key])
            except:
                pass
            user_data.pop(key, None)
    
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
        text=f"📊 Membuat chart & menghitung konfluensi {info['emoji']} {symbol} ({interval})..."
    )
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path, confluence = generate_chart_with_confluence(data, filename, symbol, interval, market_type)
    
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
                caption = f"{info['emoji']} {symbol}/USDT ({interval})\n⏳ Menganalisa dengan AI..."
            else:
                caption = f"{info['emoji']} {symbol} - {info['name']} ({interval})\n⏳ Menganalisa dengan AI..."
            
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
            if context.user_data is not None:
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
        text=f"🤖 Menganalisa chart {symbol} dengan AI + Konfluensi Multi-Indikator..."
    )
    
    analysis = analyze_with_gemini(chart_path, symbol, market_type, interval, confluence)
    formatted = format_analysis_reply(analysis)
    
    signal_code, signal_text = extract_signal_from_analysis(analysis)
    
    if not signal_text:
        signal_text = "✅ Analisa selesai"
    
    try:
        if market_type == "crypto":
            new_caption = f"{info['emoji']} {symbol}/USDT ({interval})\n{signal_text}"
        else:
            new_caption = f"{info['emoji']} {symbol} - {info['name']} ({interval})\n{signal_text}"
        
        await context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=photo_message.message_id,
            caption=new_caption
        )
    except Exception as e:
        logger.warning(f"Gagal update caption chart: {e}")
    
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
        if context.user_data is not None:
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
        if context.user_data is not None:
            context.user_data['last_button_message_id'] = button_message.message_id
    except:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="📊 Lanjutkan analisa:",
            reply_markup=get_after_analysis_keyboard(symbol, market_type)
        )
        if context.user_data is not None:
            context.user_data['last_button_message_id'] = button_message.message_id
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /analyze [symbol] [timeframe]"""
    if not update.message:
        return
    
    args = context.args or []
    
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
    
    await update.message.reply_text("📊 Membuat chart & menghitung konfluensi...")
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path, confluence = generate_chart_with_confluence(data, filename, symbol, interval, market_type)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        if market_type == "crypto":
            caption = f"{info['emoji']} {symbol}/USDT ({interval})\n⏳ Menganalisa dengan AI..."
        else:
            caption = f"{info['emoji']} {symbol} ({interval})\n⏳ Menganalisa dengan AI..."
        photo_msg = await update.message.reply_photo(photo=photo, caption=caption)
    
    analysis = analyze_with_gemini(chart_path, symbol, market_type, interval, confluence)
    formatted = format_analysis_reply(analysis)
    
    signal_code, signal_text = extract_signal_from_analysis(analysis)
    
    if not signal_text:
        signal_text = "✅ Analisa selesai"
    
    try:
        if market_type == "crypto":
            new_caption = f"{info['emoji']} {symbol}/USDT ({interval})\n{signal_text}"
        else:
            new_caption = f"{info['emoji']} {symbol} ({interval})\n{signal_text}"
        
        await context.bot.edit_message_caption(
            chat_id=update.message.chat.id,
            message_id=photo_msg.message_id,
            caption=new_caption
        )
    except Exception as e:
        logger.warning(f"Gagal update caption chart: {e}")
    
    await update.message.reply_text(
        f"{info['emoji']} Hasil Analisa Pro {symbol} ({interval}):\n\n{formatted}\n\n"
        "⚠️ Peringatan: Ini bukan saran keuangan.",
        reply_markup=get_after_analysis_keyboard(symbol, market_type)
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /price [symbol]"""
    if not update.message:
        return
    
    args = context.args or []
    
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
    if not update.message:
        return
    
    crypto_list = ", ".join(SUPPORTED_COINS.keys())
    forex_list = ", ".join(FOREX_PAIRS.keys())
    
    help_text = f"""📖 *Panduan Penggunaan Bot Analisa Pro*

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

*Fitur Analisa Pro:*
• Chart dengan 8+ Indikator Teknikal
• EMA 20, EMA 50, EMA 200 (Tren Multi-Timeframe)
• Bollinger Bands & Fibonacci Retracement
• RSI (14) dengan level 30/50/70
• Stochastic RSI (lebih sensitif)
• MACD dengan Histogram
• Sistem Konfluensi Multi-Indikator
• Deteksi RSI & MACD Divergence
• ADX untuk Kekuatan Tren
• ATR untuk Volatilitas & Penentuan SL/TP
• Analisa AI Gemini Vision Enhanced
• Sinyal STRONG BUY/BUY/HOLD/SELL/STRONG SELL
• 3 Level Target Profit
• Support & Resistance Multi-Level

*Sumber Data:*
• TradingView - Data candlestick historical
• Yahoo Finance - Sumber data cadangan
• KuCoin - Sumber data cadangan crypto
• Google Gemini Vision - Analisa AI

⚠️ *Peringatan:* Bot ini hanya untuk edukasi. Bukan saran keuangan."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    error_str = str(context.error)
    
    if "Message is not modified" in error_str:
        return
    
    if "Query is too old" in error_str:
        return
    
    logger.error(f"Exception saat menangani update: {context.error}")
    
    if "Conflict" in error_str:
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
