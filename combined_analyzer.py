import os
import io
import base64
import logging
import requests
import asyncio
import nest_asyncio
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
from pytz import timezone as tz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN_COMBINED")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TV_AVAILABLE = False
YF_AVAILABLE = False

try:
    from tvDatafeed import TvDatafeed, Interval
    TV_AVAILABLE = True
    tv = TvDatafeed()
    logging.info("TradingView DataFeed tersedia")
except ImportError:
    logging.warning("tvDatafeed tidak tersedia")

try:
    import yfinance as yf
    YF_AVAILABLE = True
    logging.info("Yahoo Finance tersedia")
except ImportError:
    logging.warning("yfinance tidak tersedia")

TV_INTERVAL_MAP = {
    "1hour": Interval.in_1_hour if TV_AVAILABLE else None,
    "4hour": Interval.in_4_hour if TV_AVAILABLE else None,
    "1day": Interval.in_daily if TV_AVAILABLE else None,
}

YF_INTERVAL_MAP = {
    "1hour": "1h",
    "4hour": "4h",
    "1day": "1d",
}

CRYPTO_COINS = {
    "BTC": {"name": "Bitcoin", "yf_symbol": "BTC-USD", "tv_symbol": "BTCUSDT"},
    "ETH": {"name": "Ethereum", "yf_symbol": "ETH-USD", "tv_symbol": "ETHUSDT"},
    "SOL": {"name": "Solana", "yf_symbol": "SOL-USD", "tv_symbol": "SOLUSDT"},
    "BNB": {"name": "BNB", "yf_symbol": "BNB-USD", "tv_symbol": "BNBUSDT"},
    "XRP": {"name": "XRP", "yf_symbol": "XRP-USD", "tv_symbol": "XRPUSDT"},
    "ADA": {"name": "Cardano", "yf_symbol": "ADA-USD", "tv_symbol": "ADAUSDT"},
    "DOGE": {"name": "Dogecoin", "yf_symbol": "DOGE-USD", "tv_symbol": "DOGEUSDT"},
    "AVAX": {"name": "Avalanche", "yf_symbol": "AVAX-USD", "tv_symbol": "AVAXUSDT"},
    "MATIC": {"name": "Polygon", "yf_symbol": "MATIC-USD", "tv_symbol": "MATICUSDT"},
    "LINK": {"name": "Chainlink", "yf_symbol": "LINK-USD", "tv_symbol": "LINKUSDT"},
    "DOT": {"name": "Polkadot", "yf_symbol": "DOT-USD", "tv_symbol": "DOTUSDT"},
    "ATOM": {"name": "Cosmos", "yf_symbol": "ATOM-USD", "tv_symbol": "ATOMUSDT"},
    "UNI": {"name": "Uniswap", "yf_symbol": "UNI-USD", "tv_symbol": "UNIUSDT"},
    "LTC": {"name": "Litecoin", "yf_symbol": "LTC-USD", "tv_symbol": "LTCUSDT"},
}

CRYPTO_EXCHANGES = ["BINANCE", "BYBIT", "COINBASE", "KRAKEN", "BITSTAMP"]

FOREX_PAIRS = {
    "XAUUSD": {"name": "Gold/USD", "yf_symbol": "GC=F", "tv_symbol": "XAUUSD"},
    "XAGUSD": {"name": "Silver/USD", "yf_symbol": "SI=F", "tv_symbol": "XAGUSD"},
    "EURUSD": {"name": "EUR/USD", "yf_symbol": "EURUSD=X", "tv_symbol": "EURUSD"},
    "GBPUSD": {"name": "GBP/USD", "yf_symbol": "GBPUSD=X", "tv_symbol": "GBPUSD"},
    "USDJPY": {"name": "USD/JPY", "yf_symbol": "USDJPY=X", "tv_symbol": "USDJPY"},
    "USDCHF": {"name": "USD/CHF", "yf_symbol": "USDCHF=X", "tv_symbol": "USDCHF"},
    "AUDUSD": {"name": "AUD/USD", "yf_symbol": "AUDUSD=X", "tv_symbol": "AUDUSD"},
    "USDCAD": {"name": "USD/CAD", "yf_symbol": "USDCAD=X", "tv_symbol": "USDCAD"},
    "NZDUSD": {"name": "NZD/USD", "yf_symbol": "NZDUSD=X", "tv_symbol": "NZDUSD"},
    "EURJPY": {"name": "EUR/JPY", "yf_symbol": "EURJPY=X", "tv_symbol": "EURJPY"},
    "GBPJPY": {"name": "GBP/JPY", "yf_symbol": "GBPJPY=X", "tv_symbol": "GBPJPY"},
    "EURGBP": {"name": "EUR/GBP", "yf_symbol": "EURGBP=X", "tv_symbol": "EURGBP"},
    "BTCUSD": {"name": "BTC/USD (Forex)", "yf_symbol": "BTC-USD", "tv_symbol": "BTCUSD"},
    "ETHUSD": {"name": "ETH/USD (Forex)", "yf_symbol": "ETH-USD", "tv_symbol": "ETHUSD"},
    "OIL": {"name": "Crude Oil", "yf_symbol": "CL=F", "tv_symbol": "USOIL"},
    "NATGAS": {"name": "Natural Gas", "yf_symbol": "NG=F", "tv_symbol": "NATURALGAS"},
}

FOREX_EXCHANGES = ["OANDA", "FXCM", "FX_IDC", "FOREXCOM", "CAPITALCOM"]


def fetch_crypto_from_tradingview(symbol, interval, n_bars=200):
    if not TV_AVAILABLE:
        return None
    
    tv_interval = TV_INTERVAL_MAP.get(interval)
    if not tv_interval:
        return None
    
    coin_info = CRYPTO_COINS.get(symbol)
    if not coin_info:
        return None
    
    tv_symbol = coin_info["tv_symbol"]
    
    for exchange in CRYPTO_EXCHANGES:
        try:
            logging.info(f"Mencoba mengambil data {tv_symbol} dari TradingView ({exchange}) interval {interval}...")
            df = tv.get_hist(symbol=tv_symbol, exchange=exchange, interval=tv_interval, n_bars=n_bars)
            
            if df is not None and not df.empty:
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
                logging.info(f"Berhasil mengambil {len(candles)} candle {tv_symbol} dari TradingView ({exchange})")
                return candles
        except Exception as e:
            logging.error(f"Gagal mengambil data dari {exchange}: {e}")
            continue
    
    return None


def fetch_crypto_from_yfinance(symbol, interval, n_bars=200):
    if not YF_AVAILABLE:
        return None
    
    coin_info = CRYPTO_COINS.get(symbol)
    if not coin_info:
        return None
    
    yf_symbol = coin_info["yf_symbol"]
    yf_interval = YF_INTERVAL_MAP.get(interval)
    
    if not yf_interval:
        return None
    
    try:
        logging.info(f"Mencoba mengambil data {yf_symbol} dari Yahoo Finance interval {yf_interval}...")
        
        if interval == "1hour":
            period = "7d"
        elif interval == "4hour":
            period = "60d"
        else:
            period = "1y"
        
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=yf_interval)
        
        if df is not None and not df.empty:
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
            
            if len(candles) > n_bars:
                candles = candles[-n_bars:]
            
            logging.info(f"Berhasil mengambil {len(candles)} candle dari Yahoo Finance")
            return candles
    except Exception as e:
        logging.error(f"Gagal mengambil data dari Yahoo Finance: {e}")
    
    return None


def fetch_crypto_from_kucoin(symbol, interval):
    interval_map = {
        "1hour": "1hour",
        "4hour": "4hour",
        "1day": "1day"
    }
    
    kucoin_interval = interval_map.get(interval, "1hour")
    
    url = f"https://api.kucoin.com/api/v1/market/candles?type={kucoin_interval}&symbol={symbol}-USDT"
    try:
        logging.info(f"Mencoba mengambil data {symbol} dari KuCoin...")
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("code") == "200000" and data.get("data"):
            candles = [[int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])] for c in data["data"]]
            candles.reverse()
            logging.info(f"Berhasil mengambil {len(candles)} candle dari KuCoin")
            return candles
    except Exception as e:
        logging.error(f"Gagal mengambil data dari KuCoin: {e}")
    return None


def fetch_crypto_data(symbol, interval):
    data = fetch_crypto_from_tradingview(symbol, interval)
    if data:
        logging.info(f"Data {symbol} berhasil diambil dari TradingView")
        return data
    
    data = fetch_crypto_from_yfinance(symbol, interval)
    if data:
        logging.info(f"Data {symbol} berhasil diambil dari Yahoo Finance")
        return data
    
    data = fetch_crypto_from_kucoin(symbol, interval)
    if data:
        logging.info(f"Data {symbol} berhasil diambil dari KuCoin")
        return data
    
    logging.error(f"Gagal mengambil data {symbol} dari semua sumber")
    return None


def fetch_forex_from_tradingview(symbol, interval, n_bars=200):
    if not TV_AVAILABLE:
        return None
    
    tv_interval = TV_INTERVAL_MAP.get(interval)
    if not tv_interval:
        return None
    
    pair_info = FOREX_PAIRS.get(symbol)
    if not pair_info:
        return None
    
    tv_symbol = pair_info["tv_symbol"]
    
    for exchange in FOREX_EXCHANGES:
        try:
            logging.info(f"Mencoba mengambil data {tv_symbol} dari TradingView ({exchange}) interval {interval}...")
            df = tv.get_hist(symbol=tv_symbol, exchange=exchange, interval=tv_interval, n_bars=n_bars)
            
            if df is not None and not df.empty:
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
                logging.info(f"Berhasil mengambil {len(candles)} candle {tv_symbol} dari TradingView ({exchange})")
                return candles
        except Exception as e:
            logging.error(f"Gagal mengambil data dari {exchange}: {e}")
            continue
    
    return None


def fetch_forex_from_yfinance(symbol, interval, n_bars=200):
    if not YF_AVAILABLE:
        return None
    
    pair_info = FOREX_PAIRS.get(symbol)
    if not pair_info:
        return None
    
    yf_symbol = pair_info["yf_symbol"]
    yf_interval = YF_INTERVAL_MAP.get(interval)
    
    if not yf_interval:
        return None
    
    try:
        logging.info(f"Mencoba mengambil data {yf_symbol} dari Yahoo Finance interval {yf_interval}...")
        
        if interval == "1hour":
            period = "7d"
        elif interval == "4hour":
            period = "60d"
        else:
            period = "1y"
        
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=yf_interval)
        
        if df is not None and not df.empty:
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
            
            if len(candles) > n_bars:
                candles = candles[-n_bars:]
            
            logging.info(f"Berhasil mengambil {len(candles)} candle dari Yahoo Finance")
            return candles
    except Exception as e:
        logging.error(f"Gagal mengambil data dari Yahoo Finance: {e}")
    
    return None


def fetch_forex_data(symbol, interval):
    data = fetch_forex_from_tradingview(symbol, interval)
    if data:
        logging.info(f"Data {symbol} berhasil diambil dari TradingView")
        return data
    
    data = fetch_forex_from_yfinance(symbol, interval)
    if data:
        logging.info(f"Data {symbol} berhasil diambil dari Yahoo Finance")
        return data
    
    logging.error(f"Gagal mengambil data {symbol} dari semua sumber")
    return None


def get_crypto_price(symbol):
    if TV_AVAILABLE:
        data = fetch_crypto_from_tradingview(symbol, "1hour", 1)
        if data and len(data) > 0:
            return data[-1][2]
    
    if YF_AVAILABLE:
        coin_info = CRYPTO_COINS.get(symbol)
        if coin_info:
            try:
                ticker = yf.Ticker(coin_info["yf_symbol"])
                data = ticker.history(period="1d")
                if not data.empty:
                    return float(data["Close"].iloc[-1])
            except:
                pass
    
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}-USDT"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("code") == "200000":
            return float(data["data"]["price"])
    except:
        pass
    
    return None


def get_forex_price(symbol):
    if TV_AVAILABLE:
        data = fetch_forex_from_tradingview(symbol, "1hour", 1)
        if data and len(data) > 0:
            return data[-1][2]
    
    if YF_AVAILABLE:
        pair_info = FOREX_PAIRS.get(symbol)
        if pair_info:
            try:
                ticker = yf.Ticker(pair_info["yf_symbol"])
                data = ticker.history(period="1d")
                if not data.empty:
                    return float(data["Close"].iloc[-1])
            except:
                pass
    
    return None


def generate_chart(data, symbol, tf, market_type="crypto"):
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

    ema20 = df["Close"].ewm(span=20).mean()
    ema50 = df["Close"].ewm(span=50).mean()

    style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        rc={'font.size': 10}
    )

    filename = f"/tmp/{symbol}_{tf}_chart.png"
    
    adds = [
        mpf.make_addplot(ema20, color='blue', width=1, label='EMA20'),
        mpf.make_addplot(ema50, color='orange', width=1, label='EMA50')
    ]

    if market_type == "crypto":
        title = f"\n{symbol}/USDT ({tf}) - TradingView"
        ylabel = "Price (USDT)"
    else:
        pair_info = FOREX_PAIRS.get(symbol, {})
        name = pair_info.get("name", symbol)
        title = f"\n{name} ({tf}) - TradingView"
        ylabel = "Price"

    mpf.plot(
        df, type='candle', volume=True, style=style,
        title=title,
        ylabel=ylabel,
        ylabel_lower="Volume",
        savefig=dict(fname=filename, dpi=150, bbox_inches='tight'),
        figratio=(16, 9),
        figscale=1.3,
        addplot=adds
    )

    return filename


def analyze_chart_with_gemini(image_path, symbol, tf, market_type="crypto"):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    if market_type == "crypto":
        asset_name = CRYPTO_COINS.get(symbol, {}).get("name", symbol)
        prompt = f"""Analisis teknikal untuk {asset_name} ({symbol}/USDT) pada timeframe {tf}.

Berikan analisis dalam format berikut:
1. TREND: [Bullish/Bearish/Sideways]
2. SUPPORT & RESISTANCE:
   - Support terdekat: $XXX
   - Resistance terdekat: $XXX
3. INDIKATOR:
   - EMA20 & EMA50: [Golden Cross/Death Cross/Netral]
   - Volume: [Meningkat/Menurun/Stabil]
4. REKOMENDASI:
   - Entry: $XXX
   - Stop Loss: $XXX
   - Take Profit: $XXX
5. KESIMPULAN: [Ringkasan singkat dalam 2-3 kalimat]

Berikan analisis yang jelas dan actionable."""
    else:
        pair_info = FOREX_PAIRS.get(symbol, {})
        pair_name = pair_info.get("name", symbol)
        prompt = f"""Analisis teknikal untuk {pair_name} ({symbol}) pada timeframe {tf}.

Berikan analisis dalam format berikut:
1. TREND: [Bullish/Bearish/Sideways]
2. SUPPORT & RESISTANCE:
   - Support terdekat: XXX
   - Resistance terdekat: XXX
3. INDIKATOR:
   - EMA20 & EMA50: [Golden Cross/Death Cross/Netral]
   - Volume: [Meningkat/Menurun/Stabil]
4. REKOMENDASI:
   - Entry: XXX
   - Stop Loss: XXX
   - Take Profit: XXX
5. KESIMPULAN: [Ringkasan singkat dalam 2-3 kalimat]

Berikan analisis yang jelas dan actionable."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": image_data
                    }
                }
            ]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Gagal mendapatkan analisis dari Gemini AI."
    except Exception as e:
        logging.error(f"Error Gemini API: {e}")
        return f"Error: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🪙 Crypto", callback_data="market_crypto"),
            InlineKeyboardButton("💱 Forex & Commodities", callback_data="market_forex")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = """🤖 *Combined Technical Analysis Bot*

Selamat datang! Bot ini menyediakan analisis teknikal untuk:

🪙 *Cryptocurrency*
Bitcoin, Ethereum, Solana, dan 11 coin lainnya

💱 *Forex & Commodities*
Gold, Silver, EUR/USD, GBP/USD, Oil, dan lainnya

📊 Data dari TradingView dengan AI Analysis

Pilih market yang ingin dianalisis:"""
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🪙 Crypto", callback_data="market_crypto"),
            InlineKeyboardButton("💱 Forex & Commodities", callback_data="market_forex")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 Pilih market untuk analisis:",
        reply_markup=reply_markup
    )


def get_crypto_menu():
    coins = list(CRYPTO_COINS.keys())
    keyboard = []
    for i in range(0, len(coins), 3):
        row = []
        for coin in coins[i:i+3]:
            row.append(InlineKeyboardButton(coin, callback_data=f"crypto_{coin}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def get_forex_menu():
    pairs = list(FOREX_PAIRS.keys())
    keyboard = []
    for i in range(0, len(pairs), 3):
        row = []
        for pair in pairs[i:i+3]:
            row.append(InlineKeyboardButton(pair, callback_data=f"forex_{pair}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def get_timeframe_menu(market_type, symbol):
    keyboard = [
        [
            InlineKeyboardButton("1H", callback_data=f"tf_{market_type}_{symbol}_1hour"),
            InlineKeyboardButton("4H", callback_data=f"tf_{market_type}_{symbol}_4hour"),
            InlineKeyboardButton("1D", callback_data=f"tf_{market_type}_{symbol}_1day")
        ],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"market_{market_type}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_main":
        keyboard = [
            [
                InlineKeyboardButton("🪙 Crypto", callback_data="market_crypto"),
                InlineKeyboardButton("💱 Forex & Commodities", callback_data="market_forex")
            ]
        ]
        await query.edit_message_text(
            "📊 Pilih market untuk analisis:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "market_crypto":
        await query.edit_message_text(
            "🪙 *Pilih Cryptocurrency:*\n\nPilih coin untuk melihat analisis teknikal.",
            parse_mode="Markdown",
            reply_markup=get_crypto_menu()
        )
    
    elif data == "market_forex":
        await query.edit_message_text(
            "💱 *Pilih Forex/Commodities:*\n\nPilih pair untuk melihat analisis teknikal.",
            parse_mode="Markdown",
            reply_markup=get_forex_menu()
        )
    
    elif data.startswith("crypto_"):
        symbol = data.replace("crypto_", "")
        coin_info = CRYPTO_COINS.get(symbol, {})
        name = coin_info.get("name", symbol)
        price = get_crypto_price(symbol)
        
        price_text = f"${price:,.2f}" if price else "N/A"
        
        await query.edit_message_text(
            f"🪙 *{name} ({symbol})*\n\n💰 Harga: {price_text}\n\n⏰ Pilih timeframe:",
            parse_mode="Markdown",
            reply_markup=get_timeframe_menu("crypto", symbol)
        )
    
    elif data.startswith("forex_"):
        symbol = data.replace("forex_", "")
        pair_info = FOREX_PAIRS.get(symbol, {})
        name = pair_info.get("name", symbol)
        price = get_forex_price(symbol)
        
        if symbol in ["XAUUSD", "XAGUSD"]:
            price_text = f"${price:,.2f}" if price else "N/A"
        elif symbol in ["OIL", "NATGAS"]:
            price_text = f"${price:,.3f}" if price else "N/A"
        else:
            price_text = f"{price:.5f}" if price else "N/A"
        
        await query.edit_message_text(
            f"💱 *{name}*\n\n💰 Harga: {price_text}\n\n⏰ Pilih timeframe:",
            parse_mode="Markdown",
            reply_markup=get_timeframe_menu("forex", symbol)
        )
    
    elif data.startswith("tf_"):
        parts = data.split("_")
        market_type = parts[1]
        symbol = parts[2]
        timeframe = parts[3]
        
        tf_display = {"1hour": "1H", "4hour": "4H", "1day": "1D"}.get(timeframe, timeframe)
        
        await query.edit_message_text(
            f"⏳ Mengambil data {symbol} ({tf_display})...\n\nMohon tunggu sebentar."
        )
        
        if market_type == "crypto":
            candle_data = fetch_crypto_data(symbol, timeframe)
            chart_market_type = "crypto"
        else:
            candle_data = fetch_forex_data(symbol, timeframe)
            chart_market_type = "forex"
        
        if not candle_data:
            keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data=f"market_{market_type}")]]
            await query.edit_message_text(
                f"❌ Gagal mengambil data {symbol}.\n\nSilakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        await query.edit_message_text(f"📊 Membuat chart {symbol}...")
        
        try:
            chart_path = generate_chart(candle_data, symbol, tf_display, chart_market_type)
        except Exception as e:
            logging.error(f"Error generating chart: {e}")
            keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data=f"market_{market_type}")]]
            await query.edit_message_text(
                f"❌ Gagal membuat chart: {str(e)}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        await query.edit_message_text(f"🤖 Menganalisis chart dengan AI...")
        
        analysis = analyze_chart_with_gemini(chart_path, symbol, tf_display, chart_market_type)
        
        keyboard = [
            [
                InlineKeyboardButton("1H", callback_data=f"tf_{market_type}_{symbol}_1hour"),
                InlineKeyboardButton("4H", callback_data=f"tf_{market_type}_{symbol}_4hour"),
                InlineKeyboardButton("1D", callback_data=f"tf_{market_type}_{symbol}_1day")
            ],
            [InlineKeyboardButton("⬅️ Kembali", callback_data=f"market_{market_type}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        with open(chart_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption=f"📊 *Analisis {symbol} ({tf_display})*\n\n{analysis}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        
        await query.message.delete()
        
        if os.path.exists(chart_path):
            os.remove(chart_path)


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "💰 *Harga Terkini*\n\n"
    
    msg += "🪙 *Cryptocurrency:*\n"
    for symbol in list(CRYPTO_COINS.keys())[:5]:
        price = get_crypto_price(symbol)
        if price:
            msg += f"• {symbol}: ${price:,.2f}\n"
    
    msg += "\n💱 *Forex & Commodities:*\n"
    for symbol in ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD"]:
        price = get_forex_price(symbol)
        if price:
            if symbol in ["XAUUSD", "XAGUSD"]:
                msg += f"• {symbol}: ${price:,.2f}\n"
            else:
                msg += f"• {symbol}: {price:.5f}\n"
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Analisis", callback_data="back_main")
        ]
    ]
    
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 *Panduan Penggunaan Bot*

*Perintah:*
/start - Mulai bot & pilih market
/analyze - Analisis teknikal
/price - Harga terkini
/help - Panduan penggunaan

*Market yang Tersedia:*

🪙 *Crypto (14 coin):*
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC

💱 *Forex & Commodities (16 pair):*
XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURJPY, GBPJPY, EURGBP, BTCUSD, ETHUSD, OIL, NATGAS

*Timeframe:*
• 1H - 1 Jam
• 4H - 4 Jam
• 1D - 1 Hari

*Fitur:*
• Chart candlestick dengan EMA20 & EMA50
• Analisis AI dengan Gemini Vision
• Support & Resistance otomatis
• Rekomendasi entry, SL, TP

📊 Data dari TradingView"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


def main():
    if not TELEGRAM_BOT_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN_COMBINED tidak ditemukan!")
        return
    
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY tidak ditemukan!")
        return
    
    logging.info("Memulai Combined Technical Analysis Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    logging.info("Bot siap menerima perintah!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
