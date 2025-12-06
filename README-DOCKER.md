# Panduan Deployment Docker - Trading Analysis Bot

## Prasyarat

- Docker Engine 20.10+
- Docker Compose 2.0+

## Mode Bot

Bot mendukung 2 mode operasi:

| Mode | Kegunaan | Keterangan |
|------|----------|------------|
| **Polling** | Development | Default, tidak perlu URL publik |
| **Webhook** | Production | Lebih efisien, butuh URL publik (HTTPS) |

## Auto-Detect Webhook (Baru!)

Bot secara otomatis mendeteksi webhook URL dari environment variables:

| Prioritas | Variable | Contoh |
|-----------|----------|--------|
| 1 | `WEBHOOK_URL` | `https://bot.example.com` |
| 2 | `APP_DOMAIN` | `bot.example.com` |
| 3 | `VIRTUAL_HOST` | `bot.example.com` (nginx-proxy) |

**Webhook path juga auto-generate** jika tidak diset manual.

## Langkah Deployment

### 1. Clone atau Copy Project

```bash
git clone <repository-url>
cd trading-analysis-bot
```

### 2. Buat File Environment

**Mode Polling (Development):**
```bash
# .env
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
BOT_MODE=polling
```

**Mode Webhook (Production) - Auto-detect:**
```bash
# .env
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
BOT_MODE=webhook
APP_DOMAIN=bot.yourdomain.com
```

### 3. Build dan Jalankan

```bash
docker-compose up -d --build
```

### 4. Cek Log & Status

```bash
docker-compose logs -f trading-bot
```

Output saat auto-detect berhasil:
```
✓ WEBHOOK_URL: https://bot.yourdomain.com (auto-detect)
✓ WEBHOOK_PATH: /webhook_abc12345 (auto-generate)
```

### 5. Stop Bot

```bash
docker-compose down
```

## Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `TELEGRAM_BOT_TOKEN` | Token bot dari @BotFather | - (wajib) |
| `GEMINI_API_KEY` | API key dari Google AI Studio | - (opsional) |
| `BOT_MODE` | `polling` atau `webhook` | `polling` |
| `APP_DOMAIN` | Domain aplikasi (auto-detect webhook) | - |
| `VIRTUAL_HOST` | Domain untuk nginx-proxy | - |
| `WEBHOOK_URL` | URL lengkap webhook (override auto) | - |
| `WEBHOOK_PORT` | Port webhook server | `5000` |
| `WEBHOOK_PATH` | Path webhook (auto-generate jika kosong) | - |

## Contoh Deployment

### Docker Compose Standar

```bash
# .env
TELEGRAM_BOT_TOKEN=123456:ABC...
GEMINI_API_KEY=AIza...
BOT_MODE=webhook
APP_DOMAIN=trading-bot.example.com
```

```bash
docker-compose up -d --build
```

### Dengan Nginx Reverse Proxy

```bash
# .env
TELEGRAM_BOT_TOKEN=123456:ABC...
GEMINI_API_KEY=AIza...
BOT_MODE=webhook
VIRTUAL_HOST=trading-bot.example.com
LETSENCRYPT_HOST=trading-bot.example.com
```

Bot akan otomatis menggunakan `VIRTUAL_HOST` sebagai webhook URL.

### Dengan Traefik

```yaml
services:
  trading-bot:
    labels:
      - "traefik.http.routers.bot.rule=Host(`bot.example.com`)"
    environment:
      - APP_DOMAIN=bot.example.com
      - BOT_MODE=webhook
```

## Perintah Berguna

| Perintah | Fungsi |
|----------|--------|
| `docker-compose up -d` | Jalankan di background |
| `docker-compose down` | Hentikan |
| `docker-compose restart` | Restart |
| `docker-compose logs -f` | Log realtime |
| `docker-compose build --no-cache` | Rebuild |

## Troubleshooting

### Cek mode yang aktif
```bash
docker-compose logs trading-bot | grep "BOT_MODE"
```

### Webhook tidak terdeteksi
Pastikan salah satu variabel ini diset:
- `WEBHOOK_URL`
- `APP_DOMAIN`  
- `VIRTUAL_HOST`

### Bot fallback ke polling
Jika webhook URL tidak terdeteksi, bot otomatis fallback ke mode polling.

### Rebuild setelah update
```bash
docker-compose down && docker-compose up -d --build
```

## Auto-Trading dengan MetaTrader 5

Bot mendukung auto-trading terintegrasi dengan MetaTrader 5 melalui Wine di Linux container.

### Prasyarat MT5

1. Akun broker yang mendukung MetaTrader 5
2. Kredensial login MT5 (login, password, server)
3. Instalasi MetaTrader 5 (dari Windows atau portable)

### Instalasi MT5 untuk Docker

MetaTrader 5 adalah software proprietary yang harus diinstal secara terpisah. Ada 2 cara:

**Opsi 1: Mount dari Windows Host (Recommended)**

Jika Anda menjalankan Docker di Windows dengan WSL2:

```yaml
# docker-compose.yml
volumes:
  - ./logs:/app/logs
  - mt5-data:/root/.wine
  - "C:/Program Files/MetaTrader 5:/app/mt5:ro"
```

**Opsi 2: Copy Portable MT5**

1. Download MT5 dari broker Anda
2. Install di Windows, lalu copy folder instalasi
3. Mount folder tersebut ke container:

```yaml
volumes:
  - ./mt5-portable:/app/mt5:ro
```

**Struktur folder MT5 yang diperlukan:**
```
mt5/
├── terminal64.exe  # atau terminal.exe
├── config/
├── MQL5/
└── ...
```

**Tanpa MT5 Terminal**

Jika MT5 terminal tidak tersedia, bot akan berjalan dalam mode **analisa saja** tanpa fitur trading. Anda akan melihat pesan:
```
WARNING: MetaTrader 5 terminal not found!
The bot will run in analysis-only mode without MT5.
```

### Environment Variables MT5

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `MT5_LOGIN` | Nomor akun MT5 | - (wajib untuk trading) |
| `MT5_PASSWORD` | Password akun MT5 | - (wajib untuk trading) |
| `MT5_SERVER` | Nama server broker MT5 | - (wajib untuk trading) |
| `MT5_PATH` | Path instalasi MT5 di container | auto-detect |
| `MT5_ENABLE_TRADING` | Aktifkan fitur trading | `false` |
| `MT5_RISK_PERCENT` | Risiko per trade (% dari balance) | `1.0` |
| `MT5_MAX_POSITIONS` | Maksimum posisi terbuka | `5` |

### Konfigurasi MT5 di .env

```bash
# .env
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
BOT_MODE=polling

# MT5 Auto-Trading
MT5_LOGIN=12345678
MT5_PASSWORD=your_mt5_password
MT5_SERVER=YourBroker-Demo
MT5_ENABLE_TRADING=true
MT5_RISK_PERCENT=1.0
MT5_MAX_POSITIONS=5
```

### Perintah Bot MT5

| Perintah | Fungsi |
|----------|--------|
| `/mt5status` | Cek status koneksi MT5 |
| `/positions` | Lihat posisi terbuka |
| `/trade <SYMBOL> <BUY/SELL> <LOT>` | Eksekusi trade manual |
| `/close <TICKET>` atau `/close all` | Tutup posisi |
| `/autotrade <on/off>` | Toggle auto-trading |

### Port yang Digunakan

| Port | Fungsi |
|------|--------|
| 5000 | Webhook server |
| 5900 | VNC (akses desktop MT5) |
| 8001 | MT5 bridge (internal) |

### Akses VNC ke Desktop MT5

Untuk melihat GUI MetaTrader 5:

```bash
# Gunakan VNC viewer ke localhost:5900
vncviewer localhost:5900
```

### Catatan Penting MT5

1. **Mode Demo dulu**: Selalu test dengan akun demo sebelum akun real
2. **Risk Management**: Atur `MT5_RISK_PERCENT` sesuai toleransi risiko
3. **Monitoring**: Gunakan VNC untuk memantau status MT5
4. **Wine Limitation**: Beberapa fitur MT5 mungkin terbatas di Wine

## Catatan Keamanan

- Jangan commit file `.env` ke repository
- Gunakan Docker secrets untuk production
- Pastikan SSL certificate valid untuk webhook
- Batasi akses port 5000 dari reverse proxy saja
- **Lindungi kredensial MT5** - jangan share password trading
