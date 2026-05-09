---
version: beta
name: Dygyn Fan Vote
summary: Photo-first Telegram Mini App for fan confidence voting around the Dygyn Games.
colors:
  bg: "#07090D"
  bg-2: "#0F1218"
  card: "#12151B"
  card-2: "#1B2028"
  text: "#FFF6E8"
  muted: "#B8AD9B"
  accent: "#E2B152"
  accent-soft: "#FFD98B"
  accent-text: "#201405"
  info: "#69BFFF"
  success: "#41CE7A"
  danger: "#FF6575"
  line: "rgba(255,224,161,.16)"
  line-strong: "rgba(255,224,161,.28)"
typography:
  display: "Iowan Old Style, Noto Serif, Georgia, Times New Roman, serif"
  body: "-apple-system, BlinkMacSystemFont, Inter, Segoe UI, Roboto, Arial, sans-serif"
layout:
  max-width: 520px
  bottom-nav: fixed
  card-radius: 24px
  hero-radius: 34px
---

# Design System — Dygyn Fan Vote

## Product Feel

A premium sports fan app inside Telegram. The first screen must feel like a finished launch product: dark arena mood, athlete photos, warm gold accent, concise promise, and a countdown to the start.

It is not a bookmaker. No casino styling, odds, balances, deposits, payouts, or money-prize language.

## Core Rule

One strong hero only on the main screen. No repeated event banner across every tab.

Each screen must answer one job:

- Main: explain bot, show photos, countdown, CTA to vote.
- Vote: choose 1–2 athletes, distribute 100 confidence points, save, then show only saved choice + PNG.
- Rating: show support and fan leaderboard.
- Athletes: browse photo grid, open stats.
- Rules: short legal/product rules.
- Admin: browser-only operational forms, no TMA bottom dock.

## Visual Direction

Style name: `Northern Arena`.

Character:

- dark, cinematic, photo-first;
- gold as rare highlight, never flood;
- Yakut ornament only as sparse SVG mask/accent;
- large rounded photo cards;
- crisp sans body, ceremonial serif display headings;
- glassy cards with subtle borders and shadows;
- bottom Telegram-native dock.

## Copy Rules

Keep copy short and direct.

Use:

- vote;
- fan choice;
- confidence points;
- support;
- leaderboard;
- athlete stats;
- live results.

Avoid repeated product title. Use it only where context is required. Do not place the same event banner on secondary screens.

Do not mention restricted social network names in UI copy. If athlete social URLs exist, show only a neutral social icon link.

## Main Screen

Required content:

- photo collage from active participants plus fallback logo/photo;
- one-line context: `Дыгын Оонньуулара`;
- headline: short fan voting promise;
- one compact description of what bot does;
- countdown to event start from `starts_at`;
- primary CTA: choose participants.

No user/debug login line. No refresh button. No legal notice in hero.

## Athlete Browsing

Athlete list is a two-column photo grid.

Each tile:

- large portrait;
- name;
- region/origin;
- compact stats button;
- optional neutral social icon if social URL exists.

No long bio in list. Full profile, history, discipline tables, source links, and social icon live in detail view.

## Voting

Voting remains utilitarian and obvious:

- select up to two athletes;
- show support percent/progress;
- show selected points as `мой голос`;
- allocation must total exactly 100;
- presets stay visible for 1 or 2 selections;
- save button appears only after at least one athlete is selected and stays sticky above bottom nav;
- after a saved vote, hide voting controls and show saved choice plus PNG action only.

## Sharing

Share flow must be generic:

- single visible action: `PNG для сторис`;
- no separate copy/share buttons;
- native file share or download fallback may happen under the hood;
- no restricted social network names in UI copy.

Story/PNG image should show selected athlete photo, name, origin, confidence points, and bot CTA.

## Component Guidance

Use Vue 3 Composition API with focused components:

- `HomeHero`: main hero, photo collage, countdown, CTA.
- `useCountdown`: timer state and derived countdown parts.
- `PlayerGridCard`: one athlete tile.
- `SocialIconLink`: neutral social icon link.

Global CSS holds tokens, app shell, cards, forms, nav, tables. Feature components own scoped layout details.

## Do / Don't

Do:

- make photos dominant;
- use short labels;
- keep gold meaningful;
- keep secondary screens calm;
- preserve Telegram small-screen readability;
- keep admin plain and reliable.

Don't:

- repeat the event banner everywhere;
- write long promotional paragraphs;
- use betting/casino language;
- mention restricted social network names in UI;
- hide the 100-point total;
- add animation that hurts TMA performance.
