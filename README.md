<p align="center">
  <h1 align="center">Bot Analisa Teknikal Trading</h1>
  <p align="center">
    <strong>Analisa Teknikal Berbasis AI untuk Pasar Crypto & Forex</strong>
  </p>
  <p align="center">
    Bot Telegram yang menghasilkan chart candlestick profesional dengan indikator teknikal<br>
    dan memberikan insight trading menggunakan Google Gemini Vision
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Lisensi-MIT-blue.svg" alt="Lisensi"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Telegram-Bot%20API-blue.svg" alt="Telegram"></a>
  <a href="#"><img src="https://img.shields.io/badge/AI-Gemini%20Vision-orange.svg" alt="Gemini"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  <a href="#fitur">Fitur</a> •
  <a href="#indikator-teknikal">Indikator</a> •
  <a href="#instalasi">Instalasi</a> •
  <a href="#penggunaan">Penggunaan</a> •
  <a href="#konfigurasi">Konfigurasi</a> •
  <a href="#kontribusi">Kontribusi</a>
</p>

---

## Ringkasan

Bot Telegram terpadu untuk analisa pasar real-time:

| Pasar | Aset | Timeframe |
|-------|------|-----------|
| **Cryptocurrency** | 14 koin | 8 timeframe |
| **Forex & Komoditas** | 16 pasangan | 7 timeframe |

Bot ini menggunakan **Google Gemini Vision API** untuk menganalisa chart candlestick dan memberikan insight trading dalam bahasa natural, pengenalan pola, dan sinyal yang dapat ditindaklanjuti.

## Fitur

### Chart Profesional Multi-Panel

Setiap analisa menghasilkan chart 4-panel yang komprehensif:

```
┌─────────────────────────────────────────┐
│  Candlestick + EMA + Bollinger + Fib    │  Panel 1: Aksi Harga
├─────────────────────────────────────────┤
│            Bar Volume                    │  Panel 2: Volume
├─────────────────────────────────────────┤
│     RSI (14) dengan level 70/30         │  Panel 3: RSI
├─────────────────────────────────────────┤
│   MACD + Signal + Histogram             │  Panel 4: MACD
└─────────────────────────────────────────┘
```

### Indikator Teknikal

| Indikator | Parameter | Deskripsi |
|-----------|-----------|-----------|
| **EMA** | 20, 50 periode | Exponential Moving Average untuk arah tren |
| **Bollinger Bands** | 20 periode, 2σ | Band volatilitas dengan upper/middle/lower |
| **RSI** | 14 periode | Relative Strength Index dengan overbought (70) / oversold (30) |
| **MACD** | 12/26/9 | Moving Average Convergence Divergence dengan histogram |
| **Fibonacci** | Otomatis | Level retracement: 23.6%, 38.2%, 50%, 61.8% |

### Analisa Berbasis AI

Gemini Vision API menganalisa chart untuk memberikan:

- **Sinyal Trading**: BELI / JUAL / TAHAN dengan tingkat kepercayaan
- **Harga Masuk**: Saran harga entry
- **Target Profit**: Target TP1 dan TP2
- **Stop Loss**: Level manajemen risiko
- **Pengenalan Pola**: Pola candlestick dan chart
- **Analisa Tren**: Arah pasar saat ini
- **Support/Resistance**: Level harga penting
- **Kesimpulan**: Insight trading yang actionable

### Pasar yang Didukung

<details>
<summary><strong>Cryptocurrency - 14 Koin</strong></summary>

| Simbol | Nama | Simbol | Nama |
|--------|------|--------|------|
| BTC | Bitcoin | LINK | Chainlink |
| ETH | Ethereum | DOT | Polkadot |
| SOL | Solana | ATOM | Cosmos |
| BNB | Binance Coin | UNI | Uniswap |
| XRP | Ripple | LTC | Litecoin |
| ADA | Cardano | AVAX | Avalanche |
| DOGE | Dogecoin | MATIC | Polygon |

**Timeframe**: 1m, 5m, 15m, 30m, 1j, 4j, 1h, 1mg

</details>

<details>
<summary><strong>Forex & Komoditas - 16 Pasangan</strong></summary>

**Komoditas**
| Simbol | Nama |
|--------|------|
| XAUUSD | Emas |
| XAGUSD | Perak |
| USOIL | Minyak Mentah |

**Pasangan Utama**
| Simbol | Pasangan |
|--------|----------|
| EURUSD | Euro / Dolar AS |
| GBPUSD | Poundsterling / Dolar AS |
| USDJPY | Dolar AS / Yen Jepang |
| USDCHF | Dolar AS / Franc Swiss |
| AUDUSD | Dolar Australia / Dolar AS |
| USDCAD | Dolar AS / Dolar Kanada |
| NZDUSD | Dolar Selandia Baru / Dolar AS |

**Pasangan Silang**
| Simbol | Pasangan |
|--------|----------|
| EURGBP | Euro / Poundsterling |
| EURJPY | Euro / Yen Jepang |
| GBPJPY | Poundsterling / Yen Jepang |
| AUDJPY | Dolar Australia / Yen Jepang |
| EURAUD | Euro / Dolar Australia |
| EURCHF | Euro / Franc Swiss |

**Timeframe**: 1m, 5m, 15m, 30m, 1j, 4j, 1h

</details>

## Instalasi

### Prasyarat

- Python 3.11 atau lebih tinggi
- Token Bot Telegram (dari [@BotFather](https://t.me/BotFather))
- Google Gemini API Key (dari [Google AI Studio](https://aistudio.google.com/app/apikey))

### Mulai Cepat

```bash
# Clone repository
git clone https://github.com/yourusername/ai-trading-analysis-bots.git
cd ai-trading-analysis-bots

# Install dependencies
pip install -r requirements.txt

# Konfigurasi environment variables
cp .env.example .env
# Edit .env dengan API key Anda

# Jalankan bot
python main.py
```

### Menggunakan UV (Direkomendasikan)

```bash
# Install UV jika belum ada
pip install uv

# Install dependencies
uv sync

# Jalankan bot
uv run python main.py
```

### Deploy di Replit

[![Run on Replit](https://replit.com/badge/github/yourusername/ai-trading-analysis-bots)](https://replit.com/github/yourusername/ai-trading-analysis-bots)

1. Fork repository ini di Replit
2. Tambahkan API key di tab Secrets
3. Jalankan workflow

## Konfigurasi

### Environment Variables

Bot mengambil konfigurasi dari file `.env` atau environment variables.

| Variabel | Deskripsi | Wajib |
|----------|-----------|-------|
| `TELEGRAM_BOT_TOKEN` | Token bot dari BotFather | Ya |
| `GEMINI_API_KEY` | Google Gemini API key | Ya |

### Cara Mendapatkan API Key

<details>
<summary><strong>Token Bot Telegram</strong></summary>

1. Buka Telegram dan cari [@BotFather](https://t.me/BotFather)
2. Kirim perintah `/newbot`
3. Ikuti petunjuk untuk membuat bot Anda
4. Salin token yang diberikan

</details>

<details>
<summary><strong>Google Gemini API Key</strong></summary>

1. Kunjungi [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Masuk dengan akun Google Anda
3. Klik "Create API Key"
4. Salin key yang dihasilkan

</details>

### Contoh File .env

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIjKlMnOpQrStUvWxYz
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Penggunaan

### Perintah Bot

| Perintah | Deskripsi |
|----------|-----------|
| `/start` | Mulai bot dan tampilkan menu utama |
| `/analyze <simbol> <tf>` | Analisa langsung (contoh: `/analyze BTC 15min`) |
| `/price <simbol>` | Lihat harga terkini |
| `/help` | Tampilkan panduan penggunaan |

### Cara Kerja

1. **Mulai** bot dengan perintah `/start`
2. **Pilih** pasar (Cryptocurrency atau Forex)
3. **Pilih** aset yang ingin dianalisa
4. **Pilih** timeframe yang diinginkan
5. **Terima** chart profesional dengan analisa AI

### Output Analisa

Bot memberikan analisa terstruktur meliputi:

```
📊 HASIL ANALISA [SIMBOL] - [TIMEFRAME]

📈 SINYAL: BELI/JUAL/TAHAN
   Alasan: [Penjelasan AI]

💰 HARGA MASUK: $XX,XXX
📈 TARGET PROFIT 1: $XX,XXX
📈 TARGET PROFIT 2: $XX,XXX
🛑 STOP LOSS: $XX,XXX

🕯️ POLA: [Pola candlestick]
📊 TREN: [Tren pasar]
📍 SUPPORT: $XX,XXX
📍 RESISTANCE: $XX,XXX

💡 KESIMPULAN: [Ringkasan]
```

## Struktur Proyek

```
ai-trading-analysis-bots/
├── main.py                  # Bot utama (Crypto + Forex)
├── src/
│   ├── __init__.py          # Inisialisasi package
│   ├── btc_analyzer.py      # [DEPRECATED] Gunakan main.py
│   └── xau_analyzer.py      # [DEPRECATED] Gunakan main.py
├── docs/                    # Dokumentasi
├── assets/                  # Gambar dan screenshot
├── examples/                # Contoh penggunaan
├── .env.example             # Template environment
├── .gitignore              # Aturan git ignore
├── CHANGELOG.md            # Riwayat versi
├── CODE_OF_CONDUCT.md      # Panduan komunitas
├── CONTRIBUTING.md         # Panduan kontribusi
├── LICENSE                 # Lisensi MIT
├── README.md               # File ini
├── pyproject.toml          # Konfigurasi proyek
├── replit.md               # Dokumentasi Replit
└── requirements.txt        # Dependencies
```

## Sumber Data

Bot menggunakan beberapa sumber data dengan fallback otomatis:

| Prioritas | Sumber | Tipe | Cakupan |
|-----------|--------|------|---------|
| 1 | TradingView | Utama | Semua pasar |
| 2 | Yahoo Finance | Cadangan | Forex, Crypto |
| 3 | KuCoin API | Cadangan | Crypto saja |

Arsitektur multi-sumber ini memastikan ketersediaan tinggi dan meminimalkan downtime.

## Kontribusi

Kontribusi sangat diterima! Silakan baca [Panduan Kontribusi](CONTRIBUTING.md) dan [Kode Etik](CODE_OF_CONDUCT.md) sebelum mengirim PR.

### Setup Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Jalankan tests
pytest

# Format kode
black src/
isort src/

# Lint
ruff check src/
```

## Peringatan

**Software ini hanya untuk tujuan edukasi dan informasi.**

- Bukan saran keuangan
- Lakukan riset sendiri sebelum trading
- Kinerja masa lalu tidak menjamin hasil di masa depan
- Trading cryptocurrency dan forex memiliki risiko signifikan

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file [LICENSE](LICENSE) untuk detail.

## Pengakuan

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Wrapper Telegram Bot API
- [mplfinance](https://github.com/matplotlib/mplfinance) - Library charting keuangan
- [Google Gemini](https://ai.google.dev/) - Analisa AI vision
- [TradingView](https://tradingview.com/) - Data pasar

---

<p align="center">
  Dibuat dengan ❤️ untuk para trader
</p>

<p align="center">
  <a href="#bot-analisa-teknikal-trading">Kembali ke atas</a>
</p>
