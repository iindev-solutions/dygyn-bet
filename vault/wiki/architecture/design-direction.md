# Design Direction — Игры Дыгына — голосование

## Source Reference

Root file `ref.md` contains the working visual/product reference in Russian. This document is the canonical English summary for the vault.

## Positioning

The product must feel like a sports voting app, not a bookmaker.

Target style name:

```text
Игры Дыгына — голосование
```

Character:

- dark;
- fast;
- ceremonial A1 poster direction;
- sports-oriented;
- Telegram-native;
- no casino/betting vibe;
- Yakut SVG ornament accents through warm gold, used sparingly.

## Design Principles

Do:

- use a ceremonial app hero with SVG ornament strip and temporary photo preview;
- use event cards;
- show large support percentages;
- show participant cards with progress bars;
- make the main action obvious;
- keep copy short;
- show support and leaderboard clearly;
- keep no-money positioning in rules/legal copy, not noisy top-screen copy.

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

- vote;
- voting;
- confidence points;
- support;
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
--bg: #07090d;
--card: #111419;
--card-2: #1b2029;
--text: #f8f1e4;
--muted: #b4a996;
--accent: #d9a441;
--brown: #7a4b00;
--accent-2: #5eb6ff;
--success: #40c979;
--danger: #ff5c6c;
--border: rgba(255,224,161,.16);
```

Gold is for main actions, badges, and highlights only. Do not flood the interface with gold. Current live direction uses a ceremonial serif stack for a stronger local feel.

## Screen Model

### Main Screen

Purpose: user instantly understands what to do.

Content:

- SVG Yakut ornament strip;
- temporary photo preview area;
- product title;
- active event card;
- event status;
- participant count;
- vote count;
- top support preview;
- open/select action;
- no visible user-login line or refresh button in the hero.

### Event Screen

Purpose: choose up to two participants.

Content:

- event title/status;
- participant cards;
- support percentage and progress bar;
- confidence points controls with number input, slider, and quick presets;
- sticky/obvious save button above the bottom dock;
- share card actions after selection.

### Support Stats

Purpose: show who users support.

Content:

- ranked participant list;
- support percentage;
- vote count;
- confidence point total;
- progress bars.

### Players Tab Card

Purpose: quick athlete recognition and entry to detail.

Content:

- large athlete photo;
- name;
- region/ulus and city/village when known;
- short description;
- one `Open statistics` action.

Do not show a summary stat grid in the list card. Put full stats, history, source URLs, and discipline tables in the detail view.

### Leaderboard

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
- event hero card;
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
