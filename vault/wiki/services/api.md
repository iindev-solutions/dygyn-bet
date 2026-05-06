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
- current user's pick;
- results.

### `POST /api/picks`

Creates or updates current user's pick.

Request:

```json
{
  "event_id": 1,
  "player_id": 2,
  "confidence_points": 25
}
```

Rules:

- confidence points are clamped/validated to 1–100;
- event must exist;
- event status must be `open`;
- event `starts_at` must be in the future;
- player must be linked to the event;
- one pick per user per event.

### `GET /api/players`

Returns players with recent history and summary.

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

## Error Behavior

- `401` for invalid/missing Telegram auth.
- `403` for blocked user or missing admin rights.
- `404` for missing event detail.
- `400` for invalid pick/admin operations.
- `429` for rate limit.
