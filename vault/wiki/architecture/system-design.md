# System Design

## High-Level Architecture

```text
Telegram user
    ↓
Telegram bot /start
    ↓ web_app button
Telegram Mini App frontend (`web/`)
    ↓ HTTPS + X-Telegram-Init-Data
FastAPI backend (`app/main.py`)
    ↓
SQLite database (`data/dygyn.sqlite3`)
```

## Components

### Telegram Bot

- Implemented with aiogram in `app/bot.py`.
- Sends Mini App buttons for opening predictions and stats.
- Supports `/start`, `/app`, `/rules`.
- Runs via polling when `ENABLE_POLLING=true` and `BOT_TOKEN` is set.

### Frontend

- Vanilla HTML/CSS/JS in `web/`.
- Served by FastAPI as static assets.
- Uses Telegram WebApp JS SDK when opened inside Telegram.
- Sends raw `tg.initData` in `X-Telegram-Init-Data` header.
- Provides tabs for events, stats, players, and rules.

### Backend

- FastAPI app in `app/main.py`.
- Owns auth, rate limiting, API routes, static serving, startup/shutdown lifecycle.
- Starts DB schema and demo seed on startup.
- Optional bot polling runs in the same process for MVP/dev.

### Database

- SQLite via `sqlite3` in `app/db.py`.
- Schema is created on startup.
- Default path: `./data/dygyn.sqlite3`.
- WAL mode enabled.

## Why This Design

- FastAPI gives simple API and static serving for MVP.
- SQLite is enough for early small-audience testing.
- Aiogram is enough for Telegram bot commands and Mini App buttons.
- Vanilla JS avoids build tooling and deploy complexity.

## Production Upgrade Path

When real usage grows:

- SQLite → PostgreSQL.
- In-memory rate limit → Redis-backed rate limit.
- Bot polling → webhook.
- Curl/admin API → protected admin panel.
- Manual result entry → verified import flow.
- Local SQLite files → automated backups.
- Single process → split bot/API workers if needed.

## Security Notes

- Never trust `initDataUnsafe` from the browser.
- Validate raw Telegram `initData` on backend.
- Keep `ALLOW_DEV_LOGIN=false` in production.
- Do not store secrets in git.
- Admin APIs require Telegram ID in `ADMIN_IDS`, except local dev admin when dev login is enabled.
