# Multi-Coin Technical Analysis Bot (Advanced Version)

Bot Telegram untuk analisa teknikal cryptocurrency menggunakan AI Gemini Vision.

## Fitur

- **14 Cryptocurrency Didukung**: BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC
- Chart candlestick real-time dari KuCoin API
- Indikator EMA20 dan EMA50
- Analisa AI menggunakan Google Gemini Vision
- Multiple timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
- Interactive keyboard untuk navigasi mudah
- Output terstruktur dengan sinyal trading

## Cryptocurrency yang Didukung

| Symbol | Name | Emoji |
|--------|------|-------|
| BTC | Bitcoin | ₿ |
| ETH | Ethereum | Ξ |
| SOL | Solana | ◎ |
| BNB | BNB | 🔶 |
| XRP | Ripple | ✕ |
| ADA | Cardano | ₳ |
| DOGE | Dogecoin | 🐕 |
| AVAX | Avalanche | 🔺 |
| MATIC | Polygon | ⬡ |
| LINK | Chainlink | ⬡ |
| DOT | Polkadot | ● |
| ATOM | Cosmos | ⚛ |
| UNI | Uniswap | 🦄 |
| LTC | Litecoin | Ł |

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
2. Pilih cryptocurrency yang ingin dianalisa
3. Pilih timeframe yang diinginkan (1m - 1w)
4. Bot akan generate chart dan menganalisa dengan AI
5. Hasil analisa akan ditampilkan beserta chart
6. Pilih coin atau timeframe lain untuk analisa ulang

## Commands

- `/start` - Memulai bot dan menampilkan pilihan coin
- `/analyze <coin> <timeframe>` - Analisa langsung (contoh: `/analyze BTC 15min`)
- `/coins` - Lihat daftar coin yang didukung dengan harga terkini
- `/help` - Menampilkan bantuan

## Screenshot

```
[GAMBAR CHART]
₿ BTC/USDT Chart (15min)

₿ Hasil Analisa BTC/USDT (15min)
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
