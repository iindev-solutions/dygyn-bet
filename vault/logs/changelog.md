# Changelog

## 2026-05-07 — Redesign Preview Skeletons

- Added static redesign preview with three mobile skeleton directions: ceremonial entry, sports grid, ornament minimalism.
- Added provided Dygyn logo/photo and Yakut ornament assets under `web/assets/` for preview use.
- Kept production Mini App unchanged while exploring visual direction.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; `git diff --check`.
- Deployment follow-up: deployed preview to VPS; VPS `pytest` 9 passed; services active; preview HTML/CSS/assets return 200.

## 2026-05-07 — Allocation Number Input

- Added numeric input beside each allocation slider so users can type confidence points directly.
- Kept slider control and 100-point validation unchanged.
- Verified: `node --check web/app.js`; `git diff --check`.
- Deployment follow-up: deployed to VPS; VPS `pytest` 9 passed; services active; health OK; public static JS contains `allocation-number`.

## 2026-05-07 — Top-2 Voting Reset

- Changed voting model to maximum two participants per event vote.
- Removed equal three-way special case; backend now requires 1–2 participants and exactly 100 total confidence points.
- Updated TMA allocation UI, bot rules, README, brief, design guide, tests, and vault/API/frontend/data-model docs.
- Production cleanup requested: clear votes plus result/live-result tables after DB backup during deploy.
- Verified locally: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; top-2 DB smoke; `design.md lint DESIGN.md`. Full local pytest still unavailable: `No module named pytest`.
- Deployment follow-up: deployed to VPS; VPS `pytest` 9 passed; services active; DB backed up; cleared `picks`, `results`, `event_standings`, `event_discipline_results`, `event_days`; event status is open; public static JS uses `MAX_PICKS = 2`.

## 2026-05-07 — Equal Three-Way Vote Split

- Changed equal split for three selected participants from `34/33/33` to `33/33/33`.
- Backend now accepts exact `100` totals or equal `33/33/33`; arbitrary 99-point totals still fail.
- Startup migration converts old equal `34/33/33` vote rows to `33/33/33` and adjusts awarded `34` to `33`.
- Rating award for a three-way equal vote now gives winner `33`; the 1-point remainder is not awarded.
- Updated TMA copy, bot rule text, README, and vault/API/frontend/data-model docs.
- Verified locally: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; custom DB smoke for `33/33/33` award/migration passed; `design.md lint DESIGN.md`; `git diff --check`. Full local pytest still unavailable: `No module named pytest`.
- Deployment follow-up: VPS DB backed up; VPS `pytest` 10 passed; services active; public static JS contains `33/33/33`; old `34/33/33` groups migrated from 1 to 0.

## 2026-05-07 — Removed Old Voting Branding

- Replaced old English sports-brand naming with `Игры Дыгына — голосование` across UI, docs, and design guide.
- Removed old sports-brand wording from current user-facing copy; product positioning is now simple participant voting.
- Renamed event hero CSS/function references away from arena terminology.
- Updated README, bot copy, DESIGN.md, vault docs, old wiki copy, and visible TMA text.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; `design.md lint DESIGN.md`; `git diff --check`; branding search has no old-brand matches.
- Deployment follow-up: deployed to VPS; VPS `pytest` 8 passed; services active; public HTML/static use `Игры Дыгына — голосование`; server old-brand search passed.

## 2026-05-06 — DESIGN.md Added

- Added root `DESIGN.md` following Google Labs `design.md` format: YAML design tokens plus markdown rationale.
- Captured Игры Дыгына — голосование palette, typography, layout, components, and do/don't rules.
- Updated quick start and code map.
- Verified: `design.md lint DESIGN.md` passed with 0 errors/0 warnings; `git diff --check` passed.

## 2026-05-06 — VPS Admin ID Configured

- Added user Telegram numeric ID to VPS `ADMIN_IDS` in `/opt/dygyn-bet/.env`.
- Restarted `dygyn-bet.service` and `dygyn-bet-bot.service`; both active.
- Verified public health OK and `ADMIN_IDS` count is 1.
- Next: reopen Mini App in Telegram and QA admin tab.

## 2026-05-06 — Admin Live Results Flow

- Added live two-day result tables: event days, event discipline results, and event standings.
- Added public `GET /api/events/{event_id}/results` and `GET /api/disciplines`.
- Added admin APIs for Day 1/Day 2 discipline results, standings, and final finish/award.
- Added admin-only TMA tab visible via `ADMIN_IDS`; supports entering discipline results, standings, and final winner.
- Public event detail now renders live results/standings when present.
- Added DB flow test for live results and finish scoring.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; direct live admin DB smoke; `git diff --check`.
- Not verified: full `python -m pytest` because local environment lacks pytest.
- Deployment follow-up: deployed to VPS; DB backed up; VPS `pytest` 8 passed; services active; public health and static JS OK.
- Note: VPS `ADMIN_IDS` is empty, so admin tab is not visible until real Telegram numeric ID is configured.

## 2026-05-06 — VPS Deploy with Imported Data

- Deployed latest app to `/opt/dygyn-bet` on `iind-vps`.
- Backed up SQLite DB under `/opt/dygyn-bet/backups/` before import.
- Fixed old-schema migration bug by moving extension indexes after column migrations; added regression test.
- Applied `data/import/dygyn_2026/` to production DB.
- Production DB now has 1 event, 16 active participants, 7 disciplines, 16 event participants, and 126 discipline result rows.
- Restarted `dygyn-bet.service` and `dygyn-bet-bot.service`; both active.
- Verified on VPS: import validation, import apply, final `pytest` 7 passed, services active, public health OK, static JS 200, DB counts OK.
- Next: user QA inside Telegram bot/Mini App.

## 2026-05-06 — 100-Point Prediction Allocation

- Changed voting model to enforce exactly 100 confidence points across 1–3 participants per user/event.
- Added canonical `POST /api/events/{event_id}/prediction` endpoint; kept legacy `/api/picks` with same 100-point validation.
- Added `closes_at` fallback validation: voting closes at `closes_at` or `starts_at`.
- Updated event totals and leaderboard counts to count logical votes/users instead of pick rows.
- Updated frontend voting UI to allocate 100 points, rebalance evenly, and save only when total is 100.
- Updated tests and vault docs.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; direct 100-point DB flow smoke; `git diff --check`.
- Not verified: full `python -m pytest` because local environment lacks pytest.

## 2026-05-06 — Participant Discipline Tables Exposed

- Added `get_player()` DB detail with history, summary, and discipline results joined to discipline metadata.
- Added `GET /api/players/{player_id}` and `/api/participants/{player_id}` alias.
- Updated Players tab: participant cards open detail view with profile, strengths, prior Dygyn note, and discipline-result tables.
- Added styles for photos, profile detail, and result tables.
- Updated import test expectations for player detail.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `node --check web/app.js`; temp DB player-detail smoke; `git diff --check`.
- Not verified: full `python -m pytest` because local environment lacks pytest.

## 2026-05-06 — Import Validator and Importer

- Added SQLite schema support for sources, import metadata, disciplines, and player discipline results.
- Added `app/import_data.py` to validate/import `data/import/dygyn_2026/`.
- Added `scripts/import_dygyn_data.py` CLI with validate/apply modes.
- Import apply purges seeded demo rows before loading real data.
- Added import tests for pack validation and temp-DB import.
- Public player list now hides historical-only imported players.
- Verified: `python -m py_compile app/*.py tests/*.py scripts/import_dygyn_data.py`; `python scripts/import_dygyn_data.py --json`; temp DB import smoke.
- Not verified: full `python -m pytest` because local environment lacks pytest.

## 2026-05-06 — Import Data Pack Reviewed

- Reviewed CSV/XLSX data pack and renamed folder to `data/import/dygyn_2026/`.
- Data includes 7 disciplines, one 2026 event, 16 qualified participants, 16 event links, 2025 overall results, 112 discipline result rows, 14 partial 2026 qualifier result rows, and 9 sources.
- Validation found no duplicate core keys, no broken source/discipline/event/participant references, and 2025 overall sums match discipline-place totals.
- Noted import risks: current DB still demo, 2025 result rows use names not participant IDs, `ё/е` and alias matching needed, raw result coverage is partial, and some qualifier result values are text/range values.
- Recorded admin panel as mandatory for imports, events, participants, Day 1/Day 2 results, standings, and final finish.
- Updated `vault/QUICK_START.md`, `vault/CODE_MAP.md`, sprint, MVP decisions, and API notes.
- Verified: CSV validation script and `git diff --check` passed.

## 2026-05-06 — Two-Day Results Requirement

- Recorded that Dygyn Games run across two days.
- Added target support for Day 1, Day 2, overall/final results, provisional/official state, and final winners.
- Clarified rating-score awarding should happen only after final official winner.
- Updated README, quick start, MVP decisions, data-model plan, and planned API notes.
- Verified: `git diff --check` passed.

## 2026-05-06 — README Rewrite

- Rewrote `README.md` again as a short product-only description.
- Removed local setup, admin curl examples, implementation status, source/data instructions, and excess MVP/TMA wording.
- Kept core product idea, 100-point vote model, participant stats, visual style, and no-money boundary.
- Polished opening copy and legal boundary wording before push.
- Updated `vault/QUICK_START.md` and `vault/CODE_MAP.md`.
- Verified: `git diff --check` passed.

## 2026-05-06 — New MVP Brief Documented

- Reviewed `new_brief.md` against current app and vault docs.
- User declared `new_brief.md` canonical MVP brief.
- Recorded decisions in `vault/wiki/architecture/mvp-product-decisions.md`.
- Target voting model: one user/event vote with exactly 100 virtual points distributed across 1–3 participants.
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

## 2026-05-06 — Игры Дыгына — голосование Frontend Pass

### Done

- Added `ref.md` as the root design reference after cleaning launch-phase wording.
- Added canonical English design direction at `vault/wiki/architecture/design-direction.md`.
- Restyled frontend toward Игры Дыгына — голосование: dark sports UI, warm gold accent, event hero, bottom navigation, participant cards, support progress bars, confidence chips, sticky save action.
- Changed stats tab into support statistics plus leaderboard.
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
- Public HTML shows `Игры Дыгына — голосование` and updated no-money copy.

### Next

- Test layout in Telegram on mobile.
- Add admin-only TMA tab after admin Telegram numeric ID is provided.

## 2026-05-06 — Removed Launch-Phase Product Copy

### Done

- Removed launch-phase wording from user-facing UI, bot messages, README, and project docs.
- Renamed old scope doc to `wiki/01-scope.md`.
- Kept product meaning unchanged: predictions, no money.

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
