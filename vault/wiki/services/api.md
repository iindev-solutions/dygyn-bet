# API Service

Base service: FastAPI in `app/main.py`.

## Auth Header

All user/admin APIs except `/` and `/health` require:

```http
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

Local exception: when `ALLOW_DEV_LOGIN=true`, browser requests without this header use the fixed dev user.

## Public Endpoints

### `GET /`

Serves `web/index.html`.

### `GET /health`

Returns app version plus DB and disk checks:

```json
{"ok": true, "version": "0.1.0", "db": {"ok": true, "players": 16, "events": 1}, "disk_free_mb": 12345}
```

## User Endpoints

### `GET /api/me`

Returns current user:

```json
{"user": {}}
```

### `GET /api/events`

Returns event list with participant and pick counts:

```json
{"events": []}
```

### `GET /api/events/{event_id}`

Returns detailed event with:

- participants;
- pick counts;
- confidence sums;
- totals;
- current user's picks;
- results.

### `POST /api/events/{event_id}/prediction`

Canonical vote endpoint.

Request:

```json
{
  "items": [
    {"participant_id": 2, "confidence_points": 60},
    {"participant_id": 3, "confidence_points": 40}
  ]
}
```

Rules:

- one vote per user/event;
- vote contains 1–2 participants;
- confidence points must be positive and sum to exactly 100;
- event must exist;
- event status must be `open`;
- current time must be before event `closes_at` or fallback `starts_at`;
- every selected player must be linked to the event;
- backend stores one row per selected participant with `UNIQUE(event_id, user_id, player_id)`.

### `POST /api/picks`

Legacy-compatible endpoint. Prefer `/api/events/{event_id}/prediction` for new code. It accepts either `allocations` or old `player_ids/confidence_points`, and uses the same 100-point validation.

### `GET /api/players`

Returns active players with recent history and summary. Historical-only imported players are hidden from this public list for now.

### `GET /api/players/{player_id}`

Returns participant profile detail with:

- imported profile fields;
- recent history;
- summary;
- discipline results joined with discipline metadata.

### `GET /api/participants/{player_id}`

Alias for player detail, matching the canonical brief wording.

### `GET /api/participants/{player_id}/avatar`

Public same-origin avatar proxy for known participant photos used by the PNG story-card canvas. It only fetches the stored `avatar_url` for that participant, checks image content type/size, and returns a cacheable image response.

### `GET /api/events/{event_id}/results`

Return Day 1, Day 2, overall/final standings, discipline results, final winners, and last updated time.

### `GET /api/disciplines`

Returns seven Dygyn disciplines with display metadata.

### `GET /api/leaderboard`

Returns top 100 users ordered by rating score, correct picks, and pick count.

### `POST /api/analytics`

Records an allowlisted product analytics event. Requires normal user auth but stores no Telegram ID, username, IP, or raw user identity in the analytics row.

Allowed `event_name` values:

- `app_open`
- `rating_open`
- `rules_open`
- `participant_detail_open`
- `vote_save`
- `png_share`

Request:

```json
{
  "event_name": "vote_save",
  "anonymous_id": "client-random-id",
  "path": "/events",
  "metadata": {"event_id": 1, "picks": 2}
}
```

Stored fields are sanitized: hashed anonymous ID, path without query, allowlisted metadata only, hashed user agent.

## Admin Endpoints

Admin means browser admin session cookie, current Telegram ID in `ADMIN_IDS`, or local dev admin. TMA hides admin navigation and redirects `/#/admin*` away when Telegram initData exists; browser admin login remains at `/#/admin-login`. Admin mutations are written to `admin_audit_logs`. Admin `source_url` fields accept only empty, `http://`, or `https://` values.

### `GET /api/admin/analytics`

Returns aggregate analytics for admin dashboard.

Query:

```http
/api/admin/analytics?days=14
```

Response shape:

```json
{
  "analytics": {
    "days": 14,
    "since": "2026-05-01",
    "daily": [{"day": "2026-05-09", "count": 12, "unique_count": 5, "events": {"app_open": 5}}],
    "events": [{"event_name": "app_open", "count": 5, "unique_count": 5}],
    "top_paths": [{"path": "/events", "count": 7}]
  }
}
```

### `POST /api/admin/players`

Create player.

```json
{
  "name": "Participant Name",
  "region": "Yakutsk",
  "bio": "Short bio",
  "avatar_url": "https://..."
}
```

### `POST /api/admin/players/{player_id}/history`

Add player history.

```json
{
  "year": 2025,
  "competition": "Dygyn Games",
  "place": 1,
  "score": 42,
  "notes": "Verified source",
  "source_url": "https://..."
}
```

### `POST /api/admin/events`

Create event and attach participants.

```json
{
  "title": "Final",
  "starts_at": "2026-06-27T09:00:00+00:00",
  "description": "Event description",
  "player_ids": [1, 2, 3]
}
```

### `POST /api/admin/events/{event_id}/discipline-results`

Upsert per-athlete discipline result for Day 1 or Day 2.

```json
{
  "day_number": 1,
  "participant_id": 1,
  "discipline_id": "run_400m",
  "result_text": "54.00",
  "result_value": 54.0,
  "result_unit": "seconds",
  "place": 1,
  "points": 1,
  "status": "provisional"
}
```

### `POST /api/admin/events/{event_id}/standings`

Upsert Day 1, Day 2, or overall/final standings row. `day_number=0` means overall/final.

```json
{
  "day_number": 0,
  "participant_id": 1,
  "place": 1,
  "total_points": 30,
  "is_winner": true,
  "status": "official"
}
```

### `POST /api/admin/events/{event_id}/finish`

Set official winner, mark event settled, and award rating points. Uses a SQLite write lock and refuses already-settled events.

```json
{"winner_participant_id": 1}
```

### `POST /api/admin/events/{event_id}/settle`

Legacy final result endpoint. Prefer `/finish` for the canonical live-results flow. Requires exactly one first-place winner, validates event participants, uses a SQLite write lock, and refuses already-settled events.

## Import CLI

`python scripts/import_dygyn_data.py --json` validates `data/import/dygyn_2026/`.

`python scripts/import_dygyn_data.py --apply --db <sqlite-path>` imports the pack into SQLite.

Imported data:

- sources;
- disciplines;
- 2026 participants and event links;
- 2025 overall history;
- 2025 discipline results;
- partial 2026 qualifier results.

## Admin Panel

Admin panel UI is browser-first at `/#/admin-login`. Admin API accepts a browser admin session cookie or Telegram initData from a user in `ADMIN_IDS`.

Current admin actions:

- enter/update Day 1 and Day 2 discipline results;
- publish Day 1, Day 2, or overall/final standings;
- finish event and award rating points.

Still planned:

- validate/import CSV data pack from UI;
- create/update events and participants;
- attach participants to events.

## Error Behavior

- `401` for invalid/missing Telegram auth.
- `403` for blocked user or missing admin rights.
- `404` for missing event detail.
- `400` for invalid pick/admin operations.
- `429` for rate limit.
