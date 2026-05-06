# Roadmap

## Phase 1 — Launch Readiness

- Keep vault-first project memory current.
- Run locally with dev login.
- Configure real Telegram bot token and HTTPS URL.
- Replace demo participants/events with verified Dygyn Games data.
- Add source URLs for every real history record.
- Test auth, event list, three-pick creation/update, stats, player list, leaderboard.
- Test admin APIs for player/event/result management.

## Phase 2 — Content and Admin Operations

- Build a simple admin page or admin scripts.
- Add CSV import for players/history/events.
- Add participant photos.
- Add stricter source tracking.
- Add notification before prediction close.

## Phase 3 — Social Mechanics

- Improve Instagram Stories sharing after mobile tests.
- Share prediction to Telegram.
- Friend or region leaderboards.
- Reactions or comments.
- Public page showing fan support distribution.

## Phase 4 — Reliability

- Decide deployment target.
- Add database backups.
- Add monitoring/error logs.
- Move SQLite to PostgreSQL if usage grows.
- Move in-memory rate limit to Redis.
- Move bot polling to webhook.
- Add admin audit log.

## Money Discussion

Only after legal decision. Money is not a small feature extension; it changes product, compliance, data model, auth requirements, and operations.
