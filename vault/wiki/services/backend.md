# Backend Service

## Responsibilities

- Serve FastAPI API.
- Serve static Mini App files from `web-vue/dist`.
- Validate Telegram Mini App auth.
- Manage SQLite schema and data access.
- Seed demo data only when explicitly enabled for local/dev.
- Run API service.
- Bot polling can run in a separate systemd service via `app.bot_runner`.
- Enforce basic rate limiting and admin checks.

## Main Files

- `app/main.py` — app, middleware, lifecycle, routes, dependencies.
- `app/db.py` — schema and persistence functions.
- `app/config.py` — env settings.
- `app/telegram_auth.py` — Telegram auth validation.
- `app/bot.py` — Telegram bot polling handlers.
- `app/bot_runner.py` — standalone bot polling entrypoint.

## Environment Variables

From `.env.example`:

- `BOT_TOKEN` — BotFather token.
- `WEB_APP_URL` — public HTTPS Mini App URL.
- `ADMIN_IDS` — comma-separated Telegram numeric IDs.
- `ALLOW_DEV_LOGIN` — local browser dev login; must be `false` in production.
- `ENABLE_POLLING` — run aiogram polling inside FastAPI process. For VPS deployment, keep this `false` and run `app.bot_runner` as separate service.
- `FRONTEND_DIR` — frontend build path; production uses `/opt/dygyn-bet/web-vue/dist`.
- `ADMIN_WEB_USERNAME`, `ADMIN_WEB_PASSWORD`, `ADMIN_WEB_SESSION_HOURS` — browser admin login/session config.
- `SEED_DEMO` — local/dev demo seed flag; production must keep this `false`.
- `DB_PATH` — SQLite DB path.
- `BACKUP_DIR`, `BACKUP_KEEP` — defaults for `scripts/backup_sqlite.py`.
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
- Set real `ADMIN_IDS` if Telegram admin access is needed; browser admin also works through `/#/admin-login`.
- Decide whether polling is acceptable or switch to webhook.
- Ensure `data/` is persistent and backed up; use `python scripts/backup_sqlite.py --db <db> --out-dir <dir>` from cron/systemd timer.
- Keep `SEED_DEMO=false`; use imported Dygyn data.
- Consider PostgreSQL when usage or ops requirements grow.

## Tests

Run:

```bash
pytest
```

Current tests cover Telegram initData validation, DB pick/settle flow, import validation, source URL validation, browser admin auth, analytics, and hardened settle behavior.
