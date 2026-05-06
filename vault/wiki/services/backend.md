# Backend Service

## Responsibilities

- Serve FastAPI API.
- Serve static Mini App files from `web/`.
- Validate Telegram Mini App auth.
- Manage SQLite schema and data access.
- Seed demo data for empty local database.
- Run aiogram bot polling when enabled.
- Enforce basic rate limiting and admin checks.

## Main Files

- `app/main.py` — app, middleware, lifecycle, routes, dependencies.
- `app/db.py` — schema and persistence functions.
- `app/config.py` — env settings.
- `app/telegram_auth.py` — Telegram auth validation.
- `app/bot.py` — Telegram bot polling.

## Environment Variables

From `.env.example`:

- `BOT_TOKEN` — BotFather token.
- `WEB_APP_URL` — public HTTPS Mini App URL.
- `ADMIN_IDS` — comma-separated Telegram numeric IDs.
- `ALLOW_DEV_LOGIN` — local browser dev login; must be `false` in production.
- `ENABLE_POLLING` — run aiogram polling inside FastAPI process.
- `DB_PATH` — SQLite DB path.
- `AUTH_MAX_AGE_SECONDS` — max age for Telegram initData.
- `RATE_LIMIT_WINDOW_SECONDS` — rate window.
- `RATE_LIMIT_MAX_REQUESTS` — max requests per window.

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000`. With `ALLOW_DEV_LOGIN=true`, browser testing works without Telegram.

## Docker Run

```bash
cp .env.example .env
# edit .env
docker compose up --build
```

## Production Notes

- Use HTTPS.
- Set `ALLOW_DEV_LOGIN=false`.
- Set real `BOT_TOKEN`.
- Set real `ADMIN_IDS`.
- Decide whether polling is acceptable or switch to webhook.
- Ensure `data/` is persistent and backed up.
- Replace demo data before launch.
- Consider PostgreSQL when usage or ops requirements grow.

## Tests

Run:

```bash
pytest
```

Current tests cover Telegram initData validation and basic DB pick/settle flow.
