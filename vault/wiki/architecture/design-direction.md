# Design Direction — Dygyn Fan Arena

## Source Reference

Root file `ref.md` contains the working visual/product reference in Russian. This document is the canonical English summary for the vault.

## Positioning

The product must feel like a sports fan prediction arena, not a bookmaker.

Target style name:

```text
Dygyn Fan Arena
```

Character:

- dark;
- fast;
- sports-oriented;
- Telegram-native;
- no casino/betting vibe;
- light Yakut festive accent through warm gold, used sparingly.

## Design Principles

Do:

- use event cards;
- show large support percentages;
- show participant cards with progress bars;
- make the main action obvious;
- keep copy short;
- show fan support and leaderboard clearly;
- keep no-money positioning visible.

Do not use:

- odds;
- balances;
- deposits;
- withdrawals;
- bookmaker terminology;
- red/green win/loss betting patterns;
- complex charts before the product needs them.

## Preferred Terms

Use:

- prediction;
- fan pick;
- confidence points;
- fan support;
- leaderboard;
- performance history.

Avoid:

- bet;
- odds;
- win/winnings;
- bank;
- withdrawal;
- deposit;
- payout.

## Visual System

Core palette:

```css
--bg: #0f1115;
--card: #171a21;
--card-2: #1f2430;
--text: #f4f6fb;
--muted: #9aa3b2;
--accent: #f2b84b;
--accent-2: #2ea6ff;
--success: #40c979;
--danger: #ff5c6c;
--border: rgba(255,255,255,.08);
```

Gold is for main actions, badges, and highlights only. Do not flood the interface with gold.

## Screen Model

### Main Screen

Purpose: user instantly understands what to do.

Content:

- product title;
- active event card;
- event status;
- participant count;
- vote count;
- top support preview;
- open/select action.

### Event Screen

Purpose: choose up to three participants.

Content:

- event title/status;
- participant cards;
- support percentage and progress bar;
- confidence points controls;
- sticky/obvious save button;
- share card actions after selection.

### Support Stats

Purpose: show who fans support.

Content:

- ranked participant list;
- support percentage;
- vote count;
- confidence point total;
- progress bars.

### Participant Card

Purpose: show past results.

Content:

- name;
- region/ulus;
- recent years;
- placements;
- discipline results when data model is expanded;
- source URLs.

### Fan Leaderboard

Purpose: gamification.

Content:

- rank;
- user name;
- score;
- pick count;
- correct pick count.

## Current Implementation Notes

Implemented first visual pass:

- dark sports UI;
- bottom navigation;
- arena hero card;
- participant support cards;
- progress bars;
- confidence chips;
- sticky save action;
- story-card sharing retained.

## Next Design Tasks

- Add admin-only TMA tab after `ADMIN_IDS` is configured.
- Expand participant stats model for discipline-level historical data.
- Add participant detail view or expanded cards.
- Test final look in Telegram dark and light themes on iOS/Android.
