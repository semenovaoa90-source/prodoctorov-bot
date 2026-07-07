import os
import json
import requests
from datetime import date

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://prodoctorov.ru/ajax/schedule/slots_bulk/"

STATE_FILE = "state.json"

PAYLOAD = {
    "days": 30,
    "dt_start": str(date.today()),
    "all_slots": False,
    "town_timedelta": 3,
    "doctors_lpus": [
        {
            "doctor_id": 1032093,
            "lpu_id": 101921,
            "lpu_timedelta": 3,
            "has_slots": True
        }
    ]
}


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=20
    )


def get_slots():
    response = requests.post(
        API_URL,
        json=PAYLOAD,
        headers={
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://prodoctorov.ru/nnovgorod/vrach/1032093-ivanova/"
        },
        timeout=20
    )

    data = response.json()

    slots = []

    for doctor in data.get("result", []):
        for day, times in doctor["slots"].items():
            for slot in times:
                if slot.get("free"):
                    slots.append(
                        f"{day} {slot['time']}"
                    )

    return sorted(slots)


def load_old():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_state(slots):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(slots, f, ensure_ascii=False)


def main():

    old_slots = load_old()
    new_slots = get_slots()

    added = set(new_slots) - set(old_slots)

    if added:
        message = "🔔 Новые окна:\n\n"
        message += "\n".join(sorted(added))
        send_message(message)

    save_state(new_slots)


if __name__ == "__main__":
    main()
