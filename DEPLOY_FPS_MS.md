# Panduan Deploy ke fps.ms

## Langkah 1: Daftar Akun
1. Buka https://panel.fps.ms/
2. Daftar akun gratis (tidak perlu kartu kredit)

## Langkah 2: Buat Server Baru
1. Klik "Create Server"
2. Pilih "Telegram Bot"
3. Pilih lokasi server (US atau Netherlands)

## Langkah 3: Upload File Bot

### Untuk BTC Analyzer Bot:
Upload file-file berikut:
- `btc_analyzer.py` (file utama bot)
- `requirements.txt` (dependencies)

### Untuk XAU Analyzer Bot:
Upload file-file berikut:
- `xau_analyzer.py` (file utama bot)
- `requirements.txt` (dependencies)

**Catatan:** Jika ingin menjalankan 2 bot, buat 2 server terpisah di fps.ms

## Langkah 4: Install Dependencies
1. Buka terminal/console di panel fps.ms
2. Jalankan perintah:
```bash
pip install -r requirements.txt
```

## Langkah 5: Set Environment Variables
Di panel fps.ms, tambahkan environment variables:

### Untuk BTC Analyzer:
- `TELEGRAM_BOT_TOKEN` = token dari @BotFather
- `GEMINI_API_KEY` = API key dari Google AI Studio

### Untuk XAU Analyzer:
- `TELEGRAM_BOT_TOKEN_XAU` = token dari @BotFather (bot berbeda)
- `GEMINI_API_KEY` = API key dari Google AI Studio

## Langkah 6: Jalankan Bot

### BTC Analyzer:
```bash
python btc_analyzer.py
```

### XAU Analyzer:
```bash
python xau_analyzer.py
```

## Langkah 7: Renewal Harian
- **PENTING:** Hosting gratis fps.ms perlu di-renew setiap 24 jam
- Login ke panel dan klik tombol "Renew" setiap hari
- Jika tidak renew, bot akan offline (file tetap aman 28 hari)

---

## Cara Mendapatkan API Keys

### 1. Telegram Bot Token
1. Buka Telegram, cari @BotFather
2. Kirim `/newbot`
3. Ikuti instruksi untuk memberi nama bot
4. Copy token yang diberikan

### 2. Gemini API Key
1. Buka https://aistudio.google.com/
2. Login dengan akun Google
3. Klik "Get API Key"
4. Buat API key baru dan copy

---

## Spesifikasi fps.ms (Free Plan)
- CPU: 25%
- RAM: 128 MB
- Storage: 250 MB
- Renewal: Setiap 24 jam

## Troubleshooting

### Bot tidak jalan?
1. Pastikan semua dependencies terinstall: `pip install -r requirements.txt`
2. Cek environment variables sudah benar
3. Lihat log error di console

### Memory Error?
- Free plan hanya 128MB RAM
- Jika bot terlalu berat, pertimbangkan upgrade ke plan berbayar (€0.29/bulan)
