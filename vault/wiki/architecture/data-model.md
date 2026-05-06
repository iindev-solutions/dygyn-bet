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

User predictions/votes. A user can select up to three participants per event.

Fields:

- `event_id`.
- `user_id`.
- `player_id`.
- `confidence_points` — virtual points from 1 to 100.
- `awarded_points` — fan points after settlement.
- `created_at`, `updated_at`.

Constraint:

- `UNIQUE(event_id, user_id, player_id)` — one row per selected participant.

Application rule:

- maximum three selected participants per user per event.

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

## Planned Canonical Result Model

Not implemented yet. Needed for `new_brief.md` alignment and two-day Dygyn Games updates.

### `disciplines`

Seven Dygyn disciplines.

Fields:

- `code`, `name`, `unit`, `sort_order`.
- `lower_is_better` — e.g. time disciplines rank lower values higher.

### `event_days`

Two-day competition structure.

Fields:

- `event_id`.
- `day_number` — `1` or `2`.
- `title`, `starts_at`, `status`.

### `event_discipline_results`

Per-athlete results entered during/after each day.

Fields:

- `event_id`, `event_day_id`, `player_id`, `discipline_id`.
- `result_text` — display value, e.g. `5:40`, `50 reps`.
- `result_value` — sortable numeric value, e.g. seconds/reps.
- `place`, `points`.
- `status` — `provisional` or `official`.
- `source_url`, `notes`, `updated_at`.

### `event_standings`

Overall/day standings and final winners.

Fields:

- `event_id`, `day_number` nullable for final/overall.
- `player_id`, `place`, `total_points`, `is_winner`.
- `status` — `provisional` or `official`.
- `source_url`, `updated_at`.

Fan leaderboard scoring should use only final official standings.

## Demo Data

`seed_demo()` creates four demo participants, one open demo event, and demo history when the database has no players.

Before public launch, demo names and demo history must be replaced with verified data and source URLs.
