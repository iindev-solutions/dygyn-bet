# QUICK_START — dygyn-bet

Read this first. Read deep docs only when task needs them.

## Now

- Product: Telegram Mini App fan predictions for Dygyn Games.
- Public URL: `https://iindiinda.duckdns.org/dygyn-bet/`.
- Style: `Dygyn Fan Arena` — dark sports cards, gold accent, no casino vibe.
- User flow: open bot → TMA → choose up to 3 participants → set confidence → save → share story card.
- Legal line: fan votes only. No money, odds, deposits, withdrawals, payouts, prizes with value.

## Stack

- Backend: FastAPI, SQLite, aiogram.
- Frontend: vanilla HTML/CSS/JS.
- Tests: pytest.
- Deploy: nginx prefix `/dygyn-bet/` → API `127.0.0.1:8010`.
- VPS: SSH alias `iind-vps`.
- Services: `dygyn-bet.service` API, `dygyn-bet-bot.service` bot.
- Server path: `/opt/dygyn-bet`.
- DB: `/opt/dygyn-bet/data/dygyn.sqlite3`.

## Current State

- 3-pick voting works.
- Story-card sharing works.
- Dygyn Fan Arena UI deployed.
- VPS tests passed last deploy.
- README rewritten as short product-only description; no setup/admin/API noise.
- `new_brief.md` is canonical MVP brief.
- Product decisions recorded in `vault/wiki/architecture/mvp-product-decisions.md`.
- Target product mechanic: one event prediction = distribute exactly 100 virtual confidence points across 1–3 participants.
- Participant detail vision: minimal bot/TMA shows each athlete with tabular verified stats for all 7 Dygyn disciplines by year/event.
- Dygyn Games are a two-day event; target app must show Day 1, Day 2, overall/final results, provisional/official state, and final winners.
- Admin panel is mandatory: `ADMIN_IDS`-only TMA tab for imports, events, participants, Day 1/Day 2 results, standings, and final finish.
- `ADMIN_IDS` still needed from user.
- Real participants/results still demo in deployed DB; local import CLI now validates/applies `data/import/dygyn_2026/` into SQLite.

## Next Best Tasks

1. Finish/review import CLI commit, then apply import to local/dev DB.
2. Implement backend API to expose participant discipline stats and imported 2026 event data.
3. Implement backend schema/API: 100-point allocation, `closes_at`, stats, leaderboard/profile, two-day standings.
4. Add mandatory admin-only TMA tab for imports, events, participants, Day 1/Day 2 results, standings, and finish.
5. Add public frontend screens: Home/Forecast/Stats/Rating/Profile + athlete stat/result tables.
6. Get user Telegram numeric ID → add to `ADMIN_IDS` on VPS.
7. Build CSV import/validation from `data/import/dygyn_2026/` and replace demo DB data.
8. Mobile QA in Telegram.

## Read Deep Docs Only If Needed

- Design: `vault/wiki/architecture/design-direction.md`
- Deploy: `vault/wiki/services/deployment.md`
- API: `vault/wiki/services/api.md`
- DB: `vault/wiki/architecture/data-model.md`
- Frontend: `vault/wiki/services/frontend.md`
- Code map: `vault/CODE_MAP.md`

## End Rule

Meaningful work → update `vault/logs/changelog.md` terse. Update `QUICK_START.md` if current state/next tasks changed.
