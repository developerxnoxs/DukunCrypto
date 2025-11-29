# BTC/USDT Technical Analysis Bot

Bot Telegram untuk analisa teknikal Bitcoin (BTC/USDT) menggunakan AI Gemini Vision.

## Fitur

- Chart candlestick real-time dari KuCoin API
- Indikator EMA20 dan EMA50
- Analisa AI menggunakan Google Gemini Vision
- Multiple timeframe: 1m, 5m, 15m, 1h, 4h, 1d
- Output terstruktur dengan sinyal trading

## Output Analisa

Bot memberikan analisa lengkap meliputi:

- **SINYAL**: BUY/SELL/HOLD dengan alasan
- **ENTRY**: Harga entry yang disarankan
- **TAKE PROFIT**: Target TP1 dan TP2
- **STOP LOSS**: Level stop loss
- **SUPPORT & RESISTANCE**: Level-level penting
- **POLA**: Pola candlestick yang terdeteksi
- **TREND**: Arah trend saat ini
- **KESIMPULAN**: Ringkasan analisa

## Teknologi

- Python 3.11
- python-telegram-bot
- mplfinance (untuk chart)
- pandas
- Google Gemini AI Vision API
- KuCoin API (data market)

## Environment Variables

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

## Cara Penggunaan

1. Start bot dengan command `/start`
2. Pilih timeframe yang diinginkan (1m, 5m, 15m, 1h, 4h, 1d)
3. Bot akan generate chart dan menganalisa dengan AI
4. Hasil analisa akan ditampilkan beserta chart
5. Pilih timeframe lain untuk analisa ulang

## Commands

- `/start` - Memulai bot dan menampilkan pilihan timeframe
- `/analyze <timeframe>` - Analisa langsung (contoh: `/analyze 15min`)
- `/help` - Menampilkan bantuan

## Screenshot

```
[GAMBAR CHART]
📊 BTC/USDT Chart (15min)

📈 Hasil Analisa BTC/USDT (15min)
━━━━━━━━━━━━━━━━━━━━

📊 SINYAL:
BUY - Harga memantul dari support...

─── Trading Setup ───
🎯 ENTRY: 95000
💰 TAKE PROFIT: TP1: 95500, TP2: 96000
🛑 STOP LOSS: 94500

─── Support & Resistance ───
🔻 SUPPORT: 94500
🔺 RESISTANCE: 96000

─── Technical Analysis ───
🕯️ POLA: Bullish Engulfing
📈 TREND: Uptrend

─── Kesimpulan ───
🧠 KESIMPULAN: BTC menunjukkan sinyal bullish...

━━━━━━━━━━━━━━━━━━━━
⚠️ Disclaimer: Ini bukan financial advice.
```

## Disclaimer

Bot ini hanya untuk tujuan edukasi. Bukan merupakan saran investasi atau financial advice. Selalu lakukan riset sendiri sebelum melakukan trading.

## License

MIT License
