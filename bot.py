"""Минимальный бот для мессенджера MAX на Python: приветствие, кнопки, ответы на сообщения.

Запуск:
    MAX_BOT_TOKEN=... python bot.py

Подробный разбор кода: https://vne-rutiny.ru/blog/bot-max-na-python
"""
import os
import time

import requests

API = "https://platform-api2.max.ru"
CA_FILE = os.environ.get("MAX_CA_FILE", "russian_trusted_root_ca.pem")

session = requests.Session()
session.headers["Authorization"] = os.environ["MAX_BOT_TOKEN"]  # без "Bearer"
session.verify = CA_FILE  # сертификат Минцифры: без него CERTIFICATE_VERIFY_FAILED


def keyboard(buttons):
    """Кнопки под сообщением: [("Текст", "payload"), ...] — по одной в ряд."""
    return [{"type": "inline_keyboard", "payload": {"buttons": [
        [{"type": "callback", "text": label, "payload": payload}] for label, payload in buttons
    ]}}]


def send(user_id, text, buttons=()):
    body = {"text": text, "attachments": keyboard(buttons) if buttons else []}
    response = session.post(f"{API}/messages", params={"user_id": user_id}, json=body, timeout=15)
    response.raise_for_status()


def answer_callback(callback_id, text):
    """Подтверждает нажатие кнопки и заменяет текст сообщения, на котором она была."""
    response = session.post(f"{API}/answers", params={"callback_id": callback_id},
                            json={"message": {"text": text, "attachments": []}}, timeout=15)
    response.raise_for_status()


MENU = [("Записаться", "book"), ("Задать вопрос", "question")]
ANSWERS = {
    "book": "Напишите удобные день и время — мы подтвердим запись.",
    "question": "Задайте вопрос одним сообщением, ответим в течение дня.",
}


def handle(update):
    kind = update.get("update_type")
    if kind == "bot_started":
        send(update["user"]["user_id"], "Здравствуйте! Чем могу помочь?", MENU)
    elif kind == "message_created":
        message = update["message"]
        if message["sender"].get("is_bot"):
            return
        text = message["body"].get("text") or ""
        send(message["sender"]["user_id"], f"Вы написали: {text}\n\nЧто дальше?", MENU)
    elif kind == "message_callback":
        callback = update["callback"]
        answer_callback(callback["callback_id"], ANSWERS.get(callback["payload"], "Не понял команду"))


def main():
    me = session.get(f"{API}/me", timeout=15)
    me.raise_for_status()
    print("Бот запущен:", me.json().get("name"))

    marker = None
    while True:
        params = {"timeout": 30, "limit": 100, "types": "bot_started,message_created,message_callback"}
        if marker is not None:
            params["marker"] = marker
        try:
            response = session.get(f"{API}/updates", params=params, timeout=40)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            print("Ошибка получения событий, повтор через 5 секунд:", error)
            time.sleep(5)
            continue
        for update in data.get("updates", []):
            try:
                handle(update)
            except requests.RequestException as error:
                print("Не удалось обработать событие:", error)
        marker = data.get("marker", marker)


if __name__ == "__main__":
    main()
