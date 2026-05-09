# CODE_MAP — dygyn-bet

## Root

- `AGENTS.md` — vault-first project rules for coding agents.
- `README.md` — short Russian product description.
- `DESIGN.md` — canonical visual identity for coding agents.
- `new_brief.md` — Russian canonical MVP brief.
- `vault/AUDIT.md` — current product/privacy/security/ops audit.
- `vault/PRIVACY_PLAN.md` — privacy-policy source notes and launch checklist.
- `data/import/dygyn_2026/` — CSV/XLSX import data pack.
- `requirements.txt` — Python dependencies: FastAPI, uvicorn, aiogram, python-dotenv, pytest, httpx.
- `Dockerfile` — multi-stage image: builds Vue frontend with Node 22, then serves FastAPI from Python 3.12 slim.
- `docker-compose.yml` — `dygyn-tma` service exposing port 8000 and mounting `./data`.

## Backend: `app/`

- `app/main.py` — FastAPI app, Vue asset mount, auth dependencies, user/event/player/avatar/prediction/live-results/leaderboard/analytics/admin API endpoints.
- `app/db.py` — SQLite schema and persistence functions: users, players, events, vote items, final/live results, sources, disciplines, history, leaderboard, analytics, admin audit logs, health checks, demo seed.
- `app/config.py` — environment loading and immutable settings.
- `app/import_data.py` — validates/imports `data/import/dygyn_2026/` CSV pack.
- `app/telegram_auth.py` — Telegram Mini App initData HMAC validation.
- `app/bot.py` — aiogram polling bot with `/start`, `/app`, `/rules`, and Mini App buttons.
- `app/bot_runner.py` — standalone bot polling entrypoint for systemd.

## Frontend: `web-vue/`

- `web-vue/` — current Vue 3 TMA frontend. Build with `npm ci && npm run build`; FastAPI serves `web-vue/dist`.
- `web-vue/src/main.ts` — app bootstrap, Pinia, router, admin route guard; redirects admin routes away inside Telegram.
- `web-vue/src/App.vue` — app shell, user-only bottom tabs, boot/auth loading, toast, app-open analytics.
- `web-vue/src/components/events/HomeHero.vue` — main-only photo hero, countdown, CTA hidden after saved vote.
- `web-vue/src/components/players/PlayerGridCard.vue` — two-column athlete grid tile.
- `web-vue/src/components/players/SocialIconLink.vue` — neutral social icon link.
- `web-vue/src/components/admin/AdminAnalyticsPanel.vue` — no-library admin analytics KPI/bar chart panel.
- `web-vue/src/composables/useTelegramInit.ts` — guarded Telegram SDK init.
- `web-vue/src/composables/useAnalytics.ts` — random client ID + allowlisted analytics event sender.
- `web-vue/src/api/` — typed fetch API client and endpoint modules; `adminAuth.ts` handles browser admin login/logout.
- `web-vue/src/stores/` — Pinia stores for user, events/vote allocations, players, leaderboard, admin.
- `web-vue/src/views/EventsView.vue` — home/vote/saved PNG flow/live results.
- `web-vue/src/views/StatsView.vue` — support stats and top-100 fan leaderboard.
- `web-vue/src/views/PlayersView.vue` — athlete grid and detail discipline tables.
- `web-vue/src/views/AdminView.vue` — browser-only admin forms plus analytics.
- `web-vue/src/views/RulesView.vue` — rules, privacy note, iindev link.
- `web-vue/src/utils/storyCard.ts` — PNG generation/share/download using same-origin participant avatar endpoint.
- `web-vue/src/utils/display.ts` — display helpers including allocation, support %, discipline result/outcome formatting.
- `web-vue/vite.config.ts` — Vite config with `/dygyn-bet/` production base, lazy chunks, visualizer, manifest.
- `web-vue/scripts/check-bundle-budget.mjs` — enforces initial JS gzip budget <=150KB.

## Legacy Frontend: `web/`

- `web/index.html`, `web/app.js`, `web/styles.css` — legacy vanilla frontend retained for rollback via `FRONTEND_DIR=web`.

## Scripts

- `scripts/import_dygyn_data.py` — CLI for validating/applying the Dygyn 2026 import data pack.
- `scripts/backup_sqlite.py` — CLI for consistent SQLite backups with old-backup pruning.

## Tests

- `tests/test_telegram_auth.py` — signed initData validation.
- `tests/test_db_flow.py` — pick creation and event settlement flow.
- `tests/test_hardening.py` — admin source URL validation and settle/finish behavior.
- `tests/test_admin_web_auth.py` — browser admin password hashing and session lifecycle.
- `tests/test_import_data.py` — data pack import tests.
- `tests/test_analytics.py` — analytics event recording, allowlist, summary behavior.
- `web-vue/src/**/*.test.ts` — Vitest frontend unit tests.

## Key Flows

### User Auth

1. Vue waits for `window.Telegram.WebApp` through `useTelegramInit()`.
2. API client sends raw `initData` as `X-Telegram-Init-Data`.
3. Backend validates HMAC and `auth_date`.
4. Backend upserts user by Telegram ID.
5. Browser admin login at `/#/admin-login` creates HttpOnly `dygyn_admin_session` cookie.
6. `ALLOW_DEV_LOGIN=true` allows local browser access without Telegram header.

### Pick Flow

1. User opens app and event loads.
2. User selects 1–2 participants and distributes exactly 100 confidence points.
3. Backend validates event/time/participants/point total.
4. Backend replaces current user's event vote rows.
5. Frontend hides voting controls after saved vote and exposes only PNG story card action.

### Analytics Flow

1. Frontend sends allowlisted product events with random client ID and route path.
2. Backend stores hashed client ID, hashed user-agent, sanitized metadata, timestamp.
3. No raw Telegram ID, username, IP, raw initData, vote text, or participant names are stored in analytics rows.
4. Browser admin dashboard reads aggregate analytics from `/api/admin/analytics`.

### Live Result/Admin Flow

1. Browser admin enters Day 1/Day 2 discipline results.
2. Admin publishes standings as provisional/official.
3. Public event detail shows live results and last updated time.
4. Admin finishes event by choosing official winner.
5. Event becomes `settled`; winner pick rows receive `awarded_points = confidence_points`.
