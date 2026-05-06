# CODE_MAP — dygyn-bet

## Root

- `AGENTS.md` — vault-first project rules for coding agents.
- `README.md` — Russian product overview, local run instructions, Telegram setup, Docker, admin curl examples, legal warning.
- `.env.example` — configuration template for bot token, web app URL, admins, dev login, polling, SQLite path, Telegram auth age.
- `.gitignore` — ignores Python env/cache, `.env`, SQLite data files, pyc.
- `requirements.txt` — Python dependencies: FastAPI, uvicorn, aiogram, python-dotenv, pytest, httpx.
- `Dockerfile` — Python 3.12 slim app image, installs requirements, runs uvicorn.
- `docker-compose.yml` — `dygyn-tma` service exposing port 8000 and mounting `./data`.

## Backend: `app/`

- `app/main.py` — FastAPI app, static web mount, rate limit middleware, startup DB seed, optional bot polling, auth dependencies, user/event/player/leaderboard/admin API endpoints.
- `app/db.py` — SQLite schema and all persistence functions: users, players, events, participants, picks, results, history, leaderboard, demo seed.
- `app/config.py` — environment loading and immutable `Settings` dataclass.
- `app/telegram_auth.py` — Telegram Mini App initData HMAC validation, `TelegramUser`, test initData helper.
- `app/bot.py` — aiogram polling bot with `/start`, `/app`, `/rules`, and Mini App buttons.
- `app/bot_runner.py` — standalone bot polling entrypoint for systemd.

## Frontend: `web/`

- `web/index.html` — Telegram Mini App shell with tabs: events, stats, players, rules.
- `web/app.js` — vanilla JS client: Telegram WebApp init, prefix-safe API wrapper, arena event rendering, three-pick flow, support stats, leaderboard, player cards, story-card sharing, HTML escaping, toast.
- `web/styles.css` — Dygyn Fan Arena dark sports UI: card layout, bottom navigation, progress bars, confidence chips, sticky save action.

## Tests: `tests/`

- `tests/test_telegram_auth.py` — validates signed initData, rejects tampering and expired auth data.
- `tests/test_db_flow.py` — exercises pick creation and event settlement flow in temporary SQLite DB.

## Docs

- `wiki/` — older Russian documentation; keep as source/history unless explicitly migrated or removed.
- `vault/` — canonical English project memory.

## Runtime Data

- `data/dygyn.sqlite3` — default SQLite DB path from `.env.example`; ignored by git.
- `data/*.sqlite3-*` — SQLite WAL/SHM files; ignored by git.

## Key Flows

### User Auth

1. Frontend reads raw `window.Telegram.WebApp.initData`.
2. Frontend sends it as `X-Telegram-Init-Data`.
3. Backend validates HMAC and `auth_date`.
4. Backend upserts user by Telegram ID.
5. `ALLOW_DEV_LOGIN=true` allows local browser access without Telegram header.

### Pick Flow

1. User loads events.
2. User opens event details.
3. User selects up to three participants and confidence points.
4. Backend checks event exists, status is `open`, start time is future, and every selected player belongs to event.
5. Backend replaces current user's event picks and stores one row per selected participant using `UNIQUE(event_id, user_id, player_id)`.

### Settlement Flow

1. Admin posts results.
2. Backend deletes old results for event.
3. Backend inserts submitted result rows.
4. Event status becomes `settled`.
5. Pick rows for first-place player receive `awarded_points = confidence_points`; others become 0.
