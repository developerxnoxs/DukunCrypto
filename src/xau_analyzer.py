#!/usr/bin/env python3
"""
Forex & Commodities Technical Analysis Bot
Tool CLI untuk analisa teknikal Forex dan Komoditas menggunakan Telegram Bot dan Gemini AI Vision
Menggunakan TradingView untuk data historical (untuk pembelajaran)
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
from datetime import datetime, timezone, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pytz import timezone as tz

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
    }

try:
    import yfinance as yf
except ImportError:
    yf = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN_XAU", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

FOREX_PAIRS = {
    "XAUUSD": {"name": "Gold", "emoji": "🥇", "yf_symbol": "GC=F", "category": "commodity"},
    "XAGUSD": {"name": "Silver", "emoji": "🥈", "yf_symbol": "SI=F", "category": "commodity"},
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
    "USOIL": {"name": "Crude Oil", "emoji": "🛢️", "yf_symbol": "CL=F", "category": "commodity"},
}

INTERVAL_MAP = {
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "30min": "30m",
    "1hour": "1h",
    "4hour": "4h",
    "1day": "1d",
}


def fetch_forex_from_tradingview(symbol="XAUUSD", interval="1hour", n_bars=200):
    """Mengambil data candlestick Forex dari TradingView menggunakan xnoxs-fetcher"""
    
    if not TV_AVAILABLE:
        logger.error("xnoxs-fetcher library tidak tersedia")
        return None
    
    if interval not in TV_INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None
    
    if symbol not in FOREX_PAIRS:
        logger.error(f"Symbol tidak valid: {symbol}")
        return None
    
    tv_interval = TV_INTERVAL_MAP[interval]
    
    exchanges = ['OANDA', 'FXCM', 'FX_IDC', 'FOREXCOM', 'CAPITALCOM']
    
    for exchange in exchanges:
        try:
            logger.info(f"Mencoba mengambil data {symbol} dari TradingView ({exchange}) interval {interval}...")
            
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
                
                logger.info(f"Berhasil mengambil {len(candles)} candle {symbol} dari TradingView ({exchange})")
                return candles
                
        except Exception as e:
            logger.warning(f"Gagal dari {exchange}: {e}")
            continue
    
    logger.error(f"Gagal mengambil data {symbol} dari semua exchange TradingView")
    return None


def fetch_forex_from_yfinance(symbol="XAUUSD", interval="1hour"):
    """Mengambil data candlestick Forex dari Yahoo Finance (fallback)"""
    
    if not yf:
        logger.error("yfinance library tidak tersedia")
        return None
    
    if interval not in INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None
    
    if symbol not in FOREX_PAIRS:
        logger.error(f"Symbol tidak valid: {symbol}")
        return None

    try:
        yf_symbol = FOREX_PAIRS[symbol]["yf_symbol"]
        logger.info(f"Mengambil data {symbol} dari Yahoo Finance ({yf_symbol}) interval {interval}...")
        
        yf_interval = INTERVAL_MAP[interval]
        ticker = yf.Ticker(yf_symbol)
        
        if interval in ["1min", "5min", "15min", "30min"]:
            period = "3d"
        else:
            period = "1y"
        
        df = ticker.history(period=period, interval=yf_interval)
        
        if df.empty:
            logger.warning(f"Tidak ada data {symbol} dari Yahoo Finance")
            return None
        
        df = df.dropna()
        if df.empty:
            logger.warning(f"Semua data {symbol} adalah NaN")
            return None
        
        if interval in ["1min", "5min", "15min", "30min"]:
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                volume_q75 = df['Volume'].quantile(0.75)
                volume_q25 = df['Volume'].quantile(0.25)
                iqr = volume_q75 - volume_q25
                upper_bound = volume_q75 + (1.5 * iqr)
                df['Volume'] = df['Volume'].clip(upper=upper_bound)
        
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
        
        logger.info(f"Berhasil mengambil {len(candles)} candle {symbol} dari Yahoo Finance")
        return candles[-200:] if len(candles) > 200 else candles
        
    except Exception as e:
        logger.error(f"Error mengambil data {symbol} dari Yahoo Finance: {e}")
        return None


def fetch_forex_data(symbol="XAUUSD", interval="1hour"):
    """Mengambil data candlestick Forex - prioritas TradingView, fallback ke Yahoo Finance"""
    
    if interval not in INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None
    
    if symbol not in FOREX_PAIRS:
        logger.error(f"Symbol tidak valid: {symbol}")
        return None
    
    data = fetch_forex_from_tradingview(symbol, interval)
    
    if data and len(data) >= 20:
        logger.info(f"Data {symbol} berhasil diambil dari TradingView")
        return data
    
    logger.info("Fallback ke Yahoo Finance...")
    data = fetch_forex_from_yfinance(symbol, interval)
    
    if data and len(data) >= 20:
        logger.info(f"Data {symbol} berhasil diambil dari Yahoo Finance")
        return data
    
    logger.error(f"Gagal mengambil data {symbol} dari semua sumber")
    return None


def get_current_price(symbol="XAUUSD"):
    """Mengambil harga terkini untuk symbol tertentu"""
    
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
        except Exception as e:
            logger.warning(f"Error getting {symbol} price from TradingView: {e}")
    
    if yf:
        try:
            yf_symbol = FOREX_PAIRS[symbol]["yf_symbol"]
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data.iloc[-1]["Close"])
        except Exception as e:
            logger.error(f"Error getting {symbol} price from Yahoo: {e}")
    
    return None


def calculate_rsi(series, period=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement levels based on recent swing high/low"""
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


def generate_forex_chart(data, symbol="XAUUSD", filename="forex_chart.png", tf="1hour"):
    """Generate chart candlestick Forex dengan RSI, MACD, Bollinger Bands, dan Fibonacci"""
    if not data:
        logger.error("Data kosong, tidak bisa generate chart")
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

        pair_info = FOREX_PAIRS.get(symbol, {"name": symbol, "emoji": "📊"})
        chart_title = f"\n{symbol} - {pair_info['name']} ({tf}) - Technical Analysis"
        
        mpf.plot(
            df, type='candle', volume=True, style=style,
            title=chart_title,
            ylabel="Price",
            ylabel_lower="Volume",
            savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
            figratio=(16, 12),
            figscale=1.5,
            tight_layout=True,
            addplot=addplots,
            warn_too_much_data=500,
            panel_ratios=(6, 2, 2, 2)
        )
        
        logger.info(f"Chart {symbol} berhasil disimpan: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generate chart: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_forex_with_gemini(image_path, symbol="XAUUSD"):
    """Analisa chart Forex menggunakan Gemini Vision API"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY tidak ditemukan. Set environment variable terlebih dahulu."
    
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return f"File tidak ditemukan: {image_path}"
    except Exception as e:
        return f"Error membaca file: {e}"
    
    pair_info = FOREX_PAIRS.get(symbol, {"name": symbol})
    pair_name = pair_info["name"]

    prompt = f"""Analisa chart candlestick {symbol} ({pair_name}) ini secara teknikal. 

Chart ini memiliki indikator:
- EMA 20 (biru) dan EMA 50 (orange)
- Bollinger Bands (ungu, garis putus-putus)
- Fibonacci Retracement (garis kuning-orange)
- RSI (panel bawah pertama, dengan garis overbought 70 dan oversold 30)
- MACD (panel bawah kedua, dengan histogram hijau/merah)

Berikan analisa dalam format berikut:

SINYAL: [BUY/SELL/HOLD] - [Alasan singkat]
ENTRY: [Harga entry yang disarankan]
TAKE PROFIT: [Target TP1] dan [Target TP2]
STOP LOSS: [Harga SL yang disarankan]
POLA: [Pola candlestick yang terlihat, misalnya: Bullish Engulfing, Doji, Hammer, dll]
TREND: [Trend saat ini: Uptrend/Downtrend/Sideways]
RSI: [Nilai RSI dan kondisi: Overbought/Oversold/Netral]
MACD: [Kondisi MACD: Bullish Crossover/Bearish Crossover/Momentum positif/negatif]
BOLLINGER: [Posisi harga terhadap Bollinger Bands: Upper/Middle/Lower band]
FIBONACCI: [Level Fibonacci terdekat yang signifikan]
SUPPORT: [Level support terdekat]
RESISTANCE: [Level resistance terdekat]
KESIMPULAN: [Ringkasan analisa dalam 2-3 kalimat berdasarkan semua indikator untuk trading {symbol}]

Berikan angka spesifik berdasarkan chart yang terlihat."""

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
        logger.info(f"Mengirim chart {symbol} ke Gemini untuk analisa...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    if text:
                        logger.info(f"Analisa Gemini {symbol} berhasil")
                        return text
            
            return "Format respons Gemini tidak sesuai. Coba lagi."
        elif response.status_code == 400:
            return "Error: Request tidak valid"
        elif response.status_code == 403:
            return "Error: API key tidak valid"
        elif response.status_code == 429:
            return "Error: Rate limit tercapai"
        else:
            return f"Error dari Gemini API (status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return "Timeout saat menghubungi Gemini API"
    except Exception as e:
        return f"Error: {e}"


def format_analysis_reply(text):
    """Format hasil analisa menjadi lebih readable"""
    if not text or text.startswith("Error"):
        return text
    
    text_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text_clean = re.sub(r'\*([^*]+)\*', r'\1', text_clean)
    text_clean = re.sub(r'`([^`]+)`', r'\1', text_clean)
    text_clean = re.sub(r'^\s*[-•]\s*', '', text_clean, flags=re.MULTILINE)
    
    section_keywords = [
        {'keywords': ['sinyal', 'signal'], 'emoji': '📊', 'group': 'signal'},
        {'keywords': ['entry', 'masuk'], 'emoji': '🎯', 'group': 'trading'},
        {'keywords': ['take profit', 'target', 'tp1', 'tp2'], 'emoji': '💰', 'group': 'trading'},
        {'keywords': ['stop loss', 'stoploss', 'sl'], 'emoji': '🛑', 'group': 'trading'},
        {'keywords': ['pola', 'pattern', 'candlestick'], 'emoji': '🕯️', 'group': 'analysis'},
        {'keywords': ['trend', 'arah'], 'emoji': '📈', 'group': 'analysis'},
        {'keywords': ['rsi'], 'emoji': '📉', 'group': 'indicators'},
        {'keywords': ['macd'], 'emoji': '📊', 'group': 'indicators'},
        {'keywords': ['bollinger', 'bb'], 'emoji': '〰️', 'group': 'indicators'},
        {'keywords': ['fibonacci', 'fib'], 'emoji': '🔢', 'group': 'indicators'},
        {'keywords': ['support', 's1', 's2'], 'emoji': '🔻', 'group': 'levels'},
        {'keywords': ['resistance', 'r1', 'r2'], 'emoji': '🔺', 'group': 'levels'},
        {'keywords': ['kesimpulan', 'conclusion'], 'emoji': '🧠', 'group': 'conclusion'},
    ]
    
    sections = {
        'signal': [],
        'trading': [],
        'analysis': [],
        'indicators': [],
        'levels': [],
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
    if sections['signal']:
        result_parts.append('\n\n'.join(sections['signal']))
    if sections['trading']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Trading Setup ───')
        result_parts.append('\n\n'.join(sections['trading']))
    if sections['levels']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Support & Resistance ───')
        result_parts.append('\n\n'.join(sections['levels']))
    if sections['analysis']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Technical Analysis ───')
        result_parts.append('\n\n'.join(sections['analysis']))
    if sections['indicators']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Indicators ───')
        result_parts.append('\n\n'.join(sections['indicators']))
    if sections['conclusion']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Kesimpulan ───')
        result_parts.append('\n\n'.join(sections['conclusion']))
    
    return '\n'.join(result_parts) if result_parts else text


def get_symbol_keyboard():
    """Generate keyboard untuk pilihan symbol Forex"""
    commodities = [s for s, info in FOREX_PAIRS.items() if info["category"] == "commodity"]
    majors = [s for s, info in FOREX_PAIRS.items() if info["category"] == "major"]
    crosses = [s for s, info in FOREX_PAIRS.items() if info["category"] == "cross"]
    
    buttons = []
    
    buttons.append([InlineKeyboardButton("─── Komoditas ───", callback_data='ignore')])
    row = []
    for symbol in commodities:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'sym_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("─── Major Pairs ───", callback_data='ignore')])
    row = []
    for symbol in majors:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'sym_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("─── Cross Pairs ───", callback_data='ignore')])
    row = []
    for symbol in crosses:
        info = FOREX_PAIRS[symbol]
        row.append(InlineKeyboardButton(f"{info['emoji']} {symbol}", callback_data=f'sym_{symbol}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(buttons)


def get_timeframe_keyboard(symbol="XAUUSD"):
    """Generate keyboard untuk pilihan timeframe"""
    info = FOREX_PAIRS.get(symbol, {"emoji": "📊"})
    emoji = info["emoji"]
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1m", callback_data=f'tf_{symbol}_1min'),
            InlineKeyboardButton("5m", callback_data=f'tf_{symbol}_5min'),
            InlineKeyboardButton("15m", callback_data=f'tf_{symbol}_15min'),
            InlineKeyboardButton("30m", callback_data=f'tf_{symbol}_30min'),
        ],
        [
            InlineKeyboardButton("1h", callback_data=f'tf_{symbol}_1hour'),
            InlineKeyboardButton("4h", callback_data=f'tf_{symbol}_4hour'),
            InlineKeyboardButton("1d", callback_data=f'tf_{symbol}_1day'),
        ],
        [
            InlineKeyboardButton("⬅️ Kembali ke daftar pair", callback_data='back_to_symbols'),
        ],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    welcome_text = """📊 *Forex & Commodities Technical Analysis Bot*
━━━━━━━━━━━━━━━━━━━━

*Fitur:*
• 16 pasangan Forex & Komoditas
• Chart candlestick real-time (TradingView)
• EMA20 & EMA50 indicators
• Analisa AI dengan Gemini Vision
• Multiple timeframe (1m - 1d)

━━━━━━━━━━━━━━━━━━━━
*Pilih pair untuk analisa:*"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_symbol_keyboard(),
        parse_mode='Markdown'
    )


async def handle_symbol_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button symbol selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'ignore':
        return
    
    if query.data == 'back_to_symbols':
        await query.edit_message_text(
            "📊 *Pilih pair untuk analisa:*",
            reply_markup=get_symbol_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    symbol = query.data.replace('sym_', '')
    
    if symbol not in FOREX_PAIRS:
        return
    
    info = FOREX_PAIRS[symbol]
    context.user_data['selected_symbol'] = symbol
    
    current_price = get_current_price(symbol)
    price_text = f"💵 Harga saat ini: {current_price:.5f}" if current_price else ""
    
    await query.edit_message_text(
        f"{info['emoji']} *{symbol} - {info['name']}*\n{price_text}\n\n*Pilih timeframe:*",
        reply_markup=get_timeframe_keyboard(symbol),
        parse_mode='Markdown'
    )


async def handle_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button timeframe"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.replace('tf_', '').rsplit('_', 1)
    if len(parts) != 2:
        return
    
    symbol = parts[0]
    interval = parts[1]
    
    if symbol not in FOREX_PAIRS or interval not in INTERVAL_MAP:
        return
    
    info = FOREX_PAIRS[symbol]
    chat_id = query.message.chat_id
    current_message_id = query.message.message_id
    
    if 'last_chart_message_id' in context.user_data:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['last_chart_message_id'])
        except:
            pass
        context.user_data.pop('last_chart_message_id', None)
    
    if 'last_analysis_message_id' in context.user_data:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['last_analysis_message_id'])
        except:
            pass
        context.user_data.pop('last_analysis_message_id', None)
    
    status_message = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ Mengambil data {info['emoji']} {symbol} ({interval})..."
    )
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
    except:
        pass
    
    data = fetch_forex_data(symbol, interval)
    
    if not data:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Gagal mengambil data {symbol}. Coba lagi nanti.\n\n{info['emoji']} Pilih timeframe lain:",
            reply_markup=get_timeframe_keyboard(symbol)
        )
        return
    
    if len(data) < 20:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Data terlalu sedikit ({len(data)} candle). Coba timeframe lain.",
            reply_markup=get_timeframe_keyboard(symbol)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"📊 Generating chart {info['emoji']} {symbol} ({interval})..."
    )
    
    filename = f"forex_chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_forex_chart(data, symbol, filename, interval)
    
    if not chart_path:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Gagal membuat chart.\n\n{info['emoji']} Pilih timeframe:",
            reply_markup=get_timeframe_keyboard(symbol)
        )
        return
    
    try:
        with open(chart_path, "rb") as photo:
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"{info['emoji']} {symbol} - {info['name']} ({interval})"
            )
            context.user_data['last_chart_message_id'] = photo_message.message_id
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal mengirim chart.",
            reply_markup=get_timeframe_keyboard(symbol)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"🤖 Menganalisa chart {symbol} dengan AI..."
    )
    
    analysis = analyze_forex_with_gemini(chart_path, symbol)
    formatted = format_analysis_reply(analysis)
    
    result_text = f"""{info['emoji']} *Hasil Analisa {symbol} ({interval})*
━━━━━━━━━━━━━━━━━━━━

{formatted}

━━━━━━━━━━━━━━━━━━━━
⚠️ _Disclaimer: Ini bukan financial advice._"""
    
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
            text=f"{info['emoji']} *Pilih timeframe untuk analisa lagi:*",
            parse_mode='Markdown',
            reply_markup=get_timeframe_keyboard(symbol)
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    except:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text=f"{info['emoji']} Pilih timeframe untuk analisa lagi:",
            reply_markup=get_timeframe_keyboard(symbol)
        )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /analyze [symbol] [timeframe]"""
    args = context.args
    
    if len(args) < 2:
        symbols_list = ", ".join(FOREX_PAIRS.keys())
        await update.message.reply_text(
            f"Penggunaan: /analyze <symbol> <timeframe>\n"
            f"Contoh: /analyze EURUSD 1hour\n\n"
            f"Symbol tersedia: {symbols_list}\n"
            f"Timeframe tersedia: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day"
        )
        return
    
    symbol = args[0].upper()
    interval = args[1].lower()
    
    if symbol not in FOREX_PAIRS:
        await update.message.reply_text(
            f"❌ Symbol tidak valid: {symbol}\n"
            f"Symbol tersedia: {', '.join(FOREX_PAIRS.keys())}"
        )
        return
    
    if interval not in INTERVAL_MAP:
        await update.message.reply_text(
            f"❌ Timeframe tidak valid: {interval}\n"
            "Gunakan: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day"
        )
        return
    
    info = FOREX_PAIRS[symbol]
    await update.message.reply_text(f"⏳ Mengambil data {info['emoji']} {symbol} ({interval})...")
    
    data = fetch_forex_data(symbol, interval)
    if not data or len(data) < 20:
        await update.message.reply_text(f"❌ Gagal mengambil data {symbol}. Coba lagi nanti.")
        return
    
    await update.message.reply_text("📊 Generating chart...")
    
    filename = f"forex_chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_forex_chart(data, symbol, filename, interval)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"{info['emoji']} {symbol} ({interval})\n⏳ Menganalisa..."
        )
    
    analysis = analyze_forex_with_gemini(chart_path, symbol)
    formatted = format_analysis_reply(analysis)
    
    await update.message.reply_text(
        f"{info['emoji']} Hasil Analisa {symbol} ({interval}):\n\n{formatted}\n\n"
        "⚠️ Disclaimer: Bukan financial advice."
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /price [symbol]"""
    args = context.args
    symbol = args[0].upper() if args else "XAUUSD"
    
    if symbol not in FOREX_PAIRS:
        await update.message.reply_text(
            f"❌ Symbol tidak valid: {symbol}\n"
            f"Symbol tersedia: {', '.join(FOREX_PAIRS.keys())}"
        )
        return
    
    info = FOREX_PAIRS[symbol]
    price = get_current_price(symbol)
    
    if price:
        if info["category"] == "commodity":
            price_str = f"${price:,.2f}"
        else:
            price_str = f"{price:.5f}"
        
        await update.message.reply_text(
            f"{info['emoji']} *Harga {symbol} ({info['name']}) Saat Ini*\n\n"
            f"💵 *{price_str}*",
            parse_mode='Markdown',
            reply_markup=get_timeframe_keyboard(symbol)
        )
    else:
        await update.message.reply_text(
            f"❌ Gagal mengambil harga {symbol}. Coba lagi nanti."
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    symbols_commodities = [f"{info['emoji']} {s}" for s, info in FOREX_PAIRS.items() if info["category"] == "commodity"]
    symbols_major = [f"{info['emoji']} {s}" for s, info in FOREX_PAIRS.items() if info["category"] == "major"]
    symbols_cross = [f"{info['emoji']} {s}" for s, info in FOREX_PAIRS.items() if info["category"] == "cross"]
    
    help_text = f"""📖 *Panduan Penggunaan Forex Analysis Bot*

*Commands:*
/start - Pilih pair dan timeframe dengan tombol
/analyze <symbol> <tf> - Analisa langsung
/price <symbol> - Lihat harga terkini
/help - Tampilkan bantuan ini

*Contoh:*
/analyze EURUSD 1hour
/price XAUUSD

*Komoditas:* {', '.join(symbols_commodities)}
*Major Pairs:* {', '.join(symbols_major)}
*Cross Pairs:* {', '.join(symbols_cross)}

*Timeframe:* 1min, 5min, 15min, 30min, 1hour, 4hour, 1day

*Fitur:*
• Chart candlestick dengan EMA20 & EMA50
• Analisa AI menggunakan Gemini Vision
• Sinyal BUY/SELL/HOLD
• Entry, TP, dan SL recommendation

*Data Source:*
• TradingView - Historical candlestick data
• Yahoo Finance - Fallback data source
• Google Gemini Vision - AI Analysis

⚠️ *Disclaimer:* Bot ini hanya untuk edukasi. Bukan financial advice."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Exception: {context.error}")


def main():
    """Fungsi utama untuk menjalankan bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN_XAU tidak ditemukan!")
        print("Set environment variable: export TELEGRAM_BOT_TOKEN_XAU='your_token'")
        print("Buat bot baru di @BotFather untuk Forex analyzer")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        print("⚠️ Warning: GEMINI_API_KEY tidak ditemukan!")
        print("Analisa AI tidak akan berfungsi tanpa API key.")
        print("Set environment variable: export GEMINI_API_KEY='your_key'")
    
    print("📊 Starting Forex & Commodities Analysis Bot...")
    print(f"📊 Telegram Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"📊 Supported Pairs: {len(FOREX_PAIRS)} symbols")
    print(f"📊 Data Source: TradingView + Yahoo Finance fallback")
    print(f"📊 TradingView: {'Available' if TV_AVAILABLE else 'Not available'}")
    print(f"🤖 Gemini API: {'Configured' if GEMINI_API_KEY else 'Not configured'}")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(handle_symbol_callback, pattern=r'^(sym_|ignore|back_to_symbols)'))
    app.add_handler(CallbackQueryHandler(handle_timeframe_callback, pattern=r'^tf_'))
    app.add_error_handler(error_handler)
    
    print("✅ Bot Forex siap menerima pesan!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
