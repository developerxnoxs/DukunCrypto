# Bot Analisa Teknikal Trading Pro

## Ringkasan

Proyek ini adalah bot Telegram yang menyediakan analisa teknikal PROFESIONAL berbasis AI untuk pasar cryptocurrency dan forex/komoditas. Sistem menggunakan Google Gemini Vision API dengan sistem konfluensi multi-indikator untuk menganalisa chart candlestick, memberikan insight akurat ke pengguna melalui Telegram.

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

## Indikator Teknikal (Enhanced - v3.0)

### Indikator Overlay (Panel Utama)
- **EMA20**: Exponential Moving Average 20-period (biru)
- **EMA50**: Exponential Moving Average 50-period (orange)
- **EMA200**: Exponential Moving Average 200-period (merah) - Tren Jangka Panjang
- **Bollinger Bands**: 20-period, 2 standard deviations (ungu)
- **Fibonacci Retracement**: Level otomatis (23.6%, 38.2%, 50%, 61.8%)

### Indikator Momentum
- **RSI (14)**: dengan level 30/50/70
- **Stochastic RSI**: dengan level 20/80 untuk deteksi overbought/oversold ekstrem
- **MACD (12/26/9)**: dengan signal line dan histogram

### Indikator Konfluensi (Baru)
- **ADX (Average Directional Index)**: Mengukur kekuatan tren
  - ADX > 40: Tren SANGAT KUAT
  - ADX > 25: Tren KUAT
  - ADX > 20: Tren SEDANG
  - ADX < 20: Tren LEMAH / Ranging
- **ATR (Average True Range)**: Volatilitas untuk kalkulasi SL/TP dinamis
- **RSI Divergence Detection**: Deteksi bullish/bearish divergence
- **MACD Divergence Detection**: Deteksi bullish/bearish divergence

## Sistem Konfluensi Multi-Indikator (Baru - v3.0)

Sistem menghitung 10+ sinyal untuk menentukan kekuatan dan arah tren:

| Sinyal | Kondisi Bullish | Kondisi Bearish |
|--------|-----------------|-----------------|
| EMA Crossover | EMA20 > EMA50 | EMA20 < EMA50 |
| Trend Direction | Harga > EMA20 > EMA50 | Harga < EMA20 < EMA50 |
| EMA200 Position | Harga > EMA200 | Harga < EMA200 |
| RSI | < 30 (oversold) | > 70 (overbought) |
| Stochastic RSI | < 20 (oversold) | > 80 (overbought) |
| MACD Crossover | MACD > Signal | MACD < Signal |
| MACD Histogram | Momentum positif & naik | Momentum negatif & turun |
| Bollinger Position | Di bawah Lower Band | Di atas Upper Band |
| RSI Divergence | Bullish Divergence | Bearish Divergence |
| MACD Divergence | Bullish Divergence | Bearish Divergence |

### Output Sinyal
- **STRONG_BUY**: Skor bullish >= 70% dengan konfirmasi tinggi
- **BUY**: Skor bullish > bearish x 1.3
- **HOLD**: Sinyal seimbang atau konflik
- **SELL**: Skor bearish > bullish x 1.3
- **STRONG_SELL**: Skor bearish >= 70% dengan konfirmasi tinggi

## Layout Chart (Enhanced - v3.0)

Layout profesional 5-panel dengan rasio 6:2:1.5:1.5:1.5:
1. **Candlestick + EMA20 + EMA50 + EMA200 + Bollinger + Fibonacci**
2. **Volume bars**
3. **RSI (14)** dengan level 30/50/70
4. **Stochastic RSI** dengan level 20/80
5. **MACD** dengan histogram

## Analisa Berbasis Timeframe (v2.1)

Prompt analisa AI disesuaikan berdasarkan timeframe untuk memberikan target yang lebih realistis dan prediksi waktu spesifik:

| Timeframe | Tipe Trading | Target Profit | Stop Loss | Prediksi Waktu |
|-----------|--------------|---------------|-----------|----------------|
| 1min | Scalping | 0.1% - 0.3% | 0.05% - 0.15% | 1-5 menit |
| 5min | Scalping | 0.2% - 0.5% | 0.1% - 0.25% | 5-15 menit |
| 15min | Intraday | 0.3% - 0.8% | 0.15% - 0.4% | 15-45 menit |
| 30min | Intraday | 0.5% - 1.2% | 0.25% - 0.6% | 30-90 menit |
| 1hour | Swing Trading | 1% - 2.5% | 0.5% - 1.2% | 1-4 jam |
| 4hour | Swing Trading | 2% - 5% | 1% - 2.5% | 4-12 jam |
| 1day | Position Trading | 3% - 10% | 1.5% - 5% | 1-3 hari |
| 1week | Position/Investment | 5% - 20% | 3% - 10% | 1-4 minggu |

**Fitur Prediksi Berbasis Waktu:**
- PREDIKSI X KE DEPAN: Contoh "PREDIKSI 1 MENIT KE DEPAN: NAIK - Keyakinan Tinggi"
- PERKIRAAN PERGERAKAN: Contoh "Dalam 1-5 menit, harga diperkirakan naik menuju $100,500"
- RASIO RR: Risk:Reward ratio untuk evaluasi trade
- WAKTU HOLD: Estimasi durasi berdasarkan timeframe
- KONFIRMASI: Jumlah indikator yang mendukung sinyal (X dari 5)
- KESIMPULAN: Menyebutkan arah prediksi spesifik untuk timeframe yang dipilih

## Konfigurasi Environment

Bot mengambil konfigurasi dari file `.env` atau environment variables.

**Cara Setup:**
1. Salin `.env.example` ke `.env`
2. Isi dengan nilai yang benar

| Variable | Deskripsi |
|----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram (dari @BotFather) |
| `GEMINI_API_KEY` | Google Gemini API key (dari Google AI Studio) |

**Contoh file .env:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIjKlMnOpQrStUvWxYz
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Workflow

| Nama | Perintah | Deskripsi |
|------|----------|-----------|
| Trading Analysis Bot | `uv run python main.py` | Bot analisa crypto & forex |

## Sumber Data

1. **TradingView** (utama) - via xnoxs_fetcher
2. **Yahoo Finance** (cadangan) - via yfinance
3. **KuCoin API** (cadangan crypto) - REST API langsung

## Fitur Bot (Enhanced - v3.0)

- Menu pilihan pasar (Cryptocurrency / Forex)
- Pilihan timeframe interaktif
- Chart candlestick dengan 8+ indikator teknikal
- Sistem Konfluensi Multi-Indikator
- Deteksi RSI & MACD Divergence
- ADX untuk kekuatan tren
- ATR untuk volatilitas & penentuan SL/TP dinamis
- EMA200 untuk tren jangka panjang
- Stochastic RSI untuk momentum sensitif
- Analisa AI Gemini Vision Enhanced dengan konteks konfluensi
- Sinyal STRONG BUY/BUY/HOLD/SELL/STRONG SELL
- 3 Level Target Profit + Stop Loss Optimal
- Support & Resistance Multi-Level
- Output dalam Bahasa Indonesia

## Perubahan Terbaru

- 2024-12-04: **v3.1 - Signal Consistency Fix**
  - Memperbaiki masalah sinyal yang tidak konsisten antara caption chart dan analisa Gemini
  - Caption chart sekarang menampilkan "Menganalisa dengan AI..." saat proses analisa
  - Setelah Gemini selesai menganalisa, caption chart diupdate dengan sinyal dari hasil AI
  - Menambahkan fungsi extract_signal_from_analysis() untuk mengekstrak sinyal dari respons Gemini
  - Menghapus sinyal confluence dari caption chart untuk menghindari kebingungan
  - Caption chart sekarang selalu sinkron dengan hasil analisa Gemini AI

- 2024-12-04: **v3.0 - Enhanced Analysis System**
  - Menambahkan EMA200 untuk identifikasi tren jangka panjang
  - Menambahkan Stochastic RSI untuk momentum sensitif
  - Menambahkan ADX untuk mengukur kekuatan tren
  - Menambahkan ATR untuk kalkulasi volatilitas dan SL/TP dinamis
  - Implementasi sistem konfluensi multi-indikator (10+ sinyal)
  - Implementasi deteksi RSI & MACD divergence
  - Upgrade prompt Gemini AI dengan konteks konfluensi lengkap
  - Chart sekarang 5-panel (Price, Volume, RSI, Stoch RSI, MACD)
  - Sinyal baru: STRONG_BUY dan STRONG_SELL
  - 3 level target profit
  - Kekuatan sinyal (X dari 8 indikator)
  - Peringatan risiko dalam analisa
- 2024-12-03: Menggabungkan btc_analyzer dan xau_analyzer menjadi main.py
- 2024-12-03: Menambahkan menu pilihan pasar (crypto/forex)
- 2024-12-03: Mengubah semua output ke Bahasa Indonesia
- 2024-12-02: Menambahkan indikator RSI, MACD, Bollinger Bands, Fibonacci
- 2024-12-02: Reorganisasi struktur proyek untuk GitHub
- 2024-12-02: Menambahkan dokumentasi lengkap
