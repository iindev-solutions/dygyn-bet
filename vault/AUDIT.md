# Audit — dygyn-bet

Date: 2026-05-09

## Scope

Product, privacy, analytics, frontend UX, backend/API, storage, admin, deploy.

## Current Verdict

MVP is safe enough for voting pilot if privacy copy stays visible and analytics remains first-party/minimal. Biggest remaining risks are admin/browser QA, legal/privacy formalization, and real-device Telegram QA.

## Product / Legal

Status: mostly OK.

- App is voting/prediction only.
- No deposits, withdrawals, odds, payouts, balances, or money prizes in product rules.
- Rules mention virtual confidence points, not money.
- Needed before wider public launch: formal privacy policy text and operator/contact details.

Risk: medium until final privacy policy/contact is published.

## Personal Data

Stored by product:

- Telegram ID;
- username, first name, last name, language code;
- votes/picks and confidence points;
- timestamps;
- admin session/audit rows.

Analytics storage now avoids:

- raw Telegram ID;
- username/name;
- IP;
- raw initData;
- participant names or vote text.

Analytics stores:

- event name;
- hashed random client ID;
- route path without query;
- allowlisted metadata IDs/counts only;
- hashed user-agent;
- timestamp.

Risk: medium, because Telegram profile + vote data is still personal data in main product tables.

## Analytics

Decision: custom SQLite analytics, not Ackee, for MVP.

Reasons:

- avoids MongoDB/service dependency;
- keeps data in same backup/deploy model;
- can enforce project-specific allowlist;
- enough for MVP dashboard.

Implemented events:

- `app_open`
- `rating_open`
- `rules_open`
- `participant_detail_open`
- `vote_save`
- `png_share`

Admin dashboard:

- KPI cards;
- daily bar chart;
- event totals;
- top paths.

Risk: low if retention is later added.

Next improvement:

- add retention job or admin action to purge analytics older than 180 days.

## Frontend UX

Status: improved.

- One main hero only.
- TMA user nav has no admin tab.
- Admin browser route is separate.
- Saved vote hides voting controls and shows only PNG action.
- Athlete list is photo grid.
- Participant detail table removed duplicated place/points columns.
- Rules include privacy note and iindev link.

Risk: medium until real mobile Telegram QA.

## Backend / API

Status: good for MVP.

- Telegram initData required for user APIs.
- Browser admin uses HttpOnly session cookie.
- Admin mutations audited.
- Source URLs validated.
- Rate limit exists.
- Health check includes DB/disk/frontend.
- Analytics endpoint has allowlisted event names and sanitized metadata.

Risk: low/medium.

Next improvements:

- QA deployed direct browser `/#/admin` refresh/session rehydration in production browser;
- add tests for `/api/admin/analytics` HTTP auth path;
- add retention cleanup for expired admin sessions and analytics;
- move FastAPI deprecated `on_event` to lifespan later.

## Admin

Status: separated from TMA.

- Browser login only at `/#/admin-login`.
- TMA redirects `/#/admin*` away when Telegram initData exists.
- Admin panel includes analytics and result forms.
- Direct browser `/#/admin` session rehydration is deployed; production browser QA pending.

Risk: medium until browser admin QA on safe data.

## Deployment / Ops

Status: OK.

- App isolated under `/dygyn-bet/`.
- Existing root app untouched.
- Static dist backup taken before deploys.
- SQLite backup script exists.
- Services monitored through systemd.

Risk: medium due to SQLite single-node backup discipline.

Next improvements:

- scheduled DB backups verified by restore test;
- deploy script to reduce manual tar/copy risk;
- retention script for analytics.

## Must Do Before Public Push

1. QA browser admin on safe data, including direct `/#/admin` with valid/expired session.
2. Publish final privacy policy/operator/contact details.
3. Real mobile Telegram QA.
4. Add analytics retention plan/job.
5. Add restore test for DB backups.

## Nice Later

- Admin UI for imports/events/participants.
- More analytics charts: funnel conversion, participant detail opens, PNG conversion by day.
- CSV export for analytics aggregates.
- Playwright smoke for main TMA routes.
