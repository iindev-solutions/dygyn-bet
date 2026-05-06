# Vault Workflow

## Session Start

Read these files in order:

1. `vault/master_index.md`
2. `vault/WORKFLOW.md`
3. `vault/sprint.md`
4. `vault/resume-plan.md`

Then read task-specific files:

- `vault/CODE_MAP.md`
- relevant docs under `vault/wiki/architecture/`
- relevant docs under `vault/wiki/services/`

## During Work

- Keep changes surgical.
- Do not add speculative features.
- Preserve the fan-prediction/no-money product boundary.
- If architecture, API, data model, deployment, or legal assumptions change, update `vault/` in the same session.
- Do not trust browser-supplied Telegram user data unless backend validates raw `Telegram.WebApp.initData`.

## Session End

Before closing meaningful work, update:

1. `vault/logs/changelog.md`

Update when relevant:

1. `vault/resume-plan.md`
2. `vault/sprint.md`
3. `vault/CODE_MAP.md`
4. `vault/SESSION_LEDGER.md`

## Verification

Prefer concrete checks:

- `pytest`
- API smoke checks via local server or FastAPI test client
- manual Telegram Mini App smoke check when Telegram behavior changes
- file tree review when documentation/vault structure changes

## Rule

Do not leave important state only in chat. Move it into `vault/`.
