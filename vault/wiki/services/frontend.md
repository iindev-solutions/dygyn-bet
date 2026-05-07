# Frontend Service

## Responsibilities

- Provide Telegram Mini App user interface.
- Initialize Telegram WebApp SDK.
- Send raw Telegram initData to backend.
- Render events, participants, picks, statistics, player history, discipline-result tables, rules, and leaderboard.

## Main Files

- `web/index.html` — app shell and tabs.
- `web/app.js` — client state, API calls, rendering, event handlers.
- `web/styles.css` — UI styling using Telegram theme variables.

## Tabs

- Games — event hero, event list, event detail, 1–3 participant choices, 100-point allocation controls, equal `33/33/33` split, share actions.
- Support — support statistics and leaderboard.
- Players — participant cards, detail view, profile fields, and discipline-result tables.
- Admin — `ADMIN_IDS`-only live operations: Day 1/Day 2 discipline results, standings, finish event.
- Rules — product rules and no-money notice.

## Auth Behavior

`web/app.js` reads:

```js
const tg = window.Telegram?.WebApp;
```

When present, it calls:

```js
tg.ready();
tg.expand();
```

Frontend can run at root (`/`) or behind a prefix such as `/dygyn-bet/`. It derives the base path from `static/app.js` and prefixes API calls.

For API calls, it sends:

```http
X-Telegram-Init-Data: tg.initData
```

## API Wrapper

`api(path, options)`:

- sets `Content-Type: application/json`;
- adds Telegram initData header if available;
- parses JSON response;
- throws error from `json.detail` when response is not OK.

## UI Safety

Dynamic text uses `escapeHtml()` before inserting into HTML templates.

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

## Manual Smoke Check

1. Open locally with `ALLOW_DEV_LOGIN=true`.
2. Confirm user line loads.
3. Confirm event hero card renders.
4. Select event.
5. Pick 1–3 participants.
6. Distribute 100 confidence points, or use `33/33/33` for three participants equally.
7. Save the vote through the sticky save action.
8. Confirm toast and updated statistics.
9. If admin, open Admin tab and test a provisional result/standing on a non-production DB first.
10. Copy share text or download the story card.
10. Open support tab.
11. Open players tab.
12. Open rules tab and verify no-money warning.
13. Repeat inside Telegram with real HTTPS URL and bot button.
