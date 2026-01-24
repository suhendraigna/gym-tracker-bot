from telebot import telebot, types
from datetime import datetime
from sheet_client import append_workout, get_today_workouts, get_week_stats
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN belum diset")

bot = telebot.TeleBot(BOT_TOKEN)

def build_main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    btn_add = types.KeyboardButton("➕ Add Workout")
    btn_list = types.KeyboardButton("📋 List Today")
    btn_stats = types.KeyboardButton("📊 Stats Week")

    keyboard.add(btn_add, btn_list, btn_stats)
    return keyboard

@bot.message_handler(commands=["start"])
def handle_start(message):
    welcome_text=(
        "👋 Welcome to Gym Tracker Bot\n\n"
        "Catat workout kamu langsung lewat chat.\n"
        "Pilih menu di bawah untuk mulai 💪"
    )

    bot.send_message(
        message.chat.id, welcome_text, reply_markup=build_main_menu()
    )

@bot.message_handler(
    func=lambda m: m.text is not None and m.text in[
        "➕ Add Workout",
        "📋 List Today",
        "📊 Stats Week"
    ]
)
def handle_menu_button(message):
    text = message.text

    if text == "➕ Add Workout":
        bot.send_message(
            message.chat.id,
            "Contoh input:\n\n"
            "chest bench 4x8 80\n\n"
            "Format:\n"
            "<muscle> <exercise> <sets>x<reps> <weight>"
        )
    elif text == "📋 List Today":
        handle_list_today(message)
    elif text == "📊 Stats Week":
        handle_stats_week(message)
    
@bot.message_handler(
        func=lambda m: (
            m.text is not None and
            not m.text.startswith("/") and 
            len(m.text.split()) == 4
        )
)

def shortcut_handle(message):
    parts = message.text.split()

    if not handle_add_workout(message, parts):
        bot.reply_to(
            message,
            "Tidak paham\n"
            "Gunakan:\n"
            "chest bench 4x8 80"
        )
    
def handle_add_workout(message, parts):
    if len(parts) != 4:
        return False
    
    muscle, exercise, set_reps, weight = parts

    if "x" not in set_reps:
        return False
    
    sets, reps = set_reps.split("x")

    if not(sets.isdigit() and reps.isdigit() and weight.isdigit()):
        return False
    
    workout = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": message.from_user.username or message.from_user.first_name,
        "muscle": muscle,
        "exercise": exercise,
        "sets": int(sets),
        "reps": int(reps),
        "weight": int(weight)
    }

    try:
        append_workout(workout)
    except Exception as e:
        print("ERROR append_workout", e)
        bot.reply_to(message, "❌ Gagal menyimpan workout")
        return True
    
    reply = (
        "✅ Workout tersimpan\n"
        f"{muscle} - {exercise}\n"
        f"{sets}x{reps} @{weight} kg"
    )

    bot.reply_to(message, reply)
    return True


@bot.message_handler(commands=["add"])
def add_workout(message):
    parts = message.text.split()[1:]
    if not handle_add_workout(message, parts):
        bot.reply_to(
            message,
            "Format salah\n"
            "Contoh:\n"
            "/add chest bench 4x8 80"
        )

def handle_list_today(message):
    try:
        workouts = get_today_workouts()
    except Exception as e:
        print("ERROR get_today_workouts:", e)
        bot.reply_to(message, "❌ Gagal ambil data. Coba lagi nanti.")
        return
    
    if not workouts:
        bot.reply_to(message, "📭 Belum ada workout hari ini")
        return
    
    lines = ["🏋️ Workout hari ini:"]
    for w in workouts:
        lines.append(
            f"- {w['exercise']} {w['sets']}x{w['reps']} @ {w['weight']}kg"
        )

    bot.reply_to(message, "\n".join(lines))

@bot.message_handler(commands=["list"])
def list_workout(message):
    parts = message.text.split()

    if len(parts) != 2 or parts[1] != "today":
        bot.reply_to(message, "Gunakan:\n/list today")
        return
    
    handle_list_today(message)

def handle_stats_week(message):
    try:
        stats = get_week_stats()
    except Exception as e:
        print("ERROR get_week_stats:", e)
        bot.reply_to(message, "Gagal ambil statistik")
        return
    
    if stats["sessions"] == 0:
        bot.reply_to(message, "Belum ada workout minggu ini")
        return
    
    reply = (
        "Statistik 7 Hari Terakhir\n"
        f"- Sesi       : {stats['sessions']}\n"
        f"- Total Set  : {stats['sets']}\n"
        f"- Total Reps : {stats['reps']}\n"
        f"- Volume     : {stats['volume']} kg"
    )

    bot.reply_to(message, reply)

@bot.message_handler(commands=["stats"])
def stats_handler(message):
    if message.text.strip() != "/stats week":
        bot.reply_to(message, "Gunakan:\n/stats week")
        return
    
    handle_stats_week(message)
 
print("Bot sedang jalan...")
bot.infinity_polling()