# Project Vision

## Product

`dygyn-bet` is a Telegram Mini App for voting around the Dygyn Games.

Despite the repository name, the product must behave as a voting service, not a betting product.

## Target Users

- Telegram users interested in the Dygyn Games.
- Users who want to support a participant and see community sentiment.
- Administrators who enter participants, events, history, and final results.

## Core Problem

Users need a lightweight way inside Telegram to:

- pick who they support in an event;
- express confidence with virtual points;
- see support distribution across participants;
- compare rating scores after official results are manually entered.

## Primary Workflow

1. User opens the Telegram bot.
2. Bot sends a Mini App button.
3. User opens the Mini App inside Telegram.
4. Backend verifies raw Telegram `initData`.
5. User selects an event and 1–2 participants.
6. User distributes virtual confidence points across selected participants on a 100-point scale.
7. User can share text or download an Instagram Stories card for manual repost.
8. App shows vote counts, confidence totals, percentages, player history, and leaderboard.
8. Admin enters results after an event.
9. Correct picks receive rating points.

## In Scope

- Telegram bot launch button.
- Telegram Mini App frontend.
- Server-side Telegram initData verification.
- SQLite storage.
- One vote per user/event with 1–2 participants inside it.
- 100-point virtual confidence scale per event vote.
- Event locking after close time, start time, or admin status change.
- Participant history and discipline-level stats with source URLs.
- Admin APIs for players, history, events, and settlement.

## Out of Scope

- Real-money bets.
- Deposits or withdrawals.
- Odds.
- Paid entry.
- Monetary or property-value prizes for voting results.
- Bookmaker mechanics.
- KYC or age verification.
- Automatic official-result scraping.
- Complex admin panel.

## Non-Negotiable Product Boundary

Use terms like vote, rating points, confidence points, support. Avoid product logic or UI based on bet, deposit, withdrawal, odds, win, payout, or balance unless a separate legal decision changes the product model.
