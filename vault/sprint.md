# Sprint — Product Stabilization

## Goal

Turn the existing Dygyn Telegram Mini App into a reliable fan-prediction product with clear project memory in `vault/`.

## Current Tasks

| # | Task | Status |
|---|------|--------|
| 0.1 | Add vault-first project memory | DONE |
| 0.2 | Keep old `wiki/` as historical source docs | DONE |
| 0.3 | Replace demo players/events with verified real data | TODO |
| 0.3a | Allow up to three participant picks per user/event | DONE |
| 0.3b | Add Instagram Stories manual share card | DONE |
| 0.4 | Validate Telegram launch flow with real bot token and HTTPS URL | TODO |
| 0.5 | Add or improve admin data-entry workflow | TODO |
| 0.6 | Add source URLs for all real player history records | TODO |
| 0.7 | Decide deployment target and backup plan | TODO |
| 0.8 | Scout existing `iind-vps` route deployment | DONE |
| 0.9 | Deploy preview to `iindiinda.duckdns.org/dygyn-bet/` | DONE |
| 0.10 | Configure real admin Telegram IDs on VPS | TODO |
| 0.11 | Split API and bot into separate systemd services | DONE |
| 0.12 | Add Dygyn Fan Arena design direction | DONE |
| 0.13 | Restyle frontend toward sports fan arena UI | DONE |
| 0.14 | Switch vault workflow to compact QUICK_START mode | DONE |
| 0.15 | Record `new_brief.md` as canonical MVP brief | DONE |
| 0.16 | Design target 100-point allocation model | DONE |
| 0.17 | Implement 100-point allocation backend/frontend | TODO |
| 0.18 | Add participant discipline stat tables for all 7 Dygyn disciplines | TODO |

## Current Priority

1. Keep product legally safe: fan votes only, no money.
2. Implement canonical 100-point allocation model from `new_brief.md`.
3. Add verified participant discipline stats for all 7 Dygyn disciplines.
4. Replace demo data before any public launch.
5. Test Telegram auth and TMA open flow in real Telegram.

## Success Criteria

- Project sessions start from `vault/`.
- Product can run locally with `ALLOW_DEV_LOGIN=true`.
- Production config has `ALLOW_DEV_LOGIN=false`, real `BOT_TOKEN`, real `ADMIN_IDS`, and HTTPS `WEB_APP_URL`.
- All real sports data has manually checked sources.
- Prediction model enforces exactly 100 confidence points across 1–3 participants per user/event.
