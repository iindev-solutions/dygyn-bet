# Vault Workflow

## Default Session Start

Read only:

1. `vault/QUICK_START.md`

Then decide if deep docs needed.

## Deep Docs On Demand

- Code/layout task → `vault/CODE_MAP.md`
- Design task → `vault/wiki/architecture/design-direction.md`
- Deploy task → `vault/wiki/services/deployment.md`
- API task → `vault/wiki/services/api.md`
- DB task → `vault/wiki/architecture/data-model.md`
- Frontend task → `vault/wiki/services/frontend.md`

Do not read all wiki by default.

## During Work

- Surgical changes only.
- No speculative features.
- Preserve no-money product boundary.
- Backend must validate raw Telegram `initData`; never trust browser identity.
- If important project state changes, put it in `QUICK_START.md`.

## Session End

Always for meaningful work:

1. Update `vault/logs/changelog.md` terse.
2. Update `vault/QUICK_START.md` if state/next changed.

Update deep docs only when facts changed.

## Changelog Style

Use compact blocks:

```md
## YYYY-MM-DD — Short Title
- Changed: ...
- Verified: ...
- Next: ...
```

No long prose. No duplicated summaries.

## Verification

Prefer concrete checks:

- `pytest`
- `node --check web/app.js`
- `python -m py_compile app/*.py tests/*.py`
- `curl /health`
- mobile Telegram smoke when UI/auth changes
