# Бот для MAX на Python

Минимальный рабочий пример бота для российского мессенджера [MAX](https://max.ru) на Python и `requests` — без сторонних SDK. Официальные библиотеки у MAX есть только для TypeScript и Go, поэтому здесь всё сделано напрямую через [MAX Bot API](https://dev.max.ru).

Что умеет пример:
- проверяет токен через `GET /me`;
- здоровается при старте и показывает кнопки;
- отвечает на сообщения;
- обрабатывает нажатия кнопок (`POST /answers`);
- получает события через long polling с `marker`.

Пошаговый разбор кода, вебхук и частые ошибки (401, 429, сертификат) — в статье [«Как написать бота для MAX на Python»](https://vne-rutiny.ru/blog/bot-max-na-python?utm_source=github&utm_medium=readme).

## Запуск

1. Создайте бота на [платформе MAX для партнёров](https://business.max.ru) и получите токен.
2. Скачайте корневой сертификат Минцифры «Russian Trusted Root CA» с [gosuslugi.ru/crt](https://www.gosuslugi.ru/crt) и сохраните рядом с `bot.py` как `russian_trusted_root_ca.pem`. API MAX использует этот сертификат, и без него Python падает с `CERTIFICATE_VERIFY_FAILED`. Не отключайте проверку сертификата: токен уходит в каждом запросе.
3. Установите зависимости и запустите:

```bash
pip install -r requirements.txt
MAX_BOT_TOKEN=ваш_токен python bot.py
```

В Windows (PowerShell):

```powershell
$env:MAX_BOT_TOKEN = "ваш_токен"; python bot.py
```

4. Откройте бота в MAX и нажмите «Начать».

## Переменные окружения

| Переменная | Что это |
|---|---|
| `MAX_BOT_TOKEN` | токен бота, обязательно |
| `MAX_CA_FILE` | путь к сертификату, по умолчанию `russian_trusted_root_ca.pem` |

## Что важно знать про MAX Bot API

- Адрес API — `https://platform-api2.max.ru`.
- Токен передаётся в заголовке `Authorization` как есть, без `Bearer`. Передача токена в параметре запроса не поддерживается.
- `marker` из ответа `GET /updates` нужно передавать в следующий запрос, иначе события придут повторно.
- В продакшене лучше вебхук: `POST /subscriptions` с `url`, `update_types` и `secret`; секрет приходит в заголовке `X-Max-Bot-Api-Secret`.
- `GET /chats` с июня 2026 года не поддерживается.

## Нужен бот под задачу бизнеса?

Пример показывает основу. Боевой бот — это ещё хранение состояния, защита от дублей, повторы при сбоях, интеграции с CRM и таблицами. Такие боты для MAX и Telegram под ключ делает команда [«Вне рутины»](https://vne-rutiny.ru/?utm_source=github&utm_medium=readme).

## Лицензия

MIT
