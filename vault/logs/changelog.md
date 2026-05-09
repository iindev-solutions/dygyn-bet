# Changelog

## 2026-05-09 — Browser Admin Direct Route Fix

- Fixed local browser `/#/admin` direct route to load admin session cookie via `/api/me` before showing missing-rights state.
- Added Vue unit test covering direct admin route session hydration.
- Verified: red/green `npm run test:unit -- src/views/AdminView.test.ts`; `npm run test:unit` (5 passed); `npm run typecheck`; `npm run lint`; `npm run format`; `npm run build` (bundle 42.3KB gzip initial JS).
- Deployed static Vue dist to VPS after dist backup `/opt/dygyn-bet/web-vue/dist.bak-20260509-071037`; services active; public health OK; admin asset returns 200 and contains session rehydrate code.

## 2026-05-08 — Browser Admin Login

- Added browser admin auth: username/password login at `/#/admin-login`, hashed admin credentials in SQLite, HttpOnly admin session cookie, and logout.
- Backend accepts Telegram initData or valid web-admin session cookie for admin APIs; legacy Telegram admin still works.
- Added optional env seeding: `ADMIN_WEB_USERNAME`, `ADMIN_WEB_PASSWORD`, `ADMIN_WEB_SESSION_HOURS`.
- Verified locally: `npm run format`; `npm run lint`; `npm run test:unit` (3 passed); `npm run build`; `python -m pytest` (18 passed); bundle budget 42.0KB gzip initial JS.
- Deployed to VPS after DB backup `/opt/dygyn-bet/backups/dygyn.sqlite3.20260508-150605.bak`; set `ADMIN_WEB_USERNAME/PASSWORD`; VPS `pytest` 18 passed; services active; public login smoke succeeded with admin cookie and `/api/me.is_admin=true`.
