# Auth Flow

## Current Mode

Telegram Mini App authentication through signed `Telegram.WebApp.initData`.

## Client Behavior

- `web/app.js` reads `window.Telegram?.WebApp`.
- Calls `tg.ready()` and `tg.expand()` when available.
- Sends raw `tg.initData` as HTTP header:

```http
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

The client must not send or rely on `initDataUnsafe` as trusted identity.

## Backend Validation

Implemented in `app/telegram_auth.py`:

1. Parse raw initData query string.
2. Remove received `hash`.
3. Build Telegram data check string from sorted key/value pairs.
4. Derive secret key with HMAC-SHA256 using key `WebAppData` and bot token.
5. Compute expected hash.
6. Compare with received hash using `hmac.compare_digest`.
7. Validate `auth_date` against `AUTH_MAX_AGE_SECONDS`.
8. Parse Telegram user JSON.
9. Upsert user by Telegram ID.

## User Model

`TelegramUser` fields:

- `id`
- `first_name`
- `last_name`
- `username`
- `language_code`

Backend stores/upserts these in `users` table.

## Local Dev Login

If no `X-Telegram-Init-Data` header is present and `ALLOW_DEV_LOGIN=true`, backend uses a fixed dev user:

- Telegram ID: `1000001`
- first name: `Dev`
- last name: `User`
- username: `dev_user`

This user is treated as admin only when `ALLOW_DEV_LOGIN=true`.

## Production Requirements

- Set `BOT_TOKEN` to real BotFather token.
- Set `ALLOW_DEV_LOGIN=false`.
- Set `ADMIN_IDS` to real Telegram numeric IDs.
- Serve over HTTPS.
- Set `WEB_APP_URL` to the public HTTPS Mini App URL.
- Keep `AUTH_MAX_AGE_SECONDS` finite unless there is a deliberate security decision.

## Failure Modes

Backend returns `401` for:

- missing initData when dev login is disabled;
- missing bot token;
- missing hash;
- invalid signature;
- missing or invalid auth date;
- expired auth date;
- missing Telegram user object.

Backend returns `403` when stored user has `is_blocked` or lacks admin rights.
