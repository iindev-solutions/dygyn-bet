# Data Model

SQLite schema lives in `app/db.py` as `SCHEMA`.

## `users`

Telegram users.

Important fields:

- `telegram_id` — unique Telegram account ID; main anti-abuse key.
- `username`, `first_name`, `last_name`, `language_code` — refreshed on each login.
- `is_blocked` — manual block flag.
- `created_at`, `last_seen_at` — timestamps.

## `players`

Dygyn Games participants/athletes.

Fields:

- `name` — required participant name.
- `region` — city/ulus/region.
- `bio` — short profile.
- `avatar_url` — optional image URL for future use.
- `is_active` — manual active flag.
- `created_at`.

## `events`

Prediction/voting events.

Fields:

- `title` — event name.
- `description`.
- `starts_at` — ISO timestamp.
- `status` — `draft`, `open`, `locked`, or `settled`.
- `created_at`.

## `event_participants`

Many-to-many link between events and players.

Primary key:

- `(event_id, player_id)`.

## `picks`

User predictions/votes.

Fields:

- `event_id`.
- `user_id`.
- `player_id`.
- `confidence_points` — virtual points from 1 to 100.
- `awarded_points` — fan points after settlement.
- `created_at`, `updated_at`.

Constraint:

- `UNIQUE(event_id, user_id)` — one pick per user per event.

## `results`

Event final results.

Fields:

- `event_id`.
- `player_id`.
- `place` — required, must be at least 1.
- `score` — optional numeric result.
- `prize_text` — display-only text if needed.
- `created_at`.

Constraint:

- `UNIQUE(event_id, player_id)`.

## `player_history`

Historical performance records for participants.

Fields:

- `player_id`.
- `year`.
- `competition`.
- `place`.
- `score`.
- `notes`.
- `source_url` — required in practice for real data provenance.
- `created_at`.

## Demo Data

`seed_demo()` creates four demo participants, one open demo event, and demo history when the database has no players.

Before public launch, demo names and demo history must be replaced with verified data and source URLs.
