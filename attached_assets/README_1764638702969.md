# XnoxsFetcher

## Apa itu XnoxsFetcher?

**XnoxsFetcher** adalah library Python yang memungkinkan Anda mengambil data pasar keuangan (saham, crypto, forex, komoditas) dari TradingView secara otomatis. Dengan library ini, Anda bisa mendapatkan data harga historis dan data real-time untuk analisis trading atau pembuatan bot trading.

**Author:** developerxnoxs  
**Versi:** 3.0.0  
**Lisensi:** MIT

---

## Daftar Isi

1. [Instalasi](#instalasi)
2. [Penggunaan Dasar](#penggunaan-dasar)
3. [Mengambil Data Saham](#mengambil-data-saham)
4. [Mengambil Data Cryptocurrency](#mengambil-data-cryptocurrency)
5. [Memilih Timeframe](#memilih-timeframe)
6. [Data Futures (Kontrak Berjangka)](#data-futures-kontrak-berjangka)
7. [Extended Trading Session](#extended-trading-session)
8. [Live Data Streaming](#live-data-streaming)
9. [Autentikasi TradingView](#autentikasi-tradingview)
10. [Daftar Exchange yang Didukung](#daftar-exchange-yang-didukung)
11. [Troubleshooting](#troubleshooting)
12. [Contoh Lengkap](#contoh-lengkap)

---

## Instalasi

### Langkah 1: Pastikan Python Terinstall

Buka terminal/command prompt dan ketik:

```bash
python --version
```

Jika muncul versi Python (minimal 3.9), lanjut ke langkah 2. Jika tidak, install Python terlebih dahulu dari [python.org](https://python.org).

### Langkah 2: Install Dependencies

```bash
pip install pandas websocket-client requests python-dateutil
```

### Langkah 3: Download Library

**Cara 1: Clone dari GitHub**
```bash
git clone https://github.com/developerxnoxs/xnoxs_fetcher.git
cd xnoxs_fetcher
pip install -e .
```

**Cara 2: Install langsung dari GitHub**
```bash
pip install git+https://github.com/developerxnoxs/xnoxs_fetcher.git
```

### Langkah 4: Verifikasi Instalasi

Buat file Python baru dan jalankan:

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame
print("Instalasi berhasil!")
```

Jika tidak ada error, library siap digunakan.

---

## Penggunaan Dasar

### Membuat Fetcher

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

# Buat instance fetcher (tanpa login - mode anonymous)
fetcher = XnoxsFetcher()
```

### Mengambil Data

```python
# Ambil 10 bar data harian Apple
data = fetcher.get_historical_data(
    symbol="AAPL",           # Kode saham
    exchange="NASDAQ",       # Nama bursa
    timeframe=TimeFrame.DAILY,  # Timeframe harian
    bars=10                  # Jumlah bar yang diambil
)

# Tampilkan data
print(data)
```

### Hasil Output

```
                          symbol     open    high       low   close      volume
datetime                                                                       
2025-11-17 14:30:00  NASDAQ:AAPL  268.815  270.49  265.7300  267.46  45018260.0
2025-11-18 14:30:00  NASDAQ:AAPL  269.990  270.71  265.3200  267.44  45677278.0
...
```

**Penjelasan kolom:**
- `datetime`: Waktu bar
- `symbol`: Kode simbol dengan exchange
- `open`: Harga pembukaan
- `high`: Harga tertinggi
- `low`: Harga terendah
- `close`: Harga penutupan
- `volume`: Volume perdagangan

---

## Mengambil Data Saham

### Saham Amerika (NASDAQ, NYSE)

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Apple dari NASDAQ
apple = fetcher.get_historical_data(
    symbol="AAPL",
    exchange="NASDAQ",
    timeframe=TimeFrame.DAILY,
    bars=100
)

# Tesla dari NASDAQ
tesla = fetcher.get_historical_data(
    symbol="TSLA",
    exchange="NASDAQ",
    timeframe=TimeFrame.HOUR_1,
    bars=50
)

# Microsoft dari NASDAQ
msft = fetcher.get_historical_data(
    symbol="MSFT",
    exchange="NASDAQ",
    timeframe=TimeFrame.MINUTE_15,
    bars=200
)
```

### Saham Indonesia (IDX)

```python
# Bank BCA
bbca = fetcher.get_historical_data(
    symbol="BBCA",
    exchange="IDX",
    timeframe=TimeFrame.DAILY,
    bars=100
)

# Telkom
tlkm = fetcher.get_historical_data(
    symbol="TLKM",
    exchange="IDX",
    timeframe=TimeFrame.DAILY,
    bars=100
)
```

### Saham India (NSE, BSE)

```python
# Reliance Industries
reliance = fetcher.get_historical_data(
    symbol="RELIANCE",
    exchange="NSE",
    timeframe=TimeFrame.DAILY,
    bars=100
)

# Tata Consultancy Services
tcs = fetcher.get_historical_data(
    symbol="TCS",
    exchange="NSE",
    timeframe=TimeFrame.HOUR_4,
    bars=200
)
```

---

## Mengambil Data Cryptocurrency

### Bitcoin

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Bitcoin vs USD dari Binance
btc = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.HOUR_1,
    bars=500
)

print(f"Harga BTC terakhir: ${btc['close'].iloc[-1]:,.2f}")
```

### Ethereum

```python
# Ethereum vs USDT dari Binance
eth = fetcher.get_historical_data(
    symbol="ETHUSDT",
    exchange="BINANCE",
    timeframe=TimeFrame.MINUTE_15,
    bars=1000
)

print(f"Harga ETH terakhir: ${eth['close'].iloc[-1]:,.2f}")
```

### Altcoins Lainnya

```python
# Solana
sol = fetcher.get_historical_data(
    symbol="SOLUSDT",
    exchange="BINANCE",
    timeframe=TimeFrame.HOUR_4,
    bars=200
)

# Cardano
ada = fetcher.get_historical_data(
    symbol="ADAUSDT",
    exchange="BINANCE",
    timeframe=TimeFrame.DAILY,
    bars=100
)

# XRP
xrp = fetcher.get_historical_data(
    symbol="XRPUSDT",
    exchange="BINANCE",
    timeframe=TimeFrame.HOUR_1,
    bars=300
)
```

---

## Memilih Timeframe

Timeframe menentukan interval waktu setiap candlestick/bar. Berikut semua timeframe yang tersedia:

### Tabel Timeframe

| Kategori | TimeFrame | Penjelasan |
|----------|-----------|------------|
| **Menit** | `TimeFrame.MINUTE_1` | 1 menit per bar |
| | `TimeFrame.MINUTE_3` | 3 menit per bar |
| | `TimeFrame.MINUTE_5` | 5 menit per bar |
| | `TimeFrame.MINUTE_15` | 15 menit per bar |
| | `TimeFrame.MINUTE_30` | 30 menit per bar |
| | `TimeFrame.MINUTE_45` | 45 menit per bar |
| **Jam** | `TimeFrame.HOUR_1` | 1 jam per bar |
| | `TimeFrame.HOUR_2` | 2 jam per bar |
| | `TimeFrame.HOUR_3` | 3 jam per bar |
| | `TimeFrame.HOUR_4` | 4 jam per bar |
| **Harian+** | `TimeFrame.DAILY` | 1 hari per bar |
| | `TimeFrame.WEEKLY` | 1 minggu per bar |
| | `TimeFrame.MONTHLY` | 1 bulan per bar |

### Contoh Penggunaan Berbagai Timeframe

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Data 1 menit - untuk scalping
data_1m = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.MINUTE_1,
    bars=500
)

# Data 4 jam - untuk swing trading
data_4h = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.HOUR_4,
    bars=200
)

# Data harian - untuk investasi jangka panjang
data_daily = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.DAILY,
    bars=365  # 1 tahun terakhir
)

# Data mingguan - untuk analisis makro
data_weekly = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.WEEKLY,
    bars=52  # 1 tahun terakhir
)
```

---

## Data Futures (Kontrak Berjangka)

Untuk mengambil data futures/kontrak berjangka, gunakan parameter `futures_contract`:

- `futures_contract=1` : Kontrak bulan depan (front month)
- `futures_contract=2` : Kontrak bulan berikutnya (next month)

### Contoh Futures

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Crude Oil Futures - front month
crude_oil = fetcher.get_historical_data(
    symbol="CRUDEOIL",
    exchange="MCX",
    timeframe=TimeFrame.HOUR_4,
    bars=100,
    futures_contract=1  # Kontrak bulan depan
)

# Nifty Futures - front month
nifty_fut = fetcher.get_historical_data(
    symbol="NIFTY",
    exchange="NSE",
    timeframe=TimeFrame.MINUTE_15,
    bars=200,
    futures_contract=1
)

# Gold Futures - next month
gold = fetcher.get_historical_data(
    symbol="GOLD",
    exchange="MCX",
    timeframe=TimeFrame.HOUR_1,
    bars=150,
    futures_contract=2  # Kontrak bulan berikutnya
)
```

---

## Extended Trading Session

Untuk mendapatkan data pre-market dan after-hours (sesi perdagangan diperpanjang), gunakan parameter `extended_session=True`:

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Data Apple termasuk pre-market dan after-hours
apple_extended = fetcher.get_historical_data(
    symbol="AAPL",
    exchange="NASDAQ",
    timeframe=TimeFrame.MINUTE_5,
    bars=500,
    extended_session=True  # Termasuk sesi diperpanjang
)

# Data Tesla - hanya jam perdagangan reguler
tesla_regular = fetcher.get_historical_data(
    symbol="TSLA",
    exchange="NASDAQ",
    timeframe=TimeFrame.MINUTE_5,
    bars=500,
    extended_session=False  # Default: hanya jam reguler
)
```

---

## Live Data Streaming

Untuk mendapatkan data real-time yang terus diupdate, gunakan `XnoxsLiveFeed`:

### Contoh Live Streaming

```python
from xnoxs_fetcher import XnoxsLiveFeed, TimeFrame
import time

# Buat live feed
live = XnoxsLiveFeed()

# Buat symbol set untuk Bitcoin 1 menit
seis = live.create_symbol_set(
    symbol="BTCUSD",
    exchange="BINANCE",
    interval=TimeFrame.MINUTE_1
)

# Definisikan callback - fungsi yang dipanggil setiap ada data baru
def on_new_price(symbol_set, data):
    close_price = data['close'].iloc[0]
    timestamp = data.index[0]
    print(f"[{timestamp}] BTC: ${close_price:,.2f}")

# Daftarkan consumer
consumer = seis.create_consumer(on_new_price)

# Biarkan streaming berjalan selama 5 menit
print("Streaming data BTC... (tekan Ctrl+C untuk berhenti)")
try:
    time.sleep(300)  # 5 menit
except KeyboardInterrupt:
    pass

# Berhenti streaming
live.shutdown()
print("Streaming dihentikan.")
```

### Streaming Multiple Symbols

```python
from xnoxs_fetcher import XnoxsLiveFeed, TimeFrame

live = XnoxsLiveFeed()

# Callback untuk BTC
def on_btc_update(seis, data):
    print(f"BTC: ${data['close'].iloc[0]:,.2f}")

# Callback untuk ETH
def on_eth_update(seis, data):
    print(f"ETH: ${data['close'].iloc[0]:,.2f}")

# Buat symbol sets
btc_seis = live.create_symbol_set("BTCUSD", "BINANCE", TimeFrame.MINUTE_1)
eth_seis = live.create_symbol_set("ETHUSDT", "BINANCE", TimeFrame.MINUTE_1)

# Daftarkan consumers
btc_consumer = btc_seis.create_consumer(on_btc_update)
eth_consumer = eth_seis.create_consumer(on_eth_update)

# Streaming akan berjalan di background
# Panggil live.shutdown() untuk menghentikan
```

---

## Autentikasi TradingView

Untuk akses data yang lebih lengkap, Anda bisa login dengan akun TradingView:

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

# Dengan login TradingView
fetcher = XnoxsFetcher(
    username="email_tradingview_anda@gmail.com",
    password="password_tradingview_anda"
)

# Sekarang bisa mengakses data premium
data = fetcher.get_historical_data(
    symbol="AAPL",
    exchange="NASDAQ",
    timeframe=TimeFrame.MINUTE_1,
    bars=5000  # Bisa ambil lebih banyak data
)
```

**Catatan:** Mode anonymous (tanpa login) juga berfungsi, tapi beberapa data mungkin terbatas.

---

## Daftar Exchange yang Didukung

Berikut beberapa exchange populer yang didukung:

### Saham Amerika
| Exchange | Kode | Contoh Simbol |
|----------|------|---------------|
| NASDAQ | `NASDAQ` | AAPL, TSLA, MSFT, GOOGL |
| NYSE | `NYSE` | JPM, BAC, WMT, DIS |
| AMEX | `AMEX` | SPY, GLD, SLV |

### Cryptocurrency
| Exchange | Kode | Contoh Simbol |
|----------|------|---------------|
| Binance | `BINANCE` | BTCUSD, ETHUSDT, BNBUSDT |
| Coinbase | `COINBASE` | BTCUSD, ETHUSD |
| Bybit | `BYBIT` | BTCUSDT, ETHUSDT |

### Saham Asia
| Exchange | Kode | Contoh Simbol |
|----------|------|---------------|
| Indonesia | `IDX` | BBCA, TLKM, BBRI |
| India NSE | `NSE` | RELIANCE, TCS, INFY |
| India BSE | `BSE` | RELIANCE, TCS |
| Hong Kong | `HKEX` | 0700, 9988 |
| Tokyo | `TSE` | 7203, 9984 |

### Forex
| Exchange | Kode | Contoh Simbol |
|----------|------|---------------|
| FX | `FX` | EURUSD, GBPUSD, USDJPY |
| OANDA | `OANDA` | EURUSD, GBPUSD |

### Komoditas
| Exchange | Kode | Contoh Simbol |
|----------|------|---------------|
| MCX India | `MCX` | GOLD, SILVER, CRUDEOIL |
| COMEX | `COMEX` | GC1!, SI1! |
| NYMEX | `NYMEX` | CL1!, NG1! |

---

## Troubleshooting

### Error: "Symbol search blocked by TradingView"

**Penyebab:** TradingView membatasi pencarian simbol dari server.

**Solusi:** Gunakan simbol yang sudah Anda ketahui langsung. Pencarian simbol bisa dilakukan di website TradingView.

### Error: "WebSocket error: Connection to remote host was lost"

**Penyebab:** Koneksi terputus saat mengambil data terlalu cepat.

**Solusi:** Tambahkan jeda antar request:

```python
import time

data1 = fetcher.get_historical_data("AAPL", "NASDAQ", TimeFrame.DAILY, 10)
time.sleep(1)  # Tunggu 1 detik
data2 = fetcher.get_historical_data("TSLA", "NASDAQ", TimeFrame.DAILY, 10)
```

### Error: Data return None

**Penyebab:** Simbol atau exchange salah.

**Solusi:** Pastikan kode simbol dan exchange benar. Cek di TradingView.com.

### Tips Performance

1. **Jangan terlalu banyak request sekaligus** - Beri jeda 1-2 detik antar request
2. **Gunakan jumlah bars yang wajar** - Maksimal 5000 bars per request
3. **Cache data yang sudah diambil** - Simpan ke file untuk menghindari request berulang

---

## Contoh Lengkap

### Contoh 1: Analisis Saham Sederhana

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame
import pandas as pd

# Inisialisasi
fetcher = XnoxsFetcher()

# Ambil data Apple 1 tahun terakhir
data = fetcher.get_historical_data(
    symbol="AAPL",
    exchange="NASDAQ",
    timeframe=TimeFrame.DAILY,
    bars=252  # Sekitar 1 tahun trading days
)

if data is not None:
    # Hitung statistik
    print("=" * 50)
    print("ANALISIS SAHAM APPLE (AAPL)")
    print("=" * 50)
    print(f"Periode: {data.index[0]} - {data.index[-1]}")
    print(f"Jumlah data: {len(data)} hari")
    print()
    print(f"Harga tertinggi: ${data['high'].max():,.2f}")
    print(f"Harga terendah: ${data['low'].min():,.2f}")
    print(f"Harga terakhir: ${data['close'].iloc[-1]:,.2f}")
    print()
    print(f"Volume rata-rata: {data['volume'].mean():,.0f}")
    print(f"Volume tertinggi: {data['volume'].max():,.0f}")
    print()
    
    # Hitung return
    first_price = data['close'].iloc[0]
    last_price = data['close'].iloc[-1]
    returns = ((last_price - first_price) / first_price) * 100
    print(f"Return 1 tahun: {returns:,.2f}%")
else:
    print("Gagal mengambil data")
```

### Contoh 2: Monitoring Crypto Real-time

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame
import time

fetcher = XnoxsFetcher()

cryptos = [
    ("BTCUSD", "BINANCE"),
    ("ETHUSDT", "BINANCE"),
    ("SOLUSDT", "BINANCE"),
]

print("=" * 60)
print("MONITORING CRYPTO REAL-TIME")
print("=" * 60)

while True:
    print(f"\n[{time.strftime('%H:%M:%S')}] Harga terkini:")
    print("-" * 40)
    
    for symbol, exchange in cryptos:
        data = fetcher.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            timeframe=TimeFrame.MINUTE_1,
            bars=1
        )
        
        if data is not None:
            price = data['close'].iloc[-1]
            print(f"  {symbol}: ${price:,.2f}")
        
        time.sleep(0.5)  # Jeda antar request
    
    time.sleep(60)  # Update setiap 1 menit
```

### Contoh 3: Export Data ke CSV

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame

fetcher = XnoxsFetcher()

# Ambil data
data = fetcher.get_historical_data(
    symbol="BTCUSD",
    exchange="BINANCE",
    timeframe=TimeFrame.DAILY,
    bars=365
)

if data is not None:
    # Simpan ke CSV
    filename = "btcusd_daily.csv"
    data.to_csv(filename)
    print(f"Data berhasil disimpan ke {filename}")
    print(f"Total {len(data)} baris data")
else:
    print("Gagal mengambil data")
```

### Contoh 4: Membandingkan Beberapa Saham

```python
from xnoxs_fetcher import XnoxsFetcher, TimeFrame
import time

fetcher = XnoxsFetcher()

stocks = [
    ("AAPL", "NASDAQ", "Apple"),
    ("GOOGL", "NASDAQ", "Google"),
    ("MSFT", "NASDAQ", "Microsoft"),
    ("AMZN", "NASDAQ", "Amazon"),
    ("META", "NASDAQ", "Meta"),
]

print("=" * 70)
print("PERBANDINGAN SAHAM TECH")
print("=" * 70)
print(f"{'Nama':<15} {'Simbol':<10} {'Harga':<12} {'Volume':<15}")
print("-" * 70)

for symbol, exchange, name in stocks:
    data = fetcher.get_historical_data(
        symbol=symbol,
        exchange=exchange,
        timeframe=TimeFrame.DAILY,
        bars=1
    )
    
    if data is not None:
        price = data['close'].iloc[-1]
        volume = data['volume'].iloc[-1]
        print(f"{name:<15} {symbol:<10} ${price:<11,.2f} {volume:<15,.0f}")
    
    time.sleep(1)  # Jeda untuk menghindari rate limit

print("-" * 70)
```

---

## Bantuan & Dukungan

Jika mengalami masalah:

1. Pastikan semua dependencies terinstall dengan benar
2. Cek koneksi internet
3. Verifikasi simbol dan exchange di TradingView.com
4. Tambahkan jeda antar request untuk menghindari rate limiting

**Repository:** https://github.com/developerxnoxs/xnoxs_fetcher

---

## Lisensi

MIT License - Bebas digunakan untuk keperluan pribadi maupun komersial.

---

**Selamat trading! - developerxnoxs**
