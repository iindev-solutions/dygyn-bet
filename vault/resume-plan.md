# Resume Plan

## Stop Point

- `vault/` has been added and initialized from the vault-first template.
- Existing Russian `wiki/` docs were studied and summarized into English canonical vault docs.
- Codebase is a FastAPI + aiogram + vanilla JS Telegram Mini App product.
- Current database is SQLite and seeds demo players/events automatically when empty.
- App currently allows a user to select up to three participants per event.
- Target MVP model from `new_brief.md`: one vote per user/event, 100 total confidence points distributed across 1–3 participants.
- `POST /api/picks` currently accepts `player_ids` and replaces current user's picks for the event.
- Frontend includes share text, native share, and generated PNG story card for manual Instagram Stories repost.
- Frontend now follows Игры Дыгына — голосование direction: dark sports cards, bottom navigation, support progress bars, confidence chips, and sticky save action.
- Frontend now supports prefix deployment such as `/dygyn-bet/` by deriving API base path from `static/app.js`.
- VPS `iind-vps` now hosts the app under `https://iindiinda.duckdns.org/dygyn-bet/` without touching existing public root.
- Server API service is `dygyn-bet.service`, bot service is `dygyn-bet-bot.service`, app path is `/opt/dygyn-bet`, local API port is `127.0.0.1:8010`.

## Next Step

1. Read `vault/master_index.md`, `vault/WORKFLOW.md`, `vault/sprint.md`, and this file.
2. For product/architecture work, read `vault/wiki/architecture/*`.
3. For implementation work, read `vault/CODE_MAP.md` and relevant service doc.
4. Next likely deployment task: add real `ADMIN_IDS` to `/opt/dygyn-bet/.env`, restart `dygyn-bet.service`, and test bot `/start` from Telegram.
5. Next likely technical task: implement 100-point allocation model backend-first, preserving no-money language.
6. Next likely data task: collect exact 7 Dygyn disciplines, units, ranking direction, participant list, and source-backed results.
7. Next likely validation task: install dependencies and run full `python -m pytest`.
8. Next likely product task: manually test voting and story-card sharing on mobile Telegram.

## Session Restart Prompt

```text
Read vault/master_index.md, vault/WORKFLOW.md, vault/sprint.md, and vault/resume-plan.md.
This is dygyn-bet: Telegram Mini App voting for Dygyn Games, no money. Continue from the current sprint priorities and update vault before ending meaningful work.
```
