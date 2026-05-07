---
version: alpha
name: Игры Дыгына — голосование
description: Dark sports voting visual identity for the Dygyn Games Telegram Mini App.
colors:
  primary: "#0F1115"
  secondary: "#171A21"
  tertiary: "#F2B84B"
  neutral: "#F4F6FB"
  bg-raised: "#121621"
  card-elevated: "#1F2430"
  text-muted: "#9AA3B2"
  gold-soft: "#FFD989"
  blue: "#2EA6FF"
  success: "#40C979"
  danger: "#FF5C6C"
  line: "#2A2E38"
  ink: "#10131A"
typography:
  h1:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Roboto, Arial, sans-serif"
    fontSize: 40px
    fontWeight: 900
    lineHeight: 0.96
    letterSpacing: -0.055em
  h2:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Roboto, Arial, sans-serif"
    fontSize: 21px
    fontWeight: 900
    lineHeight: 1.15
    letterSpacing: -0.02em
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Roboto, Arial, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Roboto, Arial, sans-serif"
    fontSize: 12px
    fontWeight: 900
    lineHeight: 1.2
    letterSpacing: 0.12em
rounded:
  sm: 14px
  md: 18px
  lg: 24px
  xl: 26px
  full: 999px
spacing:
  xs: 8px
  sm: 10px
  md: 14px
  lg: 18px
  xl: 24px
components:
  app-shell:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    width: 520px
    padding: 14px
  bottom-nav:
    backgroundColor: "{colors.bg-raised}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    height: 66px
  card:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: 16px
  event-card:
    backgroundColor: "{colors.card-elevated}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: 18px
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: 52px
  button-secondary:
    backgroundColor: "{colors.card-elevated}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.full}"
    height: 42px
  badge:
    backgroundColor: "{colors.card-elevated}"
    textColor: "{colors.tertiary}"
    rounded: "{rounded.full}"
    padding: 10px
  info-badge:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    padding: 10px
  progress:
    backgroundColor: "{colors.line}"
    textColor: "{colors.gold-soft}"
    rounded: "{rounded.full}"
    height: 9px
  valid-total:
    backgroundColor: "{colors.success}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    padding: 8px
  invalid-total:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    padding: 8px
  muted-copy:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text-muted}"
    typography: "{typography.body}"
---

## Overview

Игры Дыгына — голосование is a dark, premium sports interface for users following the Dygyn Games. It must feel like a Telegram-native voting app for support, voting, athlete stats, and live results — never like a casino or bookmaker.

The mood is compact, confident, and athletic: dark cards, sharp hierarchy, warm gold accents, clear progress bars, and readable result tables. The product should feel local and ceremonial through restraint, not decoration overload.

## Colors

The palette is dark-first with one main accent.

- **Primary (`primary`, #0F1115):** App foundation. Use for page background and bottom navigation.
- **Raised background (`bg-raised`, #121621):** Subtle depth behind fixed controls.
- **Secondary (`secondary`, #171A21):** Default surface for content blocks.
- **Elevated card (`card-elevated`, #1F2430):** Hero cards, selected states, secondary controls.
- **Neutral (`neutral`, #F4F6FB):** Primary readable text.
- **Muted text (`text-muted`, #9AA3B2):** Metadata, captions, helper copy.
- **Tertiary (`tertiary`, #F2B84B):** Primary actions, key badges, selected state, progress highlights.
- **Gold soft (`gold-soft`, #FFD989):** Progress gradients and small highlights only.
- **Blue (`blue`, #2EA6FF):** Secondary informational accent, used rarely.
- **Success (`success`, #40C979):** Valid states and completed actions.
- **Danger (`danger`, #FF5C6C):** Invalid totals, destructive warnings, errors.
- **Line (`line`, #2A2E38):** Borders and track backgrounds.

Gold must be used sparingly. It marks what matters; it must not flood the UI.

## Typography

Use the system sans stack for speed and Telegram-native feel. Typography should be bold enough for sports energy but not loud.

- **H1:** Very bold, tight, used for product/event title.
- **H2:** Card titles and screen sections.
- **Body:** Clear 16px reading text.
- **Label:** Small uppercase metadata, badges, and eyebrow text.

Avoid decorative fonts unless a future brand package explicitly supplies them.

## Layout

Mobile-first. Main width is capped at 520px and centered. Screens are built from stacked cards with 13–14px gaps and a fixed bottom navigation.

Core layout rules:

- Cards first, tables second, charts only when needed.
- Main CTA must be obvious and reachable near the bottom.
- Admin forms should remain simple: labeled fields, two-column groups on wide phones, one column on narrow screens.
- Result tables may scroll horizontally, but primary athlete/event cards should not.
- Keep copy short. Dense sports data is okay; decorative text is not.

## Elevation & Depth

Use soft depth, not glossy effects.

- Cards use subtle borders and low dark shadows.
- Hero cards can use a faint radial gold/blue glow.
- Sticky save/admin actions use blur and a dark translucent background.
- Avoid neon casino glow, spinning effects, flashing gradients, or red/green betting patterns.

## Shapes

The system is rounded and card-based.

- Default card radius: 24px.
- Input/button radius: 14–18px.
- Pills/badges: 999px.
- Photos: rounded rectangles, not hard circles, except small initials avatars.
- Progress bars: fully rounded.

## Components

Primary components:

- **Event hero:** Event title, status, participant count, vote count, top support preview.
- **Participant card:** Name, region, support stats, selected state, confidence allocation.
- **Confidence allocator:** 1–3 selected participants, exactly 100 total points, visible valid/invalid total.
- **Support progress:** Gold gradient bar over dark track.
- **Leaderboard row:** Rank, user name, pick count, score badge.
- **Participant detail:** Photo, bio, strengths, prior Dygyn note, result tables by year/event.
- **Live results block:** Day 1, Day 2, overall standings, provisional/official state, last updated time.
- **Admin form:** Plain operational UI for entering discipline results, standings, and final winner.

Components should use existing tokens before adding new styles.

## Do's and Don'ts

Do:

- Use support, vote, confidence points, rating points, leaderboard.
- Keep the no-money boundary visible in product copy.
- Show athlete stats and live results in clear tables.
- Make selected states unmistakable.
- Prefer simple controls over clever interactions.
- Preserve Telegram Mini App performance and small-screen readability.

Don't:

- Use bet, odds, payout, deposit, withdrawal, balance, jackpot, casino, win money, or bookmaker language.
- Add red/green betting psychology or odds boards.
- Hide the 100-point total from the voting screen.
- Make admin operations ambiguous; finishing an event must require confirmation.
- Overuse gold, glow, animations, or ornamental patterns.
