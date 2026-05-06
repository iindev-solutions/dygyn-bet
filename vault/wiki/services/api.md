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

Returns:

```json
{"ok": true, "version": "0.1.0"}
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

Canonical prediction endpoint.

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

- one prediction per user/event;
- prediction contains 1–3 participants;
- confidence points must be positive and sum to exactly 100;
- event must exist;
- event status must be `open`;
- current time must be before event `closes_at` or fallback `starts_at`;
- every selected player must be linked to the event;
- backend stores one row per selected participant with `UNIQUE(event_id, user_id, player_id)`.

### `POST /api/picks`

Legacy-compatible endpoint. Prefer `/api/events/{event_id}/prediction` for new code. It accepts either `allocations` or old `player_ids/confidence_points`, but still enforces the 100-point total.

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

### `GET /api/leaderboard`

Returns top 100 users ordered by fan score, correct picks, and pick count.

## Admin Endpoints

Admin means current Telegram ID is listed in `ADMIN_IDS`, or local dev admin is active.

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

### `POST /api/admin/events/{event_id}/settle`

Set results and award fan points to users who picked first place.

```json
{
  "results": [
    {"player_id": 1, "place": 1, "score": 42},
    {"player_id": 2, "place": 2, "score": 39}
  ]
}
```

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

## Planned Admin Panel

Admin panel is required and should live inside the Telegram Mini App behind `ADMIN_IDS` access.

MVP admin actions:

- validate/import CSV data pack;
- create/update events and participants;
- attach participants to events;
- enter/update Day 1 and Day 2 discipline results;
- publish provisional/official standings;
- finish event and award fan points.

## Planned Result Endpoints

Not implemented yet. Needed for two-day Dygyn Games result updates.

### `GET /api/events/{event_id}/results`

Return Day 1, Day 2, overall standings, final winners, status, and last updated time.

Query options:

```http
?day=1
?day=2
?phase=final
```

### `POST /api/admin/events/{event_id}/discipline-results`

Admin upserts per-athlete discipline results for Day 1 or Day 2.

### `POST /api/admin/events/{event_id}/standings`

Admin publishes provisional or official standings after Day 1, Day 2, or final finish.

### `POST /api/admin/events/{event_id}/finish`

Admin marks final official winners and triggers fan-score awarding.

## Error Behavior

- `401` for invalid/missing Telegram auth.
- `403` for blocked user or missing admin rights.
- `404` for missing event detail.
- `400` for invalid pick/admin operations.
- `429` for rate limit.
