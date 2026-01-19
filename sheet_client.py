import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open("Gym Tracker").sheet1
    return sheet

def append_workout(workout: dict):
    sheet = get_sheet()
    sheet.append_row([
        workout['date'],
        workout['user'],
        workout['muscle'],
        workout['exercise'],
        workout['sets'],
        workout['reps'],
        workout['weight'],
    ])

def get_today_workouts():
    sheet = get_sheet()
    rows = sheet.get_all_records()

    today = datetime.now().strftime("%Y-%m-%d")

    return [
        row for row in rows
        if row.get("date") == today
    ]

def get_week_stats():
    sheet = get_sheet()
    rows = sheet.get_all_records()

    today = datetime.now().date()
    start = today - timedelta(days=0)

    week_rows = []
    for r in rows:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
        except Exception:
            continue

        if start <= d <= today:
            week_rows.append(r)

    stats = {
        "sessions": len(week_rows),
        "sets": 0,
        "reps": 0,
        "volume": 0
    }

    for r in week_rows:
        sets = int(r.get("sets", 0)) 
        reps = int(r.get("reps", 0)) 
        weight = int(r.get("weight", 0))

        stats["sets"] += sets 
        stats["reps"] += reps 
        stats["volume"] += sets * reps * weight

    return stats 