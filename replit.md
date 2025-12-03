# Bot Analisa Teknikal Trading

## Ringkasan

Proyek ini adalah bot Telegram yang menyediakan analisa teknikal berbasis AI untuk pasar cryptocurrency dan forex/komoditas. Sistem menggunakan Google Gemini Vision API untuk menganalisa chart candlestick dengan indikator teknikal, memberikan insight langsung ke pengguna melalui Telegram.

Bot mendukung:
- **Cryptocurrency**: 14 koin populer (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, MATIC, LINK, DOT, ATOM, UNI, LTC)
- **Forex & Komoditas**: 16 pasangan (XAUUSD, XAGUSD, USOIL, EUR/USD, GBP/USD, dan lainnya)

Semua output dalam **Bahasa Indonesia**.

## Preferensi Pengguna

- Gaya komunikasi: Bahasa sehari-hari yang sederhana
- Bahasa: Indonesia (Bahasa Indonesia)

## Struktur Proyek

```
ai-trading-analysis-bots/
├── main.py                  # Bot utama (gabungan crypto + forex)
├── src/
│   ├── __init__.py          # Package initialization
│   ├── btc_analyzer.py      # [DEPRECATED] Gunakan main.py
│   └── xau_analyzer.py      # [DEPRECATED] Gunakan main.py
├── docs/
│   ├── API.md               # Dokumentasi API
│   └── TECHNICAL_INDICATORS.md
├── assets/                  # Gambar dan screenshots
├── examples/                # Contoh penggunaan
├── CHANGELOG.md             # Riwayat versi
├── CODE_OF_CONDUCT.md       # Panduan komunitas
├── CONTRIBUTING.md          # Panduan kontribusi
├── LICENSE                  # MIT License
├── README.md                # Dokumentasi utama
├── pyproject.toml           # Konfigurasi proyek
├── requirements.txt         # Dependencies
└── replit.md                # File ini
```

## Indikator Teknikal

- **EMA20 dan EMA50**: Exponential Moving Averages (overlay harga)
- **Bollinger Bands**: 20-period, 2 standard deviations
- **Fibonacci Retracement**: Level otomatis (23.6%, 38.2%, 50%, 61.8%)
- **RSI**: 14-period dengan garis overbought (70) / oversold (30)
- **MACD**: 12/26/9 dengan signal line dan histogram

## Layout Chart

Layout profesional 4-panel dengan rasio 6:2:2:2:
1. Candlestick + EMA + Bollinger + Fibonacci
2. Volume bars
3. Indikator RSI
4. Indikator MACD

## Environment Variables

| Variable | Deskripsi |
|----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram |
| `GEMINI_API_KEY` | Google Gemini API key |

## Workflow

| Nama | Perintah | Deskripsi |
|------|----------|-----------|
| Trading Analysis Bot | `uv run python main.py` | Bot analisa crypto & forex |

## Sumber Data

1. **TradingView** (utama) - via xnoxs_fetcher
2. **Yahoo Finance** (cadangan) - via yfinance
3. **KuCoin API** (cadangan crypto) - REST API langsung

## Fitur Bot

- Menu pilihan pasar (Cryptocurrency / Forex)
- Pilihan timeframe interaktif
- Chart candlestick dengan indikator lengkap
- Analisa AI dengan Gemini Vision
- Sinyal BELI/JUAL/TAHAN
- Rekomendasi harga masuk, target profit, stop loss
- Output dalam Bahasa Indonesia

## Perubahan Terbaru

- 2024-12-03: Menggabungkan btc_analyzer dan xau_analyzer menjadi main.py
- 2024-12-03: Menambahkan menu pilihan pasar (crypto/forex)
- 2024-12-03: Mengubah semua output ke Bahasa Indonesia
- 2024-12-02: Menambahkan indikator RSI, MACD, Bollinger Bands, Fibonacci
- 2024-12-02: Reorganisasi struktur proyek untuk GitHub
- 2024-12-02: Menambahkan dokumentasi lengkap
