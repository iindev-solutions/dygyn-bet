# Frontend Service

## Responsibilities

- Provide Telegram Mini App UI through Vue 3.
- Initialize Telegram WebApp SDK with delayed-load guard.
- Send raw Telegram initData to backend for user APIs.
- Render main voting flow, support stats, leaderboard, athlete grid/detail, rules/privacy copy, and browser-only admin tools.
- Emit first-party analytics events without storing Telegram identity in analytics rows.

## Main Files

- `web-vue/src/App.vue` — app shell, bottom user tabs, boot/error/toast UI; no global hero.
- `web-vue/src/views/EventsView.vue` — home hero, participant selection, 100-point allocation, saved vote state, PNG story card, live results.
- `web-vue/src/components/events/HomeHero.vue` — photo hero, `Дыгын Оонньуулара` eyebrow, countdown, CTA hidden after saved vote.
- `web-vue/src/views/StatsView.vue` — support stats and fan leaderboard (`Топ-100`).
- `web-vue/src/views/PlayersView.vue` — two-column athlete photo grid and detail discipline tables.
- `web-vue/src/views/AdminView.vue` — browser-only admin result/standing/final forms plus analytics panel.
- `web-vue/src/components/admin/AdminAnalyticsPanel.vue` — no-library analytics KPI/cards/bar chart.
- `web-vue/src/composables/useTelegramInit.ts` — waits for late `window.Telegram.WebApp`, then calls `ready()`/`expand()`.
- `web-vue/src/composables/useAnalytics.ts` — generates random client ID and sends allowlisted analytics events.
- `web-vue/src/api/client.ts` — typed fetch wrapper; API base uses `import.meta.env.BASE_URL` or `VITE_API_BASE`.
- `web-vue/src/assets/styles/main.css` — global tokens, shell, cards, forms, nav, tables.
- `web/` — legacy vanilla frontend retained only for rollback via `FRONTEND_DIR=web`.

## Tabs

User TMA tabs:

- Главная — photo hero, countdown, vote flow, saved vote state, PNG story card.
- Рейтинг — support statistics and top-100 fan leaderboard.
- Атлеты — photo grid and athlete detail stats.
- Правила — rules, privacy note, iindev link.

Admin is not a TMA tab. Browser admin opens only at:

```text
https://iindiinda.duckdns.org/dygyn-bet/#/admin-login
```

Inside Telegram, `/#/admin*` redirects back to user flow when Telegram initData exists.

## Auth Behavior

### Telegram auth

`useTelegramInit()` polls for `window.Telegram?.WebApp` before the first API load. When found, it calls:

```ts
webApp.ready()
webApp.expand()
```

For user API calls, `src/api/client.ts` waits for this guard, reads `webApp.initData`, and sends:

```http
X-Telegram-Init-Data: <raw initData>
```

### Browser admin auth

Backend seeds/updates a hashed SQLite admin row from server env:

```env
ADMIN_WEB_USERNAME=<admin login>
ADMIN_WEB_PASSWORD=<admin password>
ADMIN_WEB_SESSION_HOURS=12
```

Login creates an HttpOnly `dygyn_admin_session` cookie. Admin APIs accept this session cookie. Telegram admin support exists server-side, but TMA navigation hides admin UI.

## Analytics

Current first-party events:

- `app_open`
- `rating_open`
- `rules_open`
- `participant_detail_open`
- `vote_save`
- `png_share`

Frontend sends:

- random client ID from localStorage;
- route path;
- allowlisted metadata (`event_id`, `participant_id`, `picks`, `shared`, `has_saved_vote`).

Backend stores only hashed client ID, hashed user-agent, sanitized path/metadata, and timestamp. It does not store raw Telegram ID, username, raw initData, IP, participant names, or vote text in analytics rows.

Admin analytics panel uses `/api/admin/analytics?days=14` and renders KPI cards, a daily bar chart, event totals, and top paths without external scripts.

## UI Safety

Dynamic text is rendered through Vue text bindings. `v-html` is disallowed by ESLint.

## Visual Direction

Current style follows `vault/wiki/architecture/design-direction.md` and root `DESIGN.md`:

- dark photo-first sports UI;
- warm gold accent;
- card-first layout;
- support progress bars;
- sticky save action only after a participant is selected;
- no casino/bookmaker visual language.

## Product Copy Rule

Frontend must keep no-money language visible in rules/privacy areas. Avoid betting, deposit, withdrawal, odds, payout, or prize wording without legal approval.

## PNG Story Card Sharing

Direct social app posting is not reliable from a Telegram Mini App web context. Current product exposes one visible action after saved vote: `PNG для сторис`.

Under the hood:

- native file share when available;
- download fallback;
- no restricted social network names in UI copy.

PNG card includes selected participant photo(s), confidence points, name, origin/region/ulus, and CTA `Заходи и голосуй за своего фаворита` plus `@dygyn_games_bet_bot`.

## Vue Build and Bundle Check

```bash
cd web-vue
npm ci
npm run build        # production /dygyn-bet/ base
npm run build:local  # local FastAPI root base
```

Build writes `dist/bundle-stats.html` via `rollup-plugin-visualizer` and enforces initial JS gzip budget <=150KB. Current build stays near 42KB gzip initial JS.

## Manual Smoke Check

1. Open TMA from Telegram bot button.
2. Confirm hero, countdown, and no admin tab.
3. Pick 1–2 participants.
4. Distribute exactly 100 points.
5. Save vote; confirm voting controls hide and PNG action remains.
6. Generate/download/share PNG card.
7. Open Rating; confirm support stats and top-100 leaderboard.
8. Open Athletes; open a detail card and confirm discipline table uses `Итог` column.
9. Open Rules; verify privacy note and iindev link.
10. In browser, open `/#/admin-login`; log in and confirm analytics panel plus admin forms.
