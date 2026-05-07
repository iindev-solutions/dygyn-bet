# Anti-Abuse

## Current Protections

1. Telegram initData HMAC validation.
2. Maximum two picks per event per user enforced in application logic.
3. One row per selected participant enforced by `UNIQUE(event_id, user_id, player_id)`.
4. Event start-time lock: if `starts_at` is in the past, `set_picks()` changes event status to `locked` and rejects the pick.
5. Event statuses: `draft`, `open`, `locked`, `settled`.
5. In-memory rate limit in FastAPI middleware.
6. Manual user block field: `users.is_blocked`.
7. Admin APIs require Telegram ID from `ADMIN_IDS`, except local dev admin under `ALLOW_DEV_LOGIN=true`.

## Current Rate Limit

Configured through env:

- `RATE_LIMIT_WINDOW_SECONDS` default: `60`.
- `RATE_LIMIT_MAX_REQUESTS` default: `90`.

Key:

- `X-Telegram-Init-Data` header when present;
- otherwise request client IP;
- static files are skipped.

Limit is in memory and resets on process restart. It is not multi-instance safe.

## Before Public Launch

Add or decide:

- Redis-backed rate limit if running more than one process/instance.
- Admin audit log: who created players/events/history/results.
- Suspicious activity logs: many new accounts, rapid pick changes, request bursts.
- Optional rule: prevent pick changes N minutes before start.
- Optional Telegram channel/chat membership check if access should be restricted to a community.
- Backups for SQLite or migration to PostgreSQL.

## Telegram ID Limitation

Telegram ID is not proof of real-world identity. One person can theoretically use several Telegram accounts. This is acceptable for voting. It is not acceptable for real-money flows, which would require KYC, age checks, and legal infrastructure.
