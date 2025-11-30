#!/usr/bin/env python3
"""
XAUUSD (Gold) Technical Analysis Bot
Tool CLI untuk analisa teknikal Gold/XAUUSD menggunakan Telegram Bot dan Gemini AI Vision
Menggunakan Finnhub API untuk data historical gold
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

INTERVAL_MAP = {
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "30min": "30m",
    "1hour": "1h",
    "4hour": "4h",
    "1day": "1d",
}


def fetch_xauusd_data(interval="1hour"):
    """Mengambil data candlestick XAUUSD dari Yahoo Finance"""
    
    if not yf:
        logger.error("yfinance library tidak tersedia")
        return None
    
    if interval not in INTERVAL_MAP:
        logger.error(f"Interval tidak valid: {interval}")
        return None

    try:
        logger.info(f"Mengambil data XAUUSD interval {interval}...")
        
        yf_interval = INTERVAL_MAP[interval]
        
        # Download data using yfinance
        ticker = yf.Ticker("GC=F")  # Gold futures (XAUUSD proxy)
        
        # Determine period based on interval - use less data for intraday to avoid weekend gaps
        if interval in ["1min", "5min", "15min", "30min"]:
            period = "3d"  # Changed from 5d to 3d to avoid weekend data
        else:
            period = "1y"
        
        df = ticker.history(period=period, interval=yf_interval)
        
        if df.empty:
            logger.warning("Tidak ada data XAUUSD dari Yahoo Finance")
            return None
        
        # Drop NaN values
        df = df.dropna()
        if df.empty:
            logger.warning("Semua data XAUUSD adalah NaN")
            return None
        
        # For intraday, remove outlier volumes (likely flash trades/gaps)
        if interval in ["1min", "5min", "15min", "30min"]:
            volume_q75 = df['Volume'].quantile(0.75)
            volume_q25 = df['Volume'].quantile(0.25)
            iqr = volume_q75 - volume_q25
            upper_bound = volume_q75 + (1.5 * iqr)
            # Cap extreme volume spikes
            df['Volume'] = df['Volume'].clip(upper=upper_bound)
        
        # Convert to candlestick format (list of arrays like btc_analyzer)
        candles = []
        for timestamp, row in df.iterrows():
            candles.append([
                int(timestamp.timestamp()),
                float(row["Open"]),
                float(row["Close"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Volume"])
            ])
        
        logger.info(f"Berhasil mengambil {len(candles)} candle XAUUSD")
        return candles[-200:] if len(candles) > 200 else candles
        
    except Exception as e:
        logger.error(f"Error mengambil data XAUUSD: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_current_gold_price():
    """Mengambil harga gold terkini dari Yahoo Finance"""
    
    if not yf:
        return None
    
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return float(data.iloc[-1]["Close"])
    except Exception as e:
        logger.error(f"Error getting gold price: {e}")
    return None


def generate_xauusd_chart(data, filename="xau_chart.png", tf="1hour"):
    """Generate chart candlestick XAUUSD dari data OHLCV"""
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
        
        addplots = [
            mpf.make_addplot(ema20, color='blue', width=1, label='EMA20'),
            mpf.make_addplot(ema50, color='orange', width=1, label='EMA50')
        ]

        mpf.plot(
            df, type='candle', volume=True, style=style,
            title=f"\nXAUUSD - Gold ({tf})",
            ylabel="Price (USD)",
            ylabel_lower="Volume",
            savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
            figratio=(16, 9),
            figscale=1.3,
            tight_layout=True,
            addplot=addplots,
            warn_too_much_data=500
        )
        
        logger.info(f"Chart XAUUSD berhasil disimpan: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generate chart: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_xauusd_with_gemini(image_path):
    """Analisa chart XAUUSD menggunakan Gemini Vision API"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY tidak ditemukan. Set environment variable terlebih dahulu."
    
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return f"File tidak ditemukan: {image_path}"
    except Exception as e:
        return f"Error membaca file: {e}"

    prompt = """Analisa chart candlestick XAUUSD (Gold/Emas vs USD) ini secara teknikal. Berikan analisa dalam format berikut:

SINYAL: [BUY/SELL/HOLD] - [Alasan singkat]
ENTRY: [Harga entry yang disarankan dalam USD]
TAKE PROFIT: [Target TP1] dan [Target TP2]
STOP LOSS: [Harga SL yang disarankan]
POLA: [Pola candlestick yang terlihat, misalnya: Bullish Engulfing, Doji, Hammer, dll]
TREND: [Trend saat ini: Uptrend/Downtrend/Sideways]
SUPPORT: [Level support terdekat]
RESISTANCE: [Level resistance terdekat]
KESIMPULAN: [Ringkasan analisa dalam 1-2 kalimat untuk trading Gold/XAUUSD]

Berikan angka spesifik berdasarkan chart yang terlihat. Perhatikan bahwa ini adalah chart Gold (XAUUSD) dengan harga dalam USD per troy ounce."""

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
        logger.info("Mengirim chart XAUUSD ke Gemini untuk analisa...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    if text:
                        logger.info("Analisa Gemini XAUUSD berhasil")
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
        {'keywords': ['support', 's1', 's2'], 'emoji': '🔻', 'group': 'levels'},
        {'keywords': ['resistance', 'r1', 'r2'], 'emoji': '🔺', 'group': 'levels'},
        {'keywords': ['kesimpulan', 'conclusion'], 'emoji': '🧠', 'group': 'conclusion'},
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
    if sections['conclusion']:
        if result_parts:
            result_parts.append('')
        result_parts.append('─── Kesimpulan ───')
        result_parts.append('\n\n'.join(sections['conclusion']))
    
    return '\n'.join(result_parts) if result_parts else text


def get_timeframe_keyboard():
    """Generate keyboard untuk pilihan timeframe XAUUSD"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1m", callback_data='xau_1min'),
            InlineKeyboardButton("5m", callback_data='xau_5min'),
            InlineKeyboardButton("15m", callback_data='xau_15min'),
            InlineKeyboardButton("30m", callback_data='xau_30min'),
        ],
        [
            InlineKeyboardButton("1h", callback_data='xau_1hour'),
            InlineKeyboardButton("4h", callback_data='xau_4hour'),
            InlineKeyboardButton("1d", callback_data='xau_1day'),
        ],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    current_price = get_current_gold_price()
    price_text = f"💵 Harga saat ini: ${current_price:,.2f}/oz" if current_price else ""
    
    welcome_text = f"""🥇 *XAUUSD (Gold) Technical Analysis Bot*
━━━━━━━━━━━━━━━━━━━━

{price_text}

*Fitur:*
• Chart candlestick real-time
• EMA20 & EMA50 indicators
• Analisa AI dengan Gemini Vision
• Multiple timeframe (1m - 1d)

━━━━━━━━━━━━━━━━━━━━
*Pilih timeframe untuk analisa XAUUSD:*"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_timeframe_keyboard(),
        parse_mode='Markdown'
    )


async def handle_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button timeframe"""
    query = update.callback_query
    await query.answer()
    
    interval = query.data.replace('xau_', '')
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
        text=f"⏳ Mengambil data 🥇 XAUUSD ({interval})..."
    )
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
    except:
        pass
    
    data = fetch_xauusd_data(interval)
    
    if not data:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal mengambil data XAUUSD. Pastikan FINNHUB_API_KEY sudah di-set.\n\n🥇 Pilih timeframe lain:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    if len(data) < 20:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"❌ Data terlalu sedikit ({len(data)} candle). Coba timeframe lain.",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"📊 Generating chart 🥇 XAUUSD ({interval})..."
    )
    
    filename = f"xau_chart_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_xauusd_chart(data, filename, interval)
    
    if not chart_path:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal membuat chart.\n\n🥇 Pilih timeframe:",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    try:
        with open(chart_path, "rb") as photo:
            photo_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🥇 XAUUSD Chart ({interval})"
            )
            context.user_data['last_chart_message_id'] = photo_message.message_id
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="❌ Gagal mengirim chart.",
            reply_markup=get_timeframe_keyboard()
        )
        return
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_message.message_id,
        text=f"🤖 Menganalisa chart XAUUSD dengan AI..."
    )
    
    analysis = analyze_xauusd_with_gemini(chart_path)
    formatted = format_analysis_reply(analysis)
    
    result_text = f"""🥇 *Hasil Analisa XAUUSD ({interval})*
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
            text="🥇 *Pilih timeframe untuk analisa lagi:*",
            parse_mode='Markdown',
            reply_markup=get_timeframe_keyboard()
        )
        context.user_data['last_button_message_id'] = button_message.message_id
    except:
        button_message = await context.bot.send_message(
            chat_id=chat_id,
            text="🥇 Pilih timeframe untuk analisa lagi:",
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
            "Contoh: /analyze 1hour\n\n"
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
    
    await update.message.reply_text(f"⏳ Mengambil data 🥇 XAUUSD ({interval})...")
    
    data = fetch_xauusd_data(interval)
    if not data or len(data) < 20:
        await update.message.reply_text("❌ Gagal mengambil data. Pastikan FINNHUB_API_KEY sudah di-set.")
        return
    
    await update.message.reply_text("📊 Generating chart...")
    
    filename = f"xau_chart_{interval}_{int(datetime.now().timestamp())}.png"
    chart_path = generate_xauusd_chart(data, filename, interval)
    
    if not chart_path:
        await update.message.reply_text("❌ Gagal membuat chart.")
        return
    
    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"🥇 XAUUSD ({interval})\n⏳ Menganalisa..."
        )
    
    analysis = analyze_xauusd_with_gemini(chart_path)
    formatted = format_analysis_reply(analysis)
    
    await update.message.reply_text(
        f"🥇 Hasil Analisa XAUUSD ({interval}):\n\n{formatted}\n\n"
        "⚠️ Disclaimer: Bukan financial advice."
    )
    
    try:
        os.remove(chart_path)
    except:
        pass


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /price"""
    price = get_current_gold_price()
    
    if price:
        await update.message.reply_text(
            f"🥇 *Harga Gold (XAUUSD) Saat Ini*\n\n"
            f"💵 *${price:,.2f}* per troy ounce",
            parse_mode='Markdown',
            reply_markup=get_timeframe_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Gagal mengambil harga gold. Pastikan FINNHUB_API_KEY sudah di-set."
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    help_text = """📖 *Panduan Penggunaan Bot XAUUSD*

*Commands:*
/start - Pilih timeframe dengan tombol
/analyze <tf> - Analisa langsung (misal: /analyze 1hour)
/price - Lihat harga gold terkini
/help - Tampilkan bantuan ini

*Timeframe tersedia:*
1min, 5min, 15min, 30min, 1hour, 4hour, 1day

*Fitur:*
• Chart candlestick dengan EMA20 & EMA50
• Analisa AI menggunakan Gemini Vision
• Sinyal BUY/SELL/HOLD
• Entry, TP, dan SL recommendation

*API yang digunakan:*
• Finnhub - XAUUSD historical candlestick data
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
        print("Buat bot baru di @BotFather untuk XAUUSD analyzer")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        print("⚠️ Warning: GEMINI_API_KEY tidak ditemukan!")
        print("Analisa AI tidak akan berfungsi tanpa API key.")
        print("Set environment variable: export GEMINI_API_KEY='your_key'")
    
    print("🥇 Starting XAUUSD (Gold) Analysis Bot...")
    print(f"📊 Telegram Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"📊 Data Source: Yahoo Finance (GC=F)")
    print(f"🤖 Gemini API: {'Configured' if GEMINI_API_KEY else 'Not configured'}")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(handle_timeframe_callback, pattern=r'^xau_'))
    app.add_error_handler(error_handler)
    
    print("✅ Bot XAUUSD siap menerima pesan!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
