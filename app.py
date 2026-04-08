from flask import Flask, request
import requests
import json
import datetime

app = Flask(__name__)

# -----------------------------
# CONFIGURATION
# -----------------------------
BOT_ID = "0fde4fedbc3580a8f1b1d6c52f"

GOALS = {
    "simple_preaching": 5000,
    "meaningful_preaching": 20,
    "bible_study": 20,
    "fruit": 5,
    "ga_signatures": 20
}

DATA_FILE = "data.json"

# -----------------------------
# LOAD OR INITIALIZE DATA
# -----------------------------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "simple_preaching": 0,
            "meaningful_preaching": 0,
            "bible_study": 0,
            "fruit": 0,
            "ga_signatures": 0,
            "month": datetime.datetime.now().month
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# -----------------------------
# MONTHLY RESET CHECK
# -----------------------------
def check_month_reset(data):
    current_month = datetime.datetime.now().month
    if data.get("month") != current_month:
        data = {
            "simple_preaching": 0,
            "meaningful_preaching": 0,
            "bible_study": 0,
            "fruit": 0,
            "ga_signatures": 0,
            "month": current_month
        }
        save_data(data)
    return data

# -----------------------------
# SEND MESSAGE TO GROUPME
# -----------------------------
def send_message(text):
    url = "https://api.groupme.com/v3/bots/post"
    payload = {"bot_id": BOT_ID, "text": text}
    requests.post(url, json=payload)

# -----------------------------
# FORMAT TOTALS
# -----------------------------
def format_totals(data):
    lines = []
    lines.append(f"Totals for this month:\n")

    categories = [
        ("Simple Preaching", "simple_preaching"),
        ("Meaningful Preaching", "meaningful_preaching"),
        ("Bible Study", "bible_study"),
        ("Fruit", "fruit"),
        ("GA Signatures", "ga_signatures")
    ]

    for label, key in categories:
        current = data[key]
        goal = GOALS[key]
        percent = (current / goal) * 100 if goal > 0 else 0
        lines.append(f"{label}: {current} / {goal} ({percent:.1f}%)")

    return "\n".join(lines)

# -----------------------------
# MAIN BOT LOGIC
# -----------------------------
@app.route("/", methods=["POST"])
def webhook():
    data = load_data()
    data = check_month_reset(data)

    message = request.json.get("text", "").lower().strip()

    # ADD
    if message.startswith("add"):
        parts = message.split()
        if len(parts) == 6:
            nums = list(map(int, parts[1:]))

            data["simple_preaching"] += nums[0]
            data["meaningful_preaching"] += nums[1]
            data["bible_study"] += nums[2]
            data["fruit"] += nums[3]
            data["ga_signatures"] += nums[4]

            save_data(data)
            send_message("Updated!\n\n" + format_totals(data))
