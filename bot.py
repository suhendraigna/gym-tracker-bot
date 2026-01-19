import telebot
from datetime import datetime
from sheet_client import append_workout, get_today_workouts, get_week_stats

TOKEN = "8250931576:AAHpd2M-7XhKFIhdQ68OLEGJH7QN0C1_jLk"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, 
                 "🏋️ Gym Tracker aktif\n"
                 "Gunakan:\n"
                 "/add chest bench 4x8 80"                 
                 )
    
@bot.message_handler(func=lambda message: True)
def shortcut_handle(message):
    parts = message.text.split()
    handled = handle_add_workout(message, parts)

    if not handled:
        bot.reply_to(
            message,
            "🤔 Tidak paham\n"
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
            "❌ Format salah\n"
            "Contoh:\n"
            "/add chest bench 4x8 80" 
        )
    
    if len(parts) != 5:
        bot.reply_to(
            message,
            "❌ Format salah\n"
            "Contoh:\n"
            "/add chest bench 4x8 80"
        )
        return
    
    _, muscle, exercise, set_reps, weight = parts

    if "x" not in set_reps:
        bot.reply_to(message, "❌ Format set x reps harus seperti 4x8")
        return
    
    sets, reps = set_reps.split("x")

    if not (sets.isdigit() and reps.isdigit() and weight.isdigit()):
        bot.reply_to(message, "❌ Set, reps, dan weight harus angka")
        return
    
    workout = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": message.from_user.username or message.from_user.first_name,
        "muscle": muscle,
        "exercise": exercise,
        "sets": int(sets),
        "reps":int(reps),
        "weight":int(weight)
    }

    try:
        append_workout(workout)
    except Exception as e:
        print("ERROR append_workout:", e)
        bot.reply_to(
            message,
            "❌ Gagal menyimpan workout. Coba sebentar lagi ya."   
        )

    reply = (
         "✅ Workout tersimpan\n"
         f"Tanggal  : {workout['date']}\n"
         f"User     : {workout['user']}\n"
         f"Muscle   : {muscle}\n"
         f"Exercise : {exercise}\n"
         f"{sets}x{reps} @ {weight}kg"
    )

    bot.reply_to(message, reply)

@bot.message_handler(commands=["list"])
def list_workout(message):
    parts = message.text.split()

    if len(parts) != 2 or parts[1] != "today":
        bot.reply_to(
            message,
            "❌ Gunakan:\n"
            "/list today"
        )
        return

    try:
        workouts = get_today_workouts()
    except Exception as e:
        print("ERROR get_today_workouts:", e)
        bot.reply_to(
            message,
            "❌ Gagal ambil data. Coba lagi nanti."
        )

    if not workouts:
        bot.reply_to(message, "📭 Belum ada workout hari ini")
        return
    
    lines = ["🏋️ Workout Hari Ini:"]
    
    for w in workouts:
        line = (
            f"- {w['exercise']} "
            f"{w['sets']}x{w['reps']} @ {w['weight']}kg"
        )
        lines.append(line)

    reply = "\n".join(lines)
    bot.reply_to(message, reply)

@bot.message_handler(commands=["stats"])
def stats_handler(message):
    parts = message.text.split()

    if len(parts) != 2 or parts[1] != "week":
        bot.reply_to(
            message,
            "❌ Gunakan:\n"
            "/stats week"
        )
        return

    try:
        stats = get_week_stats()
    except Exception as e:
        print("ERROR get_week_stats:", e)
        bot.reply_to(message, "❌ Gagal ambil statistik")
        return
    
    if stats["sessions"] == 0:
        bot.reply_to(message, "📭 Belum ada workout minggu ini")
        return
    
    reply = (
        "📊 Statistik 7 Hari Terakhir\n"
        f"- Sesi : {stats['sessions']}\n"
        f"- Total Set : {stats['sets']}\n"
        f"- total Reps: {stats['reps']}\n"
        f"- Volume    : {stats['volume']} kg\n"
    )

    bot.reply_to(message, reply)
 
print("Bot sedang jalan...")
bot.infinity_polling()