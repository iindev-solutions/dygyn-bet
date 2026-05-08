# CODE_MAP — dygyn-bet

## Root

- `AGENTS.md` — vault-first project rules for coding agents.
- `README.md` — short Russian product description: voting app idea, 100-point vote model, participant stats, visual style, legal boundary.
- `DESIGN.md` — machine-readable and human-readable Игры Дыгына — голосование visual identity for coding agents.
- `new_brief.md` — Russian canonical MVP brief for product/UI/backend direction.
- `data/import/dygyn_2026/` — CSV/XLSX import data pack: sources, disciplines, 2026 event/participants, 2025 overall and discipline results, partial 2026 qualifier results.
- `.env.example` — configuration template for bot token, web app URL, admins, dev login, polling, SQLite path, Telegram auth age, frontend directory.
- `.gitignore` — ignores Python env/cache, `.env`, SQLite data files, pyc, Vue `node_modules/dist` outputs.
- `.dockerignore` — excludes local env/cache/data and Vue build folders from Docker context.
- `requirements.txt` — Python dependencies: FastAPI, uvicorn, aiogram, python-dotenv, pytest, httpx.
- `Dockerfile` — multi-stage image: builds Vue frontend with Node 22, then serves FastAPI from Python 3.12 slim.
- `docker-compose.yml` — `dygyn-tma` service exposing port 8000 and mounting `./data`.

## Backend: `app/`

- `app/main.py` — FastAPI app, Vue asset mount, legacy static rollback mount, rate limit middleware, optional demo seed, optional bot polling, auth dependencies, user/event/player/avatar/prediction/live-results/leaderboard/admin API endpoints.
- `app/db.py` — SQLite schema and persistence functions: users, players, events, participants, 100-point vote items, final results, live two-day results/standings, sources, disciplines, discipline results, history, leaderboard, admin audit logs, health checks, demo seed.
- `app/config.py` — environment loading and immutable `Settings` dataclass, including prod-safe demo seed flag and configurable `FRONTEND_DIR`.
- `app/import_data.py` — validates/imports `data/import/dygyn_2026/` CSV pack into SQLite sources, disciplines, players, event links, history, and discipline-result tables.
- `app/telegram_auth.py` — Telegram Mini App initData HMAC validation, `TelegramUser`, test initData helper.
- `app/bot.py` — aiogram polling bot with `/start`, `/app`, `/rules`, and Mini App buttons.
- `app/bot_runner.py` — standalone bot polling entrypoint for systemd.

## Frontend: `web-vue/`

- `web-vue/` — current Vue 3 TMA frontend. Build with `npm ci && npm run build`; FastAPI serves `web-vue/dist` by default.
- `web-vue/src/main.ts` — app bootstrap, Pinia, router, admin route guard.
- `web-vue/src/App.vue` — app shell, A1 hero, bottom tabs, boot/auth loading, toast.
- `web-vue/src/composables/useTelegramInit.ts` — guarded Telegram SDK init; waits for late `window.Telegram.WebApp`, calls `ready()`/`expand()`, exposes initData.
- `web-vue/src/api/` — typed fetch API client and endpoint modules; API base comes from `import.meta.env.BASE_URL`/`VITE_API_BASE`.
- `web-vue/src/stores/` — Pinia stores for user, events/vote allocations, players, leaderboard, admin.
- `web-vue/src/views/` — Games, Support, Players, Admin, Rules views.
- `web-vue/src/utils/storyCard.ts` — story PNG generation/share/download using same-origin participant avatar endpoint.
- `web-vue/vite.config.ts` — Vite config with `/dygyn-bet/` production base, lazy chunks, visualizer, manifest.
- `web-vue/scripts/check-bundle-budget.mjs` — enforces initial JS gzip budget <=150KB.

## Legacy Frontend: `web/`

- `web/index.html` — legacy vanilla Telegram Mini App shell.
- `web/app.js` — legacy vanilla JS client, retained for rollback.
- `web/styles.css` — source style ported into Vue; retained for rollback.

## Scripts

- `scripts/import_dygyn_data.py` — CLI for validating or applying the Dygyn 2026 import data pack.
- `scripts/backup_sqlite.py` — CLI for consistent SQLite backups with old-backup pruning.

## Tests: `tests/`

- `tests/test_telegram_auth.py` — validates signed initData, rejects tampering and expired auth data.
- `tests/test_db_flow.py` — exercises pick creation and event settlement flow in temporary SQLite DB.
- `tests/test_hardening.py` — covers admin source URL validation and hardened settle/finish behavior.
- `tests/test_import_data.py` — validates CSV pack and imports it into a temporary SQLite DB.
- `web-vue/src/**/*.test.ts` — Vitest frontend unit tests, including allocation formatting and Telegram SDK delayed-init guard.

## Docs

- `wiki/` — older Russian documentation; keep as source/history unless explicitly migrated or removed.
- `vault/` — canonical English project memory.
- `vault/wiki/architecture/mvp-product-decisions.md` — compact record of canonical MVP decisions: 100-point allocation, participant discipline stats, bot/TMA shape, scale assumptions.

## Runtime Data

- `data/dygyn.sqlite3` — default SQLite DB path from `.env.example`; ignored by git.
- `data/*.sqlite3-*` — SQLite WAL/SHM files; ignored by git.

## Key Flows

### User Auth

1. Vue frontend waits for `window.Telegram.WebApp` through `useTelegramInit()` to avoid SDK load races.
2. API client reads raw `window.Telegram.WebApp.initData` and sends it as `X-Telegram-Init-Data`.
3. Backend validates HMAC and `auth_date`.
4. Backend upserts user by Telegram ID.
5. `ALLOW_DEV_LOGIN=true` allows local browser access without Telegram header.

### Pick Flow

1. User loads events.
2. User opens event details.
3. User selects 1–2 participants and distributes confidence points on a 100-point scale.
4. Backend checks event exists, status is `open`, close time is future, point total is 100, and every selected player belongs to event.
5. Backend replaces current user's event vote items and stores one row per selected participant using `UNIQUE(event_id, user_id, player_id)`.

### Live Result/Admin Flow

1. Admin enters Day 1/Day 2 discipline results from the TMA admin tab.
2. Admin publishes Day 1, Day 2, or overall standings as provisional/official.
3. Public event detail shows live results and last updated time.
4. Admin finishes event by choosing the official winner.
5. Event status becomes `settled`; pick rows for the winner receive `awarded_points = confidence_points`, others become 0.
