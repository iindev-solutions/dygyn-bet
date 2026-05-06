# 02. Архитектура

## Компоненты

```text
Telegram user
    ↓
Telegram bot /start
    ↓ web_app button
Telegram Mini App frontend
    ↓ HTTPS + X-Telegram-Init-Data
FastAPI backend
    ↓
SQLite database
```

## Почему так

- FastAPI быстро даёт API и статическую раздачу фронтенда.
- SQLite достаточно для ранней версии и маленькой аудитории.
- Aiogram нужен только для бота и кнопки открытия Mini App.
- Vanilla JS быстрее всего поддерживать на ранней версии: нет сборки, Vite, React и сложного deploy.

## Production-замены

Когда появится нагрузка:

- SQLite → PostgreSQL.
- In-memory rate limit → Redis rate limit.
- Polling → webhook.
- Curl admin API → отдельная админ-панель.
- Ручной ввод результатов → импорт из проверенного источника.

## Telegram auth

Frontend не передаёт `initDataUnsafe`. Он передаёт только сырой `Telegram.WebApp.initData` в заголовке `X-Telegram-Init-Data`. Backend проверяет HMAC-SHA256 и срок действия `auth_date`, затем извлекает Telegram user ID.

## Security notes

- Не доверять данным из браузера без проверки подписи Telegram.
- Не принимать прогнозы после `starts_at`.
- Не давать пользователю делать больше одного прогноза на событие.
- Не хранить секреты в репозитории.
- Не включать `ALLOW_DEV_LOGIN=true` в production.
