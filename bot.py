import os
import json
import requests
from datetime import date

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API = "https://prodoctorov.ru/ajax/schedule/slots_bulk/"

PAYLOAD = {
    "days": 30,
    "dt_start": str(date.today()),
    "all_slots": False,
    "doctors_lpus": [
        {
            "doctor_id": 1032093,
            "lpu_id": 101921,
            "lpu_timedelta": 3,
            "has_slots": True
        }
    ],
    "town_timedelta": 3
}


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


def get_slots():
    r = requests.post(
        API,
        json=PAYLOAD,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    data = r.json()

    slots = []

    for item in data["result"]:
        for day, times in item["slots"].items():
            for slot in times:
                if slot.get("free"):
                    slots.append(
                        f"{day} {slot['time']}"
                    )

    return set(slots)


def main():
    old = set()

    send("🟢 Монитор ProDoctorov запущен")

    while True:
        try:
            current = get_slots()

            new = current - old

            if new:
                send(
                    "🔔 Новые окна:\n\n" +
                    "\n".join(sorted(new))
                )

            old = current

        except Exception as e:
            send(f"⚠️ Ошибка: {e}")


if __name__ == "__main__":
    main()
