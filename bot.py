from telebot import telebot, types
from datetime import datetime
from sheet_client import append_workout, get_today_workouts, get_week_stats
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN belum diset")

user_states = {}

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

def build_muscle_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    muscles = [
        ("Chest", "muscle:chest"),
        ("Back", "muscle:back"),
        ("Legs", "muscle:legs"),
        ("Shoulders", "muscle:shoulders"),
        ("Arms", "muscle:arms")
    ]

    buttons = [
        types.InlineKeyboardButton(text=name, callback_data=cb)
        for name, cb in muscles
    ]

    keyboard.add(*buttons)
    return keyboard

def build_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("❌ Cancel", callback_data="action:cancel")
    )
    return keyboard

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
        user_states[message.from_user.id] = {
            "step": "muscle",
            "data": {}
        }

        bot.send_message(
            message.chat.id,
            "💪 Oke, mulai catat workout\n\n"
            "Pilih muscle group:",
            reply_markup=build_muscle_keyboard()
        )
    elif text == "📋 List Today":
        handle_list_today(message)
    elif text == "📊 Stats Week":
        handle_stats_week(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("muscle:"))
def handle_muscle_callback(call):
    user_id = call.from_user.id

    if user_id not in user_states:
        bot.answer_callback_query(call.id, "Session sudah tidak aktif")
        return
    
    muscle = call.data.split(":")[1]

    state = user_states[user_id]
    state["data"]["muscle"] = muscle
    state["step"] = "exercise"

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"Muscle dipilih: *{muscle}*\n\n"
        "Sekarang masukkan nama exercise:",
        reply_markup=None
    )

@bot.callback_query_handler(func=lambda call: call.data == "action:cancel")
def handle_inline_cancel(call):
    user_id = call.from_user.id

    if user_id in user_states:
        del user_states[user_id]
    
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "Input dibatalkan.\nBalik ke menu.",
        reply_markup=build_main_menu()
    )
    
@bot.message_handler(commands=["cancel"])
def cancel_state(message):
    user_id = message.from_user.id

    if user_id in user_states:
        del user_states[user_id]

        bot.send_message(
            message.chat.id,
            "Input dibatalkan.\n"
            "Kita balik ke menu ya.",
            reply_markup=build_main_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Tidak ada input yang sedang berjalan.",
            reply_markup=build_main_menu()
        )

@bot.message_handler(
    func=lambda m:(
        m.text is not None and
        m.from_user.id in user_states
    )
)
def handle_state_input(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    text = message.text.strip().lower()

    if text in ["batal", "cancel"]:
        del user_states[user_id]
        bot.send_message(
            message.chat.id,
            "Input dibatalkan.\n"
            "Balik ke menu.",
            reply_markup=build_main_menu()
        )
        return

    if state["step"] == "exercise":
        state["data"]["exercise"] = text
        state["step"] = "sets_reps"

        bot.reply_to(
            message,
            "🔢 Set x Reps?\n"
            "contoh: 4x8",
            reply_markup=build_cancel_keyboard()
        )

    elif state["step"] == "sets_reps":
        if "x" not in text:
            bot.reply_to(message, "❌ Format salah. Contoh: 4x8")
            return
    
        sets, reps = text.split("x")
        if not (sets.isdigit() and reps.isdigit()):
            bot.reply_to(message, "❌ Set & reps harus angka")
            return
        
        state["data"]["sets"] = int(sets)
        state["data"]["reps"] = int(reps)
        state["step"] = "weight"

        bot.reply_to(
            message,
            "⚖️ Berat (kg)?\n"
            "contoh: 80"
        )

    elif state["step"] == "weight":
        if not text.isdigit():
            bot.reply_to(message, "❌ Weight harus angka")
            return
        
        state["data"]["weight"] = int(text)

        workout = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "user": message.from_user.username or message.from_user.first_name,
            **state["data"]
        }

        try:
            append_workout(workout)
        except Exception as e:
            print("ERROR append_workout", e)
            bot.reply_to(message, "❌ Gagal menyimpan workout")
            return
        
        bot.reply_to(
            message,
            "✅ Workout tersimpan!\n"
            f"{workout['muscle']} - {workout['exercise']}\n"
            f"{workout['sets']}x{workout['reps']} @{workout['weight']} kg"
        )

        del user_states[message.from_user.id]

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