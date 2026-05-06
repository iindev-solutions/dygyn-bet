# AGENTS.md — dygyn-bet

> Build with discipline. Record with `vault/`.

This project uses one hard rule:

`vault/` is the source of truth.

## Mandatory Session Start

Read these files in order at the start of every session:

1. `vault/master_index.md`
2. `vault/WORKFLOW.md`
3. `vault/sprint.md`
4. `vault/resume-plan.md`

Then read task-specific docs under `vault/wiki/` and `vault/CODE_MAP.md`.

## Mandatory Session End

Before closing meaningful work, update:

1. `vault/logs/changelog.md`

Update when relevant:

1. `vault/resume-plan.md`
2. `vault/sprint.md`
3. `vault/CODE_MAP.md`
4. `vault/SESSION_LEDGER.md`

## Language Rule

All content inside `vault/` must be written in English.

## Stack

- FastAPI backend
- Vanilla Telegram Mini App frontend
- Aiogram bot
- SQLite database for MVP
- Pytest tests

## Product Rule

This MVP is a fan-prediction/voting service only. Do not add real-money betting, deposits, withdrawals, odds, paid entry, or prizes with monetary value without a legal decision.

## Principle

Do not leave important project knowledge only in chat. Move it into `vault/`.
