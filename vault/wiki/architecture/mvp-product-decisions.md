# MVP Product Decisions

## Source

- `new_brief.md` is the canonical MVP brief.
- This file records product decisions from the 2026-05-06 discussion.

## Product Shape

- Telegram bot is a minimal, polished entry point.
- Telegram Mini App contains the rich UI: events, participants, voting, stats, rating, profile.
- Product remains voting/support only: no money, odds, deposits, withdrawals, payouts, or valuable prizes.

## Voting Model

- One vote per user per event.
- One vote can contain 1–2 selected participants.
- Each user has a 100-point virtual confidence scale per event.
- User distributes points across selected participants.
- Valid examples: `100`, `70/30`, `50/50`.
- Backend must validate: event is open, not past `closes_at`, user not blocked, participants belong to event, 1–2 participants, all points positive, sum is exactly 100.
- User may change the vote only before `closes_at`.

## Support Stats

- `total_predictions` = number of users who saved a vote for the event.
- `supporters_count` = number of votes containing a participant.
- `confidence_sum` = sum of points allocated to a participant.
- `support_percent` = participant `confidence_sum / total_confidence * 100`.
- UI wording: support, vote, rating points, confidence points. Avoid betting/casino wording.

## Scoring

- After the event, admin sets official results.
- MVP scoring: if user selected the winner, add only the points allocated to that winner.
- If winner was not selected, add `0`.
- No odds, multipliers, prize balance, or payout logic.

## Bot UX

- Bot stays simple: `/start`, open Mini App, participants, vote, rating, rules.
- Large tables and voting flows belong in the Mini App, not Telegram chat messages.

## Admin UX

- Admin panel is required, not optional.
- Admin should be inside the Mini App and visible only to `ADMIN_IDS`.
- MVP admin tasks: import/validate CSV data pack, manage events, manage participants, attach participants to events, update Day 1/Day 2 discipline results, publish provisional/official standings, finish event, and trigger final rating-score awarding.
- Admin operations need confirmation and audit-friendly timestamps; avoid editing DB manually during live games.

## Participant Detail and Discipline Stats

- Each participant should have a detail page with profile, support stats, and verified sport history.
- Show a table for all 7 Dygyn disciplines by year/event.
- Store display and sortable values separately:
  - `result_text`: e.g. `5:40`, `50 reps`.
  - `result_value`: e.g. `340` seconds, `50` reps.
- Required discipline metadata: code, name, unit, sort order, whether lower value is better.
- Every real result needs a source URL or source note.

## Two-Day Event Results

- Dygyn Games run across two days.
- App must support result updates after Day 1, Day 2, and final finish.
- Voting closes before the event/`closes_at`; day results are informational until final official finish.
- UI should show Day 1, Day 2, overall standings, final winners, `provisional/official` state, and last updated time.
- Admin must be able to enter or correct discipline results during/after each day.
- Leaderboard points are awarded only after final official winner is set, not from provisional day standings.

## Data Needed

- Exact list of the 7 Dygyn disciplines.
- Unit and ranking direction for each discipline.
- Verified participant list: name, region/ulus/city, photo, short bio.
- Verified prior-year results by participant and discipline.
- Source links/files for all real stats.
- Preferred import format: Google Sheet or CSV.

## Infra Assumption

- Expected scale: likely a few thousand users; possible peak 10k–15k voters.
- Current FastAPI + SQLite + nginx + VPS setup is enough for this scale.
- 15k voters with up to 3 selected participants means about 45k vote-item rows per event, which is small for SQLite.
- Required ops: WAL, indexes, POST rate limit, DB backup before deploy/result settlement, no frontend-trusted user IDs.
- Move to PostgreSQL only after heavier analytics, many concurrent writes, or roughly 100k+ users.

## Implementation Order

1. Backend-first vote allocation model and validation.
2. `closes_at`, event stats, event leaderboard, profile/vote history APIs.
3. Admin close/finish/result endpoints and CSV import path.
4. Frontend 5-screen brief alignment with 100-point allocation UI.
5. Participant detail pages and discipline-stat tables.
6. Real data import and mobile Telegram QA.
