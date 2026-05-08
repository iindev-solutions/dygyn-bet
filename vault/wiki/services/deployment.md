# Deployment Service

## Target VPS

SSH alias: `iind-vps`.

Observed read-only on 2026-05-06:

- Hostname: `naval-tomato.aeza.network`.
- User: `root`.
- OS: Ubuntu Linux.
- Web server: nginx.
- Existing public domain: `iindiinda.duckdns.org`.
- Existing public root: `/var/www/iind-app/frontend/public`.
- Existing Laravel/PHP API route: `/api` mapped to `/var/www/iind-app/backend/public`.
- Existing TLS cert: `/etc/letsencrypt/live/iindiinda.duckdns.org/`.
- Python 3.12 and git are installed.

## Constraint

Do not touch the existing public folder:

- `/var/www/iind-app/frontend/public`

Do not take over root `/` or existing `/api`.

## Current Deployment

Status: deployed on 2026-05-06.

Public URL:

```text
https://iindiinda.duckdns.org/dygyn-bet/
```

Local services:

- API systemd unit: `dygyn-bet.service`
- bot systemd unit: `dygyn-bet-bot.service`
- app path: `/opt/dygyn-bet`
- API bind: `127.0.0.1:8010`
- database: `/opt/dygyn-bet/data/dygyn.sqlite3`
- env file: `/opt/dygyn-bet/.env` with `0600` permissions

Installed VPS package:

- `python3.12-venv`

## Safe Route Plan

Deploy this app under a separate path on the same domain:

```text
https://iindiinda.duckdns.org/dygyn-bet/
```

Use nginx reverse proxy with prefix stripping:

```nginx
location = /dygyn-bet {
    return 301 /dygyn-bet/;
}

location ^~ /dygyn-bet/ {
    proxy_pass http://127.0.0.1:8010/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Run FastAPI locally on `127.0.0.1:8010`.

## App Base Path Support

Frontend static and API paths must be prefix-safe:

- Vue production build uses `VITE_BASE_PATH=/dygyn-bet/`, exposed as `import.meta.env.BASE_URL`.
- Vue API client defaults to `${BASE_URL}api`, so browser calls `/dygyn-bet/api/*`.
- Nginx still strips `/dygyn-bet/` before proxying to FastAPI, so backend receives `/api/*`.
- FastAPI serves Vue assets from `/assets/*` and excludes `/assets/*` from rate limiting.

Legacy rollback: set `FRONTEND_DIR=web` and restart the API service.

## Suggested Server Layout

```text
/opt/dygyn-bet/              # git checkout or copied release
/opt/dygyn-bet/.venv/        # Python venv
/opt/dygyn-bet/web-vue/dist/ # built Vue frontend
/opt/dygyn-bet/data/         # persistent SQLite data
/etc/systemd/system/dygyn-bet.service
```

## Required Production Env

```env
BOT_TOKEN=<stored only on server, do not commit>
WEB_APP_URL=https://iindiinda.duckdns.org/dygyn-bet/
ADMIN_IDS=<comma-separated Telegram numeric IDs>
ALLOW_DEV_LOGIN=false
ENABLE_POLLING=false
DB_PATH=/opt/dygyn-bet/data/dygyn.sqlite3
AUTH_MAX_AGE_SECONDS=86400
SEED_DEMO=false
FRONTEND_DIR=/opt/dygyn-bet/web-vue/dist
BACKUP_DIR=/opt/dygyn-bet/backups
BACKUP_KEEP=48
```

Current note: `ADMIN_IDS` still needs the real admin Telegram numeric ID.

## Vue Frontend Build

Before restarting the API after Vue migration:

```bash
cd /opt/dygyn-bet/web-vue
npm ci
npm run build
```

Build must pass typecheck and the initial JS gzip budget (`<=150KB`). Current branch build: 41.1KB gzip initial JS.

## Deployment Checks

Completed on 2026-05-06:

- `.venv/bin/python -m pytest` on VPS: 4 passed.
- `systemctl status dygyn-bet`: active/running.
- `systemctl status dygyn-bet-bot`: active/running.
- API service restart after split polling/API: ~0.2s.
- `nginx -t`: successful.
- `curl https://iindiinda.duckdns.org/dygyn-bet/health`: returns `ok`, app version, DB counts, and disk free MB.
- `curl https://iindiinda.duckdns.org/dygyn-bet/`: HTML served.
- Legacy check before Vue cutover: `curl -I https://iindiinda.duckdns.org/dygyn-bet/static/app.js`: 200.
- Vue check after cutover: `curl -I https://iindiinda.duckdns.org/dygyn-bet/assets/<built-js-file>.js`: 200.
- `curl https://iindiinda.duckdns.org/dygyn-bet/api/me` without Telegram auth: 401 expected.

Still required:

- Explicitly confirm Telegram bot `/start` opens the Mini App button.
- Full mobile Telegram Mini App QA.
- Add real `ADMIN_IDS`.
