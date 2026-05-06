# Changelog

## 2026-05-06 — README Rewrite

- Rewrote `README.md` again as a short product-only description.
- Removed local setup, admin curl examples, implementation status, source/data instructions, and excess MVP/TMA wording.
- Kept core product idea, 100-point prediction model, participant stats, visual style, and no-money boundary.
- Polished opening copy and legal boundary wording before push.
- Updated `vault/QUICK_START.md` and `vault/CODE_MAP.md`.
- Verified: `git diff --check` passed.

## 2026-05-06 — New MVP Brief Documented

- Reviewed `new_brief.md` against current app and vault docs.
- User declared `new_brief.md` canonical MVP brief.
- Recorded decisions in `vault/wiki/architecture/mvp-product-decisions.md`.
- Target prediction model: one user/event prediction with exactly 100 virtual points distributed across 1–3 participants.
- Recorded user vision: minimal Telegram bot/TMA with athlete detail pages and verified tabular stats for all 7 Dygyn disciplines by year/event.
- Updated project vision, roadmap, sprint, resume plan, code map, and quick start.
- Next: implement backend-first brief alignment.

## 2026-05-06 — Compact Vault Mode
- Changed: added `vault/QUICK_START.md`; session start now reads quick context first, deep docs on demand.
- Changed: updated `AGENTS.md`, `master_index.md`, `WORKFLOW.md`, and sprint for token-saving vault workflow.
- Changed: created sibling starter `../empty-template-vault` with compact vault skeleton.
- Verified: template file tree created.
- Next: keep future vault updates terse.


## 2026-05-06 — Vault Initialized

### Done

- Studied `empty-template-vault-rag` vault-first structure.
- Added `vault/` to `dygyn-bet`.
- Added root `AGENTS.md` to enforce vault-first session workflow.
- Migrated current project knowledge from `README.md`, `wiki/`, and code inspection into English vault docs.
- Kept existing Russian `wiki/` as historical/source documentation.

### Verified

- Reviewed template vault files.
- Reviewed existing project README and Russian wiki docs.
- Reviewed main code files under `app/`, `web/`, and `tests/`.
- Reviewed created `vault/` file tree.

### Not Verified

- `pytest` could not run because pytest is not installed in the current Python environment (`No module named pytest`).

### Next

- Replace seeded demo data with verified real Dygyn Games participants/events.
- Validate Telegram auth and Mini App launch with production-like config.
- Add deployment and backup runbook when target is chosen.

## 2026-05-06 — Initial Commit Prepared

### Done

- Prepared first git commit with the FastAPI Telegram Mini App product, docs, tests, Docker files, old wiki, and new vault.

### Verified

- Checked staged candidate files with `git ls-files --others --exclude-standard`.
- Checked that no `.env` or SQLite database files were found under the project root.

### Next

- Push first commit to `origin/main`.

## 2026-05-06 — Three-Pick Voting and Story Sharing

### Done

- Changed event voting from one selected participant to up to three selected participants.
- Changed `POST /api/picks` to accept `player_ids` and replace current user's event picks.
- Changed SQLite pick uniqueness to `UNIQUE(event_id, user_id, player_id)` and added migration for old local DBs.
- Updated frontend selection flow: choose up to three, save once, see selected markers.
- Added sharing actions: native share, copy text, and generated PNG story card for manual Instagram Stories upload.
- Updated bot rules, README, old wiki, vault API/data/frontend docs, code map, and sprint.

### Verified

- Ran `python -m py_compile app/*.py tests/*.py`.
- Ran `node --check web/app.js`.
- Ran `git diff --check`.
- Ran a direct SQLite DB flow script covering three picks, four-pick rejection, event detail, and settlement.
- Ran a direct SQLite migration script for the old `UNIQUE(event_id, user_id)` picks schema.

### Not Verified

- Full `pytest` still not run because project dependencies are not installed in the current Python environment (`fastapi` and `pytest` missing).
- Manual Telegram Mini App and Instagram Stories share flow not tested on device.

### Next

- Install dependencies and run full `python -m pytest`.
- Manually test on mobile Telegram with HTTPS URL.
- Test story-card download/open behavior on iOS and Android.

## 2026-05-06 — VPS Deployment Route Scouted

### Done

- Inspected `iind-vps` in read-only mode.
- Identified existing nginx site for `iindiinda.duckdns.org`.
- Confirmed existing root public folder `/var/www/iind-app/frontend/public` and existing `/api` Laravel route must not be touched.
- Planned safe deployment under `https://iindiinda.duckdns.org/dygyn-bet/` using nginx prefix proxy to local FastAPI port `8010`.
- Updated frontend to support prefix deployment by using relative static paths and deriving API base path from `static/app.js`.
- Added deployment documentation.

### Verified

- Ran `node --check web/app.js`.
- Ran `python -m py_compile app/*.py tests/*.py`.

### Not Verified

- No server files or nginx config were changed yet.
- Production bot token/admin IDs are not configured yet.

### Next

- Get production `BOT_TOKEN` and `ADMIN_IDS`.
- Deploy app to `/opt/dygyn-bet`.
- Add nginx `/dygyn-bet/` reverse proxy location and run `nginx -t`.
- Start systemd service and test public URL.

## 2026-05-06 — Deployed to VPS

### Done

- Copied app to `/opt/dygyn-bet` on `iind-vps`.
- Installed `python3.12-venv` on the VPS.
- Created Python venv and installed requirements.
- Created server-only `.env` with production `WEB_APP_URL`, `ALLOW_DEV_LOGIN=false`, `ENABLE_POLLING=false`, and SQLite path under `/opt/dygyn-bet/data`.
- Created and started `dygyn-bet.service` on port `127.0.0.1:8010`.
- Created and started separate `dygyn-bet-bot.service` for Telegram polling.
- Added nginx `/dygyn-bet/` reverse proxy route without touching existing public folder or root `/api`.

### Verified

- VPS tests: `.venv/bin/python -m pytest` passed: 4 tests.
- `systemctl status dygyn-bet`: active/running.
- `systemctl status dygyn-bet-bot`: active/running.
- API service restart after split polling/API: ~0.2s.
- `nginx -t`: successful.
- Public health: `https://iindiinda.duckdns.org/dygyn-bet/health` returns OK.
- Public HTML and static JS are served under `/dygyn-bet/`.
- Public `/dygyn-bet/api/me` returns expected 401 without Telegram auth.
- Local repository does not contain the bot token (`rg` check).

### Not Verified

- Telegram `/start` button has not been explicitly verified in chat.
- Full mobile QA still needed.
- `ADMIN_IDS` is still empty on the server until the real admin Telegram numeric ID is provided.

### Next

- Add real `ADMIN_IDS` to `/opt/dygyn-bet/.env` and restart service.
- Test bot `/start` in Telegram.
- Test Mini App voting on mobile.

## 2026-05-06 — Dygyn Fan Arena Frontend Pass

### Done

- Added `ref.md` as the root design reference after cleaning launch-phase wording.
- Added canonical English design direction at `vault/wiki/architecture/design-direction.md`.
- Restyled frontend toward Dygyn Fan Arena: dark sports UI, warm gold accent, arena hero, bottom navigation, participant cards, support progress bars, confidence chips, sticky save action.
- Changed stats tab into support statistics plus fan leaderboard.
- Updated frontend and code-map vault docs.

### Verified

- `node --check web/app.js` passed.
- `python -m py_compile app/*.py tests/*.py` passed.
- Local secret/removed-copy search passed.

### Not Verified

- Local `python -m pytest` could not run because pytest is not installed in the current local Python environment.
- Mobile Telegram visual QA not done yet.

### Deployment Follow-Up

- Deployed frontend pass to `/opt/dygyn-bet` on `iind-vps`.
- VPS tests passed: 4 tests.
- Restarted `dygyn-bet.service` and `dygyn-bet-bot.service`; both are active.
- Public health check passed at `/dygyn-bet/health`.
- Public HTML shows `Dygyn Fan Arena` and updated no-money copy.

### Next

- Test layout in Telegram on mobile.
- Add admin-only TMA tab after admin Telegram numeric ID is provided.

## 2026-05-06 — Removed Launch-Phase Product Copy

### Done

- Removed launch-phase wording from user-facing UI, bot messages, README, and project docs.
- Renamed old scope doc to `wiki/01-scope.md`.
- Kept product meaning unchanged: fan predictions, no money.

### Verified

- Local search confirms removed launch-phase wording has no remaining matches.
- Ran Python and JavaScript syntax checks locally.

### Next

- Deploy copy cleanup to VPS.
- Recheck public page and bot copy.

### Deployment Follow-Up

- Deployed cleanup to `/opt/dygyn-bet` on `iind-vps`.
- Removed old renamed scope file from server.
- VPS tests passed: 4 tests.
- Restarted `dygyn-bet.service` and `dygyn-bet-bot.service`; both are active.
- Public health check passed at `/dygyn-bet/health`.
- Server search confirms removed launch-phase wording has no remaining matches.
