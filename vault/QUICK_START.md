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
- `ADMIN_IDS` still needed from user.
- Real participants/results still demo; must replace with verified sources.

## Next Best Tasks

1. Get user Telegram numeric ID → add to `ADMIN_IDS` on VPS.
2. Add admin-only TMA tab.
3. Add discipline-level participant stats table.
4. Replace demo data with real verified Dygyn data.
5. Mobile QA in Telegram.

## Read Deep Docs Only If Needed

- Design: `vault/wiki/architecture/design-direction.md`
- Deploy: `vault/wiki/services/deployment.md`
- API: `vault/wiki/services/api.md`
- DB: `vault/wiki/architecture/data-model.md`
- Frontend: `vault/wiki/services/frontend.md`
- Code map: `vault/CODE_MAP.md`

## End Rule

Meaningful work → update `vault/logs/changelog.md` terse. Update `QUICK_START.md` if current state/next tasks changed.
