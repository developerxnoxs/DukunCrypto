#!/usr/bin/env python3
"""
Multi-Coin Technical Analysis Bot (Advanced Version)
Tool CLI untuk analisa teknikal crypto menggunakan Telegram Bot dan Gemini AI Vision
Mendukung: BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SUPPORTED_COINS = {
    "BTC": {"name": "Bitcoin", "emoji": "₿", "color": "#F7931A"},
    "ETH": {"name": "Ethereum", "emoji": "Ξ", "color": "#627EEA"},
    "SOL": {"name": "Solana", "emoji": "◎", "color": "#00FFA3"},
    "BNB": {"name": "BNB", "emoji": "🔶", "color": "#F3BA2F"},
    "XRP": {"name": "Ripple", "emoji": "✕", "color": "#23292F"},
    "ADA": {"name": "Cardano", "emoji": "₳", "color": "#0033AD"},
    "DOGE": {"name": "Dogecoin", "emoji": "🐕", "color": "#C2A633"},
    "AVAX": {"name": "Avalanche", "emoji": "🔺", "color": "#E84142"},
    "MATIC": {"name": "Polygon", "emoji": "⬡", "color": "#8247E5"},
    "LINK": {"name": "Chainlink", "emoji": "⬡", "color": "#2A5ADA"},
    "DOT": {"name": "Polkadot", "emoji": "●", "color": "#E6007A"},
    "ATOM": {"name": "Cosmos", "emoji": "⚛", "color": "#2E3148"},
    "UNI": {"name": "Uniswap", "emoji": "🦄", "color": "#FF007A"},
    "LTC": {"name": "Litecoin", "emoji": "Ł", "color": "#345D9D"},
}

INTERVAL_MAP = {
    "1min": 60, "3min": 180, "5min": 300, "15min": 900,
    "30min": 1800, "1hour": 3600, "2hour": 7200,
    "4hour": 14400, "6hour": 21600, "8hour": 28800,
    "12hour": 43200, "1day": 86400, "1week": 604800
}


def fetch_crypto_kucoin(symbol="BTC", interval="15min", candle_limit=200):
    """Mengambil data candlestick dari KuCoin API untuk berbagai coin"""
    pair = f"{symbol}-USDT"
    
    if interval not in INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None
    
    end_at = int(datetime.now(timezone.utc).timestamp())
    start_at = end_at - INTERVAL_MAP[interval] * candle_limit

    try:
        logger.info(f"Mengambil data {pair} interval {interval}...")
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
            logger.error(f"KuCoin API error: {data.get('msg', 'Unknown error')}")
            return None
        
        candles = data.get("data", [])
        if not candles:
            logger.warning("Tidak ada data candle yang diterima")
            return None
            
        sorted_candles = sorted(candles, key=lambda x: int(x[0]))
        logger.info(f"Berhasil mengambil {len(sorted_candles)} candle untuk {pair}")
        return sorted_candles
        
    except requests.exceptions.Timeout:
        logger.error("Timeout saat mengambil data dari KuCoin")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error request KuCoin: {e}")
        return None
    except Exception as e:
        logger.error(f"Error tidak terduga: {e}")
        return None


def get_current_price(symbol="BTC"):
    """Mengambil harga terkini dari KuCoin"""
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
    except Exception as e:
        logger.error(f"Error getting price: {e}")
    return None


def generate_candlestick_chart(data, filename="chart.png", symbol="BTC", tf="15min"):
    """Generate chart candlestick dari data OHLCV"""
    if not data:
        logger.error("Data kosong, tidak bisa generate chart")
        return None
    
    coin_info = SUPPORTED_COINS.get(symbol, {"name": symbol, "color": "#26a69a"})
    
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
        
        addplots = [
            mpf.make_addplot(ema20, color='blue', width=1, label='EMA20'),
            mpf.make_addplot(ema50, color='orange', width=1, label='EMA50')
        ]

        mpf.plot(
            df, type='candle', volume=True, style=style,
            title=f"\n{symbol}/USDT ({tf}) - KuCoin",
            ylabel="Price (USDT)",
            ylabel_lower="Volume",
            savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
            figratio=(16, 9),
            figscale=1.3,
            tight_layout=True,
            addplot=addplots,
            warn_too_much_data=500
        )
        
        logger.info(f"Chart berhasil disimpan: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generate chart: {e}")
        return None


def analyze_image_with_gemini(image_path, symbol="BTC"):
    """Analisa chart menggunakan Gemini Vision API"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY tidak ditemukan. Set environment variable terlebih dahulu."
    
    coin_info = SUPPORTED_COINS.get(symbol, {"name": symbol})
    
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return f"File tidak ditemukan: {image_path}"
    except Exception as e:
        return f"Error membaca file: {e}"

    prompt = f"""Analisa chart candlestick {symbol}/USDT ({coin_info.get('name', symbol)}) ini secara teknikal. Berikan analisa dalam format berikut:

SINYAL: [BUY/SELL/HOLD] - [Alasan singkat]
ENTRY: [Harga entry yang disarankan]
TAKE PROFIT: [Target TP1] dan [Target TP2]
STOP LOSS: [Harga SL yang disarankan]
POLA: [Pola candlestick yang terlihat, misalnya: Bullish Engulfing, Doji, Hammer, dll]
TREND: [Trend saat ini: Uptrend/Downtrend/Sideways]
SUPPORT: [Level support terdekat]
RESISTANCE: [Level resistance terdekat]
KESIMPULAN: [Ringkasan analisa dalam 1-2 kalimat]

Berikan angka spesifik berdasarkan chart yang terlihat. Jika tidak bisa menentukan harga exact, berikan estimasi range."""

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
                        logger.info("Analisa Gemini berhasil")
                        return text
            
            logger.warning(f"Format respons tidak sesuai: {result}")
            return "Format respons Gemini tidak sesuai. Coba lagi."
            
        elif response.status_code == 400:
            error_detail = response.json()
            logger.error(f"Bad request: {error_detail}")
            return f"Error: Request tidak valid - {error_detail.get('error', {}).get('message', 'Unknown')}"
            
        elif response.status_code == 403:
            return "Error: API key tidak valid atau tidak memiliki akses"
            
        elif response.status_code == 429:
            return "Error: Rate limit tercapai. Tunggu beberapa saat dan coba lagi."
            
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return f"Error dari Gemini API (status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return "Timeout saat menghubungi Gemini API. Coba lagi."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return f"Error koneksi: {e}"
    except Exception as e:
        logger.error(f"Error tidak terduga: {e}")
        return f"Error: {e}"


def format_analysis_reply(text):
    """Format hasil analisa menjadi lebih readable dengan spacing yang baik"""
    if not text or text.startswith("Error") or text.startswith("Timeout"):
        return text
    
    text_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text_clean = re.sub(r'\*([^*]+)\*', r'\1', text_clean)
    text_clean = re.sub(r'`([^`]+)`', r'\1', text_clean)
    text_clean = re.sub(r'^\s*[-•]\s*', '', text_clean, flags=re.MULTILINE)
    
    section_keywords = [
        {'keywords': ['sinyal', 'signal'], 'emoji': '📊', 'group': 'signal'},
        {'keywords': ['entry', 'masuk'], 'emoji': '🎯', 'group': 'trading'},
        {'keywords': ['take profit', 'target', 'tp1', 'tp2', 'tp 1', 'tp 2'], 'emoji': '💰', 'group': 'trading'},
        {'keywords': ['stop loss', 'stoploss', 'sl', 'cut loss'], 'emoji': '🛑', 'group': 'trading'},
        {'keywords': ['pola', 'pattern', 'candlestick', 'candle'], 'emoji': '🕯️', 'group': 'analysis'},
        {'keywords': ['trend', 'arah'], 'emoji': '📈', 'group': 'analysis'},
        {'keywords': ['support', 'suport', 's1', 's2', 's3'], 'emoji': '🔻', 'group': 'levels'},
        {'keywords': ['resistance', 'resisten', 'r1', 'r2', 'r3'], 'emoji': '🔺', 'group': 'levels'},
        {'keywords': ['kesimpulan', 'conclusion', 'ringkasan', 'summary'], 'emoji': '🧠', 'group': 'conclusion'},
    ]
    
    sections = {
        'signal': [],
        'trading': [],
        'analysis': [],
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
                    if keyword in key or key in keyword:
                        emoji = config['emoji']
                        label = parts[0].strip().upper()
                        formatted_line = f"{emoji} *{label}:*\n{value}"
                        sections[config['group']].append(formatted_line)
                        matched = True
                        break
                if matched:
                    break
            
            if not matched and value and len(value) > 3:
                sections['other'].append(f"• {parts[0].strip()}: {value}")
        else:
            skip_phrases = ['oke', 'berikut', 'analisa', 'berdasarkan', 'chart', 'gambar']
            should_skip = any(phrase in line.lower() for phrase in skip_phrases)
            if line and not should_skip and len(line) > 10:
                sections['other'].append(line)
    
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
    
    if sections['conclusion']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Kesimpulan ───')
        result_parts.append('\n\n'.join(sections['conclusion']))
    
    if result_parts:
        return '\n'.join(result_parts)
    else:
        return text


def get_coin_keyboard():
    """Generate keyboard untuk pilihan coin - Page 1"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("₿ BTC", callback_data='coin_BTC'),
            InlineKeyboardButton("Ξ ETH", callback_data='coin_ETH'),
            InlineKeyboardButton("◎ SOL", callback_data='coin_SOL'),
        ],
        [
            InlineKeyboardButton("🔶 BNB", callback_data='coin_BNB'),
            InlineKeyboardButton("✕ XRP", callback_data='coin_XRP'),
            InlineKeyboardButton("₳ ADA", callback_data='coin_ADA'),
        ],
        [
            InlineKeyboardButton("🐕 DOGE", callback_data='coin_DOGE'),
            InlineKeyboardButton("🔺 AVAX", callback_data='coin_AVAX'),
            InlineKeyboardButton("⬡ MATIC", callback_data='coin_MATIC'),
        ],
        [
            InlineKeyboardButton("⬡ LINK", callback_data='coin_LINK'),
            InlineKeyboardButton("● DOT", callback_data='coin_DOT'),
            InlineKeyboardButton("⚛ ATOM", callback_data='coin_ATOM'),
        ],
        [
            InlineKeyboardButton("🦄 UNI", callback_data='coin_UNI'),
            InlineKeyboardButton("Ł LTC", callback_data='coin_LTC'),
        ],
    ])


def get_timeframe_keyboard(symbol="BTC"):
    """Generate keyboard untuk pilihan timeframe"""
    coin_info = SUPPORTED_COINS.get(symbol, {"emoji": "📊"})
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
            InlineKeyboardButton("1w", callback_data=f'tf_{symbol}_1week'),
        ],
        [
            InlineKeyboardButton("⬅️ Pilih Coin Lain", callback_data='back_to_coins'),
        ],
    ])


def get_after_analysis_keyboard(symbol="BTC"):
    """Keyboard setelah analisa selesai"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🔄 Analisa {symbol} Lagi", callback_data=f'coin_{symbol}'),
            InlineKeyboardButton("📊 Coin Lain", callback_data='back_to_coins'),
        ],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    welcome_text = """📊 *Multi-Coin Technical Analysis Bot*
━━━━━━━━━━━━━━━━━━━━

🚀 *Advanced Version* - Mendukung 14 Cryptocurrency!

*Fitur:*
• Chart candlestick real-time
• EMA20 & EMA50 indicators
• Analisa AI dengan Gemini Vision
• Multiple timeframe (1m - 1w)

━━━━━━━━━━━━━━━━━━━━
*Pilih cryptocurrency untuk dianalisa:*"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_coin_keyboard(),
        parse_mode='Markdown'
    )


async def handle_coin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button pemilihan coin"""
    query = update.callback_query
    await query.answer()
    
    symbol = query.data.replace('coin_', '')
    coin_info = SUPPORTED_COINS.get(symbol, {"name": symbol, "emoji": "📊"})
    
    context.user_data['selected_coin'] = symbol
    
    current_price = get_current_price(symbol)
    price_text = f"💵 Harga: ${current_price:,.2f}" if current_price else ""
    
    text = f"""{coin_info['emoji']} *{symbol}/USDT* - {coin_info['name']}
{price_text}

📈 *Pilih timeframe untuk analisa:*"""
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_timeframe_keyboard(symbol),
        parse_mode='Markdown'
    )


async def handle_back_to_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk kembali ke pilihan coin"""
    query = update.callback_query
    await query.answer()
    
    text = """📊 *Multi-Coin Technical Analysis Bot*
━━━━━━━━━━━━━━━━━━━━
*Pilih cryptocurrency untuk dianalisa:*"""
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_coin_keyboard(),
        parse_mode='Markdown'
    )


async def handle_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button timeframe"""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.replace('tf_', '').split('_')
    symbol = data_parts[0]
    interval = data_parts[1]
    
    chat_id = query.message.chat_id
    current_message_id = query.message.message_id
    
    coin_info = SUPPORTED_COINS.get(symbol, {"name": symbol, "emoji": "📊"})
    
    if 'last_chart_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=context.user_data['last_chart_message_id']
            )
        except Exception:
            pass
        context.user_data.pop('last_chart_message_id', None)
    
    if 'last_analysis_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=context.user_data['last_analysis_message_id']
            )
        except Exception:
            pass
        context.user_data.pop('last_analysis_message_id', None)
    
    if 'last_button_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=context.user_data['last_button_message_id']
            )
        except Exception:
            pass
        context.user_data.pop('last_button_message_id', None)
    
    status_message = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ Mengambil data {coin_info['emoji']} {symbol}/USDT ({interval})..."
    )
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
    except Exception:
        pass
    
    data = fetch_crypto_kucoin(symbol, interval)
    
    if not data:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Gagal mengambil data {symbol} dari KuCoin. Coba lagi nanti.",
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        return
    
    if len(data) < 20:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Data terlalu sedikit ({len(data)} candle). Minimal 20 candle diperlukan.",
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"📊 Generating chart {coin_info['emoji']} {symbol}/USDT ({interval})..."
    )
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_candlestick_chart(data, filename, symbol, interval)
    
    if not chart_path:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal membuat chart. Coba lagi.",
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        return
    
    photo_message = None
    try:
        with open(chart_path, "rb") as photo:
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"{coin_info['emoji']} {symbol}/USDT Chart ({interval})"
            )
            context.user_data['last_chart_message_id'] = photo_message.message_id
    except Exception as e:
        logger.error(f"Error mengirim photo: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal mengirim chart.",
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"🤖 Menganalisa chart {symbol} dengan AI..."
    )
    
    analysis = analyze_image_with_gemini(chart_path, symbol)
    formatted = format_analysis_reply(analysis)
    
    result_text = f"""{coin_info['emoji']} *Hasil Analisa {symbol}/USDT ({interval})*
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
    except Exception:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=result_text.replace('*', '').replace('_', '')
        )
        context.user_data['last_analysis_message_id'] = status_message.message_id
    
    try:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="📊 *Lanjutkan analisa:*",
            parse_mode='Markdown',
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    except Exception:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="📊 Lanjutkan analisa:",
            reply_markup=get_after_analysis_keyboard(symbol)
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /analyze [coin] [timeframe]"""
    args = context.args
    
    if len(args) < 2:
        coins_list = ", ".join(SUPPORTED_COINS.keys())
        await update.message.reply_text(
            f"Penggunaan: /analyze <coin> <timeframe>\n"
            f"Contoh: /analyze BTC 15min\n"
            f"        /analyze ETH 4hour\n\n"
            f"Coins tersedia: {coins_list}\n\n"
            f"Timeframe tersedia: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week"
        )
        return
    
    symbol = args[0].upper()
    interval = args[1].lower()
    
    if symbol not in SUPPORTED_COINS:
        coins_list = ", ".join(SUPPORTED_COINS.keys())
        await update.message.reply_text(
            f"❌ Coin tidak valid: {symbol}\n"
            f"Gunakan salah satu: {coins_list}"
        )
        return
    
    if interval not in INTERVAL_MAP:
        await update.message.reply_text(
            f"❌ Timeframe tidak valid: {interval}\n"
            f"Gunakan: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week"
        )
        return
    
    coin_info = SUPPORTED_COINS.get(symbol, {"emoji": "📊"})
    
    await update.message.reply_text(f"⏳ Mengambil data {coin_info['emoji']} {symbol}/USDT ({interval})...")
    
    data = fetch_crypto_kucoin(symbol, interval)
    if not data or len(data) < 20:
        await update.message.reply_text("❌ Gagal mengambil data atau data terlalu sedikit.")
        return
    
    await update.message.reply_text("📊 Generating chart...")
    
    filename = f"chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_candlestick_chart(data, filename, symbol, interval)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"{coin_info['emoji']} {symbol}/USDT ({interval})\n⏳ Menganalisa..."
        )
    
    analysis = analyze_image_with_gemini(chart_path, symbol)
    formatted = format_analysis_reply(analysis)
    
    await update.message.reply_text(
        f"{coin_info['emoji']} Hasil Analisa {symbol}/USDT ({interval}):\n\n{formatted}\n\n"
        "⚠️ Disclaimer: Bukan financial advice.",
        reply_markup=get_after_analysis_keyboard(symbol)
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /coins - menampilkan daftar coin"""
    coins_text = "📊 *Daftar Cryptocurrency yang Didukung:*\n\n"
    
    for symbol, info in SUPPORTED_COINS.items():
        price = get_current_price(symbol)
        price_str = f"${price:,.2f}" if price else "N/A"
        coins_text += f"{info['emoji']} *{symbol}* - {info['name']}\n   └ Harga: {price_str}\n\n"
    
    coins_text += "_Gunakan /start untuk memilih coin dan timeframe_"
    
    await update.message.reply_text(
        coins_text,
        parse_mode='Markdown',
        reply_markup=get_coin_keyboard()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    coins_list = ", ".join(SUPPORTED_COINS.keys())
    help_text = f"""📖 *Panduan Penggunaan Bot*

*Commands:*
/start - Pilih coin dan timeframe dengan tombol
/analyze <coin> <tf> - Analisa langsung
/coins - Lihat daftar coin dan harga
/help - Tampilkan bantuan ini

*Contoh:*
/analyze BTC 15min
/analyze ETH 4hour
/analyze SOL 1day

*Coins tersedia ({len(SUPPORTED_COINS)}):*
{coins_list}

*Timeframe tersedia:*
1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week

*Fitur:*
• Chart candlestick dengan EMA20 & EMA50
• Analisa AI menggunakan Gemini Vision
• Sinyal BUY/SELL/HOLD
• Entry, TP, dan SL recommendation
• Pattern recognition
• Multi-coin support

⚠️ *Disclaimer:* Bot ini hanya untuk edukasi. Bukan financial advice."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    if "Conflict" in str(context.error):
        logger.warning("Bot conflict detected - another instance may be running")


def main():
    """Fungsi utama untuk menjalankan bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN tidak ditemukan!")
        print("Set environment variable: export TELEGRAM_BOT_TOKEN='your_token'")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        print("⚠️ Warning: GEMINI_API_KEY tidak ditemukan!")
        print("Analisa AI tidak akan berfungsi tanpa API key.")
        print("Set environment variable: export GEMINI_API_KEY='your_key'")
    
    print("🚀 Starting Multi-Coin Analysis Bot (Advanced Version)...")
    print(f"📊 Telegram Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"🤖 Gemini API: {'Configured' if GEMINI_API_KEY else 'Not configured'}")
    print(f"💰 Supported coins: {', '.join(SUPPORTED_COINS.keys())}")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CommandHandler("coins", cmd_coins))
    app.add_handler(CommandHandler("help", cmd_help))
    
    app.add_handler(CallbackQueryHandler(handle_coin_callback, pattern=r'^coin_'))
    app.add_handler(CallbackQueryHandler(handle_back_to_coins, pattern=r'^back_to_coins$'))
    app.add_handler(CallbackQueryHandler(handle_timeframe_callback, pattern=r'^tf_'))
    
    app.add_error_handler(error_handler)
    
    print("✅ Bot siap menerima pesan!")
    print(f"🔗 Supported coins: {len(SUPPORTED_COINS)}")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
