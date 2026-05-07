# AGENTS.md — dygyn-bet

> Build with discipline. Record with `vault/`.

This project uses one hard rule:

`vault/` is the source of truth.

## Mandatory Session Start

Read first:

1. `vault/QUICK_START.md`

Read deep docs only when task needs them:

- `vault/CODE_MAP.md`
- `vault/wiki/architecture/*`
- `vault/wiki/services/*`
- legacy `wiki/` only when explicitly needed.

## Mandatory Session End

Before closing meaningful work, update terse:

1. `vault/logs/changelog.md`
2. `vault/QUICK_START.md` if current state or next tasks changed

Update deep docs only when their facts changed.

## Language Rule

All content inside `vault/` must be written in English.

## Stack

- FastAPI backend
- Vanilla Telegram Mini App frontend
- Aiogram bot
- SQLite database for early product version
- Pytest tests

## Product Rule

This product is a prediction/voting service only. Do not add real-money betting, deposits, withdrawals, odds, paid entry, or prizes with monetary value without a legal decision.

## Token Rule

Keep vault updates compact. No duplicate long explanations. Prefer short bullets.

## Principle

Do not leave important project knowledge only in chat. Move it into `vault/`.
