import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL = "https://prodoctorov.ru/nnovgorod/vrach/1032093-ivanova/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = set()


def send(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )


async def check():
    global seen

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(5000)  # ждём JS

        text = await page.content()

        slots = set()

        # ищем времена типа 10:00
        import re
        times = re.findall(r"\b\d{1,2}:\d{2}\b", text)

        for t in times:
            slots.add(t)

        new = slots - seen

        if new:
            send("🔔 Новые окна:\n" + "\n".join(sorted(new)) + f"\n\n{URL}")

        seen = slots

        await browser.close()


def main():
    try:
        import asyncio
        asyncio.run(check())
        send("🟢 Проверка выполнена")
    except Exception as e:
        send(f"⚠️ Ошибка: {e}")


if __name__ == "__main__":
    main()
