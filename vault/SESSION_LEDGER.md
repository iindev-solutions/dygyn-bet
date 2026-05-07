# Session Ledger

## 2026-05-06 — Compact Vault Mode
- Scope: reduce token cost of future sessions and create reusable starter.
- Changed: added `QUICK_START.md`; deep docs now on-demand; changelog style compact.
- Changed: created sibling `../empty-template-vault` starter with compact vault skeleton.
- Next: use compact vault updates only.


## 2026-05-06 — Vault Initialized

- Scope: study `empty-template-vault-rag`, inspect current `dygyn-bet` docs/code, add project `vault/`.
- Changes: added root `AGENTS.md`; added vault workflow, index, sprint, resume plan, code map, changelog, architecture docs, and service docs.
- Verified: file structure reviewed; existing README, wiki docs, backend, frontend, tests, Docker, env config inspected.
- Not verified: test suite could not run because pytest is not installed in the current Python environment.
- Blockers: real participant/event data still demo; deployment target and backup plan not decided.
- Next: replace demo data with verified sources; test real Telegram bot/TMA flow.

## 2026-05-06 — Initial Commit Prepared

- Scope: create and push the first repository commit.
- Changes: no product code changes; vault ledger/changelog updated before commit.
- Verified: candidate files listed; no `.env` or SQLite database files found in project root.
- Next: commit and push to `origin/main`.

## 2026-05-06 — Three-Pick Voting and Story Sharing

- Scope: let users vote for up to three participants and add social sharing for project growth.
- Changes: backend stores up to three pick rows per user/event; frontend supports multi-select + save; share text/native share/story-card download added.
- Verified: Python compile, JS syntax check, direct SQLite DB flow script, old picks-schema migration script.
- Not verified: full pytest/app import due missing Python dependencies (`fastapi`, `pytest`); mobile Telegram/Instagram manual flow.
- Next: install deps, run full tests, and test sharing on mobile devices.

## 2026-05-06 — VPS Deployment Route Scouted

- Scope: determine whether `dygyn-bet` can be added to existing `iindiinda.duckdns.org` VPS without touching public root.
- Findings: nginx serves existing Laravel/Vue app; root public folder and `/api` are occupied; safe route is `/dygyn-bet/` proxied to local FastAPI port `8010`.
- Changes: frontend made prefix-safe; deployment doc added.
- Verified: JS syntax check and Python compile.
- Next: obtain bot token/admin IDs, then deploy via `/opt/dygyn-bet`, systemd, and nginx location.

## 2026-05-06 — Deployed to VPS

- Scope: deploy `dygyn-bet` under existing `iindiinda.duckdns.org` without touching existing public root.
- Changes: app copied to `/opt/dygyn-bet`; venv and dependencies installed; server `.env` created; `dygyn-bet.service` API started; `dygyn-bet-bot.service` polling started; nginx `/dygyn-bet/` reverse proxy added.
- Verified: VPS pytest passed; API and bot systemd services active; nginx config valid; public health/html/static/API-auth checks passed; API restart after split polling/API is fast; no token found in local repo.
- Not verified: explicit Telegram `/start` confirmation in chat; full mobile QA; admin ID not configured.
- Next: add `ADMIN_IDS`, restart service, test from Telegram mobile.

## 2026-05-06 — Игры Дыгына — голосование Frontend Pass

- Scope: apply `ref.md` design direction to the frontend without changing stack.
- Changes: added vault design direction, dark sports UI, bottom nav, event hero, participant cards, support bars, confidence chips, sticky save action, support+leaderboard tab.
- Verified: JS syntax, Python compile, local search for removed wording/secrets.
- Not verified: local pytest unavailable; mobile Telegram visual QA pending.
- Follow-up: deployed to VPS; VPS tests passed; API and bot services restarted and active; public health and updated HTML checked.
- Next: test on mobile, then plan admin-only TMA tab.

## 2026-05-06 — Removed Launch-Phase Product Copy

- Scope: remove launch-phase wording from visible product/design copy.
- Changes: UI, bot text, README, wiki, and vault docs cleaned; old scope filename renamed.
- Verified: local search has no removed launch-phase wording matches; syntax checks run.
- Next: deploy cleanup to VPS and recheck public page/bot.
- Follow-up: cleanup deployed to VPS; tests passed; API and bot services restarted and active; public health check passed.
