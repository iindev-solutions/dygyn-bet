# Design Direction — Dygyn Fan Vote

## Source Reference

Root `DESIGN.md` is canonical for current frontend visual identity.

## Current Direction

Style name: `Northern Arena`.

Goal: photo-first Telegram Mini App that feels premium, local, and sports-focused. Users should understand the product on the first screen: choose 1–2 athletes, distribute 100 confidence points, follow support and results.

## Core Rules

- One strong hero only on the main screen.
- Do not repeat the event banner on every tab.
- Keep copy short and functional.
- Use athlete photos as primary visual material.
- Use Yakut ornament as sparse SVG accent only.
- Use warm gold only for highlights and primary actions.
- Keep product clearly non-betting: no odds, balance, deposits, withdrawals, payouts, or money-prize language.
- Do not mention restricted social network names in UI copy; show neutral social icon links only when athlete social URLs exist.

## Screen Model

### Main

- Photo collage from participant avatars plus fallback logo/photo.
- Eyebrow says `Дыгын Оонньуулара`; headline says `Голосуй за фаворита`.
- Short bot description.
- Countdown to event start from `starts_at`.
- CTA scrolls to voting.
- No duplicate hero stats above the CTA.

### Vote

- Participant support list before save.
- Select up to 2 athletes.
- Allocate exactly 100 confidence points.
- Sticky save action appears only after a participant is selected.
- After saved vote, hide voting controls and show saved choice plus only `PNG для сторис`.
- No active-event summary card when there is only one event.

### Athletes

- Two-column photo grid.
- Each tile shows portrait, name, origin, stats button, optional neutral social icon.
- Detail view holds bio/history/discipline tables/source/social link.

### Rating

- Support ranking and fan leaderboard only.
- No decorative hero.

### Rules

- Short product/legal rules.
- No betting/money mechanics.

### Admin

- Browser-only operational cards and forms at `/#/admin-login`.
- No TMA bottom-nav admin tab; `/#/admin*` redirects away inside Telegram when initData exists.
- No decorative hero.

## Implemented Notes

- Global App hero removed from secondary screens.
- Main hero moved into Events view as `HomeHero`.
- Countdown composable added.
- Athletes list changed to photo grid via `PlayerGridCard`.
- Generic social icon support added for future `social_url` / `social_links` data.
- Share copy no longer names restricted social networks.
- Duplicate hero stats, active-event summary card, share/copy buttons, and TMA admin tab removed.
