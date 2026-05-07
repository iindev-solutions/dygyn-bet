# QUICK_START — dygyn-bet

Read this first. Read deep docs only when task needs them.

## Now

- Product: Telegram Mini App voting for Dygyn Games.
- Public URL: `https://iindiinda.duckdns.org/dygyn-bet/`.
- Style: `Игры Дыгына — голосование` — dark sports cards, gold accent, no casino vibe. Root `DESIGN.md` is canonical visual identity for agents.
- User flow: open bot → TMA → choose 1–3 participants → distribute confidence points → save → share story card.
- Legal line: votes only. No money, odds, deposits, withdrawals, payouts, prizes with value.

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

- 100-point allocation voting works locally: one vote uses a 100-point scale; equal three-way split is `33/33/33` and the 1-point remainder is not awarded.
- Story-card sharing works.
- Игры Дыгына — голосование UI deployed.
- Latest VPS deploy done: admin live-results flow deployed, DB backed up, services active, VPS tests passed.
- README rewritten as short product-only description; no setup/admin/API noise.
- `new_brief.md` is canonical MVP brief.
- Product decisions recorded in `vault/wiki/architecture/mvp-product-decisions.md`.
- Product mechanic implemented locally: one event vote = distribute virtual confidence points across 1–3 participants; backend accepts exact 100 or equal `33/33/33` for three participants.
- Participant detail vision: minimal bot/TMA shows each athlete with tabular verified stats for all 7 Dygyn disciplines by year/event.
- Dygyn Games are a two-day event; app now has live Day 1, Day 2, overall/final results model and public rendering.
- Admin panel exists as `ADMIN_IDS`-only TMA tab for Day 1/Day 2 results, standings, and final finish; imports/events/participants management still planned. VPS `ADMIN_IDS` is configured.
- Production DB now has imported Dygyn 2026 data: 16 active participants, 7 disciplines, 126 discipline result rows.
- Backend and frontend expose participant detail with imported discipline-result tables.

## Next Best Tasks

1. QA in Telegram bot/Mini App on mobile: event, participant tables, 100-point vote, equal 33/33/33 split, admin result forms.
2. Implement profile and event-specific leaderboard/stats APIs.
3. Add admin UI for imports/events/participants management.
4. Add public frontend screens: Home/Vote/Stats/Rating/Profile + athlete stat/result tables.

## Read Deep Docs Only If Needed

- Design: `vault/wiki/architecture/design-direction.md`
- Deploy: `vault/wiki/services/deployment.md`
- API: `vault/wiki/services/api.md`
- DB: `vault/wiki/architecture/data-model.md`
- Frontend: `vault/wiki/services/frontend.md`
- Code map: `vault/CODE_MAP.md`

## End Rule

Meaningful work → update `vault/logs/changelog.md` terse. Update `QUICK_START.md` if current state/next tasks changed.
