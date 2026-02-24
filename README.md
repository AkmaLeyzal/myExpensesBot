# 💰 Expense Tracker Telegram Bot

Bot Telegram untuk mencatat pengeluaran harian secara cepat ke Google Sheets, lengkap dengan auto-kategori, ringkasan, dan laporan PDF.

## 🛠 Tech Stack

- **Python** + pyTelegramBotAPI
- **Google Sheets** (via gspread) sebagai database
- **Flask** webhook untuk deploy di PythonAnywhere
- **fpdf2** untuk generate laporan PDF

## 📝 Cara Pakai

Kirim pesan ke bot dengan format:

```
[harga] [nama item] - [deskripsi opsional]
```

**Contoh:**

| Input | Harga | Item | Deskripsi |
|---|---|---|---|
| `25k naspad rendang - tambah telur` | 25.000 | naspad rendang | tambah telur |
| `150rb sepatu nike` | 150.000 | sepatu nike | — |
| `2.5jt laptop bekas` | 2.500.000 | laptop bekas | — |
| `5000 air mineral` | 5.000 | air mineral | — |

**Shorthand harga:** `k`/`rb` = ribu, `jt` = juta

## 🤖 Commands

| Command | Fungsi |
|---|---|
| `/start` | Selamat datang |
| `/help` | Panduan lengkap |
| `/today` | Pengeluaran hari ini |
| `/week` | Pengeluaran minggu ini |
| `/month` | Pengeluaran bulan ini |
| `/year` | Pengeluaran tahun ini |
| `/q1` `/q2` `/q3` `/q4` | Per kuartal |
| `/report` | Download laporan PDF |
| `/delete` | Hapus entri terakhir |

## 🚀 Setup Lokal

1. **Clone & masuk ke folder:**
   ```bash
   cd myExpensesBot
   ```

2. **Aktifkan virtual environment:**
   ```bash
   # Windows
   bot.venv\Scripts\activate

   # Linux/Mac
   source bot.venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup `credential.env`:**
   ```env
   BOT_API_TOKEN=<token dari BotFather>
   SPREADSHEET_ID=<ID dari URL Google Sheets>
   GOOGLE_CREDS_FILE=<nama file JSON service account>
   PYTHONANYWHERE_USERNAME=<username PythonAnywhere>
   ```

5. **Share Google Sheets** ke service account email (dengan role Editor).

6. **Jalankan bot (mode polling):**
   ```bash
   python bot.py
   ```

## ☁️ Deploy ke PythonAnywhere

1. Upload semua file ke PythonAnywhere.
2. Install dependencies: `pip install -r requirements.txt`
3. Buat Web App (Flask) di PythonAnywhere dashboard:
   - Source code: `/home/<username>/myExpensesBot`
   - WSGI file: arahkan import ke `flask_app.py`
4. Edit WSGI config file PythonAnywhere:
   ```python
   import sys
   sys.path.insert(0, '/home/<username>/myExpensesBot')
   from flask_app import app as application
   ```
5. Reload web app.
6. Buka `https://<username>.pythonanywhere.com/set_webhook` untuk setup webhook.
7. Selesai! Bot siap digunakan. 🎉

## 📁 Struktur File

```
myExpensesBot/
├── bot.py                  # Bot utama + handlers
├── config.py               # Loader konfigurasi
├── parser.py               # Parser pesan pengeluaran
├── sheets_helper.py        # Operasi Google Sheets
├── report_generator.py     # Generator laporan PDF
├── flask_app.py            # Flask app (PythonAnywhere)
├── requirements.txt        # Dependencies
├── credential.env          # Environment variables
├── *.json                  # Google service account key
└── README.md               # Dokumentasi
```