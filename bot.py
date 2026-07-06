import os
import time
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://prodoctorov.ru/nnovgorod/vrach/1032093-ivanova/"

seen_slots = set()

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def parse_slots():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    slots = set()

    # ищем все кнопки/времена (синие слоты)
    for btn in soup.find_all("button"):
        txt = btn.get_text(strip=True)
        if ":" in txt and len(txt) <= 5:
            slots.add(txt)

    return slots


def main():
    global seen_slots

    send_message("🟢 Бот запущен и следит за новыми окнами")

    while True:
        try:
            current = parse_slots()

            new_slots = current - seen_slots

            if new_slots:
                for slot in sorted(new_slots):
                    send_message(f"🔔 Новое окно: {slot}\n{URL}")

                seen_slots = current

        except Exception as e:
            print("error:", e)

        time.sleep(30)


if __name__ == "__main__":
    main()
