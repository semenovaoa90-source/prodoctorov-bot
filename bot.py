import os
import requests
from bs4 import BeautifulSoup

URL = "https://prodoctorov.ru/nnovgorod/vrach/1032093-ivanova/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )


def get_slots():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=20)

    soup = BeautifulSoup(r.text, "html.parser")

    slots = set()

    # ищем все времена вида 10:00, 11:30 и т.д.
    for el in soup.find_all(text=True):
        t = el.strip()
        if len(t) <= 5 and ":" in t:
            parts = t.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                slots.add(t)

    return slots


def load_old():
    try:
        with open("slots.txt", "r") as f:
            return set(f.read().splitlines())
    except:
        return set()


def save_new(slots):
    with open("slots.txt", "w") as f:
        f.write("\n".join(slots))


def main():
    try:
        current = get_slots()
        old = load_old()

        new = current - old

        if new:
            msg = "🔔 Новые свободные окна:\n" + "\n".join(sorted(new)) + f"\n\n{URL}"
            send_message(msg)

        save_new(current)

        # чтобы ты видел, что job реально запустился
        send_message("🟢 Проверка выполнена")

    except Exception as e:
        send_message(f"⚠️ Ошибка бота: {e}")


if __name__ == "__main__":
    main()
