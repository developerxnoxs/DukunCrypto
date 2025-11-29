#!/usr/bin/env python3
"""
BTC/USDT Technical Analysis Bot
Tool CLI untuk analisa teknikal menggunakan Telegram Bot dan Gemini AI Vision
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

INTERVAL_MAP = {
    "1min": 60, "3min": 180, "5min": 300, "15min": 900,
    "30min": 1800, "1hour": 3600, "2hour": 7200,
    "4hour": 14400, "6hour": 21600, "8hour": 28800,
    "12hour": 43200, "1day": 86400, "1week": 604800
}


def fetch_btc_kucoin(interval="15min", candle_limit=200):
    """Mengambil data candlestick BTC/USDT dari KuCoin API"""
    symbol = "BTC-USDT"
    
    if interval not in INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None
    
    end_at = int(datetime.now(timezone.utc).timestamp())
    start_at = end_at - INTERVAL_MAP[interval] * candle_limit

    try:
        logger.info(f"Mengambil data {symbol} interval {interval}...")
        response = requests.get(
            "https://api.kucoin.com/api/v1/market/candles",
            params={
                "symbol": symbol,
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
        logger.info(f"Berhasil mengambil {len(sorted_candles)} candle")
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


def generate_candlestick_chart(data, filename="chart.png", tf="15min"):
    """Generate chart candlestick dari data OHLCV"""
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
            up='#26a69a', down='#ef5350',
            wick={'up': '#26a69a', 'down': '#ef5350'},
            volume={'up': '#26a69a', 'down': '#ef5350'}
        )
        style = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle=':',
            gridcolor='#e0e0e0',
            facecolor='white',
            edgecolor='#333333'
        )

        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        addplots = [
            mpf.make_addplot(ema20, color='blue', width=1, label='EMA20'),
            mpf.make_addplot(ema50, color='orange', width=1, label='EMA50')
        ]

        mpf.plot(
            df, type='candle', volume=True, style=style,
            title=f"\nBTC/USDT ({tf}) - KuCoin",
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


def analyze_image_with_gemini(image_path):
    """Analisa chart menggunakan Gemini Vision API"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY tidak ditemukan. Set environment variable terlebih dahulu."
    
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return f"File tidak ditemukan: {image_path}"
    except Exception as e:
        return f"Error membaca file: {e}"

    prompt = """Analisa chart candlestick BTC/USDT ini secara teknikal. Berikan analisa dalam format berikut:

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
        logger.info("Mengirim chart ke Gemini untuk analisa...")
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


def get_timeframe_keyboard():
    """Generate keyboard untuk pilihan timeframe"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1m", callback_data='1min'),
            InlineKeyboardButton("5m", callback_data='5min'),
            InlineKeyboardButton("15m", callback_data='15min')
        ],
        [
            InlineKeyboardButton("1h", callback_data='1hour'),
            InlineKeyboardButton("4h", callback_data='4hour'),
            InlineKeyboardButton("1d", callback_data='1day')
        ],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    welcome_text = """📊 *BTC/USDT Technical Analysis Bot*

Pilih timeframe untuk analisa teknikal:

_Chart akan di-generate dengan EMA20 & EMA50, kemudian dianalisa menggunakan AI._"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_timeframe_keyboard(),
        parse_mode='Markdown'
    )


async def handle_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button timeframe"""
    query = update.callback_query
    await query.answer()
    
    interval = query.data
    chat_id = query.message.chat_id
    
    if 'last_chart_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=context.user_data['last_chart_message_id']
            )
        except Exception:
            pass
    
    await query.edit_message_text(f"⏳ Mengambil data BTC/USDT ({interval})...")
    
    data = fetch_btc_kucoin(interval)
    
    if not data:
        await query.edit_message_text(
            text="❌ Gagal mengambil data dari KuCoin. Coba lagi nanti.\n\n📊 Pilih timeframe lain:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    if len(data) < 20:
        await query.edit_message_text(
            text=f"❌ Data terlalu sedikit ({len(data)} candle). Minimal 20 candle diperlukan.\n\n📊 Pilih timeframe lain:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    await query.edit_message_text(f"📊 Generating chart BTC/USDT ({interval})...")
    
    filename = f"chart_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_candlestick_chart(data, filename, interval)
    
    if not chart_path:
        await query.edit_message_text(
            text="❌ Gagal membuat chart. Coba lagi.\n\n📊 Pilih timeframe:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    photo_message = None
    try:
        with open(chart_path, "rb") as photo:
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"📊 BTC/USDT Chart ({interval})\n⏳ Menganalisa dengan AI..."
            )
            context.user_data['last_chart_message_id'] = photo_message.message_id
    except Exception as e:
        logger.error(f"Error mengirim photo: {e}")
        await query.edit_message_text(
            text="❌ Gagal mengirim chart.\n\n📊 Pilih timeframe:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    await query.edit_message_text(f"🤖 Menganalisa chart BTC/USDT ({interval}) dengan AI...")
    
    analysis = analyze_image_with_gemini(chart_path)
    formatted = format_analysis_reply(analysis)
    
    caption_text = f"""📈 *Hasil Analisa BTC/USDT ({interval})*
━━━━━━━━━━━━━━━━━━━━

{formatted}

━━━━━━━━━━━━━━━━━━━━
⚠️ _Disclaimer: Ini bukan financial advice._"""
    
    try:
        await context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=photo_message.message_id,
            caption=caption_text,
            parse_mode='Markdown'
        )
    except Exception:
        try:
            await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=photo_message.message_id,
                caption=caption_text.replace('*', '').replace('_', '')
            )
        except Exception as e:
            logger.error(f"Error edit caption: {e}")
    
    select_text = "📊 *Pilih timeframe untuk analisa lagi:*"
    try:
        await query.edit_message_text(
            text=select_text,
            parse_mode='Markdown',
            reply_markup=get_timeframe_keyboard()
        )
    except Exception:
        await query.edit_message_text(
            text="📊 Pilih timeframe untuk analisa lagi:",
            reply_markup=get_timeframe_keyboard()
        )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /analyze [timeframe]"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Penggunaan: /analyze <timeframe>\n"
            "Contoh: /analyze 15min\n\n"
            "Timeframe tersedia: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day"
        )
        return
    
    interval = args[0].lower()
    if interval not in INTERVAL_MAP:
        await update.message.reply_text(
            f"❌ Timeframe tidak valid: {interval}\n"
            "Gunakan: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day"
        )
        return
    
    await update.message.reply_text(f"⏳ Mengambil data BTC/USDT ({interval})...")
    
    data = fetch_btc_kucoin(interval)
    if not data or len(data) < 20:
        await update.message.reply_text("❌ Gagal mengambil data atau data terlalu sedikit.")
        return
    
    await update.message.reply_text("📊 Generating chart...")
    
    filename = f"chart_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_candlestick_chart(data, filename, interval)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"📊 BTC/USDT ({interval})\n⏳ Menganalisa..."
        )
    
    analysis = analyze_image_with_gemini(chart_path)
    formatted = format_analysis_reply(analysis)
    
    await update.message.reply_text(
        f"📈 Hasil Analisa BTC/USDT ({interval}):\n\n{formatted}\n\n"
        "⚠️ Disclaimer: Bukan financial advice."
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    help_text = """📖 *Panduan Penggunaan Bot*

*Commands:*
/start - Pilih timeframe dengan tombol
/analyze <tf> - Analisa langsung (misal: /analyze 15min)
/help - Tampilkan bantuan ini

*Timeframe tersedia:*
1min, 5min, 15min, 30min, 1hour, 4hour, 1day

*Fitur:*
- Chart candlestick dengan EMA20 & EMA50
- Analisa AI menggunakan Gemini Vision
- Sinyal BUY/SELL/HOLD
- Entry, TP, dan SL recommendation
- Pattern recognition

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
    
    print("🚀 Starting BTC/USDT Analysis Bot...")
    print(f"📊 Telegram Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"🤖 Gemini API: {'Configured' if GEMINI_API_KEY else 'Not configured'}")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(handle_timeframe_callback))
    app.add_error_handler(error_handler)
    
    print("✅ Bot aktif! Kirim /start ke bot Telegram Anda.")
    print("Press Ctrl+C to stop.")
    print("⚠️ Pastikan tidak ada instance bot lain yang berjalan dengan token yang sama!")
    
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
