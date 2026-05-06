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
- `ADMIN_IDS` still needed from user.
- Real participants/results still demo; must replace with verified sources.

## Next Best Tasks

1. Confirm 100-point allocation model details, then implement backend-first.
2. Add brief backend gaps: `closes_at`, fixed allocation validation, event stats/leaderboard/profile, admin close/finish aliases.
3. Add participant discipline stats model/import: disciplines + per-athlete/year results with source URLs.
4. Add brief frontend gaps: Home/Forecast/Stats/Rating/Profile structure and allocation UI + athlete stat tables.
5. Get user Telegram numeric ID → add to `ADMIN_IDS` on VPS.
6. Replace demo data with real verified Dygyn data.
7. Mobile QA in Telegram.

## Read Deep Docs Only If Needed

- Design: `vault/wiki/architecture/design-direction.md`
- Deploy: `vault/wiki/services/deployment.md`
- API: `vault/wiki/services/api.md`
- DB: `vault/wiki/architecture/data-model.md`
- Frontend: `vault/wiki/services/frontend.md`
- Code map: `vault/CODE_MAP.md`

## End Rule

Meaningful work → update `vault/logs/changelog.md` terse. Update `QUICK_START.md` if current state/next tasks changed.
