# 🏋️ Gym Tracker Bot (Telegram)

Telegram bot untuk mencatat workout gym secara cepat melalui chat.
Dirancang dengan pendekatan **logic-first**, tanpa framework berat, dan fokus ke usability.

---

## ✨ Features

- Add workout via chat (step-by-step)
- Inline muscle selector (button)
- Cancel input kapan saja
- Auto save ke Google Sheets
- Daily workout list
- Weekly statistics
- Error handling (network & API safe)

---

## 🧠 Design Principles

- No web framework
- Separation of concerns
- Single source of truth
- Defensive programming
- Beginner-friendly & readable code

---

## 🧰 Tech Stack

- Python 3.12
- pyTelegramBotAPI (Telebot)
- Google Sheets API (gspread)
- dotenv (.env)
- Linux (Ubuntu)

---

## 🚀 How It Works

1. User klik **Add Workout**
2. Pilih muscle via inline button
3. Input exercise, sets x reps, weight
4. Data disimpan ke Google Sheets
5. User bisa cancel kapan saja

---

## 📂 Project Structure

gym-tracker-bot/
│
├── bot.py              # Telegram bot handlers & UX flow
├── sheet_client.py     # Google Sheets read/write logic
├── credentials.json    # Google service account (gitignored)
├── .env                # Environment variables (gitignored)
├── .gitignore
└── README.md


---

## 🔐 Security Notes

- Telegram bot token disimpan via environment variable
- Google credentials tidak pernah dipush ke repository
- `.env` dan credential file di-ignore oleh git

---

## 📝 Notes

Project ini dibuat sebagai latihan Python real-world use case
dengan fokus pada logic, robustness, dan maintainability.

## 💡 Why This Project?

Kebanyakan tutorial Telegram bot hanya fokus ke command sederhana.

Project ini mencoba mensimulasikan:
- Input bertahap seperti aplikasi nyata
- UX yang meminimalkan kesalahan user
- Error handling untuk kondisi real-world
- Struktur kode yang mudah dikembangkan

Tujuannya bukan hanya bot yang berjalan,
tapi bot yang **nyaman digunakan dan mudah dirawat**.