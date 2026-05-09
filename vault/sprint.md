# Sprint — Product Stabilization

## Goal

Turn the existing Dygyn Telegram Mini App into a reliable voting product with clear project memory in `vault/`.

## Current Tasks

| # | Task | Status |
|---|------|--------|
| 0.1 | Add vault-first project memory | DONE |
| 0.2 | Keep old `wiki/` as historical source docs | DONE |
| 0.3 | Replace demo players/events with verified real data | DONE |
| 0.3a | Allow up to two participant picks per user/event | DONE |
| 0.3b | Add PNG story card | DONE |
| 0.4 | Validate Telegram launch flow with real bot token and HTTPS URL | TODO |
| 0.5 | Add or improve admin data-entry workflow | PARTIAL |
| 0.6 | Add source URLs for all real player history records | TODO |
| 0.7 | Decide deployment target and backup plan | DONE |
| 0.8 | Scout existing `iind-vps` route deployment | DONE |
| 0.9 | Deploy preview to `iindiinda.duckdns.org/dygyn-bet/` | DONE |
| 0.10 | Configure real admin Telegram IDs on VPS | OPTIONAL |
| 0.11 | Split API and bot into separate systemd services | DONE |
| 0.12 | Add Игры Дыгына — голосование design direction | DONE |
| 0.13 | Restyle frontend toward sports voting UI | DONE |
| 0.14 | Switch vault workflow to compact QUICK_START mode | DONE |
| 0.15 | Record `new_brief.md` as canonical MVP brief | DONE |
| 0.16 | Design target 100-point allocation model | DONE |
| 0.17 | Implement 100-point allocation backend/frontend | DONE |
| 0.18 | Add participant discipline stat tables for all 7 Dygyn disciplines | DONE |
| 0.19 | Add mandatory admin-only TMA tab for live result/finish operations | DONE |
| 0.20 | Add CSV import validator/importer for Dygyn 2026 data pack | DONE |
| 0.21 | Expose participant discipline stats in API/frontend | DONE |
| 0.22 | Implement 100-point allocation voting model | DONE |

## Current Priority

1. Keep product legally safe: votes only, no money.
2. Fix and QA browser admin direct-route/session behavior.
3. Publish final privacy contact/deletion procedure.
4. Add analytics retention cleanup.
5. Run real mobile Telegram QA and browser admin QA.
6. Add deploy automation and restore-tested backups.

## Success Criteria

- Project sessions start from `vault/`.
- Product can run locally with `ALLOW_DEV_LOGIN=true`.
- Production config has `ALLOW_DEV_LOGIN=false`, real `BOT_TOKEN`, real `ADMIN_IDS`, and HTTPS `WEB_APP_URL`.
- All real sports data has manually checked sources.
- Voting model enforces a 100-point confidence scale across 1–2 participants.
