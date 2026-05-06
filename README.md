# Dygyn TMA Fan Picks MVP

Минимальный Telegram Mini App + бот для фан-прогнозов по Играм Дыгына.

## Что делает MVP

- Открывается внутри Telegram как Mini App через кнопку бота.
- Авторизует пользователя через `Telegram.WebApp.initData` на сервере.
- Даёт выбрать одного участника на событие.
- Принимает только виртуальные `confidence_points`, без денежных ставок, депозитов и выигрышей.
- Показывает поддержку участников: количество голосов, сумму виртуальных очков, проценты.
- Показывает историю участников и простой рейтинг пользователей после внесения итогов.
- Даёт админские API для добавления участников, событий, истории и результатов.

## Важное юридическое ограничение

Этот MVP намеренно сделан как сервис **фан-прогнозов/голосования без денег**. Если добавить реальные деньги, призы, имущественные права, депозиты, вывод средств или комиссию организатора, проект может попасть в регулирование азартных игр/букмекерской деятельности. Перед таким шагом нужен юрист, лицензирование, KYC/возрастные проверки, платёжная инфраструктура и соблюдение требований регуляторов.

## Быстрый запуск локально

```bash
cd dygyn-tma-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Откройте `http://localhost:8000`. По умолчанию `ALLOW_DEV_LOGIN=true`, поэтому локально можно тестировать без Telegram.

## Запуск в Telegram

1. Создайте бота в `@BotFather` и получите `BOT_TOKEN`.
2. Поднимите проект на HTTPS-домене. Для разработки подойдёт ngrok или Cloudflare Tunnel.
3. В `.env` укажите:

```env
BOT_TOKEN=...
WEB_APP_URL=https://your-domain.example
ADMIN_IDS=123456789
ALLOW_DEV_LOGIN=false
ENABLE_POLLING=true
```

4. Запустите сервер:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Напишите боту `/start`; он пришлёт кнопку открытия Mini App.

## Docker

```bash
cp .env.example .env
# отредактируйте .env
docker compose up --build
```

## Админские операции через curl

Локально при `ALLOW_DEV_LOGIN=true` админом считается dev-пользователь. В production добавьте свой Telegram ID в `ADMIN_IDS` и вызывайте админские API из TMA/скрипта с валидным `X-Telegram-Init-Data`.

Создать участника:

```bash
curl -X POST http://localhost:8000/api/admin/players \
  -H 'Content-Type: application/json' \
  -d '{"name":"Имя участника","region":"Якутск","bio":"Краткое описание"}'
```

Создать событие:

```bash
curl -X POST http://localhost:8000/api/admin/events \
  -H 'Content-Type: application/json' \
  -d '{"title":"Финал","starts_at":"2026-06-27T09:00:00+00:00","description":"Описание","player_ids":[1,2,3,4]}'
```

Закрыть событие и начислить фан-очки:

```bash
curl -X POST http://localhost:8000/api/admin/events/1/settle \
  -H 'Content-Type: application/json' \
  -d '{"results":[{"player_id":1,"place":1,"score":42},{"player_id":2,"place":2,"score":39}]}'
```

## Структура

```text
app/        FastAPI API, Telegram auth, SQLite, bot polling
web/        Минималистичный TMA фронтенд без React
wiki/       Проектная документация для разработки
 tests/     Тесты подписи Telegram initData
```

## Источники, которые полезно держать под рукой

- Telegram Mini Apps docs: https://core.telegram.org/bots/webapps
- Telegram Bot API: https://core.telegram.org/bots/api
- ФНС, перечень организаторов азартных игр: https://www.nalog.gov.ru/rn77/related_activities/adjustable/gambling_org/
- ЕРАИ: https://erai.ru/
- Контекст Игр Дыгына: региональные спортивные СМИ и официальные публикации организаторов. Все реальные результаты надо вносить только после ручной проверки источников.
