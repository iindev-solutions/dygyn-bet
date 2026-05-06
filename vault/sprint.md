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

## Current Priority

1. Keep product legally safe: fan votes only, no money.
2. Replace demo data before any public launch.
3. Test Telegram auth and TMA open flow in real Telegram.
4. Add operational notes after deployment target is known.

## Success Criteria

- Project sessions start from `vault/`.
- Product can run locally with `ALLOW_DEV_LOGIN=true`.
- Production config has `ALLOW_DEV_LOGIN=false`, real `BOT_TOKEN`, real `ADMIN_IDS`, and HTTPS `WEB_APP_URL`.
- All real sports data has manually checked sources.
