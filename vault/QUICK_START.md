# QUICK_START — dygyn-bet

Read this first. Read deep docs only when task needs them.

## Now

- Product: Telegram Mini App voting for Dygyn Games.
- Public URL: `https://iindiinda.duckdns.org/dygyn-bet/`.
- Style: A1 ceremonial poster direction — dark sports cards, SVG Yakut ornament strip, gold accent, no casino vibe. Root `DESIGN.md` is canonical visual identity for agents.
- User flow: open bot → TMA → choose 1–2 participants → distribute confidence points → save → share story card.
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

- 100-point allocation voting works locally: one vote uses a 100-point scale; votes are limited to top 2 participants and must total 100 points.
- Story-card sharing works.
- A1-style redesign first pass deployed: ceremonial hero, SVG ornament strip, no visible login line/refresh/no-money notice in top screen.
- Latest VPS deploy done: A1 redesign first pass deployed, services active, VPS tests passed.
- README rewritten as short product-only description; no setup/admin/API noise.
- `new_brief.md` is canonical MVP brief.
- Product decisions recorded in `vault/wiki/architecture/mvp-product-decisions.md`.
- Product mechanic implemented locally: one event vote = distribute virtual confidence points across 1–2 participants; backend accepts at most two participants and exactly 100 total points.
- Participant detail vision: minimal bot/TMA shows each athlete with tabular verified stats for all 7 Dygyn disciplines by year/event.
- Dygyn Games are a two-day event; app now has live Day 1, Day 2, overall/final results model and public rendering.
- Admin panel exists as `ADMIN_IDS`-only TMA tab for Day 1/Day 2 results, standings, and final finish; imports/events/participants management still planned. VPS `ADMIN_IDS` is configured.
- Production DB now has imported Dygyn 2026 data: 16 active participants, 7 disciplines, 126 discipline result rows.
- Backend and frontend expose participant detail with imported discipline-result tables.

## Next Best Tasks

1. QA in Telegram bot/Mini App on mobile: event, participant tables, 100-point vote, admin result forms.
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
