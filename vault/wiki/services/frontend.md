# Frontend Service

## Responsibilities

- Provide Telegram Mini App user interface through Vue 3.
- Initialize Telegram WebApp SDK with a delayed-load guard.
- Send raw Telegram initData to backend.
- Render events, participants, picks, statistics, player history, discipline-result tables, rules, and leaderboard.

## Main Files

- `web-vue/src/App.vue` — app shell, hero, bottom tabs, boot/error/toast UI.
- `web-vue/src/views/EventsView.vue` — games tab, participant selection, 100-point allocation, share/story actions, live results.
- `web-vue/src/views/StatsView.vue` — support stats and fan leaderboard.
- `web-vue/src/views/PlayersView.vue` — photo-forward player list and detail discipline tables.
- `web-vue/src/views/AdminView.vue` — admin result/standing/final forms.
- `web-vue/src/composables/useTelegramInit.ts` — waits for late `window.Telegram.WebApp`, then calls `ready()`/`expand()`.
- `web-vue/src/api/client.ts` — typed fetch wrapper; API base uses `import.meta.env.BASE_URL` or `VITE_API_BASE`.
- `web-vue/src/assets/styles/main.css` — current A1 CSS ported from legacy `web/styles.css`.
- `web/` — legacy vanilla frontend retained only for rollback via `FRONTEND_DIR=web`.

## Tabs

- Games — event hero, event list, event detail, 1–2 participant choices, 100-point allocation controls, share actions.
- Support — support statistics and leaderboard.
- Players — photo-forward participant cards with origin/short description, plus detail view for profile fields, title/debut/history badges, sources, performance history, and discipline-result tables.
- Admin — live operations: Day 1/Day 2 discipline results, standings, finish event. Access works via Telegram `ADMIN_IDS` or browser login at `/#/admin-login`.
- Rules — product rules and no-money notice.

## Auth Behavior

### Telegram auth

`useTelegramInit()` polls for `window.Telegram?.WebApp` before the first API load. When found, it calls:

```ts
webApp.ready()
webApp.expand()
```

This prevents real-device races where the Telegram SDK object appears after Vue mount.

For API calls, `src/api/client.ts` waits for this guard, reads `webApp.initData`, and sends:

```http
X-Telegram-Init-Data: <raw initData>
```

### Browser admin auth

Browser admin login lives at:

```text
https://iindiinda.duckdns.org/dygyn-bet/#/admin-login
```

Backend seeds/updates a hashed SQLite admin row from server env:

```env
ADMIN_WEB_USERNAME=<admin login>
ADMIN_WEB_PASSWORD=<admin password>
ADMIN_WEB_SESSION_HOURS=12
```

Login creates an HttpOnly `dygyn_admin_session` cookie. Admin APIs accept either Telegram initData from `ADMIN_IDS` or this session cookie. Logout clears the cookie.

## API Wrapper

`api(path, options)`:

- builds API base from `import.meta.env.BASE_URL` (`/dygyn-bet/` in production) or `VITE_API_BASE`;
- sets `Content-Type: application/json` for JSON bodies;
- waits for Telegram SDK init guard unless a browser-admin endpoint opts out;
- adds Telegram initData header if available;
- parses JSON response;
- throws normalized `ApiError` from `json.detail` when response is not OK.

## UI Safety

Dynamic text is rendered through Vue text bindings. `v-html` is disallowed by ESLint.

## Visual Direction

Current style follows `vault/wiki/architecture/design-direction.md`:

- dark sports UI;
- warm gold accent;
- card-first layout;
- progress bars for support statistics;
- strong sticky save action;
- no casino/bookmaker visual language.

## Product Copy Rule

Frontend must keep no-money language visible. Current notice:

- no monetary bets;
- only votes and virtual confidence points.

Avoid adding betting, deposit, withdrawal, odds, payout, or prize wording without legal approval.

## Instagram Stories Sharing

Direct Instagram Stories posting is not reliable from a Telegram Mini App web context. The product provides:

- native Web Share when available;
- copy-to-clipboard share text;
- generated PNG story card for manual Instagram Stories upload.

Current Vue story card includes simple fan copy (`В этом году я голосую за`), selected participant photo(s), confidence points, name, origin/region/ulus, and CTA `Заходи и голосуй за своего фаворита` plus `@dygyn_games_bet_bot`. Images are loaded through the same-origin known-participant avatar endpoint to avoid canvas/CORS export failures; initials are used as fallback. The card avoids showing the public duckdns URL; the frontend tries native file sharing for the PNG first, then falls back to download plus Instagram Stories instructions.

## Vue Build and Bundle Check

```bash
cd web-vue
npm ci
npm run build        # production /dygyn-bet/ base
npm run build:local  # local FastAPI root base
```

Build writes `dist/bundle-stats.html` via `rollup-plugin-visualizer` and enforces initial JS gzip budget <=150KB. Latest local build on 2026-05-07: 41.1KB gzip initial JS.

## Manual Smoke Check

1. For local FastAPI root, build Vue with `cd web-vue && npm run build:local`.
2. Run backend with `ALLOW_DEV_LOGIN=true` and `FRONTEND_DIR=./web-vue/dist`.
3. Confirm user line loads.
4. Confirm event hero card renders.
5. Select event.
6. Pick 1–2 participants.
7. Distribute 100 confidence points.
8. Save the vote through the sticky save action.
9. Confirm toast and updated statistics.
10. If admin, open Admin tab and test a provisional result/standing on a non-production DB first.
11. Copy share text or download the story card.
12. Open support tab.
13. Open players tab.
14. Open rules tab and verify no-money warning.
15. Repeat inside Telegram with real HTTPS URL and bot button; specifically watch Telegram SDK init/auth race.
