# QUICK_START — dygyn-bet

Read this first. Read deep docs only when task needs them.

## Now

- Product: Telegram Mini App fan predictions for Dygyn Games.
- Public URL: `https://iindiinda.duckdns.org/dygyn-bet/`.
- Style: `Dygyn Fan Arena` — dark sports cards, gold accent, no casino vibe.
- User flow: open bot → TMA → choose 1–3 participants → distribute 100 confidence points → save → share story card.
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

- 100-point allocation voting works locally: one prediction distributes exactly 100 points across 1–3 participants.
- Story-card sharing works.
- Dygyn Fan Arena UI deployed.
- Latest VPS deploy done: code updated, DB backed up, import applied, services active, VPS tests passed.
- README rewritten as short product-only description; no setup/admin/API noise.
- `new_brief.md` is canonical MVP brief.
- Product decisions recorded in `vault/wiki/architecture/mvp-product-decisions.md`.
- Product mechanic implemented locally: one event prediction = distribute exactly 100 virtual confidence points across 1–3 participants.
- Participant detail vision: minimal bot/TMA shows each athlete with tabular verified stats for all 7 Dygyn disciplines by year/event.
- Dygyn Games are a two-day event; app now has live Day 1, Day 2, overall/final results model and public rendering.
- Admin panel exists as `ADMIN_IDS`-only TMA tab for Day 1/Day 2 results, standings, and final finish; imports/events/participants management still planned.
- `ADMIN_IDS` still needed from user.
- Production DB now has imported Dygyn 2026 data: 16 active participants, 7 disciplines, 126 discipline result rows.
- Backend and frontend expose participant detail with imported discipline-result tables.

## Next Best Tasks

1. Add real `ADMIN_IDS` on VPS so admin tab is visible to user.
2. QA in Telegram bot/Mini App on mobile: event, participant tables, 100-point prediction, admin result forms.
3. Implement profile and event-specific leaderboard/stats APIs.
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
