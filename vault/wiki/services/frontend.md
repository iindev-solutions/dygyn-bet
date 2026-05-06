# Frontend Service

## Responsibilities

- Provide Telegram Mini App user interface.
- Initialize Telegram WebApp SDK.
- Send raw Telegram initData to backend.
- Render events, participants, picks, statistics, player history, rules, and leaderboard.

## Main Files

- `web/index.html` — app shell and tabs.
- `web/app.js` — client state, API calls, rendering, event handlers.
- `web/styles.css` — UI styling using Telegram theme variables.

## Tabs

- Events — event list, event detail, up to three participant choices, confidence slider, share actions.
- Stats — leaderboard.
- Players — participant profiles and history.
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
3. Select event.
4. Move confidence slider.
5. Pick up to three participants.
6. Save the vote.
7. Confirm toast and updated statistics.
8. Copy share text or download the story card.
9. Open stats tab.
10. Open players tab.
11. Open rules tab and verify no-money warning.
12. Repeat inside Telegram with real HTTPS URL and bot button.
